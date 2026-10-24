"""Unit Tests for Step 26: Emerging Variant Detection V1.

Tests the multi-dimensional decision engine detecting:
1. Hero emerging mutated campaigns (zero identifier overlap, invariant workflow).
2. Known patterns with recycled infrastructure.
3. Benign journeys yielding NO_SIGNIFICANT_MATCH.
4. Telemetry sparsity yielding INSUFFICIENT_EVIDENCE.
5. Backward compatibility with legacy ScamFingerprint.
"""

from typing import List
import pytest

from packages.schemas.assessment import EmergingStatus
from packages.schemas.fingerprint import ScamFingerprint, ScamFingerprintV2
from services.pattern_engine.matcher.variant_detector import (
    EmergingVariantDetector,
    EmergingVariantEvaluation,
    IdentifierMatchResult,
    WorkflowMatchResult,
)
from services.pattern_engine.patterns.scam_patterns import PatternMatch


def _create_mock_pattern_match(pattern_id: str = "KYC_IMPERSONATION", is_strong: bool = True) -> PatternMatch:
    return PatternMatch(
        pattern_id=pattern_id,
        pattern_name="Bank / KYC Suspension Impersonation",
        match_score=0.92 if is_strong else 0.45,
        matched_required=["OFFICIAL_ENTITY_IMPERSONATION"],
        matched_supporting=["URGENCY_PRESSURE_DETECTED", "OTP_INPUT_FORM_OBSERVED"],
        missing_required=[] if is_strong else ["OFFICIAL_ENTITY_IMPERSONATION"],
        is_strong_match=is_strong,
    )


def test_backward_compatibility_v1_fingerprint():
    """Ensures legacy ScamFingerprint V1 calls from existing tests and lab continue to work."""
    fp = ScamFingerprint(
        incident_id="inc_legacy_001",
        semantic_cluster_id="sbi_kyc_cluster",
        stage_sequence=["INITIAL_CONTACT", "IMPERSONATION", "SUSPICIOUS_LINK"],
        infrastructure_hash={"phone": "+919222222222", "domain": "hdfc-fake.xyz"},
        payment_profile={"vpa": "hdfc.desk@paytm"},
        confidence_score=0.88,
    )

    result = EmergingVariantDetector.evaluate(
        incident_id="inc_legacy_001",
        fingerprint=fp,
        historical_phones=["+919111111111"],
        historical_domains=["sbi-kyc-fix.online"],
        historical_vpas=["sbi.officer@oksbi"],
        pattern_match=_create_mock_pattern_match(is_strong=True),
        semantic_similarity_score=0.85,
        temporal_pace_seconds=75,
    )

    assert isinstance(result, EmergingVariantEvaluation)
    assert not result.identifier_match.phone_matched
    assert not result.identifier_match.domain_matched
    assert not result.identifier_match.payment_matched
    assert not result.identifier_match.has_any_match

    assert result.workflow_match.semantic_level == "HIGH"
    assert result.workflow_match.temporal_level == "HIGH"
    assert result.workflow_match.pattern_level == "HIGH"

    assert result.status == EmergingStatus.POSSIBLE_EMERGING_CAMPAIGN
    assert "HERO MATCH" in result.verdict_explanation


def test_hero_mutated_variant_with_scam_fingerprint_v2():
    """Hero Test:

    Known SBI KYC scam vs new HDFC KYC scam with complete mutation of identifiers
    (zero phone/domain/UPI overlap), but matching multi-stage journey and semantic intent.
    """
    known_seed = ScamFingerprintV2(
        incident_id="inc_sbi_seed",
        semantic_embedding=[0.8, 0.4, 0.1, -0.2],
        ordered_event_sequence=[
            "INITIAL_CONTACT",
            "IMPERSONATION",
            "SUSPICIOUS_LINK",
            "CREDENTIAL_SUBMIT",
            "PAYMENT_REQUEST",
        ],
        event_time_gaps=[40, 60, 30, 50],
        social_engineering_tactics=["ACCOUNT_BLOCK_THREAT", "URGENCY", "IMPERSONATION"],
        claimed_identity="State Bank of India",
        requested_actions=["UPDATE_PAN_CARD", "PAY_TOKEN_FEE"],
        pattern_matches=["BANK_KYC_SUSPENSION_SCAM"],
        infrastructure_entities={"phone": "+91-9876543210", "domain": "sbi-kyc-update.xyz"},
        payment_entities={"vpa": "sbi.fraud@ybl"},
        graph_community="campaign_bank_phish_cluster_01",
    )

    new_hdfc_variant = ScamFingerprintV2(
        incident_id="inc_hdfc_new",
        semantic_embedding=[0.79, 0.42, 0.08, -0.21],  # Highly aligned embedding
        ordered_event_sequence=[
            "INITIAL_CONTACT",
            "IMPERSONATION",
            "SUSPICIOUS_LINK",
            "CREDENTIAL_SUBMIT",
            "PAYMENT_REQUEST",
        ],
        event_time_gaps=[35, 70, 25, 45],
        social_engineering_tactics=["ACCOUNT_BLOCK_THREAT", "URGENCY", "IMPERSONATION"],
        claimed_identity="HDFC Bank",
        requested_actions=["UPDATE_PAN_CARD", "PAY_TOKEN_FEE"],
        pattern_matches=["BANK_KYC_SUSPENSION_SCAM"],
        infrastructure_entities={"phone": "+91-9123456789", "domain": "hdfc-netbanking-verify.top"},  # Fresh!
        payment_entities={"vpa": "hdfc.verify@paytm"},  # Fresh!
    )

    result = EmergingVariantDetector.evaluate(
        incident_id="inc_hdfc_new",
        fingerprint=new_hdfc_variant,
        historical_phones=["+91-9876543210"],
        historical_domains=["sbi-kyc-update.xyz"],
        historical_vpas=["sbi.fraud@ybl"],
        historical_fingerprints=[known_seed],
        pattern_match=_create_mock_pattern_match(is_strong=True),
    )

    # Identifiers: All Brand New
    assert not result.identifier_match.phone_matched
    assert not result.identifier_match.domain_matched
    assert not result.identifier_match.payment_matched
    assert not result.identifier_match.has_any_match

    # Workflow: High Alignment
    assert result.workflow_match.semantic_level == "HIGH"
    assert result.workflow_match.temporal_level == "HIGH"
    assert result.workflow_match.pattern_level == "HIGH"

    # Status: Hero Emerging Campaign / Mutated Variant
    assert result.status in (
        EmergingStatus.POSSIBLE_EMERGING_CAMPAIGN,
        EmergingStatus.MUTATED_VARIANT,
    )
    assert result.matched_incident_id == "inc_sbi_seed"
    assert result.matched_campaign == "campaign_bank_phish_cluster_01"
    assert result.similarity_breakdown["overall"] > 0.70


