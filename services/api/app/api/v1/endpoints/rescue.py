"""FastAPI Endpoints for ScamGraph Rescue (Prompt 16 / Phase 5B)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas.rescue import (
    ActionCategory,
    ActionStatus,
    EmergencyActionPlan,
    ExposureAssessment,
    ExposureCategory,
    ExposureSeverity,
    LossEvent,
    LossType,
    OfficialReportingResource,
    RecoveryScamProtection,
    RescueActionItem,
    RescueCasePackage,
    RescueTimelineEvent,
    RescueTriage,
    TimeGranularity,
)
from services.rescue_engine.case_package import case_package_generator
from services.rescue_engine.reconstruction import incident_reconstruction_service
from services.rescue_engine.resources import official_resources_registry
from services.rescue_engine.service import rescue_service

router = APIRouter()


class StartRescueRequest(BaseModel):
    incident_id: Optional[str] = None
    initial_loss_type: Optional[LossType] = Field(default=LossType.MONEY_TRANSFER)
    user_notes: str = Field(default="")
    ongoing_contact: bool = Field(default=False)
    bank_hint: Optional[str] = Field(default=None)


class RecordLossRequest(BaseModel):
    amount: float = Field(ge=0.0)
    currency: str = Field(default="INR")
    payment_method: str = Field(default="UPI")
    recipient_identifier: Optional[str] = None
    transaction_reference: Optional[str] = None
    occurred_at: Optional[datetime] = None
    time_granularity: TimeGranularity = Field(default=TimeGranularity.EXACT)
    evidence_ids: List[str] = Field(default_factory=list)


class RecordExposureRequest(BaseModel):
    category: ExposureCategory
    severity: ExposureSeverity
    target_identifier: Optional[str] = None
    details: str = Field(default="")
    remote_tool_name: Optional[str] = None
    id_document_type: Optional[str] = None
    has_secret_exposed: bool = Field(default=False)
    active_now: bool = Field(default=False)


class UpdateActionStatusRequest(BaseModel):
    status: ActionStatus


class RecoveryScamCheckRequest(BaseModel):
    message_text: str


class RescueStateResponse(BaseModel):
    incident_id: str
    status: str
    triage: RescueTriage
    action_plan: EmergencyActionPlan
    loss_events: List[LossEvent]
    total_reported_loss: float
    currency: str
    timeline: List[RescueTimelineEvent]
    official_resources: List[OfficialReportingResource]


@router.post("/start", response_model=RescueStateResponse)
def start_rescue(req: StartRescueRequest):
    """
    Initiates Rescue mode. Seamlessly transitions an existing Protect incident or
    creates a new direct Rescue encounter.
    """
    inc = rescue_service.get_or_create_incident(
        incident_id=req.incident_id,
        initial_loss_type=req.initial_loss_type,
        user_notes=req.user_notes,
    )

    triage = rescue_service.get_triage(inc.incident_id, ongoing_contact=req.ongoing_contact)
    plan = rescue_service.get_action_plan(inc.incident_id, ongoing_contact=req.ongoing_contact, bank_hint=req.bank_hint)
    loss_events = incident_reconstruction_service.get_loss_events(inc.incident_id)
    total_loss, curr, _ = incident_reconstruction_service.calculate_reported_loss(inc.incident_id)
    timeline = incident_reconstruction_service.get_timeline(inc.incident_id)
    resources = official_resources_registry.list_all("IN")

    return RescueStateResponse(
        incident_id=inc.incident_id,
        status=inc.status.value,
        triage=triage,
        action_plan=plan,
        loss_events=loss_events,
        total_reported_loss=total_loss,
        currency=curr,
        timeline=timeline,
        official_resources=resources,
    )


@router.get("/{incident_id}", response_model=RescueStateResponse)
def get_rescue_state(incident_id: str):
    """Retrieves current emergency state, action items, and reconstructed timeline."""
    inc = rescue_service.get_or_create_incident(incident_id)
    triage = rescue_service.get_triage(incident_id)
    plan = rescue_service.get_action_plan(incident_id)
    loss_events = incident_reconstruction_service.get_loss_events(incident_id)
    total_loss, curr, _ = incident_reconstruction_service.calculate_reported_loss(incident_id)
    timeline = incident_reconstruction_service.get_timeline(incident_id)
    resources = official_resources_registry.list_all("IN")

    return RescueStateResponse(
        incident_id=inc.incident_id,
        status=inc.status.value,
        triage=triage,
        action_plan=plan,
        loss_events=loss_events,
        total_reported_loss=total_loss,
        currency=curr,
        timeline=timeline,
        official_resources=resources,
    )


@router.post("/{incident_id}/loss-events", response_model=LossEvent)
def record_loss_event(incident_id: str, req: RecordLossRequest):
    """Records a monetary loss or transfer event. Automatically deduplicates identical submissions."""
    event = rescue_service.record_loss(
        incident_id=incident_id,
        amount=req.amount,
        currency=req.currency,
        payment_method=req.payment_method,
        recipient_identifier=req.recipient_identifier,
        transaction_reference=req.transaction_reference,
        occurred_at=req.occurred_at,
        time_granularity=req.time_granularity,
        evidence_ids=req.evidence_ids,
    )
    return event


@router.post("/{incident_id}/exposures", response_model=ExposureAssessment)
def record_exposure(incident_id: str, req: RecordExposureRequest):
    """Records compromised credentials, remote access, or identity document disclosure."""
    exposure = rescue_service.record_exposure(
        incident_id=incident_id,
        category=req.category,
        severity=req.severity,
        target_identifier=req.target_identifier,
        details=req.details,
        remote_tool_name=req.remote_tool_name,
        id_document_type=req.id_document_type,
        has_secret_exposed=req.has_secret_exposed,
        active_now=req.active_now,
    )
    return exposure


@router.get("/{incident_id}/action-plan", response_model=EmergencyActionPlan)
def get_action_plan(incident_id: str, bank_hint: Optional[str] = Query(default=None)):
    """Retrieves current prioritized action plan (DO NOW, DO NEXT, PRESERVE, REPORT, MONITOR)."""
    return rescue_service.get_action_plan(incident_id, bank_hint=bank_hint)


@router.post("/{incident_id}/actions/{action_id}")
def update_action_status(incident_id: str, action_id: str, req: UpdateActionStatusRequest):
    """Updates the execution status of an individual action item."""
    updated = rescue_service.update_action_status(incident_id, action_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Action item not found in incident plan")
    return {"status": "SUCCESS", "action_id": action_id, "new_status": req.status.value}


@router.get("/{incident_id}/timeline", response_model=List[RescueTimelineEvent])
def get_timeline(incident_id: str):
    """Retrieves chronological incident and response events."""
    return incident_reconstruction_service.get_timeline(incident_id)


@router.get("/{incident_id}/case-package", response_model=RescueCasePackage)
def get_case_package(incident_id: str):
    """Generates structured, privacy-safe reporting case package."""
    return rescue_service.generate_case_package(incident_id)


@router.post("/{incident_id}/export")
def export_case_package(incident_id: str, format: str = Query(default="markdown")):
    """Exports case package as human-readable Markdown or formatted text."""
    pkg = rescue_service.generate_case_package(incident_id)
    if format.lower() == "markdown" or format.lower() == "md":
        rendered = case_package_generator.render_markdown(pkg)
        return {"format": "markdown", "filename": f"rescue_case_{incident_id}.md", "content": rendered}
    return {"format": "json", "filename": f"rescue_case_{incident_id}.json", "content": pkg.dict()}


@router.post("/{incident_id}/check-recovery-scam", response_model=RecoveryScamProtection)
def check_recovery_scam(incident_id: str, req: RecoveryScamCheckRequest):
    """Screens follow-up communications received by victim for secondary advance-fee recovery fraud."""
    return rescue_service.check_recovery_scam(incident_id, req.message_text)


@router.get("/resources/reporting", response_model=List[OfficialReportingResource])
def list_official_resources(jurisdiction: str = Query(default="IN")):
    """Lists verified official authorities and banking emergency fraud numbers."""
    return official_resources_registry.list_all(jurisdiction)
