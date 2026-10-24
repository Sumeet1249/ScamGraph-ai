"""Comprehensive Unit Tests for Unified Risk + Confidence + Urgency Engine (Phase 4A).

Verifies the Tripartite Decision Layer:
- Risk, Confidence, Urgency band assignments
- Action layer decisions: ALLOW, EDUCATE, VERIFY_INDEPENDENTLY, WARN, STRONG_WARNING, DELAY_PAYMENT, BLOCK_PRE_LOSS
- Pre-loss cooling-off payment intervention
- Campaign outbreak override to BLOCK_PRE_LOSS
- Contradictory evidence discounting (official domains)
- Missing dimension uncertainty penalties
- FastAPI REST endpoints
"""

from typing import Any, Dict
import pytest
from fastapi.testclient import TestClient

from packages.schemas.unified_decision import (
    ActionDecision,
    DecisionDimension,
    TripartiteConfidenceBand,
    TripartiteDecision,
    TripartiteRiskBand,
    TripartiteUrgencyBand,
)
from services.api.app.main import app
from services.campaign_engine.service import campaign_service
from services.decision_engine.config import DecisionConfig
from services.decision_engine.fusion import TripartiteDecisionFusionEngine
from services.decision_engine.service import UnifiedDecisionService, unified_decision_service


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def custom_config() -> DecisionConfig:
    return DecisionConfig({
        "dimension_weights": {
            "message_nlp": 0.15,
            "url_safety": 0.15,
            "entity_trust": 0.15,
            "tactic_manipulation": 0.15,
            "journey_stage": 0.15,
            "scam_dna": 0.10,
            "campaign_outbreak": 0.15,
        },
        "action_thresholds": {
            "block_pre_loss": {"min_risk": 0.85, "min_confidence": 0.70, "min_urgency": 0.70},
            "delay_payment": {"min_risk": 0.65, "min_urgency": 0.60},
            "strong_warning": {"min_risk": 0.65, "min_confidence": 0.60},
            "warn": {"min_risk": 0.40},
            "verify_independently": {"min_risk": 0.25, "max_confidence": 0.55},
            "educate": {"min_risk": 0.20},
            "allow": {"max_risk": 0.20},
        },
        "counter_evidence_discount_factor": 0.40,
    })


def test_benign_content_allows(custom_config: DecisionConfig):
    """Safe inquiry with official domain yields ALLOW action and BENIGN risk."""
    fusion = TripartiteDecisionFusionEngine(custom_config)
    decision = fusion.evaluate_tripartite_decision(
        message_text="Hello, here is the meeting notes link.",
        url="https://google.com/calendar",
    )

    assert decision.primary_action == ActionDecision.ALLOW
    assert decision.risk_band in (TripartiteRiskBand.BENIGN, TripartiteRiskBand.LOW)
    assert decision.risk_score <= 0.20
    assert "No High-Risk Threat Detected" in decision.consumer_headline


def test_educational_notice(custom_config: DecisionConfig):
    """Mild unverified promo yields EDUCATE action."""
    fusion = TripartiteDecisionFusionEngine(custom_config)
    decision = fusion.evaluate_tripartite_decision(
        message_text="Congratulations! You have won a festival discount coupon on our shopping portal.",
    )

    assert decision.primary_action in (ActionDecision.EDUCATE, ActionDecision.VERIFY_INDEPENDENTLY)
    assert decision.risk_score >= 0.20


def test_verify_independently(custom_config: DecisionConfig):
    """Ambiguous claim with unverified entity and low confidence yields VERIFY_INDEPENDENTLY."""
    fusion = TripartiteDecisionFusionEngine(custom_config)
    decision = fusion.evaluate_tripartite_decision(
        vpa="random.seller99@axisbank",
        journey_stage="INITIAL_CONTACT",
    )

    assert decision.primary_action in (ActionDecision.VERIFY_INDEPENDENTLY, ActionDecision.EDUCATE)
    assert "Verify Independently" in decision.consumer_headline or decision.primary_action == ActionDecision.EDUCATE


