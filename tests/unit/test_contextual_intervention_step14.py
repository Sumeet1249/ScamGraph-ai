"""Comprehensive Unit Tests for Contextual Intervention Engine & Pre-Payment Guard (Step 14).

Tests all 15 scenarios from Prompt 14 / Phase 4B:
- Test A: Task Scam Pre-Loss Intercept
- Test B: Digital Arrest Anti-Isolation Protection
- Test C: KYC Credential Phishing Protection
- Test D: Legitimate Bank Notification (Hard Negative)
- Test E: Legitimate Rent Payment (Hard Negative)
- Test F: Zero-Day Behavioral Intervention
- Test G: Post-Loss Already-Paid Emergency Handoff
- Test H: OTP Theft Intercept
- Test I: Remote Access Software / Malicious APK Intercept
- Test J: Low Information Benign Communication
- Test K: Hinglish Localization
- Test L: Warning Fatigue Suppression
- Test M: Situational Context Escalation
- Test N: Outbreak Campaign Match
- Test O: Pre-Payment Guard API Evaluation
"""

import pytest
from fastapi.testclient import TestClient

from packages.schemas.contextual_intervention import (
    FrictionLevel,
    InterventionType,
    PaymentProximity,
    PaymentReason,
    PrePaymentContext,
    UserResponseAction,
)
from services.intervention_engine.policy import intervention_policy_engine
from services.intervention_engine.service import (
    contextual_intervention_service,
    pre_payment_guard_service,
)
from services.intervention_engine.memory import InterventionMemoryManager
from services.api.app.main import app

client = TestClient(app)


def test_scenario_a_task_scam():
    """Test A: Instagram/Telegram Task Scam monetization deposit request."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_task_scam_01",
        message_text="Complete VIP Level 3 task! Deposit Rs 10000 to receive Rs 25000 withdrawal bonus immediately.",
        url="https://t.me/vip_task_earning",
        vpa="taskvip.merchant@upi",
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        payment_reason=PaymentReason.JOB_OR_TASK,
        tactics_observed=["FAKE_REWARD", "PAT_TASK_SCAM", "URGENCY"],
    )

    assert dec.intervention_type == InterventionType.DELAY_PAYMENT
    assert dec.friction_level == FrictionLevel.DELAY_PAYMENT
    assert dec.suggested_cooling_off_minutes == 120
    assert "Task Scam" in dec.consumer_headline or "task" in dec.consumer_headline.lower()
    assert dec.verification_plan is not None
    assert dec.verification_plan.target_type == "EMPLOYER"


def test_scenario_b_digital_arrest():
    """Test B: Digital Arrest with Authority, Fear, Secrecy, and Isolation."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_digital_arrest_01",
        message_text="CBI Police Headquarters Notice: Narcotics parcel in your name. Do not disconnect Skype call. Do not inform family.",
        vpa="cbi.narcotics.escrow@icici",
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        payment_reason=PaymentReason.GOVERNMENT_OR_FINE,
        tactics_observed=["AUTHORITY", "FEAR", "ISOLATION", "SECRECY"],
    )

    assert dec.intervention_type == InterventionType.TALK_TO_TRUSTED_PERSON
    assert InterventionType.BREAK_CONTACT_AND_VERIFY in dec.secondary_interventions
    assert dec.friction_level == FrictionLevel.STRONG
    assert "Anti-Isolation" in dec.consumer_headline or "Trust" in dec.consumer_headline
    assert dec.verification_plan.target_type == "GOVERNMENT_AGENCY"
    assert "1930" in str(dec.verification_plan.steps)


def test_scenario_c_kyc_phishing():
    """Test C: Urgent KYC Credential Harvesting."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_kyc_phish_01",
        message_text="Your SBI Netbanking will be blocked today. Click link to verify your Netbanking Password and Pan.",
        url="http://sbi-kyc-reactivate.cc/login",
        journey_stage="CREDENTIAL_HARVEST",
        payment_proximity=PaymentProximity.NONE,
        payment_reason=PaymentReason.VERIFICATION_OR_KYC,
        tactics_observed=["CREDENTIAL_PRESSURE", "URGENCY", "FEAR"],
        claimed_org="SBI Bank",
    )

    assert dec.intervention_type == InterventionType.DO_NOT_SHARE_CREDENTIALS
    assert dec.friction_level == FrictionLevel.STRONG
    assert dec.verification_plan.target_type == "FINANCIAL_INSTITUTION"
    assert "official" in str(dec.verification_plan.steps).lower()


def test_scenario_d_legitimate_bank_negative():
    """Test D: Legitimate Bank Statement Notification (Hard Negative)."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_legit_bank_01",
        message_text="Dear Customer, your e-statement for SBI Account ending 4821 for October is now available. Log in to onlinesbi.sbi or Yono.",
        url="https://onlinesbi.sbi",
        journey_stage="INITIAL_CONTACT",
        payment_proximity=PaymentProximity.NONE,
        tactics_observed=[],
    )

    assert dec.intervention_type in (InterventionType.NO_ACTION, InterventionType.EDUCATE)
    assert dec.friction_level in (FrictionLevel.NONE, FrictionLevel.LIGHT)
    assert dec.suggested_cooling_off_minutes == 0


