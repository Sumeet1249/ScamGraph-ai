"""Unit tests for Step 25: Scam Fingerprint V2 & Multi-Dimensional Similarity Engine.

Validates:
1. ScamFingerprintV2 schema and builder
2. Configurable weights from config/scam_fingerprint.yaml
3. Temporal journey sequence similarity (reordering tolerance vs workflow penalty)
4. Hero Test: Mutated scam with zero identifier overlap but high workflow similarity
5. Benign Test: Normal payment does NOT trigger high similarity merely due to PAYMENT_REQUEST
6. Detailed explainability breakdown (matched dimensions, sequence alignment)
"""

from __future__ import annotations

import pytest

from packages.schemas.fingerprint import (
    FingerprintSimilarityResult,
    ScamFingerprintV2,
)
from services.pattern_engine.semantic import (
    ScamFingerprintSimilarityEngine,
    ScamFingerprintV2Builder,
    fingerprint_similarity_engine,
)


def test_fingerprint_v2_builder_and_fields():
    """Verify ScamFingerprintV2Builder constructs all multi-dimensional fields."""
    events = [
        {"event_type": "MESSAGE_RECEIVED", "timestamp_offset_seconds": 0},
        {"event_type": "URL_OPENED", "timestamp_offset_seconds": 25},
        {"event_type": "CREDENTIAL_REQUEST", "timestamp_offset_seconds": 50},
        {"event_type": "OTP_REQUEST", "timestamp_offset_seconds": 75},
        {"event_type": "PAYMENT_REQUEST", "timestamp_offset_seconds": 100},
    ]

    fp = ScamFingerprintV2Builder.build(
        incident_id="inc_kyc_001",
        events=events,
        claimed_identity="State Bank of India",
        social_engineering_tactics=["URGENCY", "AUTHORITY", "FEAR_OF_SUSPENSION"],
        requested_actions=["UPDATE_KYC", "SUBMIT_OTP", "APPROVE_INR_25000"],
        pattern_matches=["KYC_IMPERSONATION"],
        infrastructure_entities={
            "phone": "+919811100001",
            "domain": "sbi-kyc-update.example",
            "ip": "185.220.101.5",
        },
        payment_entities={
            "vpa": "fraudster.mule@fakeupi",
            "channel": "UPI",
        },
        graph_community="campaign_community_1",
        message_summary="Your SBI netbanking is blocked. Update PAN immediately.",
    )

    assert fp.incident_id == "inc_kyc_001"
    assert len(fp.ordered_event_sequence) == 5
    assert fp.ordered_event_sequence == [
        "MESSAGE_RECEIVED",
        "URL_OPENED",
        "CREDENTIAL_REQUEST",
        "OTP_REQUEST",
        "PAYMENT_REQUEST",
    ]
    assert fp.event_time_gaps == [25, 25, 25, 25]
    assert "URGENCY" in fp.social_engineering_tactics
    assert fp.claimed_identity == "State Bank of India"
    assert len(fp.semantic_embedding) > 0
    assert fp.graph_community == "campaign_community_1"


def test_configurable_weights_sum_to_one():
    """Verify weights from config/scam_fingerprint.yaml sum to 1.0."""
    engine = ScamFingerprintSimilarityEngine()
    weights = engine.weights
    total = (
        weights["semantic_weight"]
        + weights["journey_weight"]
        + weights["pattern_weight"]
        + weights["infrastructure_weight"]
        + weights["payment_weight"]
    )
    assert abs(total - 1.0) < 1e-4, f"Fingerprint weights must sum to 1.0 (got {total})"


def test_journey_sequence_similarity_reordering_tolerance():
    """Verify journey sequence similarity tolerates small reordering while penalizing different workflows."""
    engine = fingerprint_similarity_engine

    seq_base = ["MESSAGE_RECEIVED", "URL_OPENED", "CREDENTIAL_REQUEST", "OTP_REQUEST", "PAYMENT_REQUEST"]
    # Slight reordering: URL_OPENED and CREDENTIAL_REQUEST flipped
    seq_reordered = ["MESSAGE_RECEIVED", "CREDENTIAL_REQUEST", "URL_OPENED", "OTP_REQUEST", "PAYMENT_REQUEST"]
    # Missing optional intermediate step
    seq_missing_one = ["MESSAGE_RECEIVED", "URL_OPENED", "OTP_REQUEST", "PAYMENT_REQUEST"]
    # Completely divergent workflow (legitimate utility)
    seq_divergent = ["MESSAGE_RECEIVED", "PAYMENT_REQUEST"]

    sim_reordered, _ = engine.compute_journey_similarity(seq_base, seq_reordered)
    sim_missing, _ = engine.compute_journey_similarity(seq_base, seq_missing_one)
    sim_divergent, _ = engine.compute_journey_similarity(seq_base, seq_divergent)

    assert sim_reordered >= 0.85, f"Reordered sequence should score high (got {sim_reordered})"
    assert sim_missing >= 0.75, f"Missing single step should score moderately high (got {sim_missing})"
    assert sim_divergent < 0.60, f"Divergent workflow should score low (got {sim_divergent})"
    assert sim_reordered > sim_divergent


