"""Contextual Intervention Service & Pre-Payment Guard Service (Phase 4B / Prompt 14).

Orchestrates the decision flow:
Incident Context -> Unified Risk Engine (R, C, U) -> Intervention Policy -> Fatigue Manager -> Pre-Payment Guard
"""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.contextual_intervention import (
    FrictionLevel,
    InterventionDecision,
    InterventionFeedback,
    InterventionTiming,
    InterventionType,
    PaymentProximity,
    PaymentReason,
    PrePaymentContext,
    UserResponseAction,
    VerificationPlan,
)
from services.decision_engine.service import unified_decision_service
from services.intervention_engine.policy import intervention_policy_engine
from services.intervention_engine.memory import intervention_memory_manager

logger = logging.getLogger(__name__)


class GuardEvaluationResult(BaseModel):
    """Result of Pre-Payment Guard inspection before money transfer."""
    incident_id: str
    can_proceed: bool
    requires_cooling_off: bool
    cooling_off_minutes: int
    friction_level: FrictionLevel
    intervention_decision: InterventionDecision
    verification_plan: Optional[VerificationPlan] = None
    warning_summary: str


class ContextualInterventionService:
    """Enterprise service orchestrating user-facing interventions."""

    def __init__(self):
        self.policy_engine = intervention_policy_engine
        self.memory = intervention_memory_manager

    def evaluate_from_signals(
        self,
        incident_id: str,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        vpa: Optional[str] = None,
        phone: Optional[str] = None,
        journey_stage: str = "INITIAL_CONTACT",
        payment_proximity: PaymentProximity = PaymentProximity.NONE,
        payment_reason: PaymentReason = PaymentReason.UNKNOWN,
        tactics_observed: Optional[List[str]] = None,
        claimed_org: Optional[str] = None,
        already_paid: bool = False,
        lang: str = "en",
    ) -> InterventionDecision:
        """Evaluates full pipeline from raw observables to final InterventionDecision."""
        # 1. Run authoritative Unified Risk + Confidence + Urgency Engine (Prompt 13)
        decision = unified_decision_service.evaluate(
            incident_id=incident_id,
            message_text=message_text,
            url=url,
            vpa=vpa,
            phone=phone,
            journey_stage=journey_stage,
            tactics_observed=tactics_observed or [],
        )

        campaign_ctx = None
        if decision.matched_campaign_id:
            campaign_ctx = {
                "campaign_id": decision.matched_campaign_id,
                "title": decision.campaign_title,
                "lifecycle_state": decision.outbreak_status,
            }

        # 2. Run Contextual Intervention Policy Engine (Prompt 14)
        intervention = self.policy_engine.evaluate(
            subject_id=incident_id,
            risk=decision.risk_score,
            confidence=decision.confidence_score,
            urgency=decision.urgency_score,
            journey_stage=journey_stage,
            payment_proximity=payment_proximity,
            payment_reason=payment_reason,
            tactics=tactics_observed,
            claimed_org=claimed_org,
            suspect_url=url,
            suspect_phone=phone,
            campaign_context=campaign_ctx,
            already_paid=already_paid,
            lang=lang,
        )

        # 3. Apply Fatigue Control
        tactics_count = len(tactics_observed or [])
        if self.memory.should_suppress_due_to_fatigue(intervention, current_tactics_count=tactics_count):
            logger.info("Intervention %s suppressed for incident %s to prevent warning fatigue", intervention.intervention_type, incident_id)
            intervention.friction_level = FrictionLevel.PASSIVE
            intervention.timing = InterventionTiming.BACKGROUND_EDUCATION
            intervention.metadata["suppressed_for_fatigue"] = True

        self.memory.record_decision_shown(intervention, tactics_count=tactics_count)
        return intervention

    def record_feedback(self, incident_id: str, feedback: InterventionFeedback) -> Dict[str, Any]:
        """Records user interaction and dispute feedback."""
        if feedback.user_response in (UserResponseAction.VERIFY, UserResponseAction.STOPPED_PAYMENT, UserResponseAction.TALKED_TO_SOMEONE):
            self.memory.record_acknowledgment(incident_id)
        elif feedback.user_response in (UserResponseAction.CONTINUED, UserResponseAction.I_TRUST_THIS):
            self.memory.record_dismissal(incident_id)

        return {
            "status": "RECORDED",
            "incident_id": incident_id,
            "response_action": feedback.user_response.value,
        }


class PrePaymentGuardService:
    """ScamGraph Guard: evaluates transaction intent before victim authorizes payment."""

    def __init__(self, intervention_service: Optional[ContextualInterventionService] = None):
        self.intervention_service = intervention_service or contextual_intervention_service

    def check_payment(
        self,
        context: PrePaymentContext,
        lang: str = "en",
    ) -> GuardEvaluationResult:
        """Inspects payment context to determine whether transfer should proceed or be delayed."""
        intervention = self.intervention_service.evaluate_from_signals(
            incident_id=context.incident_id,
            vpa=context.recipient_vpa,
            journey_stage=context.journey_stage,
            payment_proximity=context.payment_proximity,
            payment_reason=context.payment_reason,
            tactics_observed=context.tactics_present,
            already_paid=context.already_paid,
            lang=lang,
        )

        cooling_off_needed = intervention.intervention_type in (
            InterventionType.DELAY_PAYMENT,
            InterventionType.PAUSE_AND_VERIFY,
            InterventionType.TALK_TO_TRUSTED_PERSON,
        ) or intervention.friction_level in (
            FrictionLevel.DELAY_PAYMENT,
            FrictionLevel.STRONG,
        )

        can_proceed = not cooling_off_needed and intervention.intervention_type != InterventionType.EMERGENCY_RESPONSE

        return GuardEvaluationResult(
            incident_id=context.incident_id,
            can_proceed=can_proceed,
            requires_cooling_off=cooling_off_needed,
            cooling_off_minutes=intervention.suggested_cooling_off_minutes,
            friction_level=intervention.friction_level,
            intervention_decision=intervention,
            verification_plan=intervention.verification_plan,
            warning_summary=intervention.consumer_headline,
        )


# Global singletons
contextual_intervention_service = ContextualInterventionService()
pre_payment_guard_service = PrePaymentGuardService(contextual_intervention_service)