def test_scenario_e_legitimate_rent_negative():
    """Test E: Routine Landlord Rent Transfer (Hard Negative)."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_legit_rent_01",
        message_text="Hi Sharma ji, sending Rs 22000 for October flat rent.",
        vpa="landlord.sharma@hdfcbank",
        journey_stage="PAYMENT",
        payment_proximity=PaymentProximity.REQUESTED,
        payment_reason=PaymentReason.RENT,
        tactics_observed=[],
    )

    assert dec.intervention_type == InterventionType.NO_ACTION
    assert dec.friction_level == FrictionLevel.NONE
    assert dec.suggested_cooling_off_minutes == 0


def test_scenario_f_zero_day_scam():
    """Test F: Zero-day manipulation with no prior campaign or graph history."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_zero_day_01",
        message_text="Strictly private audit notice: You are prohibited from disclosing this file. Submit 45000 audit fee immediately.",
        vpa="unseen.auditor991@paytm",
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        payment_reason=PaymentReason.LOAN_OR_FEE,
        tactics_observed=["SECRECY", "AUTHORITY", "URGENCY"],
    )

    # Must still intervene behaviorally despite zero network history
    assert dec.intervention_type in (
        InterventionType.PAUSE_AND_VERIFY,
        InterventionType.VERIFY_INDEPENDENTLY,
        InterventionType.DELAY_PAYMENT,
        InterventionType.TALK_TO_TRUSTED_PERSON,
    )
    assert dec.friction_level in (FrictionLevel.MODERATE, FrictionLevel.STRONG, FrictionLevel.DELAY_PAYMENT)


def test_scenario_g_already_paid_emergency():
    """Test G: User states they already sent money -> Emergency Response."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_already_paid_01",
        message_text="I have already transferred Rs 50000 via PhonePe as requested. Please restore my account.",
        journey_stage="LOSS_CONFIRMED",
        already_paid=True,
    )

    assert dec.intervention_type == InterventionType.EMERGENCY_RESPONSE
    assert dec.friction_level == FrictionLevel.EMERGENCY
    assert dec.priority == "EMERGENCY"
    assert "1930" in str(dec.recommended_steps)
    assert "recall" in str(dec.recommended_steps).lower() or "freeze" in str(dec.recommended_steps).lower()


def test_scenario_h_otp_theft():
    """Test H: Caller or message demanding an OTP."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_otp_theft_01",
        message_text="Please share the 6-digit OTP sent to your mobile to verify your transaction refund.",
        tactics_observed=["OTP_REQUEST", "CREDENTIAL_PRESSURE"],
    )

    assert dec.intervention_type == InterventionType.DO_NOT_SHARE_OTP
    assert dec.friction_level == FrictionLevel.STRONG
    assert "OTP" in dec.consumer_headline


def test_scenario_i_remote_access_pressure():
    """Test I: Instruction to install AnyDesk or screen-sharing software."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_remote_access_01",
        message_text="To fix your electricity bill update, install AnyDesk app from play store and accept support code.",
        tactics_observed=["REMOTE_ACCESS_PRESSURE", "URGENCY"],
    )

    assert dec.intervention_type == InterventionType.DO_NOT_INSTALL_REMOTE_ACCESS
    assert dec.friction_level == FrictionLevel.STRONG
    assert "Remote-Access" in dec.consumer_headline or "APK" in dec.consumer_headline


def test_scenario_j_low_information():
    """Test J: Ambiguous or brief communication without high-risk markers."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_low_info_01",
        message_text="Hello, please call me back when free.",
        journey_stage="INITIAL_CONTACT",
        payment_proximity=PaymentProximity.NONE,
        tactics_observed=[],
    )

    assert dec.intervention_type in (InterventionType.NO_ACTION, InterventionType.EDUCATE)
    assert dec.friction_level in (FrictionLevel.NONE, FrictionLevel.LIGHT)