def test_hero_mutated_variant_detection():
    """CRITICAL HERO TEST:

    Known Campaign: SBI KYC (Phone A, Domain A, UPI A)
    New Incident: HDFC Security Verification (Phone B, Domain B, UPI B)

    All identifiers differ completely (overlap 0.0, infrastructure 0.0).
    Yet semantic tactics, journey sequence, and pattern match are identical.

    Expected:
    - identifier_overlap == 0.0
    - infrastructure_similarity == 0.0
    - payment_similarity == 0.0
    - semantic_similarity >= 0.70
    - journey_similarity >= 0.90
    - pattern_similarity == 1.0
    - overall_similarity_index >= 0.60 (elevated despite zero shared identifiers)
    - explanation notes mutated variant
    """
    engine = fingerprint_similarity_engine

    # Known SBI KYC incident
    fp_sbi = ScamFingerprintV2Builder.build(
        incident_id="inc_sbi_known",
        events=[
            {"event_type": "MESSAGE_RECEIVED", "timestamp_offset_seconds": 0},
            {"event_type": "URL_OPENED", "timestamp_offset_seconds": 30},
            {"event_type": "CREDENTIAL_REQUEST", "timestamp_offset_seconds": 60},
            {"event_type": "OTP_REQUEST", "timestamp_offset_seconds": 90},
            {"event_type": "PAYMENT_REQUEST", "timestamp_offset_seconds": 120},
        ],
        claimed_identity="State Bank of India",
        social_engineering_tactics=["URGENCY", "AUTHORITY", "ACCOUNT_FREEZE_THREAT"],
        requested_actions=["UPDATE_KYC", "SUBMIT_CREDENTIALS", "VERIFY_OTP"],
        pattern_matches=["KYC_IMPERSONATION"],
        infrastructure_entities={
            "phone": "+919811100001",
            "domain": "sbi-kyc-verify.example",
            "ip": "103.20.10.1",
        },
        payment_entities={
            "vpa": "sbi.fraudster@oksbi",
        },
        message_summary="SBI Alert: Your netbanking is blocked due to pending KYC. Update PAN immediately.",
    )

    # New HDFC Security Verification incident (All identifiers mutated!)
    fp_hdfc = ScamFingerprintV2Builder.build(
        incident_id="inc_hdfc_new",
        events=[
            {"event_type": "MESSAGE_RECEIVED", "timestamp_offset_seconds": 0},
            {"event_type": "URL_OPENED", "timestamp_offset_seconds": 25},
            {"event_type": "CREDENTIAL_REQUEST", "timestamp_offset_seconds": 55},
            {"event_type": "OTP_REQUEST", "timestamp_offset_seconds": 80},
            {"event_type": "PAYMENT_REQUEST", "timestamp_offset_seconds": 110},
        ],
        claimed_identity="HDFC Bank Security",
        social_engineering_tactics=["URGENCY", "AUTHORITY", "ACCOUNT_FREEZE_THREAT"],
        requested_actions=["UPDATE_KYC", "SUBMIT_CREDENTIALS", "VERIFY_OTP"],
        pattern_matches=["KYC_IMPERSONATION"],
        infrastructure_entities={
            "phone": "+919822200002",
            "domain": "hdfc-secure-auth.example",
            "ip": "185.120.50.2",
        },
        payment_entities={
            "vpa": "hdfc.collector@okhdfc",
        },
        message_summary="HDFC Alert: Your account is suspended pending security verification. Update immediately.",
    )

    result = engine.compare(fp_sbi, fp_hdfc)

    # 1. Zero identifier / infrastructure overlap
    assert result.identifier_overlap == 0.0, "Zero known identifiers should match"
    assert result.infrastructure_similarity == 0.0, "Zero infrastructure features should match"
    assert result.payment_similarity == 0.0, "Zero payment handles should match"

    # 2. Strong behavioral & structural similarity
    assert result.semantic_similarity >= 0.70, f"Semantic similarity must be high (got {result.semantic_similarity})"
    assert result.journey_similarity >= 0.90, f"Journey sequence must match closely (got {result.journey_similarity})"
    assert result.pattern_similarity == 1.0, "Pattern KYC_IMPERSONATION must match identically"

    # 3. Overall similarity is elevated despite zero identifier overlap
    assert result.overall_similarity_index >= 0.60, f"Overall index must be elevated (got {result.overall_similarity_index})"

    # 4. Dimension breakdown & explainability
    assert "SEMANTIC" in result.matched_dimensions
    assert "JOURNEY" in result.matched_dimensions
    assert "PATTERN" in result.matched_dimensions
    assert "INFRASTRUCTURE" in result.different_dimensions
    assert "MUTATED VARIANT DETECTED" in result.explanation


