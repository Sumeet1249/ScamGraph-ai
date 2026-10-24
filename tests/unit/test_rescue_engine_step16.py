"""Unit Tests for ScamGraph Rescue (Prompt 16 / Phase 5B).

Covers all 20 required acceptance criteria from PART AG:
1. Task Scam multiple payments (₹500, ₹5000, ₹20000 -> 3 LossEvents, timeline, ₹25,500 total, deduplication)
2. Digital Arrest (authority threat, isolation, payment -> anti-isolation, 1930, high priority)
3. OTP disclosure only (credential exposure, NO invented financial loss)
4. Remote Access exposure (device containment prioritized, airplane mode / kill AnyDesk)
5. Identity Document disclosure (Aadhaar/PAN exposure, no invented financial loss)
6. Already existing Protect incident transitions into Rescue
7. New direct Rescue case initiation
8. Recovery Scam warning (secondary advance-fee fraud detection)
9. Additional payment pressure ('pay tax to unlock' -> RECOVERY_FEE escalation)
10. Historical scam (> 30 days -> no false emergency freeze claims)
11. Approximate and uncertain timestamp handling
12. Partial information (only ₹8,000 via UPI known)
13. Duplicate payment transaction submission deduplication
14. Evidence integrity (original preservation, SHA-256 hashing)
15. Case package factual accuracy, legal disclaimer, and non-accusatory language
16. Pre-loss vs Post-loss evidence isolation (zero future leakage)
17. Campaign intelligence feedback candidate creation
18. Privacy protections (no victim enumeration or graph leak)
19. Mobile action plan structure
20. Degraded mode resilience (works when graph/campaign offline)
"""

from datetime import datetime, timedelta, timezone
import pytest

from packages.schemas.incident import Incident, IncidentStatus
from packages.schemas.journey import JourneyStage
from packages.schemas.rescue import (
    ActionCategory,
    ActionStatus,
    ExposureCategory,
    ExposureSeverity,
    LossEvent,
    LossStatus,
    LossType,
    TimeGranularity,
)
from services.rescue_engine.case_package import case_package_generator
from services.rescue_engine.feedback_loop import rescue_intelligence_feedback
from services.rescue_engine.reconstruction import (
    IncidentReconstructionService,
    incident_reconstruction_service,
)
from services.rescue_engine.resources import official_resources_registry
from services.rescue_engine.service import RescueService, rescue_service
from services.rescue_engine.triage import RescueTriageEngine, rescue_triage_engine


# TEST 1 — TASK SCAM, MULTIPLE PAYMENTS
def test_task_scam_multiple_payments():
    service = RescueService()
    inc = service.get_or_create_incident(initial_loss_type=LossType.UPI_PAYMENT)
    iid = inc.incident_id

    # User paid ₹500, then ₹5,000, then ₹20,000
    e1 = service.record_loss(iid, amount=500.0, payment_method="UPI", recipient_identifier="task1@okaxis")
    e2 = service.record_loss(iid, amount=5000.0, payment_method="UPI", recipient_identifier="task2@oksbi")
    e3 = service.record_loss(iid, amount=20000.0, payment_method="UPI", recipient_identifier="task3@icici")

    total_loss, curr, count = incident_reconstruction_service.calculate_reported_loss(iid)
    events = incident_reconstruction_service.get_loss_events(iid)

    assert count == 3
    assert len(events) == 3
    assert total_loss == 25500.00
    assert curr == "INR"

    # Check Journey events mapping
    j_events = incident_reconstruction_service.map_to_journey_events(iid)
    assert len(j_events) == 3
    assert JourneyStage.INITIAL_PAYMENT in j_events[0].stage_candidates
    assert JourneyStage.PAYMENT_ESCALATION in j_events[1].stage_candidates
    assert JourneyStage.PAYMENT_ESCALATION in j_events[2].stage_candidates


# TEST 2 — DIGITAL ARREST
def test_digital_arrest_rescue_priorities():
    service = RescueService()
    inc = service.get_or_create_incident(initial_loss_type=LossType.BANK_TRANSFER, user_notes="CBI fake officer video call")
    inc.likely_scam_family = "digital_arrest"
    iid = inc.incident_id

    service.record_loss(iid, amount=150000.0, payment_method="RTGS", recipient_identifier="987654321012@sbi")
    triage = service.get_triage(iid, ongoing_contact=True)
    plan = service.get_action_plan(iid, ongoing_contact=True)

    assert triage.priority == "EMERGENCY_CRITICAL"
    assert triage.financial_exposure is True
    assert triage.ongoing_contact is True

    # Check anti-isolation and 1930 presence in DO NOW / DO NEXT
    do_now_titles = [a.title for a in plan.do_now]
    do_next_titles = [a.title for a in plan.do_next]

    assert any("1930" in t for t in do_now_titles)
    assert any("Cease Communication" in t for t in do_now_titles)
    assert any("Trusted Family" in t or "Colleague" in t for t in do_next_titles)


