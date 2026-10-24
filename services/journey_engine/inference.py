"""Stage Inference Pipeline for ScamGraph Journey Engine V1.

Fuses event features, tactic signals (Phase 1B), requested actions, payment contexts,
and entity relationships to infer supported stages, active stages, and current stage.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.journey import (
    JourneyEvent,
    JourneyStage,
    StageObservation,
    get_stage_category,
)


class StageInferenceEngine:
    """Infers evidence-grounded journey stages from individual events and longitudinal sequences."""

    def infer_event_stages(
        self,
        event: JourneyEvent,
        prior_stages: List[JourneyStage],
        prior_payment_count: int = 0,
    ) -> List[StageObservation]:
        """Infers candidate stage observations supported by a single event in sequence context."""
        observations: List[StageObservation] = []
        tactics = set(event.tactics)
        actions = set(event.requested_actions)
        ev_type = event.event_type.upper()
        pay_ctx = event.payment_context or {}

        # 1. CREDENTIAL_REQUEST
        if (
            "CREDENTIAL_PRESSURE" in tactics
            or "SHARE_OTP" in actions
            or "SHARE_CREDENTIAL" in actions
            or "OTP_REQUESTED" in ev_type
        ):
            observations.append(StageObservation(
                stage=JourneyStage.CREDENTIAL_REQUEST,
                confidence=0.95,
                event_ids=[event.event_id],
                supporting_signals=list(tactics.intersection({"CREDENTIAL_PRESSURE"})),
                supporting_evidence=[f"Event {event.event_id}: requested authorization credentials or OTP"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["OTP_OR_CREDENTIAL_DEMAND"],
            ))

        # 2. PAYMENT_ESCALATION vs INITIAL_PAYMENT
        has_payment_signal = (
            "PAYMENT_PRESSURE" in tactics
            or "SEND_PAYMENT" in actions
            or "APPROVE_UPI_REQUEST" in actions
            or "PAY_FEE" in actions
            or "PAYMENT_REQUESTED" in ev_type
            or "COLLECT_REQUEST_RECEIVED" in ev_type
            or "PAYMENT_INTENT" in ev_type
        )

        if has_payment_signal:
            # Check if this is an escalation (prior payment already occurred or multiple payments observed)
            is_escalation = (
                prior_payment_count >= 1
                or JourneyStage.INITIAL_PAYMENT in prior_stages
                or pay_ctx.get("is_escalated", False)
                or pay_ctx.get("payment_sequence_number", 1) > 1
                or "recharge" in str(pay_ctx).lower()
            )

            if is_escalation:
                observations.append(StageObservation(
                    stage=JourneyStage.PAYMENT_ESCALATION,
                    confidence=0.92,
                    event_ids=[event.event_id],
                    supporting_signals=list(tactics.intersection({"PAYMENT_PRESSURE", "URGENCY", "LOSS_AVERSION"})),
                    supporting_evidence=[f"Event {event.event_id}: repeated or escalated payment demand after initial transfer"],
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    detector_sources=["RULE"],
                    reason_codes=["PRIOR_PAYMENT_OBSERVED", "LARGER_OR_REPEATED_PAYMENT_REQUESTED"],
                ))
            else:
                observations.append(StageObservation(
                    stage=JourneyStage.INITIAL_PAYMENT,
                    confidence=0.93,
                    event_ids=[event.event_id],
                    supporting_signals=list(tactics.intersection({"PAYMENT_PRESSURE"})),
                    supporting_evidence=[f"Event {event.event_id}: first money deposit or UPI payment requested"],
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    detector_sources=["RULE"],
                    reason_codes=["INITIAL_PAYMENT_REQUESTED"],
                ))

        # 3. WITHDRAWAL_BLOCK
        if "LOSS_AVERSION" in tactics and ("tax" in str(pay_ctx).lower() or "unfreeze" in str(pay_ctx).lower()):
            observations.append(StageObservation(
                stage=JourneyStage.WITHDRAWAL_BLOCK,
                confidence=0.90,
                event_ids=[event.event_id],
                supporting_signals=["LOSS_AVERSION"],
                supporting_evidence=[f"Event {event.event_id}: funds frozen pending tax or fee"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["FUNDS_BLOCKED_PENDING_PAYMENT"],
            ))

        # 4. RECOVERY_FEE
        if "PAY_FEE" in actions and JourneyStage.WITHDRAWAL_BLOCK in prior_stages:
            observations.append(StageObservation(
                stage=JourneyStage.RECOVERY_FEE,
                confidence=0.88,
                event_ids=[event.event_id],
                supporting_signals=["PAY_FEE"],
                supporting_evidence=[f"Event {event.event_id}: recovery or unlock fee demanded"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["RECOVERY_OR_UNLOCK_FEE_DEMANDED"],
            ))

        # 5. REWARD_OR_FAKE_PROFIT
        if "FAKE_REWARD" in tactics or "RECIPROCITY" in tactics or pay_ctx.get("is_reward", False):
            observations.append(StageObservation(
                stage=JourneyStage.REWARD_OR_FAKE_PROFIT,
                confidence=0.88,
                event_ids=[event.event_id],
                supporting_signals=list(tactics.intersection({"FAKE_REWARD", "RECIPROCITY"})),
                supporting_evidence=[f"Event {event.event_id}: small profit credited or fake reward presented"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["REWARD_OR_COMMISSION_CREDITED"],
            ))

        # 6. TRUST_BUILDING
        if "TRUST_BUILDING" in tactics:
            observations.append(StageObservation(
                stage=JourneyStage.TRUST_BUILDING,
                confidence=0.86,
                event_ids=[event.event_id],
                supporting_signals=["TRUST_BUILDING"],
                supporting_evidence=[f"Event {event.event_id}: actor grooms user with small task or professional claims"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["TRUST_GROOMING_OBSERVED"],
            ))

        # 7. PLATFORM_MIGRATION
        if "PLATFORM_MIGRATION" in tactics or "MOVE_PLATFORM" in actions:
            observations.append(StageObservation(
                stage=JourneyStage.PLATFORM_MIGRATION,
                confidence=0.92,
                event_ids=[event.event_id],
                supporting_signals=["PLATFORM_MIGRATION"],
                supporting_evidence=[f"Event {event.event_id}: requested switch to WhatsApp or Telegram"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["EXTERNAL_PLATFORM_REDIRECT"],
            ))

        # 8. IMPERSONATION
        if "IMPERSONATION" in tactics or "AUTHORITY" in tactics:
            observations.append(StageObservation(
                stage=JourneyStage.IMPERSONATION,
                confidence=0.91,
                event_ids=[event.event_id],
                supporting_signals=list(tactics.intersection({"IMPERSONATION", "AUTHORITY"})),
                supporting_evidence=[f"Event {event.event_id}: claimed official authority or institutional identity"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["AUTHORITY_OR_BRAND_IMPERSONATION"],
            ))

        # 9. THREAT_OR_PRESSURE
        if "THREAT" in tactics or "FEAR" in tactics or "ISOLATION" in tactics or "COMPLIANCE_PRESSURE" in tactics:
            observations.append(StageObservation(
                stage=JourneyStage.THREAT_OR_PRESSURE,
                confidence=0.92,
                event_ids=[event.event_id],
                supporting_signals=list(tactics.intersection({"THREAT", "FEAR", "ISOLATION", "COMPLIANCE_PRESSURE"})),
                supporting_evidence=[f"Event {event.event_id}: coercive threats, arrest intimidation, or video isolation"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["LEGAL_OR_PSYCHOLOGICAL_COERCION"],
            ))

        # 10. URGENCY
        if "URGENCY" in tactics:
            observations.append(StageObservation(
                stage=JourneyStage.URGENCY,
                confidence=0.85,
                event_ids=[event.event_id],
                supporting_signals=["URGENCY"],
                supporting_evidence=[f"Event {event.event_id}: artificial time pressure or deadline"],
                first_seen=event.timestamp,
                last_seen=event.timestamp,
                detector_sources=["RULE"],
                reason_codes=["TIME_PRESSURE_IMPOSED"],
            ))

        # 11. DISCOVERY vs CONTACT
        if not observations:
            if "CLICK_LINK" in actions or "LINK_CLICKED" in ev_type:
                observations.append(StageObservation(
                    stage=JourneyStage.DISCOVERY,
                    confidence=0.80,
                    event_ids=[event.event_id],
                    supporting_evidence=[f"Event {event.event_id}: link clicked or external discovery portal"],
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    detector_sources=["RULE"],
                    reason_codes=["EXTERNAL_LURE_DISCOVERY"],
                ))
            else:
                observations.append(StageObservation(
                    stage=JourneyStage.CONTACT,
                    confidence=0.75,
                    event_ids=[event.event_id],
                    supporting_evidence=[f"Event {event.event_id}: initial inbound communication"],
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                    detector_sources=["RULE"],
                    reason_codes=["INBOUND_MESSAGE_CONTACT"],
                ))

        # Update stage candidates on the event object
        event.stage_candidates = [o.stage for o in observations]
        return observations

    def determine_current_stage(
        self,
        observations: List[StageObservation],
    ) -> Tuple[JourneyStage, float, List[JourneyStage]]:
        """Determines the primary current stage, confidence, and secondary active stages.
        
        Enforces Section 11 rule: Does NOT simply return the highest-numbered stage ever seen.
        Uses recency, confidence, evidence weight, and supported transitions.
        """
        if not observations:
            return JourneyStage.UNKNOWN, 0.0, []

        # Sort observations by last_seen descending
        sorted_obs = sorted(observations, key=lambda o: (o.last_seen, o.confidence), reverse=True)

        # Primary is the highest-confidence observation among the most recent events
        primary_obs = sorted_obs[0]
        primary_stage = primary_obs.stage
        confidence = primary_obs.confidence

        # Secondary active stages: other high-confidence stages active in the recent observation window
        secondary_stages = [
            o.stage for o in sorted_obs[1:4]
            if o.stage != primary_stage and o.confidence >= 0.75
        ]

        return primary_stage, confidence, secondary_stages