def test_benign_normal_payment_not_similar_to_scam():
    """BENIGN TEST:

    A normal electricity utility bill payment must NOT become highly similar
    to a scam journey merely because both involve PAYMENT_REQUEST.
    """
    engine = fingerprint_similarity_engine

    # Scammer KYC fingerprint
    fp_scam = ScamFingerprintV2Builder.build(
        incident_id="inc_scam",
        events=[
            {"event_type": "MESSAGE_RECEIVED", "timestamp_offset_seconds": 0},
            {"event_type": "URL_OPENED", "timestamp_offset_seconds": 30},
            {"event_type": "CREDENTIAL_REQUEST", "timestamp_offset_seconds": 60},
            {"event_type": "OTP_REQUEST", "timestamp_offset_seconds": 90},
            {"event_type": "PAYMENT_REQUEST", "timestamp_offset_seconds": 120},
        ],
        claimed_identity="State Bank of India",
        social_engineering_tactics=["URGENCY", "FEAR_OF_SUSPENSION"],
        requested_actions=["UPDATE_KYC", "SUBMIT_OTP"],
        pattern_matches=["KYC_IMPERSONATION"],
        infrastructure_entities={"domain": "sbi-fake.example"},
        payment_entities={"vpa": "scam.mule@fakeupi"},
        message_summary="Your account is blocked. Update KYC immediately.",
    )

    # Legitimate utility bill payment
    fp_benign = ScamFingerprintV2Builder.build(
        incident_id="inc_benign",
        events=[
            {"event_type": "MESSAGE_RECEIVED", "timestamp_offset_seconds": 0},
            {"event_type": "PAYMENT_REQUEST", "timestamp_offset_seconds": 60},
        ],
        claimed_identity="State Electricity Board",
        social_engineering_tactics=[],  # Zero coercive tactics
        requested_actions=["PAY_MONTHLY_BILL"],
        pattern_matches=[],  # No scam pattern match
        infrastructure_entities={"domain": "official-utility.gov.in"},
        payment_entities={"vpa": "electricity@officialbank"},
        message_summary="Your monthly electricity bill of INR 1,450 is generated. Due date 28-Oct.",
    )

    result = engine.compare(fp_scam, fp_benign)

    # Normal payment must have low overall similarity
    assert result.overall_similarity_index < 0.35, f"Normal payment should have low similarity (got {result.overall_similarity_index})"
    assert result.journey_similarity < 0.60
    assert result.pattern_similarity == 0.0
    assert result.identifier_overlap == 0.0
    assert "LOW SIMILARITY" in result.explanation


def test_fingerprint_similarity_result_contract():
    """Verify FingerprintSimilarityResult schema compliance and diagnostics."""
    engine = fingerprint_similarity_engine

    fp1 = ScamFingerprintV2Builder.build(
        incident_id="inc_1",
        events=[{"event_type": "MESSAGE_RECEIVED"}, {"event_type": "PAYMENT_REQUEST"}],
        pattern_matches=["GENERIC_SCAM"],
    )
    fp2 = ScamFingerprintV2Builder.build(
        incident_id="inc_2",
        events=[{"event_type": "MESSAGE_RECEIVED"}, {"event_type": "PAYMENT_REQUEST"}],
        pattern_matches=["GENERIC_SCAM"],
    )

    res = engine.compare(fp1, fp2)
    assert isinstance(res, FingerprintSimilarityResult)
    assert 0.0 <= res.overall_similarity_index <= 1.0
    assert "sequence_matcher_ratio" in res.sequence_alignment
    assert len(res.explanation) > 0