# TEST 3 — OTP ONLY
def test_otp_disclosure_no_monetary_loss():
    service = RescueService()
    inc = service.get_or_create_incident(initial_loss_type=LossType.OTP_DISCLOSURE)
    iid = inc.incident_id

    service.record_exposure(
        iid,
        category=ExposureCategory.BANK_ACCOUNT,
        severity=ExposureSeverity.HIGH,
        details="Shared 6-digit OTP received from bank",
        has_secret_exposed=True,
    )

    triage = service.get_triage(iid)
    total_loss, _, count = incident_reconstruction_service.calculate_reported_loss(iid)

    assert triage.credential_exposure is True
    assert triage.financial_exposure is False
    assert total_loss == 0.0
    assert count == 0
    assert triage.loss_status == LossStatus.CREDENTIALS_EXPOSED

    plan = service.get_action_plan(iid)
    do_now_titles = [a.title for a in plan.do_now]
    assert any("Change Account Credentials" in t for t in do_now_titles)


# TEST 4 — REMOTE ACCESS
def test_remote_access_exposure():
    service = RescueService()
    inc = service.get_or_create_incident(initial_loss_type=LossType.REMOTE_ACCESS)
    iid = inc.incident_id

    service.record_exposure(
        iid,
        category=ExposureCategory.DEVICE,
        severity=ExposureSeverity.CRITICAL,
        remote_tool_name="AnyDesk",
        active_now=True,
        details="Installed AnyDesk and gave 9-digit code",
    )

    triage = service.get_triage(iid)
    assert triage.device_exposure is True
    assert triage.remote_access_active_or_possible is True
    assert triage.priority == "EMERGENCY_CRITICAL"

    plan = service.get_action_plan(iid)
    first_action = plan.do_now[0]
    assert "Remote Access" in first_action.title
    assert "Airplane Mode" in first_action.title


# TEST 5 — IDENTITY DOCUMENT
def test_identity_document_exposure():
    service = RescueService()
    inc = service.get_or_create_incident(initial_loss_type=LossType.IDENTITY_DOCUMENT_DISCLOSURE)
    iid = inc.incident_id

    service.record_exposure(
        iid,
        category=ExposureCategory.IDENTITY,
        severity=ExposureSeverity.MEDIUM,
        id_document_type="AADHAAR",
        details="Uploaded Aadhaar card photo to fake loan app",
    )

    triage = service.get_triage(iid)
    assert triage.identity_exposure is True
    assert triage.financial_exposure is False
    assert triage.total_reported_loss == 0.0

    plan = service.get_action_plan(iid)
    do_next_titles = [a.title for a in plan.do_next]
    assert any("Aadhaar Biometrics" in t for t in do_next_titles)


# TEST 6 — ALREADY EXISTING INCIDENT TRANSITIONS
def test_protect_incident_transition_to_rescue():
    service = RescueService()
    existing_id = "inc_protect_12345"
    existing_incident = Incident(
        incident_id=existing_id,
        status=IncidentStatus.ANALYZING,
        likely_scam_family="fake_kyc",
    )
    service._incidents[existing_id] = existing_incident

    # Victim later clicks "I already paid"
    transitioned = service.get_or_create_incident(
        incident_id=existing_id,
        initial_loss_type=LossType.UPI_PAYMENT,
    )

    assert transitioned.incident_id == existing_id
    assert transitioned.status == IncidentStatus.ESCALATED
    assert transitioned.metadata.get("rescue_active") is True
    assert transitioned.likely_scam_family == "fake_kyc"


# TEST 7 — NEW DIRECT RESCUE ENTRY
def test_new_direct_rescue_entry():
    service = RescueService()
    # Victim has no prior incident; arrives directly
    new_inc = service.get_or_create_incident(
        initial_loss_type=LossType.MONEY_TRANSFER,
        user_notes="Direct emergency arrival",
    )

    assert new_inc.incident_id.startswith("inc_")
    assert new_inc.status == IncidentStatus.ESCALATED
    assert new_inc.source_context.get("origin") == "RESCUE_DIRECT"


# TEST 8 — RECOVERY SCAM WARNING
def test_recovery_scam_detection():
    service = RescueService()
    iid = "inc_recov_test"
    service.get_or_create_incident(iid)

    suspect_msg = "Hello, I am cyber investigator. Pay 5000 advance fee and I will hack back and recover your lost 50000."
    protection = service.check_recovery_scam(iid, suspect_msg)

    assert protection.secondary_contact_detected is True
    assert protection.recovery_fee_requested is True
    assert protection.risk_level == "CRITICAL"
    assert "ADVANCE_RECOVERY_FEE" in protection.threat_patterns_detected
    assert "never pay" in protection.warning_text.lower()


