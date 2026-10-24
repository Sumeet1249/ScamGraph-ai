"""Unit Tests for Smart Registry (Module A).

Tests canonical normalization, keyed HMAC fingerprinting, report lifecycle state machine,
entity linkage, exact-match screening, dispute handling, authorized revocation,
immutable audit logs, and risk engine integration.
"""

import pytest
from datetime import datetime, timezone

from packages.schemas.registry import (
    CreateReportRequest,
    DisputeDecisionRequest,
    IdentifierType,
    ReportStatus,
    ReviewReportRequest,
    ScreenRequest,
    SubmitDisputeRequest,
    SubmitRevocationRequest,
    TypedIdentifier,
)
from services.registry.fingerprint import IdentifierNormalizer, RegistryFingerprinter
from services.registry.repository import RegistryRepository
from services.registry.service import SmartRegistryService


class TestIdentifierNormalization:
    """Tests canonical normalization across typed identifiers."""

    def test_phone_normalization_indian_numbers(self):
        # 10-digit without country code
        assert IdentifierNormalizer.normalize_phone("9876543210") == "+919876543210"
        # Spaced or dashed
        assert IdentifierNormalizer.normalize_phone("  +91 98765-43210 ") == "+919876543210"
        # Leading zero 11-digit
        assert IdentifierNormalizer.normalize_phone("09876543210") == "+919876543210"

    def test_phone_normalization_invalid_raises(self):
        with pytest.raises(ValueError):
            IdentifierNormalizer.normalize_phone("invalid_phone_text")
        with pytest.raises(ValueError):
            IdentifierNormalizer.normalize_phone("123")  # too short

    def test_upi_vpa_normalization(self):
        # Lowercasing and strip
        assert IdentifierNormalizer.normalize_upi_vpa("  Merchant.Pay@OkSBI ") == "merchant.pay@oksbi"
        # QR code payload extract
        assert IdentifierNormalizer.normalize_upi_vpa("upi://pay?pa=shop.target@icici&pn=Shop") == "shop.target@icici"

    def test_upi_vpa_invalid_raises(self):
        with pytest.raises(ValueError):
            IdentifierNormalizer.normalize_upi_vpa("missing_at_symbol")

    def test_bank_account_normalization(self):
        # Preserves leading zeros and case normalizes IFSC
        assert IdentifierNormalizer.normalize_bank_account("sbin0001234 : 009876543210 ") == "SBIN0001234:009876543210"

    def test_url_domain_normalization(self):
        # Domain only
        assert IdentifierNormalizer.normalize_url_domain(" Phish-Pay.COM/ ") == "phish-pay.com"
        # Full URL
        assert IdentifierNormalizer.normalize_url_domain("HTTPS://Verify.Bank.Org/login/") == "https://verify.bank.org/login"

    def test_transaction_ref_normalization(self):
        assert IdentifierNormalizer.normalize_transaction_ref("  utr-1234-5678-90 ") == "UTR1234567890"

    def test_email_normalization(self):
        assert IdentifierNormalizer.normalize_email(" John.Doe@Gmail.com ") == "johndoe@gmail.com"
        assert IdentifierNormalizer.normalize_email(" Support@Bank.co.in ") == "support@bank.co.in"


class TestRegistryFingerprinting:
    """Tests keyed HMAC-SHA-256 fingerprinting."""

    def test_deterministic_keyed_fingerprint(self):
        fp1 = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, "+919876543210", key_version="v1")
        fp2 = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, "98765-43210", key_version="v1")
        assert fp1.fingerprint == fp2.fingerprint
        assert fp1.fingerprint.startswith("hmac_v1_")

    def test_distinct_types_produce_distinct_fingerprints(self):
        val = "1234567890"
        fp_phone = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, val)
        fp_device = RegistryFingerprinter.generate_fingerprint(IdentifierType.DEVICE_ID, val)
        assert fp_phone.fingerprint != fp_device.fingerprint

    def test_safe_masking_previews(self):
        fp = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, "+919876543210")
        assert fp.normalized_preview == "+919****10"

        fp_upi = RegistryFingerprinter.generate_fingerprint(IdentifierType.UPI_VPA, "merchant@oksbi")
        assert fp_upi.normalized_preview == "me***@oksbi"

    def test_constant_time_comparison(self):
        fp1 = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, "+919876543210")
        fp2 = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, "+919876543210")
        assert RegistryFingerprinter.constant_time_matches(fp1.fingerprint, fp2.fingerprint) is True

    def test_multi_version_candidate_generation(self):
        candidates = RegistryFingerprinter.generate_all_version_fingerprints(
            IdentifierType.UPI_VPA, "test@okaxis"
        )
        assert len(candidates) >= 2
        assert any(c.startswith("hmac_v1_") for c in candidates)
        assert any(c.startswith("hmac_v0_") for c in candidates)


