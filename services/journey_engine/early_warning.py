"""Early Warning Engine & Proactive Pre-Loss Intervention Generator for ScamGraph AI V2.

Generates calibrated early warning candidates based on stage progression, tactic density,
and monetization risk, providing actionable intervention classes before financial loss occurs.
"""

from datetime import datetime, timezone
from typing import List, Optional, Set, Tuple

from packages.schemas.journey import (
    EarlyWarningCandidate,
    JourneyEvent,
    JourneyStage,
)


class EarlyWarningEngine:
    """Evaluates journey events to produce calibrated early warning candidates."""

    @staticmethod
    def generate_early_warnings(
        events: List[JourneyEvent],
        current_stage: JourneyStage,
        scam_family: str = "UNKNOWN",
    ) -> List[EarlyWarningCandidate]:
        """Scans the event sequence to detect early risk thresholds and candidate warnings."""
        if not events:
            return []

        warnings: List[EarlyWarningCandidate] = []
        observed_stages: Set[JourneyStage] = set()
        all_tactics: Set[str] = set()

        for ev in events:
            observed_stages.update(ev.stage_candidates)
            all_tactics.update(ev.tactics)

        latest_event = events[-1]

        # 1. CREDENTIAL_RISK
        if JourneyStage.CREDENTIAL_REQUEST in observed_stages or "CREDENTIAL_PRESSURE" in all_tactics:
            warnings.append(EarlyWarningCandidate(
                warning_type="CREDENTIAL_RISK",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.95,
                supporting_evidence=["Actor is actively attempting to harvest OTPs, PINs, or banking credentials"],
                recommended_intervention_class="IMMEDIATE_PAUSE",
                timestamp=latest_event.timestamp,
            ))

        # 2. REMOTE_ACCESS_RISK
        if "REMOTE_ACCESS_PRESSURE" in all_tactics:
            warnings.append(EarlyWarningCandidate(
                warning_type="REMOTE_ACCESS_RISK",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.96,
                supporting_evidence=["Actor is requesting remote screen sharing or remote management app installation"],
                recommended_intervention_class="IMMEDIATE_PAUSE",
                timestamp=latest_event.timestamp,
            ))

        # 3. PAYMENT_RISK
        if (
            current_stage in (JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION)
            or "PAYMENT_PRESSURE" in all_tactics
        ):
            interv_class = "IMMEDIATE_PAUSE" if current_stage == JourneyStage.PAYMENT_ESCALATION else "STRONG_WARNING"
            warnings.append(EarlyWarningCandidate(
                warning_type="PAYMENT_RISK",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.92,
                supporting_evidence=["Direct money transfer, UPI collect, or wallet recharge is being pressured"],
                recommended_intervention_class=interv_class,
                timestamp=latest_event.timestamp,
            ))

        # 4. AUTHORITY_IMPERSONATION_RISK
        if (
            JourneyStage.IMPERSONATION in observed_stages
            and (JourneyStage.THREAT_OR_PRESSURE in observed_stages or "SECRECY" in all_tactics or "ISOLATION" in all_tactics)
        ):
            warnings.append(EarlyWarningCandidate(
                warning_type="AUTHORITY_IMPERSONATION_RISK",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.93,
                supporting_evidence=["Coercive law enforcement / official authority impersonation with secrecy commands"],
                recommended_intervention_class="STRONG_WARNING",
                timestamp=latest_event.timestamp,
            ))

        # 5. RECOVERY_FEE_RISK
        if (
            JourneyStage.WITHDRAWAL_BLOCK in observed_stages
            or JourneyStage.RECOVERY_FEE in observed_stages
        ):
            warnings.append(EarlyWarningCandidate(
                warning_type="RECOVERY_FEE_RISK",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.91,
                supporting_evidence=["Fake tax, clearance fee, or unfreezing fee demanded to release previous funds"],
                recommended_intervention_class="STRONG_WARNING",
                timestamp=latest_event.timestamp,
            ))

        # 6. MULTI_STAGE_SCAM_PATTERN
        if len(observed_stages) >= 3 and scam_family != "UNKNOWN":
            warnings.append(EarlyWarningCandidate(
                warning_type="MULTI_STAGE_SCAM_PATTERN",
                trigger_event_id=latest_event.event_id,
                current_stage=current_stage,
                confidence=0.88,
                supporting_evidence=[f"Multi-event progression aligns with known {scam_family} fraud journey"],
                recommended_intervention_class="WARNING",
                timestamp=latest_event.timestamp,
            ))

        return warnings