# TEST 9 — ADDITIONAL PAYMENT PRESSURE
def test_additional_payment_escalation():
    engine = RescueTriageEngine()
    iid = "inc_escalate_test"

    triage = engine.evaluate_triage(
        incident_id=iid,
        loss_events=[LossEvent(incident_id=iid, amount=25000.0)],
        exposures=[],
        additional_demands_present=True,
    )

    assert triage.additional_payment_risk is True
    assert triage.recovery_scam_risk is True


# TEST 10 — HISTORICAL IMPORT
def test_historical_scam_handling():
    engine = RescueTriageEngine()
    iid = "inc_hist_test"
    past_date = datetime.now(timezone.utc) - timedelta(days=90)

    loss = LossEvent(
        incident_id=iid,
        amount=10000.0,
        occurred_at=past_date,
    )
    triage = engine.evaluate_triage(iid, [loss], [])
    plan = engine.generate_action_plan(triage, [loss], [])

    do_now_titles = [a.title for a in plan.do_now]
    # Should NOT claim immediate 48-hour stop-payment freeze is currently available
    assert not any("Immediately" in t and "Golden Hour" in a.description for a, t in zip(plan.do_now, do_now_titles))
    assert any("Historical" in t for t in do_now_titles)


# TEST 11 — UNKNOWN / APPROXIMATE TIME
def test_approximate_time_support():
    recon = IncidentReconstructionService()
    iid = "inc_time_test"

    event, is_new = recon.record_loss_event(
        incident_id=iid,
        amount=8000.0,
        time_granularity=TimeGranularity.APPROXIMATE,
    )

    assert is_new is True
    assert event.time_granularity == TimeGranularity.APPROXIMATE

    timeline = recon.get_timeline(iid)
    assert len(timeline) == 1
    assert timeline[0].time_granularity == TimeGranularity.APPROXIMATE


# TEST 12 — PARTIAL INFORMATION PROGRESSIVE QUESTIONS
def test_partial_information_rescue():
    service = RescueService()
    iid = "inc_partial_test"
    service.get_or_create_incident(iid)

    # User only knows ₹8,000 paid through UPI
    ev = service.record_loss(iid, amount=8000.0, payment_method="UPI")
    assert ev.amount == 8000.0
    assert ev.payment_method == "UPI"

    plan = service.get_action_plan(iid)
    assert len(plan.do_now) > 0
    assert len(plan.preserve) > 0
    assert len(plan.report) > 0


# TEST 13 — DUPLICATE SUBMISSION DEDUPLICATION
def test_duplicate_loss_submission():
    recon = IncidentReconstructionService()
    iid = "inc_dedup_test"

    e1, is_new1 = recon.record_loss_event(
        incident_id=iid,
        amount=15000.0,
        payment_method="UPI",
        recipient_identifier="mule@axis",
        transaction_reference="UTR1234567890",
    )
    # Duplicate submission
    e2, is_new2 = recon.record_loss_event(
        incident_id=iid,
        amount=15000.0,
        payment_method="UPI",
        recipient_identifier="mule@axis",
        transaction_reference="UTR1234567890",
    )

    assert is_new1 is True
    assert is_new2 is False
    assert e1.loss_event_id == e2.loss_event_id

    events = recon.get_loss_events(iid)
    assert len(events) == 1
    total, _, count = recon.calculate_reported_loss(iid)
    assert total == 15000.0
    assert count == 1


# TEST 14 — EVIDENCE INTEGRITY
def test_evidence_integrity_preservation():
    service = RescueService()
    iid = "inc_evid_test"

    item = service.add_preserved_evidence(
        incident_id=iid,
        evidence_type="SCREENSHOT",
        display_title="WhatsApp Payment Demand Screenshot",
        description="Original screenshot showing beneficiary UPI QR and threat",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_path="/secure/vault/screenshots/sc_1.png",
    )

    assert item.evidence_id.startswith("evid_")
    assert item.is_original is True
    assert len(item.sha256_hash) == 64
    assert item.redaction_state == "MASKED_SECRETS"


# TEST 15 — CASE PACKAGE FACTUAL ACCURACY & DISCLAIMER
def test_case_package_accuracy_and_disclaimer():
    service = RescueService()
    iid = "inc_pkg_test"
    service.get_or_create_incident(iid)
    service.record_loss(iid, amount=22000.0, payment_method="UPI", recipient_identifier="payee@paytm")

    pkg = service.generate_case_package(
        incident_id=iid,
        contact_entities=[{"type": "PHONE", "value": "+919876543210", "role": "Suspect"}],
        urls=["https://fake-rewards-claim.xyz"],
    )

    assert pkg.incident_id == iid
    assert pkg.reported_total_loss == 22000.0
    assert pkg.confirmed_verified_loss is None  # Factual distinction
    assert "does NOT constitute an official Police FIR" in pkg.legal_disclaimer
    assert "INCIDENT SUMMARY" in pkg.copyable_incident_summary

    # Render Markdown check
    md = case_package_generator.render_markdown(pkg)
    assert "# SCAMGRAPH RESCUE — INCIDENT INFORMATION PACKAGE" in md
    assert "OFFICIAL NOTICE & DISCLAIMER" in md
    assert "22,000.00" in md