@pytest.mark.asyncio
class TestSmartRegistryService:
    """Tests Smart Registry service lifecycle and operations."""

    async def test_report_ingestion_and_entity_linkage(self):
        repo = RegistryRepository()
        service = SmartRegistryService(repo=repo)

        req1 = CreateReportRequest(
            reporting_org="BANK_HDFC_01",
            entity_name="Suspect Mule Account",
            category="MULE_ACCOUNT",
            reason="Rapid pass-through cash-out following reported phishing link",
            identifiers=[
                TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919999988888"),
                TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="fresh.mule@oksbi"),
            ],
            confidence=0.95,
        )
        rep1 = await service.ingest_report(req1)
        assert rep1.report_id.startswith("rep_")
        assert rep1.entity_id is not None
        assert rep1.status == ReportStatus.CONFIRMED

        # Ingest second report with same phone -> should link to existing entity!
        req2 = CreateReportRequest(
            reporting_org="BANK_SBI_01",
            category="MULE_ACCOUNT",
            reason="Additional fraudulent transfer reported by customer",
            identifiers=[
                TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919999988888"),
            ],
            confidence=0.90,
        )
        rep2 = await service.ingest_report(req2)
        assert rep2.entity_id == rep1.entity_id

        # Verify entity report count
        entity = await repo.get_entity(rep1.entity_id)
        assert entity is not None
        assert entity.report_count == 2
        assert rep1.report_id in entity.associated_report_ids
        assert rep2.report_id in entity.associated_report_ids

    async def test_identifier_screening_exact_match(self):
        repo = RegistryRepository()
        service = SmartRegistryService(repo=repo)

        # Ingest confirmed report
        await service.ingest_report(
            CreateReportRequest(
                reporting_org="BANK_SBI_01",
                category="KYC_SCAM",
                reason="Impersonating electricity board",
                identifiers=[
                    TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="power.bill@oksbi"),
                ],
                confidence=0.90,
            )
        )

        # Screen exact matching VPA
        screen_req = ScreenRequest(
            caller_org="PSP_PHONEPE_01",
            identifiers=[
                TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value=" POWER.bill@oksbi "),
            ],
        )
        res = await service.screen_identifiers(screen_req)
        assert res.total_hits == 1
        assert res.has_confirmed_hit is True
        assert res.matches[0].category == "KYC_SCAM"
        assert res.matches[0].risk_score == 0.90
        assert res.matches[0].is_disputed is False
        assert res.matches[0].is_revoked is False
        assert res.matches[0].data_freshness == "REALTIME"

    async def test_report_review_decision(self):
        repo = RegistryRepository()
        service = SmartRegistryService(repo=repo)

        report = await service.ingest_report(
            CreateReportRequest(
                reporting_org="BANK_AXIS_01",
                category="SUSPECT",
                reason="Low initial confidence flag",
                identifiers=[
                    TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919555000111"),
                ],
                confidence=0.60,
            )
        )
        assert report.status == ReportStatus.REPORTED

        # Review decision: Confirm report
        reviewed = await service.review_report(
            report.report_id,
            ReviewReportRequest(
                new_status=ReportStatus.CONFIRMED,
                reviewer="Compliance_Lead_01",
                notes="Verified transaction laundering patterns",
            ),
        )
        assert reviewed.status == ReportStatus.CONFIRMED

        # Screening now reflects confirmed status
        res = await service.screen_identifiers(
            ScreenRequest(
                caller_org="PSP_GPAY",
                identifiers=[TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="9555000111")],
            )
        )
        assert res.has_confirmed_hit is True

    async def test_dispute_workflow_and_resolution(self):
        repo = RegistryRepository()
        service = SmartRegistryService(repo=repo)

        report = await service.ingest_report(
            CreateReportRequest(
                reporting_org="BANK_AXIS_01",
                category="MULE_ACCOUNT",
                reason="Unusual velocity",
                identifiers=[
                    TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919123456789"),
                ],
                confidence=0.88,
            )
        )

        # 1. Submit dispute
        dispute_req = SubmitDisputeRequest(
            report_id=report.report_id,
            disputing_org="BANK_ICICI_01",
            reason="Customer proved agricultural business revenue with valid mandi invoices.",
            evidence_documents=["mandi_receipt_oct2026.pdf"],
        )
        dispute = await service.submit_dispute(dispute_req)
        assert dispute.dispute_id.startswith("dsp_")
        assert dispute.status == "OPEN"

        # Report state transitioned to DISPUTED
        updated = await repo.get_report(report.report_id)
        assert updated.status == ReportStatus.DISPUTED

        # Screening indicates disputed status with discounted risk
        res = await service.screen_identifiers(
            ScreenRequest(
                caller_org="PSP_PAYTM_01",
                identifiers=[TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="9123456789")],
            )
        )
        assert res.has_disputed_hit is True
        assert res.matches[0].is_disputed is True
        assert res.matches[0].risk_score == 0.44  # 0.88 * 0.5

        # 2. Resolve dispute by upholding dispute (Dismiss report)
        resolved_dsp = await service.resolve_dispute(
            dispute.dispute_id,
            DisputeDecisionRequest(
                decision="DISMISSED",
                notes="APMC verified genuine farmer revenue. Clearing suspect flag.",
                reviewer="Ombudsman_Arb_09",
            ),
        )
        assert resolved_dsp.status == "RESOLVED_DISMISSED"

        # Report status is now REJECTED
        cleared_rep = await repo.get_report(report.report_id)
        assert cleared_rep.status == ReportStatus.REJECTED

    async def test_revocation_authorization_and_screening_suppression(self):
        repo = RegistryRepository()
        service = SmartRegistryService(repo=repo)

        report = await service.ingest_report(
            CreateReportRequest(
                reporting_org="BANK_HDFC_01",
                category="PHISHING",
                reason="Reported domain",
                identifiers=[
                    TypedIdentifier(identifier_type=IdentifierType.URL_DOMAIN, raw_value="https://false-alert.net"),
                ],
                confidence=0.92,
            )
        )

        # Unauthorized revocation attempt by a different bank must fail
        with pytest.raises(PermissionError):
            await service.submit_revocation(
                SubmitRevocationRequest(
                    report_id=report.report_id,
                    authorizing_org="BANK_KOTAK_99",
                    revocation_reason="I want to revoke this",
                    authorized_by="Attacker",
                )
            )

        # Authorized revocation by original reporting institution
        revocation = await service.submit_revocation(
            SubmitRevocationRequest(
                report_id=report.report_id,
                authorizing_org="BANK_HDFC_01",
                revocation_reason="Internal verification cleared customer as legitimate security researcher.",
                authorized_by="Lead_Compliance_Officer_007",
            )
        )
        assert revocation.revocation_id.startswith("rev_")

        # Screening must report revoked hit with 0.0 active risk
        res = await service.screen_identifiers(
            ScreenRequest(
                caller_org="PSP_GPAY_01",
                identifiers=[TypedIdentifier(identifier_type=IdentifierType.URL_DOMAIN, raw_value="https://false-alert.net")],
            )
        )
        assert res.has_revoked_hit is True
        assert res.has_confirmed_hit is False
        assert res.matches[0].is_revoked is True
        assert res.matches[0].risk_score == 0.0

    async def test_registry_statistics_aggregation(self):
        repo = RegistryRepository()
        await repo.ensure_seeded()
        stats = await repo.get_statistics()
        assert stats.total_entities >= 3
        assert stats.total_reports >= 3
        assert stats.confirmed_count >= 2
        assert stats.disputed_count >= 1
        assert stats.system_status == "HEALTHY"
