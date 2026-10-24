"""Rescue Orchestration Service for ScamGraph AI (Prompt 16 / Phase 5B).

Central coordinator for:
- Starting rescue (transitioning existing Protect incident OR initiating direct rescue)
- Recording multi-stage loss events & exposures
- Evaluating RescueTriage and generating EmergencyActionPlan
- Generating privacy-safe RescueCasePackage
- Protecting victims against secondary recovery scams
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
from packages.schemas.common import generate_id
from packages.schemas.incident import Incident, IncidentStatus
from packages.schemas.rescue import (
    ActionCategory,
    ActionStatus,
    EmergencyActionPlan,
    EvidencePreservationItem,
    ExposureAssessment,
    ExposureCategory,
    ExposureSeverity,
    LossEvent,
    LossType,
    RecoveryScamProtection,
    RescueActionItem,
    RescueCasePackage,
    RescueTimelineEvent,
    RescueTimelineEventType,
    RescueTriage,
    TimeGranularity,
)
from services.rescue_engine.case_package import case_package_generator
from services.rescue_engine.feedback_loop import rescue_intelligence_feedback
from services.rescue_engine.reconstruction import incident_reconstruction_service
from services.rescue_engine.resources import official_resources_registry
from services.rescue_engine.triage import rescue_triage_engine


class RescueService:
    """Stateful orchestrator for post-loss victim assistance and intelligence feedback."""

    def __init__(self):
        # Store incidents and rescue sessions in memory
        self._incidents: Dict[str, Incident] = {}
        self._exposures: Dict[str, List[ExposureAssessment]] = {}
        self._action_plans: Dict[str, EmergencyActionPlan] = {}
        self._evidence_items: Dict[str, List[EvidencePreservationItem]] = {}
        self._actions_taken: Dict[str, List[str]] = {}

    def get_or_create_incident(
        self,
        incident_id: Optional[str] = None,
        initial_loss_type: Optional[LossType] = None,
        user_notes: str = "",
    ) -> Incident:
        """Transitions an existing incident into Rescue mode or creates a new direct rescue case."""
        if incident_id and incident_id in self._incidents:
            inc = self._incidents[incident_id]
            inc.status = IncidentStatus.ESCALATED
            inc.updated_at = datetime.now(timezone.utc)
            inc.metadata["rescue_active"] = True
            inc.metadata["rescue_started_at"] = datetime.now(timezone.utc).isoformat()
            if initial_loss_type:
                inc.metadata["initial_rescue_loss_type"] = initial_loss_type.value
            return inc

        # Direct Rescue entry (user's first interaction with ScamGraph is 'I already paid')
        new_id = incident_id or generate_id("inc")
        now = datetime.now(timezone.utc)
        inc = Incident(
            incident_id=new_id,
            status=IncidentStatus.ESCALATED,
            created_at=now,
            updated_at=now,
            source_context={"origin": "RESCUE_DIRECT", "notes": user_notes},
            metadata={
                "rescue_active": True,
                "rescue_started_at": now.isoformat(),
                "initial_rescue_loss_type": initial_loss_type.value if initial_loss_type else "MONEY_TRANSFER",
            },
        )
        self._incidents[new_id] = inc
        return inc

    def record_loss(
        self,
        incident_id: str,
        amount: float,
        currency: str = "INR",
        payment_method: str = "UPI",
        recipient_identifier: Optional[str] = None,
        transaction_reference: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        time_granularity: TimeGranularity = TimeGranularity.EXACT,
        evidence_ids: Optional[List[str]] = None,
    ) -> LossEvent:
        """Records a payment/loss event. Deduplicates identical submissions."""
        self.get_or_create_incident(incident_id)
        event, is_new = incident_reconstruction_service.record_loss_event(
            incident_id=incident_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            recipient_identifier=recipient_identifier,
            transaction_reference=transaction_reference,
            occurred_at=occurred_at,
            time_granularity=time_granularity,
            evidence_ids=evidence_ids,
        )
        # Invalidate cached action plan to re-evaluate priorities
        self._action_plans.pop(incident_id, None)
        return event

    def record_exposure(
        self,
        incident_id: str,
        category: ExposureCategory,
        severity: ExposureSeverity,
        target_identifier: Optional[str] = None,
        details: str = "",
        remote_tool_name: Optional[str] = None,
        id_document_type: Optional[str] = None,
        has_secret_exposed: bool = False,
        active_now: bool = False,
    ) -> ExposureAssessment:
        """Records a credential, device, or identity disclosure."""
        self.get_or_create_incident(incident_id)
        exposure = ExposureAssessment(
            incident_id=incident_id,
            category=category,
            severity=severity,
            target_identifier=target_identifier,
            details=details,
            remote_tool_name=remote_tool_name,
            id_document_type=id_document_type,
            has_secret_exposed=has_secret_exposed,
            active_now=active_now,
        )
        exps = self._exposures.setdefault(incident_id, [])
        exps.append(exposure)

        # Add corresponding timeline event
        now = datetime.now(timezone.utc)
        if category == ExposureCategory.DEVICE:
            t_type = RescueTimelineEventType.REMOTE_ACCESS_GRANTED
            t_title = f"Remote Access Tool Installed ({remote_tool_name or 'Remote Software'})"
        elif category == ExposureCategory.IDENTITY:
            t_type = RescueTimelineEventType.CREDENTIAL_SHARED
            t_title = f"Identity Document Disclosed ({id_document_type or 'Govt ID'})"
        else:
            t_type = RescueTimelineEventType.CREDENTIAL_SHARED
            t_title = f"Credentials Disclosed ({category.value})"

        incident_reconstruction_service.add_timeline_event(
            incident_id,
            RescueTimelineEvent(
                event_type=t_type,
                title=t_title,
                description=details or f"Exposure category: {category.value}",
                occurred_at=now,
                recorded_at=now,
                exposure_id=exposure.exposure_id,
                source="USER_REPORTED",
            ),
        )

        self._action_plans.pop(incident_id, None)
        return exposure

    def get_triage(self, incident_id: str, ongoing_contact: bool = False) -> RescueTriage:
        """Retrieves or calculates RescueTriage."""
        loss_events = incident_reconstruction_service.get_loss_events(incident_id)
        exposures = self._exposures.get(incident_id, [])
        inc = self.get_or_create_incident(incident_id)

        return rescue_triage_engine.evaluate_triage(
            incident_id=incident_id,
            loss_events=loss_events,
            exposures=exposures,
            ongoing_contact=ongoing_contact,
            scam_family=inc.likely_scam_family,
        )

    def get_action_plan(
        self,
        incident_id: str,
        ongoing_contact: bool = False,
        bank_hint: Optional[str] = None,
    ) -> EmergencyActionPlan:
        """Generates or updates the Emergency Action Plan."""
        triage = self.get_triage(incident_id, ongoing_contact=ongoing_contact)
        loss_events = incident_reconstruction_service.get_loss_events(incident_id)
        exposures = self._exposures.get(incident_id, [])

        plan = rescue_triage_engine.generate_action_plan(
            triage=triage,
            loss_events=loss_events,
            exposures=exposures,
            bank_hint=bank_hint,
        )
        self._action_plans[incident_id] = plan
        return plan

    def update_action_status(
        self,
        incident_id: str,
        action_id: str,
        new_status: ActionStatus,
    ) -> Optional[RescueActionItem]:
        """Marks an action item as DONE, TODO, or NOT_APPLICABLE."""
        plan = self._action_plans.get(incident_id)
        if not plan:
            plan = self.get_action_plan(incident_id)

        all_actions = plan.do_now + plan.do_next + plan.preserve + plan.report + plan.monitor
        found_item = None
        for item in all_actions:
            if item.action_id == action_id:
                item.status = new_status
                if new_status == ActionStatus.DONE:
                    item.user_confirmed_at = datetime.now(timezone.utc)
                    actions_done = self._actions_taken.setdefault(incident_id, [])
                    if item.title not in actions_done:
                        actions_done.append(item.title)
                found_item = item
                break

        plan.completed_actions = sum(1 for it in all_actions if it.status == ActionStatus.DONE)
        return found_item

    def add_preserved_evidence(
        self,
        incident_id: str,
        evidence_type: str,
        display_title: str,
        description: str,
        sha256_hash: str,
        storage_path: Optional[str] = None,
        mime_type: str = "image/png",
    ) -> EvidencePreservationItem:
        """Stores a preserved piece of digital evidence."""
        item = EvidencePreservationItem(
            evidence_id=generate_id("evid"),
            evidence_type=evidence_type,
            display_title=display_title,
            description=description,
            sha256_hash=sha256_hash,
            storage_path=storage_path,
            mime_type=mime_type,
        )
        items = self._evidence_items.setdefault(incident_id, [])
        items.append(item)
        return item

    def check_recovery_scam(self, incident_id: str, suspect_text: str) -> RecoveryScamProtection:
        """Analyzes suspect communication received after a loss for recovery scam signals."""
        t_lower = suspect_text.lower()
        patterns = [
            (r"(\brecover(y|ed)?\b.*\b(fee|charge|deposit|tax|advance|cost)\b|\b(fee|charge|deposit|tax|advance|cost|pay)\b.*\brecover)", "ADVANCE_RECOVERY_FEE"),
            (r"\bhack\s?back\b|\bethical hacker\b|\bretrieve funds\b", "FAKE_HACKER_SOLICITATION"),
            (r"\bunlock\b.*\b(withdrawal|wallet|account)\b.*\b(pay|transfer)\b", "UNFREEZE_PAYMENT_ESCALATION"),
            (r"\bshare\b.*\botp\b.*\b(refund|reverse|credit)\b", "OTP_REFUND_TRAP"),
            (r"\bcyber\s?lawyer\b.*\bupfront\b", "UNVERIFIED_CYBER_LEGAL_FEE"),
        ]

        detected: List[str] = []
        for pat, rule_id in patterns:
            if re.search(pat, t_lower):
                detected.append(rule_id)

        fee_requested = any(r in detected for r in ("ADVANCE_RECOVERY_FEE", "UNFREEZE_PAYMENT_ESCALATION"))
        risk_level = "CRITICAL" if detected else "HIGH"

        warning = (
            "CRITICAL WARNING: This message exhibits high-risk indicators of a SECONDARY RECOVERY SCAM. "
            "Never pay money, share OTPs, or install software to 'recover' previously lost funds. "
            "Legitimate police and banks never charge advance fees to investigate or hold funds."
        )

        protection = RecoveryScamProtection(
            incident_id=incident_id,
            risk_level=risk_level,
            secondary_contact_detected=True,
            recovery_fee_requested=fee_requested,
            threat_patterns_detected=detected,
            warning_text=warning,
            rules_triggered=detected,
        )

        # If detected, record timeline event
        if detected:
            incident_reconstruction_service.add_timeline_event(
                incident_id,
                RescueTimelineEvent(
                    event_type=RescueTimelineEventType.RECOVERY_SCAM_CONTACT,
                    title="Secondary Recovery Scam Encountered",
                    description=f"Suspect approached victim with claims: {', '.join(detected)}",
                    occurred_at=datetime.now(timezone.utc),
                    recorded_at=datetime.now(timezone.utc),
                    source="USER_REPORTED",
                ),
            )

        return protection

    def generate_case_package(
        self,
        incident_id: str,
        contact_entities: Optional[List[Dict[str, Any]]] = None,
        urls: Optional[List[str]] = None,
        social_handles: Optional[List[str]] = None,
        claimed_organizations: Optional[List[str]] = None,
    ) -> RescueCasePackage:
        """Assembles the final RescueCasePackage."""
        triage = self.get_triage(incident_id)
        loss_events = incident_reconstruction_service.get_loss_events(incident_id)
        timeline = incident_reconstruction_service.get_timeline(incident_id)
        evidence = self._evidence_items.get(incident_id, [])
        resources = official_resources_registry.list_all("IN")
        inc = self.get_or_create_incident(incident_id)
        actions_taken = self._actions_taken.get(incident_id, [])

        return case_package_generator.generate_package(
            incident_id=incident_id,
            triage=triage,
            loss_events=loss_events,
            timeline_events=timeline,
            evidence_items=evidence,
            reporting_resources=resources,
            contact_entities=contact_entities,
            urls_and_domains=urls,
            social_handles=social_handles,
            claimed_organizations=claimed_organizations,
            inferred_scam_family=inc.likely_scam_family,
            actions_taken=actions_taken,
        )


rescue_service = RescueService()
