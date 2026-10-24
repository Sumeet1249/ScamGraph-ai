"""FastAPI Endpoints for Smart Registry (Module A).

Implements report ingestion, identifier screening, review decisions, disputes,
revocations, entity details, audit event streams, and aggregate statistics.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from packages.schemas.registry import (
    AuditEvent,
    CreateReportRequest,
    DisputeDecisionRequest,
    DisputeRecord,
    RegistryEntity,
    RegistryEntityDetail,
    RegistryFeedbackRequest,
    RegistryReport,
    RegistryStatistics,
    ReportStatus,
    ReviewReportRequest,
    RevocationRecord,
    ScreenRequest,
    ScreenResponse,
    SubmitDisputeRequest,
    SubmitRevocationRequest,
)
from services.registry.service import SmartRegistryService, get_smart_registry_service
from services.registry.repository import RegistryRepository, get_registry_repository

router = APIRouter()


# -----------------------------------------------------------------------------
# Screening Endpoint
# -----------------------------------------------------------------------------

@router.post("/screen", response_model=ScreenResponse)
async def screen_identifiers(
    req: ScreenRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Screen one or more typed identifiers in real time using keyed HMAC-SHA-256 exact matching."""
    try:
        result = await service.screen_identifiers(req)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Screening error: {str(e)}",
        )


# -----------------------------------------------------------------------------
# Reports Endpoints
# -----------------------------------------------------------------------------

@router.post("/reports", response_model=RegistryReport, status_code=status.HTTP_201_CREATED)
async def create_registry_report(
    req: CreateReportRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Ingest a new suspect identifier / fraud report with typed evidence into Smart Registry."""
    try:
        report = await service.ingest_report(req)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest report: {str(e)}",
        )


@router.get("/reports", response_model=List[RegistryReport])
async def list_registry_reports(
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """List reports with optional status filtering."""
    return await repo.list_reports(status=status_filter, limit=limit, offset=offset)


@router.get("/reports/{report_id}", response_model=RegistryReport)
async def get_report_by_id(
    report_id: str,
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Fetch report details by ID."""
    report = await repo.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found.",
        )
    return report


@router.post("/reports/{report_id}/review", response_model=RegistryReport)
async def review_registry_report(
    report_id: str,
    req: ReviewReportRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Review and transition report status (e.g. to CONFIRMED, REJECTED, or UNDER_REVIEW)."""
    try:
        report = await service.review_report(report_id, req)
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reports/{report_id}/history", response_model=List[AuditEvent])
async def get_report_history(
    report_id: str,
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Fetch immutable audit trail for a report."""
    report = await repo.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found.",
        )
    return await repo.get_audit_trail(report_id)


# -----------------------------------------------------------------------------
# Entities Endpoints (Core Entity Models)
# -----------------------------------------------------------------------------

@router.get("/entities", response_model=List[RegistryEntity])
async def list_registry_entities(
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """List canonical RegistryEntities with status filter."""
    return await repo.list_entities(status=status_filter, limit=limit, offset=offset)


@router.get("/entities/{entity_id}", response_model=RegistryEntityDetail)
async def get_entity_detail(
    entity_id: str,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Fetch detailed registry entity with linked reports and audit trail."""
    try:
        detail = await service.get_entity_detail(entity_id)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -----------------------------------------------------------------------------
# Disputes Endpoints
# -----------------------------------------------------------------------------

@router.post("/disputes", response_model=DisputeRecord)
async def submit_dispute(
    req: SubmitDisputeRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Contest a reported identifier or account with formal evidence."""
    try:
        dispute = await service.submit_dispute(req)
        return dispute
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/disputes/{dispute_id}", response_model=DisputeRecord)
async def get_dispute_by_id(
    dispute_id: str,
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Fetch dispute details by ID."""
    dispute = await repo.get_dispute(dispute_id)
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dispute '{dispute_id}' not found.")
    return dispute


@router.post("/disputes/{dispute_id}/decision", response_model=DisputeRecord)
async def decide_dispute(
    dispute_id: str,
    req: DisputeDecisionRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Render a formal decision on an open dispute ('UPHELD' or 'DISMISSED')."""
    try:
        dispute = await service.resolve_dispute(dispute_id, req)
        return dispute
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# Revocations Endpoints
# -----------------------------------------------------------------------------

@router.post("/revocations", response_model=RevocationRecord)
async def submit_revocation(
    req: SubmitRevocationRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Revoke a previously confirmed report upon verification."""
    try:
        revocation = await service.submit_revocation(req)
        return revocation
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# Feedback & Statistics Endpoints
# -----------------------------------------------------------------------------

@router.post("/feedback")
async def log_feedback(
    req: RegistryFeedbackRequest,
    service: SmartRegistryService = Depends(get_smart_registry_service),
):
    """Submit post-screening outcome feedback (true positive / false positive)."""
    try:
        res = await service.log_feedback(req)
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/statistics", response_model=RegistryStatistics)
async def get_registry_statistics(
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Retrieve live aggregate statistics and operational health of the Smart Registry."""
    return await repo.get_statistics()


@router.get("/audit-events", response_model=List[AuditEvent])
async def list_audit_events(
    limit: int = Query(100, ge=1, le=500),
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Retrieve immutable audit ledger stream."""
    return await repo.list_all_audit_events(limit=limit)


@router.get("/review-queue", response_model=List[RegistryReport])
async def get_review_queue(
    status_filter: Optional[ReportStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RegistryRepository = Depends(get_registry_repository),
):
    """Retrieve reports queue with optional status filtering."""
    return await repo.list_reports(status=status_filter, limit=limit, offset=offset)