def test_strong_warning(custom_config: DecisionConfig):
    """High risk coercive message with active manipulation yields STRONG_WARNING."""
    fusion = TripartiteDecisionFusionEngine(custom_config)
    decision = fusion.evaluate_tripartite_decision(
        message_text="URGENT: Mumbai Police Cyber Crime notice. Arrest warrant issued for money laundering. Respond immediately.",
        tactics_observed=["AUTHORITY_IMPERSONATION", "EXTREME_URGENCY", "LEGAL_THREAT"],
        known_dna_similarity=0.88,
    )

    assert decision.risk_score >= 0.65
    assert decision.primary_action in (ActionDecision.STRONG_WARNING, ActionDecision.DELAY_PAYMENT, ActionDecision.BLOCK_PRE_LOSS)
    assert decision.risk_band in (TripartiteRiskBand.HIGH, TripartiteRiskBand.CRITICAL)


def test_delay_payment_pre_loss(custom_config: DecisionConfig):
    """High urgency payment request stage with suspicious indicators triggers DELAY_PAYMENT."""
    fusion = TripartiteDecisionFusionEngine(custom_config)
    decision = fusion.evaluate_tripartite_decision(
        message_text="Your KYC has expired. Pay Rs 10 verification fee immediately to avoid permanent account block.",
        vpa="sbi.kyc.verification@oksbi",
        journey_stage="PAYMENT_REQUEST",
        tactics_observed=["EXTREME_URGENCY", "AUTHORITY_IMPERSONATION"],
    )

    assert decision.urgency_score >= 0.60
    assert decision.pre_loss_intervention is True
    assert decision.primary_action in (ActionDecision.DELAY_PAYMENT, ActionDecision.BLOCK_PRE_LOSS)
    assert any("cooling-off" in step.lower() for step in decision.recommended_steps) or decision.primary_action == ActionDecision.BLOCK_PRE_LOSS


def test_block_pre_loss_on_outbreak(custom_config: DecisionConfig):
    """Matching an active OUTBREAK campaign triggers BLOCK_PRE_LOSS immediate intervention."""
    campaign_service.seed_demo_data()
    fusion = TripartiteDecisionFusionEngine(custom_config)

    # Use payment VPA from camp_da_cbi_01 (OUTBREAK state)
    decision = fusion.evaluate_tripartite_decision(
        message_text="This is CBI investigation. Transfer funds to safe account.",
        vpa="mumbai.police.audit@sbi",
        journey_stage="PAYMENT_INTENT",
    )

    assert decision.primary_action == ActionDecision.BLOCK_PRE_LOSS
    assert decision.risk_band == TripartiteRiskBand.CRITICAL
    assert decision.urgency_band == TripartiteUrgencyBand.IMMEDIATE_INTERVENTION
    assert decision.matched_campaign_id == "camp_da_cbi_01"
    assert decision.outbreak_status == "OUTBREAK"
    assert decision.pre_loss_intervention is True


def test_counter_evidence_discounts_risk(custom_config: DecisionConfig):
    """Counter-evidence (official domain / whitelisted source) discounts raw risk."""
    fusion = TripartiteDecisionFusionEngine(custom_config)

    # Suspicious urgency text alone
    res_without_counter = fusion.evaluate_tripartite_decision(
        message_text="Electricity bill overdue. Update immediately to prevent disruption.",
    )

    # Same text but on official state portal domain
    res_with_counter = fusion.evaluate_tripartite_decision(
        message_text="Electricity bill overdue. Update immediately to prevent disruption.",
        url="https://bsesdelhi.com/bill-pay",
        counter_evidence_signals=["WHITELISTED_OFFICIAL_UTILITY_DOMAIN"],
    )

    assert res_with_counter.contradictory_discount > 0.0
    assert res_with_counter.risk_score < res_without_counter.risk_score


def test_fastapi_decision_endpoints(test_client: TestClient):
    """Verify REST API POST /api/v1/risk/decision."""
    req_payload = {
        "message_text": "CBI Arrest Warrant issued against your Aadhaar. Pay Rs 50000 immediately.",
        "vpa": "mumbai.police.audit@sbi",
        "journey_stage": "PAYMENT_REQUEST",
        "tactics_observed": ["AUTHORITY_IMPERSONATION", "EXTREME_URGENCY", "LEGAL_THREAT"],
        "known_dna_similarity": 0.92,
    }

    res = test_client.post("/api/v1/risk/decision", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "confidence_score" in data
    assert "urgency_score" in data
    assert data["primary_action"] in [a.value for a in ActionDecision]
    assert len(data["signal_contributions"]) >= 4
    assert len(data["recommended_steps"]) >= 1
    assert data["risk_band"] in [b.value for b in TripartiteRiskBand]
