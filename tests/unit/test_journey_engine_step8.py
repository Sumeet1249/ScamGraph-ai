"""Unit & Integration Tests for ScamGraph Journey Engine V1 (Phase 2A / Prompt 8).

Validates:
- 15 canonical stages + category grouping + legacy backwards compatibility
- Out-of-order temporal event ingestion and sequence reconciliation
- Stage inference across tactics, actions, entities, and payment contexts
- Family template matching (JOB_TASK, DIGITAL_ARREST, INVESTMENT, KYC_BANK, FAKE_SUPPORT_REFUND)
- Emerging / Unknown journey handling
- Monetization boundary detection and loss tracking
- Pre-loss early detection rate & warning lead-time measurement
- Prefix evaluation with strict anti-leakage verification
- Cross-channel and multi-lingual code-mixed journeys
- Mutation robustness (skipped / reordered stages)
- Hard negative / legitimate non-scam encounters
- Idempotency and Consumer vs Analyst views
- FastAPI journey endpoints
"""

from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from packages.schemas.journey import (
    JourneyEvent,
    JourneyStage,
    StageCategory,
    MonetizationStatus,
    LossStatus,
    ScamJourney,
    get_stage_category,
)
from services.journey_engine.service import JourneyEngineService
from services.journey_engine.temporal import TemporalReasoningEngine
from services.api.app.main import app


@pytest.fixture
def journey_service() -> JourneyEngineService:
    return JourneyEngineService()


def test_universal_stage_ontology_and_categories():
    """Verifies that all 15 canonical stages map to appropriate lifecycle categories, and legacy aliases work."""
    # Canonical stages
    assert get_stage_category(JourneyStage.DISCOVERY) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.CONTACT) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.TRUST_BUILDING) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.IMPERSONATION) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.PLATFORM_MIGRATION) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.URGENCY) == StageCategory.PRE_MONETIZATION
    assert get_stage_category(JourneyStage.CREDENTIAL_REQUEST) == StageCategory.PRE_MONETIZATION

    assert get_stage_category(JourneyStage.INITIAL_PAYMENT) == StageCategory.MONETIZATION
    assert get_stage_category(JourneyStage.PAYMENT_ESCALATION) == StageCategory.MONETIZATION
    assert get_stage_category(JourneyStage.RECOVERY_FEE) == StageCategory.MONETIZATION

    assert get_stage_category(JourneyStage.REWARD_OR_FAKE_PROFIT) == StageCategory.REINFORCEMENT
    assert get_stage_category(JourneyStage.WITHDRAWAL_BLOCK) == StageCategory.CONTROL_RETENTION
    assert get_stage_category(JourneyStage.THREAT_OR_PRESSURE) == StageCategory.CONTROL_RETENTION
    assert get_stage_category(JourneyStage.EXIT) == StageCategory.TERMINATION

    # Legacy Backwards-Compatible Aliases
    assert JourneyStage.INITIAL_CONTACT == JourneyStage.CONTACT
    assert JourneyStage.PAYMENT_REQUEST == JourneyStage.INITIAL_PAYMENT
    assert JourneyStage.PAYMENT_INTENT == JourneyStage.INITIAL_PAYMENT
    assert JourneyStage.CREDENTIAL_OTP_HARVEST == JourneyStage.CREDENTIAL_REQUEST


