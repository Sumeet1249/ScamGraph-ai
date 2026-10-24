"""Unit & Integration Tests for Cross-Victim & Cross-Incident Correlation Engine (Phase 3B).

Validates:
1. End-to-end Test A: Shared rare UPI + similar task journey -> STRONGLY_RELATED
2. End-to-end Test B: Identifier rotation (all IDs altered) + strong ScamDNA -> POSSIBLY_RELATED
3. End-to-end Test C: Unrelated digital-arrest (same family, distant time, distinct IDs) -> WEAK_SIGNAL / NOT_RELATED
4. End-to-end Test D: Generic brand SBI + WhatsApp alone -> NOT_RELATED (0.0)
5. End-to-end Test E: Common CDN alone -> NOT_RELATED (0.0)
6. End-to-end Test F: Shared UPI with contradictory/incompatible journey -> contradiction penalty applied
7. Privacy firewall: Consumer tier never receives foreign incident ID, phone, UPI, or private messages
8. Multi-source candidate retrieval & budget capping
9. Super-node resilience: 20 incidents sharing Telegram do NOT explode relationships
10. Relationship reversal: on-demand recomputation updates state and retains history
11. Campaign candidate group emission (Prompt 12 preparation)
12. FastAPI endpoints integration
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from packages.schemas.correlation import (
    ConsumerNetworkSignalType,
    EvidenceStrength,
    RelationshipStatus,
)
from packages.schemas.dna import ScamDNA, DNADimensionType, DNAQuality
from packages.schemas.journey import JourneyStage, ScamJourney
from services.api.app.main import app
from services.correlation_engine.config import CorrelationConfig
from services.correlation_engine.features import CorrelationFeatureExtractor
from services.correlation_engine.retriever import CandidateRetriever
from services.correlation_engine.scorer import CorrelationScorer
from services.correlation_engine.serializer import CorrelationSerializer
from services.correlation_engine.service import (
    CrossIncidentCorrelationService,
    correlation_service,
)
from services.dna_engine.builder import ScamDNABuilder


@pytest.fixture
def test_config() -> CorrelationConfig:
    return CorrelationConfig.load()


@pytest.fixture
def service(test_config: CorrelationConfig) -> CrossIncidentCorrelationService:
    return CrossIncidentCorrelationService(config=test_config)


def test_shared_rare_upi_and_similar_task_journey_strongly_related(service: CrossIncidentCorrelationService):
    """Section 154 (Test A): Shared rare UPI + similar task journey -> STRONGLY_RELATED."""
    # Incident A: Instagram task offer -> WhatsApp -> Telegram -> ₹300 reward -> UPI X -> ₹5000 deposit
    journey_a = ScamJourney(
        incident_id="inc_task_a",
        scam_family="JOB_TASK",
        stage_history=[
            JourneyStage.CONTACT,
            JourneyStage.PLATFORM_MIGRATION,
            JourneyStage.REWARD_OR_FAKE_PROFIT,
            JourneyStage.INITIAL_PAYMENT,
            JourneyStage.PAYMENT_ESCALATION,
        ],
        channels=["INSTAGRAM", "WHATSAPP", "TELEGRAM", "UPI"],
        monetization_boundary_event_id="e_dep_a",
    )
    dna_a = ScamDNABuilder.build(
        incident_id="inc_task_a",
        journey=journey_a,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        entities=[
            {"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "merchant.task88@icici"},
            {"entity_type": "PHONE_NUMBER", "canonical_value": "+919876543210"},
        ],
        payment_context={"prior_reward": True, "deposit_requested": True, "amount": 5000},
        message_text="Complete like tasks to earn ₹300 welcome commission. Recharge ₹5000 to VIP account.",
    )

    # Incident B: Facebook review job -> WhatsApp -> private group -> ₹250 reward -> SAME UPI X -> ₹4500 recharge
    journey_b = ScamJourney(
        incident_id="inc_task_b",
        scam_family="JOB_TASK",
        stage_history=[
            JourneyStage.CONTACT,
            JourneyStage.PLATFORM_MIGRATION,
            JourneyStage.REWARD_OR_FAKE_PROFIT,
            JourneyStage.INITIAL_PAYMENT,
            JourneyStage.PAYMENT_ESCALATION,
        ],
        channels=["FACEBOOK", "WHATSAPP", "PRIVATE_CHAT", "UPI"],
        monetization_boundary_event_id="e_rech_b",
    )
    dna_b = ScamDNABuilder.build(
        incident_id="inc_task_b",
        journey=journey_b,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        entities=[
            {"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "merchant.task88@icici"},  # SAME UPI
            {"entity_type": "PHONE_NUMBER", "canonical_value": "+918765432109"},  # Different phone
        ],
        payment_context={"prior_reward": True, "deposit_requested": True, "amount": 4500},
        message_text="Merchant order evaluation part-time job. Earn ₹250 bonus. Recharge ₹4500 to unlock commission.",
    )

    service.register_incident(
        incident_id="inc_task_a",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "merchant.task88@icici"}],
        scam_family="JOB_TASK",
        dna=dna_a,
        journey=journey_a,
        channels=["INSTAGRAM", "WHATSAPP", "TELEGRAM", "UPI"],
    )
    service.register_incident(
        incident_id="inc_task_b",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "merchant.task88@icici"}],
        scam_family="JOB_TASK",
        dna=dna_b,
        journey=journey_b,
        channels=["FACEBOOK", "WHATSAPP", "PRIVATE_CHAT", "UPI"],
    )

    correlation = service.correlate_pair("inc_task_a", "inc_task_b")
    assert correlation.relationship_status == RelationshipStatus.STRONGLY_RELATED
    assert correlation.overall_score >= 0.78
    assert correlation.confidence >= 0.85
    assert correlation.evidence_strength == EvidenceStrength.VERY_STRONG
    assert "SHARED_PAYMENT_IDENTIFIER" in correlation.positive_reasons


def test_identifier_rotation_behavioral_candidate(service: CrossIncidentCorrelationService):
    """Section 155 (Test B): 100% altered identifiers + strong ScamDNA -> POSSIBLY_RELATED."""
    journey_a = ScamJourney(
        incident_id="inc_rot_a",
        scam_family="JOB_TASK",
        stage_history=[
            JourneyStage.CONTACT,
            JourneyStage.PLATFORM_MIGRATION,
            JourneyStage.REWARD_OR_FAKE_PROFIT,
            JourneyStage.INITIAL_PAYMENT,
        ],
        channels=["INSTAGRAM", "TELEGRAM"],
    )
    dna_a = ScamDNABuilder.build(
        incident_id="inc_rot_a",
        journey=journey_a,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "alpha.pay@okhdfc"}],
        payment_context={"prior_reward": True, "deposit_requested": True},
        message_text="Like 3 videos on YouTube for ₹150. Deposit ₹2000 for level 1 tasks.",
    )

    journey_b = ScamJourney(
        incident_id="inc_rot_b",
        scam_family="JOB_TASK",
        stage_history=[
            JourneyStage.CONTACT,
            JourneyStage.PLATFORM_MIGRATION,
            JourneyStage.REWARD_OR_FAKE_PROFIT,
            JourneyStage.INITIAL_PAYMENT,
        ],
        channels=["FACEBOOK", "WHATSAPP"],
    )
    dna_b = ScamDNABuilder.build(
        incident_id="inc_rot_b",
        journey=journey_b,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "beta.merchant@ybl"}],  # Completely different UPI
        payment_context={"prior_reward": True, "deposit_requested": True},
        message_text="Review 3 products on merchant site for ₹200. Recharge ₹2500 for tier 1 assignments.",
    )

    service.register_incident(
        incident_id="inc_rot_a",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "alpha.pay@okhdfc"}],
        scam_family="JOB_TASK",
        dna=dna_a,
        journey=journey_a,
    )
    service.register_incident(
        incident_id="inc_rot_b",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "beta.merchant@ybl"}],
        scam_family="JOB_TASK",
        dna=dna_b,
        journey=journey_b,
    )

    correlation = service.correlate_pair("inc_rot_a", "inc_rot_b")
    # Behavioral candidate without shared entity must NOT jump to STRONGLY_RELATED
    assert correlation.relationship_status == RelationshipStatus.POSSIBLY_RELATED
    assert 0.50 <= correlation.overall_score <= 0.65
    assert correlation.evidence_strength == EvidenceStrength.MODERATE


def test_same_family_distant_unrelated_digital_arrest(service: CrossIncidentCorrelationService):
    """Section 156 (Test C): Two independent digital arrest scams distant in time with different entities."""
    t_now = datetime.now(timezone.utc)
    t_old = t_now - timedelta(days=180)

    service.register_incident(
        incident_id="inc_da_1",
        entities=[{"entity_type": "PHONE_NUMBER", "canonical_value": "+919111111111"}],
        scam_family="DIGITAL_ARREST",
        text="FedEx parcel drugs case. Transferred to Mumbai Police.",
        observed_at=t_old,
    )
    service.register_incident(
        incident_id="inc_da_2",
        entities=[{"entity_type": "PHONE_NUMBER", "canonical_value": "+919222222222"}],
        scam_family="DIGITAL_ARREST",
        text="TRAI Aadhaar SIM cancellation notice. CBI investigation order.",
        observed_at=t_now,
    )

    correlation = service.correlate_pair("inc_da_1", "inc_da_2")
    # No shared rare entities and distant in time -> NOT_RELATED or WEAK_SIGNAL
    assert correlation.relationship_status in (RelationshipStatus.NOT_RELATED, RelationshipStatus.WEAK_SIGNAL)
    assert correlation.overall_score < 0.35


def test_generic_brand_supernode_alone_not_related(service: CrossIncidentCorrelationService):
    """Section 157 (Test D): Both incidents mention generic brand SBI and WhatsApp -> NOT_RELATED (0.0)."""
    service.register_incident(
        incident_id="inc_sbi_1",
        entities=[
            {"entity_type": "BRAND", "canonical_value": "State Bank of India"},
            {"entity_type": "PLATFORM", "canonical_value": "WhatsApp"},
        ],
        scam_family="KYC_BANK",
        text="SBI KYC blocked. Contact via WhatsApp.",
    )
    service.register_incident(
        incident_id="inc_sbi_2",
        entities=[
            {"entity_type": "BRAND", "canonical_value": "State Bank of India"},
            {"entity_type": "PLATFORM", "canonical_value": "WhatsApp"},
        ],
        scam_family="KYC_BANK",
        text="Dear customer, your SBI account reward points expire today. WhatsApp us to claim.",
    )

    correlation = service.correlate_pair("inc_sbi_1", "inc_sbi_2")
    assert correlation.relationship_status == RelationshipStatus.NOT_RELATED
    assert correlation.overall_score == 0.0
    assert any("GENERIC" in r for r in correlation.negative_reasons)


def test_common_cdn_alone_not_related(service: CrossIncidentCorrelationService):
    """Section 158 (Test E): Shared Cloudflare domain alone -> NOT_RELATED (0.0)."""
    service.register_incident(
        incident_id="inc_cdn_1",
        entities=[{"entity_type": "DOMAIN", "canonical_value": "cloudflare.com"}],
        text="Phishing ad hosted via Cloudflare CDN.",
    )
    service.register_incident(
        incident_id="inc_cdn_2",
        entities=[{"entity_type": "DOMAIN", "canonical_value": "cloudflare.com"}],
        text="Crypto promo hosted via Cloudflare CDN.",
    )

    correlation = service.correlate_pair("inc_cdn_1", "inc_cdn_2")
    assert correlation.relationship_status == RelationshipStatus.NOT_RELATED
    assert correlation.overall_score == 0.0


def test_shared_upi_with_divergent_journey_contradiction(service: CrossIncidentCorrelationService):
    """Section 159 (Test F): Shared rare UPI but completely incompatible journey -> contradiction penalty."""
    # Incident 1: Task scam
    journey_task = ScamJourney(
        incident_id="inc_mix_task",
        scam_family="JOB_TASK",
        stage_history=[JourneyStage.CONTACT, JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.INITIAL_PAYMENT],
    )
    # Incident 2: Digital arrest legal extortion
    journey_arrest = ScamJourney(
        incident_id="inc_mix_arrest",
        scam_family="DIGITAL_ARREST",
        stage_history=[JourneyStage.CONTACT, JourneyStage.IMPERSONATION, JourneyStage.THREAT_OR_PRESSURE],
    )

    service.register_incident(
        incident_id="inc_mix_task",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "shared.mule@upi"}],
        scam_family="JOB_TASK",
        journey=journey_task,
    )
    service.register_incident(
        incident_id="inc_mix_arrest",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "shared.mule@upi"}],
        scam_family="DIGITAL_ARREST",
        journey=journey_arrest,
    )

    correlation = service.correlate_pair("inc_mix_task", "inc_mix_arrest")
    # Shared UPI signal is recognized, but contradiction penalty prevents uncalibrated STRONGLY_RELATED
    assert len(correlation.contradictions) > 0
    assert "INCOMPATIBLE_SCAM_FAMILY(JOB_TASK_VS_DIGITAL_ARREST)" in correlation.contradictions
    assert correlation.relationship_status != RelationshipStatus.STRONGLY_RELATED


def test_consumer_privacy_firewall(service: CrossIncidentCorrelationService):
    """Section 160: Consumer network alert must never reveal foreign victim incident IDs, phones, or UPIs."""
    # Register 3 related incidents sharing a payment identifier
    for i in range(1, 4):
        service.register_incident(
            incident_id=f"victim_report_{i}",
            entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "mule.syndicate@paytm"}],
            scam_family="JOB_TASK",
            text=f"Victim {i} private message text containing sensitive personal info.",
        )

    # Correlate victim_report_1 against others
    service.correlate_incident("victim_report_1")
    consumer_signal = service.get_network_signal("victim_report_1")

    assert consumer_signal.network_signal == ConsumerNetworkSignalType.MULTIPLE_RELATED_SIGNALS
    assert consumer_signal.related_reports_band == "MULTIPLE_REPORTS"
    assert consumer_signal.warning_level == "CRITICAL"
    assert consumer_signal.is_aggregate_safe is True

    # Assert ZERO leakage of foreign identifiers
    serialized_str = str(consumer_signal.model_dump())
    assert "victim_report_2" not in serialized_str
    assert "victim_report_3" not in serialized_str
    assert "mule.syndicate@paytm" not in serialized_str
    assert "sensitive personal info" not in serialized_str


def test_candidate_retrieval_and_budget_bounding(service: CrossIncidentCorrelationService):
    """Sections 9-12: Multi-source candidate retriever dedups and respects budget caps."""
    # Seed 40 dummy incidents
    for i in range(40):
        service.register_incident(
            incident_id=f"inc_seed_{i}",
            entities=[
                {"entity_type": "PHONE_NUMBER", "canonical_value": "+919876500000" if i < 10 else f"+9198765000{i}"},
            ],
            scam_family="INVESTMENT",
        )

    candidates = service.find_candidates("inc_seed_0")
    assert len(candidates) > 0
    assert len(candidates) <= service.config.max_total_candidates
    # First 9 share the exact phone
    shared_phone_cands = [c for c in candidates if any("SHARED_ENTITY" in r for r in c.source_reasons)]
    assert len(shared_phone_cands) >= 9


def test_supernode_resilience_telegram_does_not_explode(service: CrossIncidentCorrelationService):
    """Section 162: 25 incidents sharing Telegram platform do NOT produce spurious correlations."""
    for i in range(25):
        service.register_incident(
            incident_id=f"tg_inc_{i}",
            entities=[{"entity_type": "PLATFORM", "canonical_value": "Telegram"}],
            scam_family="UNKNOWN",
        )

    results = service.correlate_incident("tg_inc_0")
    # All pairs sharing only Telegram are filtered out or evaluated as NOT_RELATED
    meaningful = [r for r in results if r.relationship_status != RelationshipStatus.NOT_RELATED]
    assert len(meaningful) == 0


def test_relationship_reversal_on_entity_split(service: CrossIncidentCorrelationService):
    """Section 163: Reversing an entity merge cleanly updates and downgrades correlation."""
    service.register_incident(
        incident_id="rev_a",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "disputed.acc@upi"}],
    )
    service.register_incident(
        incident_id="rev_b",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "disputed.acc@upi"}],
    )

    corr1 = service.correlate_pair("rev_a", "rev_b")
    pair_id = service.get_canonical_pair_id("rev_a", "rev_b")
    assert pair_id in service._materialized_correlations

    # Disputed merge is reversed: rev_b is updated with a separate identifier
    service._incidents["rev_b"]["entities"] = [
        {"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "legitimate.clean@upi"}
    ]
    # Recompute
    corr2 = service.recompute_pair("rev_a", "rev_b")
    assert corr2.relationship_status == RelationshipStatus.NOT_RELATED
    # Materialized correlation was revoked
    assert pair_id not in service._materialized_correlations
    # History is preserved (2 entries)
    assert len(service._correlation_history[pair_id]) == 2


def test_campaign_candidate_group_emission(service: CrossIncidentCorrelationService):
    """Sections 87, 145-146: Generates CandidateIncidentGroup for future Campaign Clustering (Prompt 12)."""
    # Create cluster of 3 strongly related incidents
    for i in range(1, 4):
        service.register_incident(
            incident_id=f"camp_mem_{i}",
            entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "syndicate.vpa@upi"}],
            scam_family="JOB_TASK",
            channels=["WHATSAPP", "TELEGRAM", "UPI"],
        )

    group = service.generate_campaign_candidate_group(["camp_mem_1", "camp_mem_2", "camp_mem_3"])
    assert group.group_id.startswith("cand_grp_")
    assert len(group.member_incident_ids) == 3
    assert group.primary_family == "JOB_TASK"
    assert group.relationship_density >= 0.90
    assert group.strong_edge_count >= 3
    assert "SHARED_PAYMENT_IDENTIFIER" in group.evidence_diversity


def test_api_correlation_endpoints():
    """Section 122-124: FastAPI correlation endpoints testing."""
    client = TestClient(app)

    # Register an incident in correlation_service
    correlation_service.register_incident(
        incident_id="api_test_inc_1",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "api.mule@upi"}],
        scam_family="JOB_TASK",
    )
    correlation_service.register_incident(
        incident_id="api_test_inc_2",
        entities=[{"entity_type": "PAYMENT_IDENTIFIER", "canonical_value": "api.mule@upi"}],
        scam_family="JOB_TASK",
    )

    # 1. Candidate retrieval
    resp = client.get("/api/v1/incidents/api_test_inc_1/correlation-candidates")
    assert resp.status_code == 200
    candidates = resp.json()
    assert isinstance(candidates, list)

    # 2. Correlate endpoint
    resp = client.post("/api/v1/incidents/api_test_inc_1/correlate")
    assert resp.status_code == 200
    corrs = resp.json()
    assert len(corrs) >= 1

    # 3. Consumer network signal
    resp = client.get("/api/v1/incidents/api_test_inc_1/network-signal")
    assert resp.status_code == 200
    data = resp.json()
    assert data["incident_id"] == "api_test_inc_1"
    assert data["is_aggregate_safe"] is True

    # 4. Related incidents: CONSUMER vs ANALYST tier
    resp_consumer = client.get("/api/v1/incidents/api_test_inc_1/related?access_tier=CONSUMER")
    assert resp_consumer.status_code == 200
    assert "network_signal" in resp_consumer.json()

    resp_analyst = client.get("/api/v1/incidents/api_test_inc_1/related?access_tier=ANALYST")
    assert resp_analyst.status_code == 200
    assert isinstance(resp_analyst.json(), list)

    # 5. Analyst pair correlation view
    resp_pair = client.get("/api/v1/incidents/api_test_inc_1/correlations/api_test_inc_2")
    assert resp_pair.status_code == 200
    pair_view = resp_pair.json()
    assert "correlation" in pair_view
    assert "explainable_graph_paths" in pair_view
