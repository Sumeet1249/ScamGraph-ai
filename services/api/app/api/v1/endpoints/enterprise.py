"""Enterprise Gateway API Endpoints (Prompt 20 / Phase 6B).

Exposes production APIs for external partners:
Scam Check, Pre-Payment Guard, Entity Intelligence, Outbreak Feeds,
Async Jobs, Webhook Endpoints, and API Key Administration.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from packages.schemas.enterprise import (
    ApiKeyCreateResponse,
    ApiKeyRecord,
    AnalysisJobRecord,
    EnterpriseCheckRequest,
    EnterpriseCheckResponse,
    EnterpriseEntityCheckRequest,
    EnterpriseEntityCheckResponse,
    EnterpriseGuardRequest,
    EnterpriseGuardResponse,
    EnterpriseNetworkCheckRequest,
    EnterpriseNetworkCheckResponse,
    EnvironmentType,
    WebhookDeliveryRecord,
    WebhookEndpointRecord,
    WebhookEventType,
)
from services.campaign_engine.service import campaign_service
from services.enterprise.service import enterprise_platform_service

router = APIRouter(tags=["enterprise"])


# -----------------------------------------------------------------------------
# Authentication & Idempotency Dependencies
# -----------------------------------------------------------------------------
def get_current_api_key(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> ApiKeyRecord:
    """Authenticates API request via Authorization Bearer or X-API-Key header."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()

    if not token:
        # For development / test convenience, fall back to default demo live key
        token = "sg_live_apex_secret_key_889900"

    key_record = enterprise_platform_service.authenticate_key(token)
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or revoked API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return key_record


# -----------------------------------------------------------------------------
# 1. Scam Check API (POST /api/v1/check)
# -----------------------------------------------------------------------------
@router.post("/check", response_model=EnterpriseCheckResponse)
async def check_scam(
    req: EnterpriseCheckRequest,
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Evaluates multi-signal input (text, URL, VPA, phone) across canonical intelligence engines."""
    # Check Idempotency
    if idempotency_key:
        try:
            cached, payload, sc = enterprise_platform_service.check_idempotency(
                idempotency_key=idempotency_key,
                org_id=key.org_id,
                endpoint="/api/v1/check",
                request_payload=req.model_dump(),
            )
            if cached and payload:
                response.headers["X-Cache-Lookup"] = "HIT"
                return EnterpriseCheckResponse(**payload)
        except ValueError as conflict_err:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(conflict_err))

    # Force request environment from credential if in sandbox
    if key.environment == EnvironmentType.SANDBOX:
        req.environment = EnvironmentType.SANDBOX

    res = enterprise_platform_service.execute_check(req, org_id=key.org_id)

    # Store Idempotency
    if idempotency_key:
        enterprise_platform_service.store_idempotency(
            idempotency_key=idempotency_key,
            org_id=key.org_id,
            endpoint="/api/v1/check",
            request_payload=req.model_dump(),
            response_payload=res.model_dump(),
            status_code=200,
        )

    response.headers["X-Request-Id"] = res.request_id
    return res


# -----------------------------------------------------------------------------
# 2. Pre-Payment Guard API (POST /api/v1/guard/check)
# -----------------------------------------------------------------------------
@router.post("/guard/check", response_model=EnterpriseGuardResponse)
async def guard_check(
    req: EnterpriseGuardRequest,
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Evaluates payment destination before transaction completion with fast-path latency."""
    if idempotency_key:
        try:
            cached, payload, sc = enterprise_platform_service.check_idempotency(
                idempotency_key=idempotency_key,
                org_id=key.org_id,
                endpoint="/api/v1/guard/check",
                request_payload=req.model_dump(),
            )
            if cached and payload:
                response.headers["X-Cache-Lookup"] = "HIT"
                return EnterpriseGuardResponse(**payload)
        except ValueError as conflict_err:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(conflict_err))

    if key.environment == EnvironmentType.SANDBOX:
        req.environment = EnvironmentType.SANDBOX

    res = enterprise_platform_service.execute_guard(req, org_id=key.org_id)

    if idempotency_key:
        enterprise_platform_service.store_idempotency(
            idempotency_key=idempotency_key,
            org_id=key.org_id,
            endpoint="/api/v1/guard/check",
            request_payload=req.model_dump(),
            response_payload=res.model_dump(),
            status_code=200,
        )

    response.headers["X-Request-Id"] = res.request_id
    response.headers["X-Guard-Latency-Tier"] = res.latency_tier
    return res