def test_known_pattern_with_recycled_infrastructure():
    """An incident that reuses a known burner phone or phishing domain must be classified as KNOWN_PATTERN."""
    reused_fp = ScamFingerprintV2(
        incident_id="inc_reused_001",
        semantic_embedding=[0.75, 0.40, 0.10, -0.20],
        ordered_event_sequence=["INITIAL_CONTACT", "IMPERSONATION", "SUSPICIOUS_LINK"],
        event_time_gaps=[40, 60],
        infrastructure_entities={"phone": "+91-9876543210", "domain": "sbi-kyc-update.xyz"},
        payment_entities={"vpa": "sbi.fraud@ybl"},
    )

    result = EmergingVariantDetector.evaluate(
        incident_id="inc_reused_001",
        fingerprint=reused_fp,
        historical_phones=["+91-9876543210"],
        historical_domains=["sbi-kyc-update.xyz"],
        historical_vpas=["sbi.fraud@ybl"],
        pattern_match=_create_mock_pattern_match(is_strong=True),
    )

    assert result.identifier_match.has_any_match
    assert result.identifier_match.phone_matched
    assert result.identifier_match.domain_matched
    assert result.identifier_match.payment_matched
    assert result.status == EmergingStatus.KNOWN_PATTERN
    assert "previously identified scam infrastructure" in result.verdict_explanation


def test_benign_normal_payment_yields_no_significant_match():
    """Legitimate bill payment or transfer with zero deceptive signals must yield NO_SIGNIFICANT_MATCH."""
    benign_fp = ScamFingerprintV2(
        incident_id="inc_benign_001",
        semantic_embedding=[-0.5, 0.1, 0.8, 0.3],
        ordered_event_sequence=["PAYMENT_REQUEST", "TRANSACTION_CONFIRMED"],
        event_time_gaps=[15],
        infrastructure_entities={"domain": "tatapower.com"},
        payment_entities={"vpa": "tatapower@icici"},
    )

    result = EmergingVariantDetector.evaluate(
        incident_id="inc_benign_001",
        fingerprint=benign_fp,
        historical_phones=["+91-9876543210"],
        historical_domains=["sbi-kyc-update.xyz"],
        historical_vpas=["sbi.fraud@ybl"],
        pattern_match=None,
        semantic_similarity_score=0.12,
    )

    assert not result.identifier_match.has_any_match
    assert result.workflow_match.semantic_level == "LOW"
    assert result.workflow_match.pattern_level == "LOW"
    assert result.status == EmergingStatus.NO_SIGNIFICANT_MATCH


def test_sparse_telemetry_yields_insufficient_evidence():
    """An incident with only 1 uncorroborated event and no patterns returns INSUFFICIENT_EVIDENCE."""
    sparse_fp = ScamFingerprintV2(
        incident_id="inc_sparse_001",
        semantic_embedding=[0.0, 0.0, 0.0, 0.0],
        ordered_event_sequence=["INITIAL_CONTACT"],
        event_time_gaps=[],
        infrastructure_entities={},
        payment_entities={},
    )

    result = EmergingVariantDetector.evaluate(
        incident_id="inc_sparse_001",
        fingerprint=sparse_fp,
        historical_phones=["+91-9876543210"],
        historical_domains=["sbi-kyc-update.xyz"],
        historical_vpas=["sbi.fraud@ybl"],
        pattern_match=None,
        semantic_similarity_score=0.05,
    )

    assert result.status == EmergingStatus.INSUFFICIENT_EVIDENCE
    assert "Telemetry too sparse" in result.verdict_explanation