def test_scenario_k_hinglish_localization():
    """Test K: Hinglish text and localization output."""
    dec = contextual_intervention_service.evaluate_from_signals(
        incident_id="inc_hinglish_01",
        message_text="Aap kisi ko mat batana, police case se bachne ke liye abhi 50000 transfer karo.",
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        tactics_observed=["ISOLATION", "AUTHORITY", "FEAR"],
        lang="hinglish",
    )

    assert dec.intervention_type == InterventionType.TALK_TO_TRUSTED_PERSON
    assert "Kisi Se Chhupayein Nahi" in dec.consumer_headline
    assert "Digital Arrest" in dec.consumer_message or "fraud" in dec.consumer_message.lower()


def test_scenario_l_warning_fatigue_suppression():
    """Test L: Suppress repeated identical modal warnings when evidence has not changed."""
    mem = InterventionMemoryManager()
    incident_id = "inc_fatigue_test_01"

    # First evaluation
    dec1 = intervention_policy_engine.evaluate(
        subject_id=incident_id,
        risk=0.50,
        confidence=0.60,
        urgency=0.40,
        journey_stage="INITIAL_CONTACT",
        tactics=["URGENCY"],
    )
    assert mem.should_suppress_due_to_fatigue(dec1, current_tactics_count=1) is False
    mem.record_decision_shown(dec1, tactics_count=1)

    # Identical second evaluation with unchanged context -> should suppress
    dec2 = intervention_policy_engine.evaluate(
        subject_id=incident_id,
        risk=0.50,
        confidence=0.60,
        urgency=0.40,
        journey_stage="INITIAL_CONTACT",
        tactics=["URGENCY"],
    )
    assert mem.should_suppress_due_to_fatigue(dec2, current_tactics_count=1) is True


def test_scenario_m_situational_escalation():
    """Test M: Advance in journey stage / payment request escalates intervention."""
    mem = InterventionMemoryManager()
    incident_id = "inc_escalate_test_01"

    # First evaluation in approach stage
    dec1 = intervention_policy_engine.evaluate(
        subject_id=incident_id,
        risk=0.50,
        confidence=0.60,
        urgency=0.30,
        journey_stage="INITIAL_CONTACT",
        payment_proximity=PaymentProximity.NONE,
        tactics=["URGENCY"],
    )
    mem.record_decision_shown(dec1, tactics_count=1)

    # Escalation: Payment requested + higher risk
    dec2 = intervention_policy_engine.evaluate(
        subject_id=incident_id,
        risk=0.75,
        confidence=0.70,
        urgency=0.85,
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        tactics=["URGENCY", "PAYMENT_PRESSURE"],
    )
    # Must NOT suppress because journey advanced to PAYMENT_REQUEST
    assert mem.should_suppress_due_to_fatigue(dec2, current_tactics_count=2) is False
    assert dec2.intervention_type == InterventionType.DELAY_PAYMENT


def test_scenario_n_campaign_outbreak_override():
    """Test N: Active campaign outbreak escalates intervention to pre-loss delay."""
    campaign_ctx = {
        "campaign_id": "camp_da_cbi_01",
        "lifecycle_state": "OUTBREAK",
    }
    dec = intervention_policy_engine.evaluate(
        subject_id="inc_outbreak_test_01",
        risk=0.70,
        confidence=0.80,
        urgency=0.75,
        journey_stage="PAYMENT_REQUEST",
        payment_proximity=PaymentProximity.REQUESTED,
        campaign_context=campaign_ctx,
    )

    assert dec.intervention_type == InterventionType.DELAY_PAYMENT
    assert dec.friction_level == FrictionLevel.DELAY_PAYMENT
    assert "RC_INTV_CAMPAIGN_OUTBREAK" in dec.trigger_reason_codes[0]


def test_scenario_o_pre_payment_guard_api():
    """Test O: REST API check for Pre-Payment Guard."""
    guard_payload = {
        "incident_id": "inc_api_guard_01",
        "payment_intent": True,
        "payment_reason": "JOB_OR_TASK",
        "recipient_vpa": "taskdeposit.scam@upi",
        "amount_inr": 15000.0,
        "amount_band": "HIGH",
        "journey_stage": "PAYMENT_REQUEST",
        "payment_proximity": "REQUESTED",
        "tactics_present": ["FAKE_REWARD", "PAT_TASK_SCAM"],
    }

    res = client.post("/api/v1/payment-guard/check", json=guard_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["can_proceed"] is False
    assert data["requires_cooling_off"] is True
    assert data["cooling_off_minutes"] == 120
    assert data["friction_level"] == "DELAY_PAYMENT"
    assert data["intervention_decision"]["intervention_type"] == "DELAY_PAYMENT"
    assert data["verification_plan"] is not None