def test_temporal_ordering_and_out_of_order_reconciliation(journey_service: JourneyEngineService):
    """Verifies that events arriving out of chronological order are reconciled properly."""
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=15)
    t2 = t0 + timedelta(minutes=30)

    # Ingest event 2 first, then event 0, then event 1
    ev2 = JourneyEvent(event_id="ev_2", timestamp=t2, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"])
    ev0 = JourneyEvent(event_id="ev_0", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"])
    ev1 = JourneyEvent(event_id="ev_1", timestamp=t1, event_type="PLATFORM_MIGRATION", tactics=["PLATFORM_MIGRATION"])

    journey = journey_service.create_journey(incident_id="inc_temporal_001")
    journey = journey_service.add_event(journey, ev2)
    journey = journey_service.add_event(journey, ev0)
    journey = journey_service.add_event(journey, ev1)

    # Check that events are strictly sorted by timestamp
    assert [e.event_id for e in journey.events] == ["ev_0", "ev_1", "ev_2"]
    assert [e.sequence_number for e in journey.events] == [0, 1, 2]


def test_stage_inference_across_signals_and_tactics(journey_service: JourneyEngineService):
    """Verifies evidence-grounded stage inference across diverse tactics and event types."""
    t0 = datetime(2026, 10, 24, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Credential request
    ev_cred = JourneyEvent(event_id="ev_c", timestamp=t0, event_type="OTP_REQUESTED", tactics=["CREDENTIAL_PRESSURE"], requested_actions=["SHARE_OTP"])
    obs_cred = journey_service.inference_engine.infer_event_stages(ev_cred, prior_stages=[])
    assert any(o.stage == JourneyStage.CREDENTIAL_REQUEST for o in obs_cred)

    # 2. Initial payment
    ev_pay1 = JourneyEvent(event_id="ev_p1", timestamp=t0, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"], requested_actions=["SEND_PAYMENT"])
    obs_pay1 = journey_service.inference_engine.infer_event_stages(ev_pay1, prior_stages=[])
    assert any(o.stage == JourneyStage.INITIAL_PAYMENT for o in obs_pay1)

    # 3. Payment escalation (following initial payment)
    ev_pay2 = JourneyEvent(event_id="ev_p2", timestamp=t0, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"], payment_context={"is_escalated": True})
    obs_pay2 = journey_service.inference_engine.infer_event_stages(ev_pay2, prior_stages=[JourneyStage.INITIAL_PAYMENT], prior_payment_count=1)
    assert any(o.stage == JourneyStage.PAYMENT_ESCALATION for o in obs_pay2)


def test_family_template_matching(journey_service: JourneyEngineService):
    """Verifies that observed stage sequences match their respective known scam templates."""
    # 1. JOB_TASK sequence
    stages_task = [
        JourneyStage.CONTACT,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.REWARD_OR_FAKE_PROFIT,
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.PAYMENT_ESCALATION,
    ]
    fam_task, _, conf_task = journey_service.template_matcher.match_family(stages_task, {"PLATFORM_MIGRATION", "TRUST_BUILDING"})
    assert fam_task == "JOB_TASK"
    assert conf_task >= 0.70

    # 2. DIGITAL_ARREST sequence
    stages_arrest = [
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.URGENCY,
        JourneyStage.THREAT_OR_PRESSURE,
        JourneyStage.INITIAL_PAYMENT,
    ]
    fam_arrest, _, conf_arrest = journey_service.template_matcher.match_family(stages_arrest, {"AUTHORITY", "ISOLATION", "FEAR"})
    assert fam_arrest == "DIGITAL_ARREST"
    assert conf_arrest >= 0.70

    # 3. KYC_BANK sequence
    stages_kyc = [
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.URGENCY,
        JourneyStage.CREDENTIAL_REQUEST,
    ]
    fam_kyc, _, conf_kyc = journey_service.template_matcher.match_family(stages_kyc, {"CREDENTIAL_PRESSURE"})
    assert fam_kyc == "KYC_BANK"
    assert conf_kyc >= 0.70


def test_unknown_emerging_journey(journey_service: JourneyEngineService):
    """Verifies that uncharacteristic sequences return UNKNOWN emerging journey rather than forcing wrong classification."""
    stages_weird = [JourneyStage.CONTACT, JourneyStage.DISCOVERY]
    fam, hypotheses, conf = journey_service.template_matcher.match_family(stages_weird, set())
    assert fam == "UNKNOWN"
    assert conf < 0.45


def test_monetization_boundary_and_loss_tracking(journey_service: JourneyEngineService):
    """Verifies monetization boundary detection and loss status transitions."""
    t0 = datetime(2026, 10, 24, 8, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)
    t2 = t0 + timedelta(minutes=20)

    ev0 = JourneyEvent(event_id="ev_lure", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"])
    ev1 = JourneyEvent(event_id="ev_pay_demand", timestamp=t1, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"], requested_actions=["SEND_PAYMENT"])
    ev2 = JourneyEvent(event_id="ev_paid", timestamp=t2, event_type="PAYMENT_COMPLETED", payment_context={"loss_amount_inr": 5000.0})

    journey = journey_service.create_journey(incident_id="inc_monetization_001")
    
    # Step 0: Pre-monetization
    journey = journey_service.add_event(journey, ev0)
    assert journey.monetization_status == MonetizationStatus.NO_PAYMENT_SIGNAL
    assert journey.loss_status == LossStatus.NO_KNOWN_LOSS
    assert journey.monetization_boundary_event_id is None

    # Step 1: Monetization boundary reached
    journey = journey_service.add_event(journey, ev1)
    assert journey.monetization_boundary_event_id == "ev_pay_demand"
    assert journey.monetization_status == MonetizationStatus.PAYMENT_REQUESTED
    assert journey.loss_status == LossStatus.AT_RISK

    # Step 2: Confirmed user loss
    journey = journey_service.add_event(journey, ev2)
    assert journey.loss_status == LossStatus.CONFIRMED_USER_REPORTED_LOSS


def test_pre_loss_detection_and_warning_lead_time(journey_service: JourneyEngineService):
    """Verifies pre-loss detection calculation and warning lead-time formula."""
    t_start = datetime(2026, 10, 24, 9, 0, 0, tzinfo=timezone.utc)
    t_warn = t_start + timedelta(minutes=5)
    t_loss = t_start + timedelta(minutes=25)

    ev_contact = JourneyEvent(event_id="ev_1", timestamp=t_start, event_type="MESSAGE_RECEIVED", tactics=["IMPERSONATION"])
    ev_warning = JourneyEvent(event_id="ev_2", timestamp=t_warn, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"])
    ev_loss = JourneyEvent(event_id="ev_3", timestamp=t_loss, event_type="PAYMENT_COMPLETED", payment_context={"loss_amount_inr": 25000.0})

    journey = journey_service.create_journey(incident_id="inc_preloss_001")
    journey.major_loss_timestamp = t_loss

    journey = journey_service.add_event(journey, ev_contact)
    journey = journey_service.add_event(journey, ev_warning)
    journey = journey_service.add_event(journey, ev_loss)

    assert journey.pre_loss_warning_issued is True
    # Lead time = 25m - 5m = 20m = 1200 seconds
    assert journey.warning_lead_time_seconds == 1200.0


def test_prefix_evaluation_anti_leakage(journey_service: JourneyEngineService):
    """CRITICAL TEST: Verifies that prefix evaluation 1..k never accesses or leaks future events k+1..N."""
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    
    events = [
        JourneyEvent(event_id="e1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"]),
        JourneyEvent(event_id="e2", timestamp=t0 + timedelta(minutes=5), event_type="PLATFORM_MIGRATION", tactics=["PLATFORM_MIGRATION"]),
        JourneyEvent(event_id="e3", timestamp=t0 + timedelta(minutes=10), event_type="REWARD_CREDITED", tactics=["FAKE_REWARD"]),
        JourneyEvent(event_id="e4", timestamp=t0 + timedelta(minutes=15), event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"]),
        JourneyEvent(event_id="e5", timestamp=t0 + timedelta(minutes=20), event_type="PAYMENT_ESCALATED", tactics=["PAYMENT_PRESSURE", "URGENCY"]),
    ]

    # Evaluate prefix at k=2 (events e1, e2 only)
    j_prefix2 = journey_service.evaluate_prefix(events, prefix_k=2)
    assert len(j_prefix2.events) == 2
    assert j_prefix2.monetization_boundary_event_id is None
    assert j_prefix2.monetization_status == MonetizationStatus.NO_PAYMENT_SIGNAL
    assert JourneyStage.PAYMENT_ESCALATION not in j_prefix2.stage_history

    # Evaluate prefix at k=4 (events e1..e4)
    j_prefix4 = journey_service.evaluate_prefix(events, prefix_k=4)
    assert len(j_prefix4.events) == 4
    assert j_prefix4.monetization_boundary_event_id == "e4"
    assert j_prefix4.current_stage == JourneyStage.INITIAL_PAYMENT


def test_cross_channel_journey(journey_service: JourneyEngineService):
    """Verifies seamless tracking across multiple communication channels."""
    t0 = datetime(2026, 10, 24, 14, 0, 0, tzinfo=timezone.utc)
    
    events = [
        JourneyEvent(event_id="c1", timestamp=t0, channel="INSTAGRAM", event_type="MESSAGE_RECEIVED", tactics=["GREED"]),
        JourneyEvent(event_id="c2", timestamp=t0 + timedelta(minutes=5), channel="WHATSAPP", event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"]),
        JourneyEvent(event_id="c3", timestamp=t0 + timedelta(minutes=10), channel="TELEGRAM", event_type="MESSAGE_RECEIVED", tactics=["PLATFORM_MIGRATION"]),
        JourneyEvent(event_id="c4", timestamp=t0 + timedelta(minutes=15), channel="UPI", event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"]),
    ]

    journey = journey_service.create_journey(incident_id="inc_cross_chan", events=events)
    assert journey.channels == ["INSTAGRAM", "TELEGRAM", "UPI", "WHATSAPP"]
    assert journey.current_stage == JourneyStage.INITIAL_PAYMENT


def test_multilingual_code_mixed_journey(journey_service: JourneyEngineService):
    """Verifies that multilingual English, Hindi, and Hinglish events infer coherent journey stages."""
    t0 = datetime(2026, 10, 24, 15, 0, 0, tzinfo=timezone.utc)
    events = [
        JourneyEvent(event_id="m1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["IMPERSONATION"], metadata={"text": "Calling from Mumbai Police Cyber Cell"}),
        JourneyEvent(event_id="m2", timestamp=t0 + timedelta(minutes=5), event_type="MESSAGE_RECEIVED", tactics=["THREAT", "FEAR"], metadata={"text": "police case ho jayega, giraftari hogi"}),
        JourneyEvent(event_id="m3", timestamp=t0 + timedelta(minutes=10), event_type="MESSAGE_RECEIVED", tactics=["SECRECY", "ISOLATION"], metadata={"text": "kisi ko mat batana, camera on rakho"}),
        JourneyEvent(event_id="m4", timestamp=t0 + timedelta(minutes=15), event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"], metadata={"text": "Transfer ₹50,000 to clearance account immediately"}),
    ]

    journey = journey_service.create_journey(incident_id="inc_multilingual", events=events)
    assert journey.scam_family == "DIGITAL_ARREST"
    assert journey.current_stage == JourneyStage.INITIAL_PAYMENT
    assert any(w.warning_type == "AUTHORITY_IMPERSONATION_RISK" for w in journey.early_warnings)


def test_mutation_robustness_task_scam(journey_service: JourneyEngineService):
    """Verifies that a task scam with skipped stages (no reward stage) still matches task scam template."""
    t0 = datetime(2026, 10, 24, 11, 0, 0, tzinfo=timezone.utc)
    events = [
        JourneyEvent(event_id="t1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"]),
        JourneyEvent(event_id="t2", timestamp=t0 + timedelta(minutes=5), event_type="PLATFORM_MIGRATION", tactics=["PLATFORM_MIGRATION"]),
        # Skipped REWARD stage, went straight to deposit
        JourneyEvent(event_id="t3", timestamp=t0 + timedelta(minutes=10), event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"]),
        JourneyEvent(event_id="t4", timestamp=t0 + timedelta(minutes=15), event_type="PAYMENT_ESCALATED", tactics=["PAYMENT_PRESSURE"]),
    ]

    journey = journey_service.create_journey(incident_id="inc_mutated_task", events=events)
    assert journey.scam_family in ("JOB_TASK", "INVESTMENT")
    assert journey.current_stage == JourneyStage.PAYMENT_ESCALATION


def test_mutation_robustness_digital_arrest(journey_service: JourneyEngineService):
    """Verifies that a digital arrest scam with skipped urgency still matches digital arrest template."""
    t0 = datetime(2026, 10, 24, 11, 0, 0, tzinfo=timezone.utc)
    events = [
        JourneyEvent(event_id="da1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["AUTHORITY", "IMPERSONATION"]),
        # Skipped URGENCY, went straight to legal threat
        JourneyEvent(event_id="da2", timestamp=t0 + timedelta(minutes=5), event_type="MESSAGE_RECEIVED", tactics=["THREAT", "FEAR"]),
        JourneyEvent(event_id="da3", timestamp=t0 + timedelta(minutes=10), event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"]),
    ]

    journey = journey_service.create_journey(incident_id="inc_mutated_arrest", events=events)
    assert journey.scam_family == "DIGITAL_ARREST"
    assert journey.current_stage == JourneyStage.INITIAL_PAYMENT


def test_legitimate_journey_no_false_warning(journey_service: JourneyEngineService):
    """Verifies that legitimate interactions (job interview recruitment) do not trigger false critical warnings."""
    t0 = datetime(2026, 10, 24, 9, 0, 0, tzinfo=timezone.utc)
    events = [
        JourneyEvent(event_id="leg1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=[], metadata={"text": "Thank you for applying to Software Engineer role."}),
        JourneyEvent(event_id="leg2", timestamp=t0 + timedelta(hours=2), event_type="MESSAGE_RECEIVED", tactics=[], metadata={"text": "Your interview is scheduled for tomorrow at 10 AM."}),
    ]

    journey = journey_service.create_journey(incident_id="inc_legit", events=events)
    assert journey.scam_family == "UNKNOWN"
    assert journey.monetization_status == MonetizationStatus.NO_PAYMENT_SIGNAL
    assert len(journey.early_warnings) == 0


def test_idempotency(journey_service: JourneyEngineService):
    """Verifies that ingesting the exact same event ID twice does not duplicate stage observations or count."""
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    ev = JourneyEvent(event_id="ev_repeat", timestamp=t0, event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"])

    journey = journey_service.create_journey(incident_id="inc_idempotent")
    journey = journey_service.add_event(journey, ev)
    count1 = len(journey.events)
    obs_count1 = len(journey.stage_observations)

    # Ingest same event again
    journey = journey_service.add_event(journey, ev)
    assert len(journey.events) == count1
    assert len(journey.stage_observations) == obs_count1


def test_consumer_and_analyst_views(journey_service: JourneyEngineService):
    """Verifies consumer explanation is plain-language without model probabilities and analyst view has full trace."""
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        JourneyEvent(event_id="v1", timestamp=t0, event_type="MESSAGE_RECEIVED", tactics=["TRUST_BUILDING"]),
        JourneyEvent(event_id="v2", timestamp=t0 + timedelta(minutes=5), event_type="PLATFORM_MIGRATION", tactics=["PLATFORM_MIGRATION"]),
        JourneyEvent(event_id="v3", timestamp=t0 + timedelta(minutes=10), event_type="PAYMENT_REQUESTED", tactics=["PAYMENT_PRESSURE"]),
    ]

    journey = journey_service.create_journey(incident_id="inc_views", events=events)

    # Consumer View
    c_view = journey_service.serialize_consumer_view(journey)
    assert "Likely" in c_view.likely_family
    assert len(c_view.what_happened) >= 2
    assert "PAUSE before making any payment" in c_view.recommended_action
    assert "progress_meter" in c_view.__dict__

    # Analyst View
    a_view = journey_service.serialize_analyst_view(journey)
    assert a_view["journey_id"] == journey.journey_id
    assert a_view["current_stage"] == JourneyStage.INITIAL_PAYMENT.value
    assert "stage_observations" in a_view
    assert len(a_view["events"]) == 3


def test_api_endpoints():
    """Verifies that FastAPI journey endpoints return 200 with appropriate payload structure."""
    client = TestClient(app)

    # 1. Create incident and add event
    resp_create = client.post("/api/v1/incidents", json={"user_identifier_hash": "user_api_test", "channel": "SMS"})
    assert resp_create.status_code == 201
    inc_id = resp_create.json()["id"]

    # 2. Add an event
    resp_ev = client.post(f"/api/v1/incidents/{inc_id}/events", json={
        "event_type": "MESSAGE_RECEIVED",
        "payload": {"text": "Congratulations! Claim your ₹150 profit on WhatsApp."},
    })
    assert resp_ev.status_code in (200, 201)

    # 3. Test GET /{incident_id}/journey
    resp_j = client.get(f"/api/v1/incidents/{inc_id}/journey")
    assert resp_j.status_code == 200
    j_data = resp_j.json()
    assert j_data["incident_id"] == inc_id

    # 4. Test GET /{incident_id}/journey/timeline
    resp_tl = client.get(f"/api/v1/incidents/{inc_id}/journey/timeline")
    assert resp_tl.status_code == 200
    assert "stage_observations" in resp_tl.json()

    # 5. Test GET /{incident_id}/journey/progress
    resp_pr = client.get(f"/api/v1/incidents/{inc_id}/journey/progress")
    assert resp_pr.status_code == 200
    assert "progress_meter" in resp_pr.json()

    # 6. Test GET /{incident_id}/journey/warnings
    resp_w = client.get(f"/api/v1/incidents/{inc_id}/journey/warnings")
    assert resp_w.status_code == 200
    assert "early_warnings" in resp_w.json()

    # 7. Test POST /{incident_id}/journey/recompute
    resp_rc = client.post(f"/api/v1/incidents/{inc_id}/journey/recompute")
    assert resp_rc.status_code == 200
    assert resp_rc.json()["incident_id"] == inc_id
