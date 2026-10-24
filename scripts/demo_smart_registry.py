"""ScamGraph Smart Registry (Module A) - Interactive Demonstration Script.

Runs an end-to-end demonstration of:
1. Versioned canonical normalization across typed identifiers
2. Keyed HMAC-SHA-256 fingerprint generation & safe masking previews
3. Real-time screening against confirmed, disputed, and revoked registry entities
4. Entity deduplication and multi-source report linkage
5. Formal dispute arbitration and risk discounting
6. Authorized revocation with active screening suppression
7. Cryptographic SHA-256 sealed immutable audit trail
"""

import asyncio
from datetime import datetime, timezone
import json

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


async def main():
    print("=" * 78)
    print("  SCAMGRAPH AI - DPIP-INSPIRED SMART SUSPECT REGISTRY (MODULE A)")
    print("=" * 78)

    repo = RegistryRepository()
    await repo.ensure_seeded()
    service = SmartRegistryService(repo=repo)

    # 1. Normalization & Fingerprinting
    print("\n[1] CANONICAL NORMALIZATION & KEYED HMAC-SHA-256 FINGERPRINTING:")
    phone_raw = "  +91 98765-43210 "
    vpa_raw = "  UPI://PAY?PA=Electricity.Desk@OkSBI&pn=PowerDesk "
    bank_raw = "sbin0001234 : 009876543210"

    norm_phone = IdentifierNormalizer.normalize(IdentifierType.PHONE, phone_raw)
    norm_vpa = IdentifierNormalizer.normalize(IdentifierType.UPI_VPA, vpa_raw)
    norm_bank = IdentifierNormalizer.normalize(IdentifierType.BANK_ACCOUNT, bank_raw)

    fp_phone = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, phone_raw)
    fp_vpa = RegistryFingerprinter.generate_fingerprint(IdentifierType.UPI_VPA, vpa_raw)

    print(f"  Phone Raw:    '{phone_raw}' -> Canonical: '{norm_phone}'")
    print(f"  Phone Mask:   {fp_phone.normalized_preview} | Fingerprint: {fp_phone.fingerprint[:32]}...")
    print(f"  UPI Raw:      '{vpa_raw[:35]}...' -> Canonical: '{norm_vpa}'")
    print(f"  UPI Mask:     {fp_vpa.normalized_preview} | Fingerprint: {fp_vpa.fingerprint[:32]}...")
    print(f"  Bank Acc:     '{bank_raw}' -> Canonical: '{norm_bank}' (leading zeros preserved)")

    # 2. Real-Time Screening Simulation
    print("\n[2] REAL-TIME SCREENING ENGINE:")
    screen_req = ScreenRequest(
        caller_org="PSP_PHONEPE_01",
        identifiers=[
            TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="electricity.desk@oksbi"),
            TypedIdentifier(identifier_type=IdentifierType.BANK_ACCOUNT, raw_value="SBIN0001234:009876543210"),
            TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="clean.user@icici"),
        ],
    )
    screen_res = await service.screen_identifiers(screen_req)

    print(f"  Total Queried:    {screen_res.total_queried}")
    print(f"  Total Hits:       {screen_res.total_hits}")
    print(f"  Highest Risk:     {screen_res.highest_risk_score}")
    print(f"  Confirmed Hit:    {screen_res.has_confirmed_hit}")
    print(f"  Disputed Hit:     {screen_res.has_disputed_hit}")

    for idx, m in enumerate(screen_res.matches, 1):
        print(f"    Hit {idx}: [{m.identifier_type.value}] {m.report_id} ({m.category}) -> Status: {m.report_status.value} | Risk: {m.risk_score}")
        if m.warnings:
            print(f"      Warning: {m.warnings[0]}")

    # 3. Report Ingestion & Entity Linkage
    print("\n[3] INGESTION & AUTOMATIC ENTITY LINKAGE:")
    new_rep_1 = await service.ingest_report(
        CreateReportRequest(
            reporting_org="BANK_HDFC_01",
            entity_name="Digital Arrest Mule Syndicate",
            category="DIGITAL_ARREST",
            reason="Victim coerced into transfer under fake Supreme Court CBI notice",
            identifiers=[
                TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919444333222"),
                TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="cbi.bail.deposit@oksbi"),
            ],
            confidence=0.96,
        )
    )
    print(f"  Created Report 1: {new_rep_1.report_id} -> Linked Entity: {new_rep_1.entity_id}")

    # Ingest second report with the same phone -> entity deduplication
    new_rep_2 = await service.ingest_report(
        CreateReportRequest(
            reporting_org="BANK_SBI_01",
            category="DIGITAL_ARREST",
            reason="Second victim report involving same phone number",
            identifiers=[
                TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919444333222"),
            ],
            confidence=0.91,
        )
    )
    print(f"  Created Report 2: {new_rep_2.report_id} -> Linked Entity: {new_rep_2.entity_id}")
    assert new_rep_1.entity_id == new_rep_2.entity_id
    print("  Entity Linkage Confirmed: Multiple reports successfully linked to same RegistryEntity!")

    # 4. Dispute Lifecycle
    print("\n[4] DISPUTE ARBITRATION LIFECYCLE:")
    dsp = await service.submit_dispute(
        SubmitDisputeRequest(
            report_id=new_rep_1.report_id,
            disputing_org="BANK_ICICI_01",
            reason="Account holder was spoofed; submitted cyber complaint proof.",
            evidence_documents=["cyber_complaint_ack_2026.pdf"],
        )
    )
    print(f"  Dispute Filed: {dsp.dispute_id} -> Status: {dsp.status}")

    # Screen after dispute -> risk score discounted
    screen_post_dsp = await service.screen_identifiers(
        ScreenRequest(
            caller_org="PSP_GPAY_01",
            identifiers=[TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919444333222")],
        )
    )
    print(f"  Post-Dispute Screening Risk: {screen_post_dsp.highest_risk_score} (Discounted 50% from 0.96)")

    # 5. Revocation & Active Risk Suppression
    print("\n[5] AUTHORIZED REVOCATION & SUPPRESSION:")
    rev = await service.submit_revocation(
        SubmitRevocationRequest(
            report_id=new_rep_1.report_id,
            authorizing_org="BANK_HDFC_01",
            revocation_reason="Internal security committee verified customer remediation and account restoration.",
            authorized_by="Lead_Compliance_Officer_401",
        )
    )
    print(f"  Revocation Executed: {rev.revocation_id} -> Status: {rev.status}")

    screen_post_rev = await service.screen_identifiers(
        ScreenRequest(
            caller_org="PSP_GPAY_01",
            identifiers=[TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="cbi.bail.deposit@oksbi")],
        )
    )
    print(f"  Post-Revocation Screening: Has Revoked Hit: {screen_post_rev.has_revoked_hit} | Active Risk: {screen_post_rev.highest_risk_score}")

    # 6. Immutable Audit Trail
    print("\n[6] CRYPTOGRAPHIC IMMUTABLE AUDIT TRAIL:")
    audit_events = await repo.list_all_audit_events(limit=5)
    for ev in audit_events:
        print(f"  [{ev.action.value}] {ev.entity_id} | Actor: {ev.actor_org} | State: {ev.previous_state or 'None'} -> {ev.new_state}")
        print(f"    SHA-256 Seal: {ev.integrity_hash}")

    # 7. System Stats
    stats = await repo.get_statistics()
    print("\n[7] REGISTRY AGGREGATE METRICS:")
    print(f"  Total Entities:     {stats.total_entities}")
    print(f"  Total Reports:      {stats.total_reports}")
    print(f"  Confirmed Suspects: {stats.confirmed_count}")
    print(f"  Disputed Suspects:  {stats.disputed_count}")
    print(f"  Revoked Suspects:   {stats.revoked_count}")
    print(f"  Screening Queries:  {stats.screening_count}")
    print(f"  Audit Event Count:  {stats.audit_event_count}")
    print(f"  System Health:      {stats.system_status}")

    print("\n" + "=" * 78)
    print("  ALL DEMONSTRATION MODULES COMPLETED SUCCESSFULLY WITH ZERO ERRORS.")
    print("=" * 78)


if __name__ == "__main__":
    asyncio.run(main())
