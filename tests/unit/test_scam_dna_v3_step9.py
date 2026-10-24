"""ScamDNA V3 Unit and Integration Test Suite (Step 9).

Validates:
1. 8-dimensional DNA building with strict privacy bounds.
2. Partial DNA handling and dynamic weight re-normalization.
3. Task scam variant mutation (zero identifier overlap).
4. Digital arrest variant mutation (differing pretext, identical coercion DNA).
5. Legitimate recruitment and banking hard negatives (false collision defense).
6. Partial-journey early DNA matching.
7. Multilingual English/Hinglish behavioral invariance.
8. Contradiction penalty handling.
9. ScamFingerprintV2 backward compatibility adapter.
10. Sub-linear two-stage candidate retrieval index.
11. Consumer and analyst serializers.
12. FastAPI HTTP endpoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient

from packages.schemas.dna import (
    ConsumerDNAView,
    DNADimensionType,
    DNAQuality,
    ScamDNA,
    ScamDNAMatch,
    VariantStatus,
)
from packages.schemas.fingerprint import ScamFingerprintV2
from packages.schemas.journey import JourneyStage, ScamJourney
from services.api.app.main import app
from services.dna_engine.adapter import ScamFingerprintV2Adapter
from services.dna_engine.builder import ScamDNABuilder
from services.dna_engine.retrieval import DNACandidateIndex
from services.dna_engine.serializer import DNASerializer
from services.dna_engine.service import ScamDNAService
from services.dna_engine.similarity import ScamDNASimilarityEngine
from services.pattern_engine.matcher.variant_detector import EmergingVariantDetector


@pytest.fixture
def sim_engine() -> ScamDNASimilarityEngine:
    return ScamDNASimilarityEngine()


@pytest.fixture
def dna_service(sim_engine: ScamDNASimilarityEngine) -> ScamDNAService:
    return ScamDNAService(similarity_engine=sim_engine)


def test_dna_builder_all_8_dimensions():
    """Verifies that ScamDNABuilder constructs all 8 dimensions with zero raw secrets."""
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    mock_journey = ScamJourney(
        incident_id="inc_build_test",
        stage_history=[JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION, JourneyStage.INITIAL_PAYMENT],
        current_stage=JourneyStage.INITIAL_PAYMENT,
        current_stage_confidence=0.85,
        channels=["INSTAGRAM", "WHATSAPP", "UPI"],
        monetization_boundary_event_id="ev_pay_1",
    )

    dna = ScamDNABuilder.build(
        incident_id="inc_build_test",
        journey=mock_journey,
        tactics=["TRUST_BUILDING", "PAYMENT_PRESSURE"],
        entities=[{"entity_type": "BRAND", "canonical_value": "State Bank of India"}],
        payment_context={"deposit_requested": True, "amount": 5000, "is_escalated": True},
        infrastructure={"channels": ["INSTAGRAM", "WHATSAPP", "UPI"]},
        temporal_context={"duration_seconds": 600, "time_gaps": [300, 300]},
        graph_context={"degree_tier": "HUB", "shared_entity_count": 3},
        message_text="Complete simple tasks and earn ₹5000 daily. Pay ₹500 activation fee.",
        requested_actions=["PAY_FEE", "COMPLETE_TASK"],
    )

    assert dna.schema_version == "3.0"
    assert len(dna.available_dimensions) == 8
    assert dna.quality in (DNAQuality.HIGH, DNAQuality.VERY_HIGH)
    assert dna.confidence >= 0.80

    # Privacy verification: raw phone numbers or secrets must NOT be in canonical signature
    assert "+91" not in dna.canonical_signature
    assert "password" not in dna.canonical_signature
    assert "family:" in dna.canonical_signature
    assert "journey:" in dna.canonical_signature


def test_partial_dna_handling_and_missing_dimensions():
    """Verifies that partial incidents mark missing dimensions as available=False instead of zeroing them out."""
    dna = ScamDNABuilder.build(
        incident_id="inc_partial",
        message_text="Urgent: Your account is suspended. Contact customer support.",
        tactics=["URGENCY", "FEAR"],
    )

    assert dna.dimensions[DNADimensionType.SEMANTIC.value].available is True
    assert dna.dimensions[DNADimensionType.TACTIC.value].available is True
    assert dna.dimensions[DNADimensionType.JOURNEY.value].available is False
    assert dna.dimensions[DNADimensionType.PAYMENT.value].available is False
    assert dna.dimensions[DNADimensionType.GRAPH.value].available is False
    assert "PAYMENT" in dna.missing_dimensions


def test_missing_dimension_weight_renormalization(sim_engine: ScamDNASimilarityEngine):
    """Verifies that the similarity engine dynamically re-normalizes weights over comparable dimensions."""
    # DNA 1: Has Semantic, Tactic, Journey, Payment
    dna1 = ScamDNABuilder.build(
        incident_id="inc_1",
        journey=ScamJourney(incident_id="inc_1", stage_history=[JourneyStage.CONTACT, JourneyStage.INITIAL_PAYMENT]),
        tactics=["URGENCY", "PAYMENT_PRESSURE"],
        payment_context={"deposit_requested": True},
        message_text="Pay ₹1000 right now",
    )

    # DNA 2: Has Semantic and Tactic only (Missing Journey and Payment)
    dna2 = ScamDNABuilder.build(
        incident_id="inc_2",
        tactics=["URGENCY", "PAYMENT_PRESSURE"],
        message_text="Pay ₹1000 right now",
    )

    match = sim_engine.compare(dna1, dna2)
    # Available in both: SEMANTIC and TACTIC
    assert match.available_comparison_dimensions == ["SEMANTIC", "TACTIC"]
    assert "JOURNEY" in match.missing_comparison_dimensions
    assert "PAYMENT" in match.missing_comparison_dimensions
    # Since SEMANTIC and TACTIC match highly, overall similarity must NOT be dragged to near zero by missing dimensions
    assert match.overall_similarity >= 0.70
    # Match confidence should reflect partial dimensional coverage
    assert match.match_confidence < 0.75


def test_task_scam_variant_mutation(sim_engine: ScamDNASimilarityEngine):
    """Section 119: Verifies that task scam variants with 100% altered identifiers match strongly."""
    # Incident A: Instagram ad -> WhatsApp -> Telegram -> ₹300 reward -> ₹5,000 deposit -> ₹15,000 request -> blocked
    dna_a = ScamDNABuilder.build(
        incident_id="inc_task_a",
        journey=ScamJourney(
            incident_id="inc_task_a",
            scam_family="JOB_TASK",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.PLATFORM_MIGRATION,
                JourneyStage.REWARD_OR_FAKE_PROFIT,
                JourneyStage.INITIAL_PAYMENT,
                JourneyStage.PAYMENT_ESCALATION,
                JourneyStage.WITHDRAWAL_BLOCK,
            ],
            channels=["INSTAGRAM", "WHATSAPP", "TELEGRAM", "UPI"],
            monetization_boundary_event_id="e_dep",
        ),
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        payment_context={
            "prior_reward": True,
            "deposit_requested": True,
            "is_escalated": True,
            "fee_after_block": True,
            "amount": 5000,
        },
        infrastructure={"channels": ["INSTAGRAM", "WHATSAPP", "TELEGRAM", "UPI"]},
        message_text="Earn money by liking YouTube videos. Get ₹300 bonus then recharge ₹5000 for VIP tasks.",
        requested_actions=["LIKE_VIDEOS", "DEPOSIT_FUNDS", "JOIN_TELEGRAM"],
    )

    # Incident B: Facebook job post -> WhatsApp -> private group -> ₹250 reward -> ₹4,500 recharge -> ₹14,000 merchant task -> fee
    dna_b = ScamDNABuilder.build(
        incident_id="inc_task_b",
        journey=ScamJourney(
            incident_id="inc_task_b",
            scam_family="JOB_TASK",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.PLATFORM_MIGRATION,
                JourneyStage.REWARD_OR_FAKE_PROFIT,
                JourneyStage.INITIAL_PAYMENT,
                JourneyStage.PAYMENT_ESCALATION,
                JourneyStage.WITHDRAWAL_BLOCK,
            ],
            channels=["FACEBOOK", "WHATSAPP", "PRIVATE_CHAT", "UPI"],
            monetization_boundary_event_id="e_rech",
        ),
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        payment_context={
            "prior_reward": True,
            "deposit_requested": True,
            "is_escalated": True,
            "fee_after_block": True,
            "amount": 4500,
        },
        infrastructure={"channels": ["FACEBOOK", "WHATSAPP", "PRIVATE_CHAT", "UPI"]},
        message_text="Merchant evaluation part-time opportunity. Receive ₹250 welcome commission. Recharge ₹4500.",
        requested_actions=["REVIEW_PRODUCTS", "RECHARGE_ACCOUNT", "SUBMIT_ORDERS"],
    )

    match = sim_engine.compare(dna_a, dna_b)
    assert match.overall_similarity >= 0.70
    assert match.variant_status in (VariantStatus.KNOWN_PATTERN, VariantStatus.LIKELY_VARIANT)
    assert "SIMILAR_PAYMENT_ESCALATION" in " ".join(match.reason_codes)


def test_digital_arrest_variant_mutation(sim_engine: ScamDNASimilarityEngine):
    """Section 120: Verifies that digital arrest variants with differing pretexts share strong coercion DNA."""
    # A: courier call -> police transfer -> arrest threat -> secrecy -> transfer request
    dna_a = ScamDNABuilder.build(
        incident_id="inc_da_a",
        journey=ScamJourney(
            incident_id="inc_da_a",
            scam_family="DIGITAL_ARREST",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.IMPERSONATION,
                JourneyStage.THREAT_OR_PRESSURE,
                JourneyStage.INITIAL_PAYMENT,
            ],
        ),
        tactics=["AUTHORITY", "THREAT", "ISOLATION", "SECRECY"],
        entities=[{"entity_type": "ORGANIZATION", "canonical_value": "Mumbai Cyber Police"}],
        payment_context={"deposit_requested": True, "amount": 50000},
        message_text="FedEx parcel found with illegal drugs. Transferred to Mumbai Cyber Police. Stay on camera.",
    )

    # B: telecom complaint -> CBI impersonation -> money-laundering threat -> isolation -> safe-account transfer
    dna_b = ScamDNABuilder.build(
        incident_id="inc_da_b",
        journey=ScamJourney(
            incident_id="inc_da_b",
            scam_family="DIGITAL_ARREST",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.IMPERSONATION,
                JourneyStage.THREAT_OR_PRESSURE,
                JourneyStage.INITIAL_PAYMENT,
            ],
        ),
        tactics=["AUTHORITY", "THREAT", "ISOLATION", "SECRECY"],
        entities=[{"entity_type": "ORGANIZATION", "canonical_value": "Central Bureau of Investigation"}],
        payment_context={"deposit_requested": True, "amount": 75000},
        message_text="TRAI notice: Your Aadhaar linked to 14 SIMs used for money laundering. CBI investigation order issued. Deposit funds to RBI verification vault.",
    )

    match = sim_engine.compare(dna_a, dna_b)
    assert match.overall_similarity >= 0.65
    assert match.variant_status in (VariantStatus.KNOWN_PATTERN, VariantStatus.LIKELY_VARIANT)
    assert any("AUTHORITY" in r or "COERCION" in r for r in match.reason_codes)


def test_legitimate_recruitment_hard_negative(sim_engine: ScamDNASimilarityEngine):
    """Section 121: Real recruitment flow should NOT match task scam DNA."""
    # Scam task DNA
    dna_scam = ScamDNABuilder.build(
        incident_id="inc_scam",
        journey=ScamJourney(
            incident_id="inc_scam",
            scam_family="JOB_TASK",
            stage_history=[JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION, JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.INITIAL_PAYMENT],
        ),
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        payment_context={"deposit_requested": True, "amount": 3000},
        message_text="Earn ₹2000 daily from home. Pay ₹3000 refundable security deposit.",
    )

    # Legitimate recruitment
    dna_legit = ScamDNABuilder.build(
        incident_id="inc_legit",
        journey=ScamJourney(
            incident_id="inc_legit",
            scam_family="UNKNOWN",
            stage_history=[JourneyStage.CONTACT, JourneyStage.CONTACT],
        ),
        tactics=[],
        payment_context={},
        message_text="Thank you for applying to Senior Engineer at Infosys. Please join Google Meet tomorrow at 11 AM.",
    )

    match = sim_engine.compare(dna_scam, dna_legit)
    assert match.overall_similarity < 0.40
    assert match.variant_status in (VariantStatus.NOVEL_PATTERN, VariantStatus.INSUFFICIENT_EVIDENCE)


def test_legitimate_bank_kyc_hard_negative(sim_engine: ScamDNASimilarityEngine):
    """Section 122: Official bank advisory should NOT match KYC phishing DNA."""
    # Phishing DNA
    dna_phish = ScamDNABuilder.build(
        incident_id="inc_phish",
        journey=ScamJourney(
            incident_id="inc_phish",
            scam_family="KYC_BANK",
            stage_history=[JourneyStage.CONTACT, JourneyStage.IMPERSONATION, JourneyStage.CREDENTIAL_REQUEST],
        ),
        tactics=["URGENCY", "FEAR", "CREDENTIAL_PRESSURE"],
        entities=[{"entity_type": "BRAND", "canonical_value": "State Bank of India"}],
        message_text="SBI Alert: Your YONO account will be blocked today. Click http://sbi-kyc-update.top to update PAN immediately.",
        requested_actions=["SUBMIT_OTP", "ENTER_NETBANKING_PASSWORD"],
    )

    # Legitimate Bank Advisory
    dna_bank = ScamDNABuilder.build(
        incident_id="inc_bank",
        journey=ScamJourney(
            incident_id="inc_bank",
            scam_family="UNKNOWN",
            stage_history=[JourneyStage.CONTACT],
        ),
        tactics=[],
        entities=[{"entity_type": "BRAND", "canonical_value": "State Bank of India"}],
        message_text="Dear SBI Customer, periodic KYC update is due for your account. Please visit your nearest branch or update via official YONO app. Never share OTP with anyone.",
    )

    match = sim_engine.compare(dna_phish, dna_bank)
    assert match.overall_similarity < 0.45
    assert match.variant_status != VariantStatus.KNOWN_PATTERN


def test_partial_journey_early_dna_match(sim_engine: ScamDNASimilarityEngine):
    """Section 123: Early partial journey prefix produces early pattern similarity with calibrated uncertainty."""
    # Full known task scam template
    full_dna = ScamDNABuilder.build(
        incident_id="inc_full_task",
        journey=ScamJourney(
            incident_id="inc_full_task",
            scam_family="JOB_TASK",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.PLATFORM_MIGRATION,
                JourneyStage.REWARD_OR_FAKE_PROFIT,
                JourneyStage.INITIAL_PAYMENT,
                JourneyStage.PAYMENT_ESCALATION,
            ],
        ),
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        payment_context={"prior_reward": True, "deposit_requested": True},
    )

    # Prefix interaction: Contact -> Migration -> Small Reward (Before deposit is requested)
    prefix_dna = ScamDNABuilder.build(
        incident_id="inc_prefix",
        journey=ScamJourney(
            incident_id="inc_prefix",
            scam_family="JOB_TASK",
            stage_history=[
                JourneyStage.CONTACT,
                JourneyStage.PLATFORM_MIGRATION,
                JourneyStage.REWARD_OR_FAKE_PROFIT,
            ],
        ),
        tactics=["TRUST_BUILDING", "FAKE_REWARD"],
        payment_context={"prior_reward": True},
    )

    match = sim_engine.compare(full_dna, prefix_dna)
    assert match.overall_similarity >= 0.55
    assert match.variant_status in (VariantStatus.POSSIBLE_VARIANT, VariantStatus.LIKELY_VARIANT)


def test_multilingual_code_mixed_dna_preservation(sim_engine: ScamDNASimilarityEngine):
    """Section 124: English vs Hinglish versions of the same task scam preserve behavioral similarity."""
    dna_en = ScamDNABuilder.build(
        incident_id="inc_en",
        journey=ScamJourney(
            incident_id="inc_en",
            stage_history=[JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION, JourneyStage.INITIAL_PAYMENT],
        ),
        tactics=["TRUST_BUILDING", "PAYMENT_PRESSURE"],
        payment_context={"deposit_requested": True},
        message_text="Part-time job: Like videos on YouTube and earn ₹2000 daily. Deposit ₹1000 to start.",
    )

    dna_hi = ScamDNABuilder.build(
        incident_id="inc_hi",
        journey=ScamJourney(
            incident_id="inc_hi",
            stage_history=[JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION, JourneyStage.INITIAL_PAYMENT],
        ),
        tactics=["TRUST_BUILDING", "PAYMENT_PRESSURE"],
        payment_context={"deposit_requested": True},
        message_text="Ghar baithe paise kamao: YouTube video like karo aur daily 2000 banao. Start karne ke liye 1000 jama karein.",
    )

    match = sim_engine.compare(dna_en, dna_hi)
    assert match.overall_similarity >= 0.70
    assert match.variant_status in (VariantStatus.KNOWN_PATTERN, VariantStatus.LIKELY_VARIANT)


def test_contradiction_penalty(sim_engine: ScamDNASimilarityEngine):
    """Section 126: Superficially similar wording with contradictory authority/identity triggers penalty."""
    dna1 = ScamDNABuilder.build(
        incident_id="c1",
        tactics=["AUTHORITY", "THREAT", "ISOLATION"],
        entities=[{"entity_type": "ORGANIZATION", "canonical_value": "Mumbai Police"}],
        message_text="Police warning: Immediate arrest warrant issued.",
    )

    dna2 = ScamDNABuilder.build(
        incident_id="c2",
        tactics=[],
        entities=[{"entity_type": "ORGANIZATION", "canonical_value": "Consumer Forum"}],
        message_text="Consumer advisory regarding online shopping rights.",
    )

    match = sim_engine.compare(dna1, dna2)
    assert len(match.contradictions) > 0
    assert match.overall_similarity < 0.40


def test_v2_backward_compatibility_adapter():
    """Verifies bidirectional conversion between ScamFingerprintV2 and ScamDNA V3."""
    legacy_fp = ScamFingerprintV2(
        fingerprint_id="fp_legacy_001",
        incident_id="inc_legacy_100",
        ordered_event_sequence=["MESSAGE_RECEIVED", "LINK_CLICKED", "PAYMENT_REQUEST"],
        social_engineering_tactics=["URGENCY", "FEAR"],
        claimed_identity="HDFC Bank",
        requested_actions=["UPDATE_KYC", "SUBMIT_OTP"],
        payment_entities={"vpa": "fraud@oksbi", "channel_type": "UPI"},
    )

    # 1. Convert to ScamDNA V3
    dna = ScamFingerprintV2Adapter.to_dna(legacy_fp)
    assert dna.incident_id == "inc_legacy_100"
    assert dna.dimensions[DNADimensionType.JOURNEY.value].available is True
    assert dna.dimensions[DNADimensionType.TACTIC.value].available is True
    assert dna.dimensions[DNADimensionType.IDENTITY.value].available is True

    # 2. Convert back to ScamFingerprintV2
    fp_back = ScamFingerprintV2Adapter.to_fingerprint_v2(dna)
    assert fp_back.incident_id == legacy_fp.incident_id
    assert fp_back.ordered_event_sequence == legacy_fp.ordered_event_sequence
    assert fp_back.claimed_identity == legacy_fp.claimed_identity

    # 3. EmergingVariantDetector handles ScamDNA directly
    eval_res = EmergingVariantDetector.evaluate(incident_id="inc_legacy_100", fingerprint=dna)
    assert eval_res.incident_id == "inc_legacy_100"


def test_two_stage_candidate_retrieval_efficiency(sim_engine: ScamDNASimilarityEngine):
    """Verifies that DNACandidateIndex retrieves and ranks top-K candidate DNAs efficiently."""
    index = DNACandidateIndex(similarity_engine=sim_engine)

    # Index 10 varied template DNAs
    for i in range(10):
        fam = "JOB_TASK" if i % 2 == 0 else "DIGITAL_ARREST"
        dna = ScamDNABuilder.build(
            incident_id=f"inc_seed_{i}",
            journey=ScamJourney(
                incident_id=f"inc_seed_{i}",
                scam_family=fam,
                stage_history=[JourneyStage.CONTACT, JourneyStage.INITIAL_PAYMENT],
            ),
            tactics=["TRUST_BUILDING"] if fam == "JOB_TASK" else ["AUTHORITY", "THREAT"],
        )
        index.index_dna(dna)

    # Query with a task scam DNA
    query = ScamDNABuilder.build(
        incident_id="inc_query",
        journey=ScamJourney(
            incident_id="inc_query",
            scam_family="JOB_TASK",
            stage_history=[JourneyStage.CONTACT, JourneyStage.INITIAL_PAYMENT],
        ),
        tactics=["TRUST_BUILDING"],
    )

    matches = index.find_similar(query, top_k=3)
    assert len(matches) <= 3
    # All top matches should be the JOB_TASK seeds
    assert all(m.overall_similarity >= 0.70 for m in matches)


def test_consumer_and_analyst_views(dna_service: ScamDNAService):
    """Verifies that serializers produce plain-language consumer views and forensic analyst views."""
    dna1 = dna_service.create_or_update_dna(
        incident_id="inc_views_test",
        journey=ScamJourney(
            incident_id="inc_views_test",
            scam_family="JOB_TASK",
            stage_history=[JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION, JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.INITIAL_PAYMENT],
            channels=["INSTAGRAM", "WHATSAPP", "TELEGRAM", "UPI"],
        ),
        tactics=["TRUST_BUILDING", "PAYMENT_PRESSURE"],
        payment_context={"prior_reward": True, "deposit_requested": True},
    )

    # 1. Consumer view
    c_view = dna_service.serialize_consumer_view("inc_views_test")
    assert c_view is not None
    assert "Task Scam" in c_view.summary_headline
    assert len(c_view.behavioral_traits) >= 1
    assert "DO NOT" in c_view.recommended_action or "PAUSE" in c_view.recommended_action
    assert c_view.confidence_label in ("HIGH", "MODERATE")

    # 2. Analyst view
    a_view = dna_service.serialize_analyst_view("inc_views_test")
    assert a_view is not None
    assert a_view["dna_id"] == dna1.dna_id
    assert "dimensions" in a_view
    assert len(a_view["dimensions"]) == 8


def test_api_endpoints():
    """Verifies that FastAPI ScamDNA endpoints return 200 with appropriate payload structure."""
    client = TestClient(app)

    # 1. Create incident and add event
    resp_create = client.post("/api/v1/incidents", json={"user_identifier_hash": "user_dna_api", "channel": "SMS"})
    assert resp_create.status_code == 201
    inc_id = resp_create.json()["id"]

    client.post(f"/api/v1/incidents/{inc_id}/events", json={
        "event_type": "MESSAGE_RECEIVED",
        "payload": {"text": "Congratulations! Claim your ₹150 profit on WhatsApp."},
    })

    # 2. GET /{incident_id}/dna
    resp_dna = client.get(f"/api/v1/incidents/{inc_id}/dna")
    assert resp_dna.status_code == 200
    dna_data = resp_dna.json()
    assert dna_data["incident_id"] == inc_id
    assert "dimensions" in dna_data

    # 3. POST /{incident_id}/dna/rebuild
    resp_reb = client.post(f"/api/v1/incidents/{inc_id}/dna/rebuild")
    assert resp_reb.status_code == 200
    assert resp_reb.json()["incident_id"] == inc_id

    # 4. GET /{incident_id}/dna/similar
    resp_sim = client.get(f"/api/v1/incidents/{inc_id}/dna/similar")
    assert resp_sim.status_code == 200
    assert isinstance(resp_sim.json(), list)

    # 5. GET /{incident_id}/dna/consumer
    resp_cv = client.get(f"/api/v1/incidents/{inc_id}/dna/consumer")
    assert resp_cv.status_code == 200
    assert "summary_headline" in resp_cv.json()