# TEST 16 — PRE-LOSS EVALUATION EXCLUDES POST-LOSS EVIDENCE
def test_pre_loss_evaluation_non_leakage():
    feedback = rescue_intelligence_feedback
    iid = "inc_leakage_test"

    boundary = datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc)
    loss = LossEvent(
        incident_id=iid,
        amount=50000.0,
        occurred_at=boundary,
    )

    evidence_stream = [
        ("ev_pre_1", datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)),
        ("ev_pre_2", datetime(2026, 10, 15, 12, 30, tzinfo=timezone.utc)),
        ("ev_post_1", datetime(2026, 10, 15, 15, 0, tzinfo=timezone.utc)),
        ("ev_post_2", datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc)),
    ]

    pre_loss, post_loss = feedback.partition_evidence(evidence_stream, boundary)

    assert pre_loss == ["ev_pre_1", "ev_pre_2"]
    assert post_loss == ["ev_post_1", "ev_post_2"]

    # Missed prevention review uses strictly pre_loss signals
    review = feedback.generate_missed_prevention_review(
        incident_id=iid,
        loss_events=[loss],
        pre_loss_evidence=pre_loss,
        post_loss_evidence=post_loss,
        had_preloss_check=True,
        preloss_warning_shown=False,
    )

    assert review.pre_loss_signals_count == 2
    assert review.post_loss_signals_count == 2
    assert "ev_post_1" not in review.pre_loss_evidence_ids


# TEST 17 — CAMPAIGN FEEDBACK CANDIDATE CREATION
def test_campaign_feedback_candidate_extraction():
    feedback = rescue_intelligence_feedback
    iid = "inc_camp_test"

    loss = LossEvent(
        incident_id=iid,
        amount=12000.0,
        recipient_identifier="mule01@axl",
    )
    entities = feedback.extract_rescue_entities(
        loss_events=[loss],
        contact_entities=[{"type": "PHONE", "value": "+919988776655", "role": "telecaller"}],
        urls=["https://fast-parttime-jobs.in"],
    )

    canonical_vals = [e.canonical_value for e in entities]
    assert "mule01@axl" in canonical_vals
    assert "+919988776655" in canonical_vals
    assert "https://fast-parttime-jobs.in" in canonical_vals
    assert all(e.verification_state.value == "OBSERVED" for e in entities)


# TEST 18 — PRIVACY CONTROLS (NO VICTIM ENUMERATION)
def test_privacy_controls_case_package():
    service = RescueService()
    iid = "inc_priv_test"
    service.get_or_create_incident(iid)
    service.record_loss(iid, amount=1000.0, transaction_reference="123456789012")

    pkg = service.generate_case_package(iid)
    pkg_dict = pkg.model_dump()

    # Ensure no other incident IDs or victim details exist
    assert "all_victims" not in pkg_dict
    assert "graph_neighbors" not in pkg_dict
    # Transaction ref is masked
    assert "123456789012" not in str(pkg_dict["payment_events"])
    assert "UTR-****9012" in str(pkg_dict["payment_events"])


# TEST 19 — MOBILE ACTION PLAN USABILITY
def test_mobile_action_plan_structure():
    service = RescueService()
    iid = "inc_mobile_test"
    service.get_or_create_incident(iid)
    service.record_loss(iid, amount=5000.0, payment_method="UPI")

    plan = service.get_action_plan(iid)
    # Mobile prioritized sections
    assert len(plan.do_now) > 0
    assert plan.do_now[0].is_immediate_lifeline is True
    assert plan.do_now[0].link_or_dial in ("1930", "1800111109", "18002586161")


# TEST 20 — DEGRADED INTELLIGENCE RESILIENCE
def test_degraded_mode_resilience():
    # When Graph and Campaign engines are offline, Rescue must function 100% locally
    service = RescueService()
    iid = "inc_degraded_test"
    service.get_or_create_incident(iid)
    service.record_loss(iid, amount=3000.0)

    triage = service.get_triage(iid)
    plan = service.get_action_plan(iid)
    pkg = service.generate_case_package(iid)

    assert triage.priority in ("EMERGENCY_CRITICAL", "URGENT")
    assert len(plan.do_now) > 0
    assert pkg.reported_total_loss == 3000.0
    assert len(pkg.official_reporting_resources) > 0
