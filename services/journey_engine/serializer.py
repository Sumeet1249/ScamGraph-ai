"""Consumer and Analyst Serialization for Scam Journey Engine V1.

Produces understandable, plain-language consumer explanations with progress meter DTOs,
and comprehensive forensic representations for cybercrime analysts.
"""

from typing import Any, Dict, List
from packages.schemas.journey import (
    ConsumerJourneyView,
    JourneyStage,
    ScamJourney,
    StageCategory,
)


class JourneySerializer:
    """Serializes ScamJourney states for consumer interfaces and analyst consoles."""

    @staticmethod
    def serialize_consumer_view(journey: ScamJourney) -> ConsumerJourneyView:
        """Constructs a privacy-safe, non-technical consumer explanation of the scam progression."""
        fam_name = journey.scam_family.replace("_", " ").title()
        if journey.scam_family == "UNKNOWN":
            title = "Suspicious Communication Pattern"
            why = "We detected multiple coercive indicators, but there is not yet enough evidence to classify a specific scam family."
        elif journey.scam_family == "JOB_TASK":
            title = "Likely Part-Time Job / Task Scam"
            why = "This progression (recruitment -> small reward -> Telegram migration -> deposit request) matches known task fraud patterns."
        elif journey.scam_family == "DIGITAL_ARREST":
            title = "High-Risk Authority & Digital Arrest Coercion"
            why = "Official police, CBI, or customs agencies never conduct arrests, interrogation, or demand clearance deposits over video calls."
        elif journey.scam_family == "INVESTMENT":
            title = "Likely High-Return Investment Fraud"
            why = "Promises of guaranteed high profits combined with deposit recharges are classic indicators of fraudulent trading portals."
        elif journey.scam_family == "KYC_BANK":
            title = "Likely Banking KYC Impersonation"
            why = "Banks never send urgent messages threatening immediate account blockage or asking you to share one-time passwords."
        else:
            title = f"Likely {fam_name} Scam Pattern"
            why = "This progression matches established cybercrime manipulation funnels."

        # Reconstruct plain-language what happened timeline
        what_happened: List[str] = []
        observed_stages = journey.stage_history or [journey.current_stage]
        for idx, stg in enumerate(observed_stages, start=1):
            if stg == JourneyStage.CONTACT:
                what_happened.append(f"{idx}. You received an unsolicited contact or invitation.")
            elif stg == JourneyStage.PLATFORM_MIGRATION:
                what_happened.append(f"{idx}. The conversation was moved to a private messaging app (Telegram/WhatsApp).")
            elif stg == JourneyStage.TRUST_BUILDING:
                what_happened.append(f"{idx}. Small tasks were offered to build rapport and confidence.")
            elif stg == JourneyStage.REWARD_OR_FAKE_PROFIT:
                what_happened.append(f"{idx}. A small payment or fake profit was shown or credited.")
            elif stg == JourneyStage.INITIAL_PAYMENT:
                what_happened.append(f"{idx}. You were asked to make an initial deposit or transfer money.")
            elif stg == JourneyStage.PAYMENT_ESCALATION:
                what_happened.append(f"{idx}. Pressure increased to deposit larger sums or upgrade your wallet.")
            elif stg == JourneyStage.WITHDRAWAL_BLOCK:
                what_happened.append(f"{idx}. Fund withdrawal was blocked citing taxes or clearance requirements.")
            elif stg == JourneyStage.IMPERSONATION:
                what_happened.append(f"{idx}. The sender claimed official or law enforcement authority.")
            elif stg == JourneyStage.THREAT_OR_PRESSURE:
                what_happened.append(f"{idx}. Coercive threats of arrest, legal prosecution, or penalty were made.")
            elif stg == JourneyStage.CREDENTIAL_REQUEST:
                what_happened.append(f"{idx}. You were pressured to provide an OTP, PIN, or password.")

        if not what_happened:
            what_happened.append("1. Suspicious interaction initiated.")

        # Determine recommended action
        if journey.current_stage in (JourneyStage.PAYMENT_ESCALATION, JourneyStage.INITIAL_PAYMENT):
            action = "PAUSE before making any payment. Verify the recipient independently through verified public directories."
        elif journey.current_stage == JourneyStage.CREDENTIAL_REQUEST:
            action = "DO NOT share your OTP, PIN, or password with anyone, even if they claim to be bank officials."
        elif journey.current_stage == JourneyStage.THREAT_OR_PRESSURE or "ISOLATION" in journey.tactics:
            action = "Immediately disconnect. Legitimate Indian authorities never conduct arrests over Skype or WhatsApp calls."
        else:
            action = "Verify the sender's identity independently before taking any requested actions."

        # Progress label
        if journey.progress:
            prog_label = journey.progress.display_stage
            warning_lvl = journey.progress.escalation_level
        else:
            prog_label = journey.current_stage.value.replace("_", " ").title()
            warning_lvl = "HIGH" if journey.early_warnings else "MEDIUM"

        progress_meter = {
            "display_stage": prog_label,
            "completed_steps": journey.progress.completed_steps if journey.progress else [],
            "current_step": journey.progress.current_step if journey.progress else prog_label,
            "possible_future_steps": journey.progress.possible_future_steps if journey.progress else [],
            "warning_level": warning_lvl,
        }

        return ConsumerJourneyView(
            likely_family=title,
            progress_label=prog_label,
            what_happened=what_happened,
            why_this_matters=why,
            recommended_action=action,
            warning_level=warning_lvl,
            progress_meter=progress_meter,
        )

    @staticmethod
    def serialize_analyst_view(journey: ScamJourney) -> Dict[str, Any]:
        """Constructs a comprehensive forensic timeline for fraud analysts."""
        return {
            "journey_id": journey.journey_id,
            "incident_id": journey.incident_id,
            "schema_version": journey.schema_version,
            "scam_family": journey.scam_family,
            "family_hypotheses": journey.family_hypotheses,
            "current_stage": journey.current_stage.value,
            "current_stage_confidence": journey.current_stage_confidence,
            "monetization_status": journey.monetization_status.value,
            "loss_status": journey.loss_status.value,
            "monetization_boundary_event_id": journey.monetization_boundary_event_id,
            "first_actionable_warning_event_id": journey.first_actionable_warning_event_id,
            "first_actionable_warning_timestamp": journey.first_actionable_warning_timestamp.isoformat() if journey.first_actionable_warning_timestamp else None,
            "warning_lead_time_seconds": journey.warning_lead_time_seconds,
            "pre_loss_warning_issued": journey.pre_loss_warning_issued,
            "stage_observations": [
                {
                    "observation_id": so.observation_id,
                    "stage": so.stage.value,
                    "category": so.category.value,
                    "confidence": so.confidence,
                    "event_ids": so.event_ids,
                    "supporting_signals": so.supporting_signals,
                    "reason_codes": so.reason_codes,
                    "first_seen": so.first_seen.isoformat(),
                    "last_seen": so.last_seen.isoformat(),
                }
                for so in journey.stage_observations
            ],
            "events_count": len(journey.events),
            "events": [
                {
                    "event_id": ev.event_id,
                    "timestamp": ev.timestamp.isoformat(),
                    "sequence_number": ev.sequence_number,
                    "event_type": ev.event_type,
                    "channel": ev.channel,
                    "tactics": ev.tactics,
                    "requested_actions": ev.requested_actions,
                    "stage_candidates": [s.value for s in ev.stage_candidates],
                }
                for ev in journey.events
            ],
            "early_warnings": [
                {
                    "warning_id": w.warning_id,
                    "warning_type": w.warning_type,
                    "current_stage": w.current_stage.value,
                    "confidence": w.confidence,
                    "recommended_intervention_class": w.recommended_intervention_class,
                }
                for w in journey.early_warnings
            ],
            "degraded": journey.degraded,
            "engine_version": journey.engine_version,
        }
