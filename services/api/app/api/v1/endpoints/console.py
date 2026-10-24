"""Console Intelligence Endpoints (Prompt 19 / Phase 6A).

Provides operational APIs for the ScamGraph Intelligence Console V2:
Command Center Telemetry, Alert Center, Review Queue, and Case Management.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas.console import (
    AlertStatus,
    CommandCenterSummary,
    IntelligenceAlert,
    InvestigationCase,
    ReviewDecisionType,
    ReviewQueueItem,
)
from services.console.service import console_intelligence_service

router = APIRouter(prefix="/console", tags=["console"])


class AlertStatusUpdateRequest(BaseModel):
    status: AlertStatus


class ReviewDecisionRequest(BaseModel):
    decision: ReviewDecisionType
    reviewer_notes: Optional[str] = None
    reviewer_id: str = "analyst_ops"


class CreateCaseRequest(BaseModel):
    title: str
    priority: str = "HIGH"
    assigned_analyst: Optional[str] = None
    linked_incident_ids: List[str] = Field(default_factory=list)
    linked_campaign_ids: List[str] = Field(default_factory=list)
    linked_entities: List[str] = Field(default_factory=list)
    initial_note: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AddNoteRequest(BaseModel):
    text: str
    author: str = "analyst"


# -----------------------------------------------------------------------------
# Command Center
# -----------------------------------------------------------------------------
@router.get("/summary", response_model=CommandCenterSummary)
async def get_command_center_summary(time_window: str = Query(default="24h")):
    """Returns aggregated operational telemetry and queues for the analyst landing page."""
    return console_intelligence_service.get_command_center_summary(time_window=time_window)


# -----------------------------------------------------------------------------
# Alerts Center
# -----------------------------------------------------------------------------
@router.get("/alerts", response_model=List[IntelligenceAlert])
async def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
):
    """Lists operational threat alerts with optional state and severity filtering."""
    return console_intelligence_service.get_alerts(status_filter=status, severity_filter=severity)


@router.patch("/alerts/{alert_id}", response_model=IntelligenceAlert)
async def update_alert_status(alert_id: str, req: AlertStatusUpdateRequest):
    """Updates operational state of an alert (e.g. ACKNOWLEDGED, INVESTIGATING, RESOLVED)."""
    updated = console_intelligence_service.update_alert_status(alert_id, req.status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found.",
        )
    return updated


# -----------------------------------------------------------------------------
# Review Center (Human-in-the-loop Queue)
# -----------------------------------------------------------------------------
@router.get("/reviews", response_model=List[ReviewQueueItem])
async def list_reviews(type: Optional[str] = None):
    """Lists pending review queue items sorted by priority score."""
    return console_intelligence_service.get_review_queue(type_filter=type)


@router.post("/reviews/{review_id}/decide", response_model=ReviewQueueItem)
async def submit_review_decision(review_id: str, req: ReviewDecisionRequest):
    """Records human analyst decision on campaign merge, entity disambiguation, or novel variant."""
    adjudicated = console_intelligence_service.submit_review_decision(
        review_id=review_id,
        decision=req.decision,
        reviewer_notes=req.reviewer_notes,
        reviewer_id=req.reviewer_id,
    )
    if not adjudicated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review item '{review_id}' not found.",
        )
    return adjudicated


# -----------------------------------------------------------------------------
# Case Management Foundation
# -----------------------------------------------------------------------------
@router.get("/cases", response_model=List[InvestigationCase])
async def list_cases(status: Optional[str] = None):
    """Lists operational investigation cases."""
    return console_intelligence_service.get_cases(status_filter=status)


@router.post("/cases", response_model=InvestigationCase, status_code=status.HTTP_201_CREATED)
async def create_case(req: CreateCaseRequest):
    """Creates a new analyst investigation case."""
    return console_intelligence_service.create_case(
        title=req.title,
        priority=req.priority,
        assigned_analyst=req.assigned_analyst,
        linked_incident_ids=req.linked_incident_ids,
        linked_campaign_ids=req.linked_campaign_ids,
        linked_entities=req.linked_entities,
        initial_note=req.initial_note,
        tags=req.tags,
    )


@router.get("/cases/{case_id}", response_model=InvestigationCase)
async def get_case(case_id: str):
    """Retrieves single investigation case details."""
    case = console_intelligence_service.get_case(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{case_id}' not found.",
        )
    return case


@router.post("/cases/{case_id}/notes", response_model=InvestigationCase)
async def add_case_note(case_id: str, req: AddNoteRequest):
    """Appends an auditable analyst note to the investigation case."""
    updated = console_intelligence_service.add_case_note(
        case_id=case_id,
        text=req.text,
        author=req.author,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{case_id}' not found.",
        )
    return updated
