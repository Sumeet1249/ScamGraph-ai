"""Intervention Memory & Warning Fatigue Manager (Phase 4B / Prompt 14).

Maintains incident-level intervention state to prevent alert fatigue while
ensuring safety alerts escalate immediately when situational context worsens.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.contextual_intervention import (
    FrictionLevel,
    InterventionDecision,
    InterventionType,
)


class IncidentSessionState(BaseModel):
    """Memory record for an active victim session."""
    incident_id: str
    interventions_generated: int = 0
    interventions_shown: int = 0
    interventions_dismissed: int = 0
    interventions_acknowledged: int = 0
    highest_friction_shown: FrictionLevel = FrictionLevel.NONE
    last_action_shown: Optional[InterventionType] = None
    last_journey_stage: str = "INITIAL_CONTACT"
    last_tactics_count: int = 0
    last_risk_score: float = 0.0
    last_shown_at: Optional[datetime] = None


class InterventionMemoryManager:
    """Controls frequency, avoids redundant popups, and gates escalations."""

    def __init__(self):
        self._sessions: Dict[str, IncidentSessionState] = {}

    def get_session(self, incident_id: str) -> IncidentSessionState:
        if incident_id not in self._sessions:
            self._sessions[incident_id] = IncidentSessionState(incident_id=incident_id)
        return self._sessions[incident_id]

    def should_suppress_due_to_fatigue(
        self,
        decision: InterventionDecision,
        current_tactics_count: int,
    ) -> bool:
        """Determines whether a modal or warning should be suppressed as fatigue.
        
        Rules:
        - NEVER suppress EMERGENCY_RESPONSE, DELAY_PAYMENT, DO_NOT_SHARE_OTP, or DO_NOT_SHARE_CREDENTIALS.
        - Suppress if the exact same warning action was shown with unchanged journey stage,
          unchanged risk band, and no new manipulation tactics.
        """
        session = self.get_session(decision.subject_id)

        # Critical non-suppressible actions
        critical_actions = {
            InterventionType.EMERGENCY_RESPONSE,
            InterventionType.DELAY_PAYMENT,
            InterventionType.DO_NOT_SHARE_OTP,
            InterventionType.DO_NOT_SHARE_CREDENTIALS,
            InterventionType.DO_NOT_INSTALL_REMOTE_ACCESS,
            InterventionType.TALK_TO_TRUSTED_PERSON,
        }
        if decision.intervention_type in critical_actions:
            return False

        if session.interventions_shown == 0:
            return False

        # If journey stage advanced to payment proximity, do NOT suppress
        if decision.journey_stage in ("PAYMENT_REQUEST", "PAYMENT_INTENT", "CREDENTIAL_HARVEST") and session.last_journey_stage not in ("PAYMENT_REQUEST", "PAYMENT_INTENT", "CREDENTIAL_HARVEST"):
            return False

        # If new tactics emerged (e.g. isolation, threats), do NOT suppress
        if current_tactics_count > session.last_tactics_count:
            return False

        # If risk surged significantly (+0.20 or more), do NOT suppress
        if decision.risk - session.last_risk_score >= 0.20:
            return False

        # If action is identical and context unchanged, suppress
        if session.last_action_shown == decision.intervention_type:
            return True

        return False

    def record_decision_shown(self, decision: InterventionDecision, tactics_count: int = 0) -> None:
        """Updates session memory after an intervention is delivered."""
        session = self.get_session(decision.subject_id)
        session.interventions_generated += 1
        session.interventions_shown += 1
        session.last_action_shown = decision.intervention_type
        session.last_journey_stage = decision.journey_stage
        session.last_tactics_count = tactics_count
        session.last_risk_score = decision.risk
        session.last_shown_at = datetime.now(timezone.utc)

    def record_acknowledgment(self, incident_id: str) -> None:
        session = self.get_session(incident_id)
        session.interventions_acknowledged += 1

    def record_dismissal(self, incident_id: str) -> None:
        session = self.get_session(incident_id)
        session.interventions_dismissed += 1


intervention_memory_manager = InterventionMemoryManager()