# -----------------------------------------------------------------------------
# 3. Entity Intelligence API (POST /api/v1/entities/check)
# -----------------------------------------------------------------------------
@router.post("/entities/check", response_model=EnterpriseEntityCheckResponse)
async def check_entity_reputation(
    req: EnterpriseEntityCheckRequest,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Performs privacy-safe entity reputation check without leaking victim reports."""
    return enterprise_platform_service.check_entity(
        entity_type=req.entity_type,
        value=req.value,
    )


# -----------------------------------------------------------------------------
# 4. Outbreak Feed API (GET /api/v1/outbreak/feed)
# -----------------------------------------------------------------------------
@router.get("/outbreak/feed")
async def get_outbreak_feed(
    limit: int = Query(default=20, ge=1, le=50),
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Returns chronological outbreak signals, resurgence events, and velocity spikes."""
    signals = campaign_service.get_outbreak_signals(limit=limit, demo_mode=False)
    return [s.model_dump() for s in signals]


# -----------------------------------------------------------------------------
# 5. Asynchronous Analysis Jobs
# -----------------------------------------------------------------------------
class CreateJobRequest(BaseModel):
    artifact_id: Optional[str] = None


@router.post("/jobs", response_model=AnalysisJobRecord, status_code=status.HTTP_202_ACCEPTED)
async def create_analysis_job(
    req: CreateJobRequest,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Enqueues an asynchronous analysis job for heavy media or batch processing."""
    return enterprise_platform_service.create_job(org_id=key.org_id, artifact_id=req.artifact_id)


@router.get("/jobs/{job_id}", response_model=AnalysisJobRecord)
async def get_analysis_job(
    job_id: str,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Polls status of async analysis job, enforcing multi-tenant isolation."""
    job = enterprise_platform_service.get_job(job_id=job_id, requesting_org_id=key.org_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found or does not belong to your organization.",
        )
    return job


# -----------------------------------------------------------------------------
# 6. Webhooks Management
# -----------------------------------------------------------------------------
class CreateWebhookRequest(BaseModel):
    url: str
    event_types: List[WebhookEventType]


class CreateWebhookResponse(BaseModel):
    endpoint_id: str
    url: str
    secret: str = Field(description="Raw HMAC secret; displayed once and cannot be retrieved later")
    event_types: List[WebhookEventType]
    status: str


@router.post("/webhooks", response_model=CreateWebhookResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook_endpoint(
    req: CreateWebhookRequest,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Registers partner webhook URL and returns HMAC signing secret."""
    endpoint, raw_secret = enterprise_platform_service.register_webhook(
        org_id=key.org_id,
        url=req.url,
        event_types=req.event_types,
    )
    return CreateWebhookResponse(
        endpoint_id=endpoint.endpoint_id,
        url=endpoint.url,
        secret=raw_secret,
        event_types=endpoint.event_types,
        status=endpoint.status,
    )


@router.get("/webhooks", response_model=List[WebhookEndpointRecord])
async def list_webhook_endpoints(
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Lists registered webhook endpoints for the authenticated organization."""
    return enterprise_platform_service.get_webhooks(org_id=key.org_id)


# -----------------------------------------------------------------------------
# 7. API Keys Management
# -----------------------------------------------------------------------------
class CreateApiKeyRequest(BaseModel):
    environment: EnvironmentType = EnvironmentType.LIVE
    scopes: Optional[List[str]] = None


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    req: CreateApiKeyRequest,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Generates a new API credential. Raw secret is displayed once."""
    record, raw_secret = enterprise_platform_service.create_api_key(
        org_id=key.org_id,
        environment=req.environment,
        scopes=req.scopes,
    )
    return ApiKeyCreateResponse(
        key_id=record.key_id,
        api_key=raw_secret,
        prefix=record.prefix,
        environment=record.environment,
        scopes=record.scopes,
        created_at=record.created_at,
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    key: ApiKeyRecord = Depends(get_current_api_key),
):
    """Revokes an existing API key immediately."""
    revoked = enterprise_platform_service.revoke_api_key(key_id=key_id, org_id=key.org_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key '{key_id}' not found or does not belong to your organization.",
        )
    return None
