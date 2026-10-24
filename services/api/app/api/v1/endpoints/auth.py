"""Authentication, Principal Resolution, Consent, Exports & Audit Endpoints (Prompt 21 / Phase 7A)."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from packages.schemas.security import (
    AuditActionType,
    AuditEvent,
    ConsentPurpose,
    ConsentRecord,
    DisputeStatus,
    EntityDisputeRecord,
    ExportJob,
    Permission,
    PrincipalContext,
    RoleType,
)
from services.security.service import security_service

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------------------------------------------------------
# Request & Response Contracts
# -----------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    session_token: str
    expires_at: str
    user_id: str
    email: str
    roles: List[str]


class ConsentSubmission(BaseModel):
    purpose: ConsentPurpose
    granted: bool


class ExportRequest(BaseModel):
    export_type: str = "CSV"
    records: List[Dict[str, Any]] = Field(default_factory=list)


class DisputeSubmission(BaseModel):
    entity_id: str
    reason: str


# -----------------------------------------------------------------------------
# Dependency: Resolve Principal Context
# -----------------------------------------------------------------------------

def get_current_principal(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    session_cookie: Optional[str] = Cookie(None, alias="scamgraph_session"),
) -> PrincipalContext:
    """FastAPI dependency resolving credentials into an authenticated PrincipalContext."""
    bearer_token = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()

    client_ip = request.client.host if request.client else None

    principal = security_service.resolve_principal(
        session_token=session_cookie,
        api_key=x_api_key,
        bearer_token=bearer_token,
        ip_address=client_ip,
    )
    return principal


def require_permission(perm: Permission):
    """Factory dependency enforcing a specific required permission."""
    def dependency(principal: PrincipalContext = Depends(get_current_principal)):
        if not principal.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for this resource.",
            )
        if not principal.has_permission(perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Principal lacks required permission '{perm.value}'.",
            )
        return principal
    return dependency


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    """Registers a new consumer user account with salted adaptive password hashing."""
    try:
        user = security_service.register_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            phone=req.phone,
        )
        return {
            "status": "registered",
            "user_id": user.user_id,
            "email": user.email,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, request: Request, response: Response):
    """Authenticates credentials, returning session token and setting HttpOnly cookie."""
    client_ip = request.client.host if request.client else None
    try:
        session, raw_token = security_service.authenticate_user(
            email=req.email,
            password=req.password,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
        )
        if not session or not raw_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Set secure HttpOnly session cookie
        response.set_cookie(
            key="scamgraph_session",
            value=raw_token,
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in HTTPS production
            max_age=86400,
        )

        user = security_service._users[session.user_id]
        mems = security_service._user_memberships.get(user.user_id, [])
        roles = [security_service._memberships[m].role.value for m in mems] or ["CONSUMER"]

        return LoginResponse(
            session_id=session.session_id,
            session_token=raw_token,
            expires_at=session.expires_at.isoformat(),
            user_id=user.user_id,
            email=user.email,
            roles=roles,
        )
    except ValueError as e:
        # Throttling error
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))


@router.post("/logout")
def logout(response: Response, principal: PrincipalContext = Depends(get_current_principal)):
    """Logs out and revokes active session."""
    if principal.session_id:
        security_service.revoke_session(principal.session_id, actor_id=principal.principal_id)
    response.delete_cookie(key="scamgraph_session")
    return {"status": "logged_out"}


@router.get("/me")
def get_me(principal: PrincipalContext = Depends(get_current_principal)):
    """Returns authenticated caller's security principal context."""
    return {
        "principal_id": principal.principal_id,
        "principal_type": principal.principal_type.value,
        "user_id": principal.user_id,
        "organization_id": principal.organization_id,
        "roles": [r.value for r in principal.roles],
        "permissions": [p.value for p in principal.permissions],
        "auth_method": principal.auth_method,
        "is_authenticated": principal.is_authenticated,
    }


@router.post("/consent")
def submit_consent(
    req: ConsentSubmission,
    principal: PrincipalContext = Depends(get_current_principal),
):
    """Submits explicit consent. Distinguishes analysis, storage, and model training."""
    if not principal.is_authenticated or not principal.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    rec = security_service.record_consent(
        subject_id=principal.user_id,
        purpose=req.purpose,
        granted=req.granted,
        actor_id=principal.principal_id,
    )
    return {
        "consent_id": rec.consent_id,
        "purpose": rec.purpose.value,
        "granted": rec.granted,
        "timestamp": rec.timestamp.isoformat(),
    }


@router.post("/exports")
def create_export(
    req: ExportRequest,
    principal: PrincipalContext = Depends(require_permission(Permission.EVIDENCE_EXPORT)),
):
    """Generates a controlled export job with formula injection sanitization."""
    job = security_service.create_export_job(
        principal=principal,
        export_type=req.export_type,
        records=req.records,
    )
    return {
        "export_id": job.export_id,
        "status": job.status.value,
        "download_token": job.download_token,
        "expires_at": job.expires_at.isoformat(),
        "item_count": job.item_count,
    }


@router.get("/exports/{token}")
def download_export(
    token: str,
    principal: PrincipalContext = Depends(get_current_principal),
):
    """Downloads sanitized export file enforcing 15-minute token TTL and tenant boundary."""
    try:
        job, data = security_service.download_export(token, principal)
        return Response(
            content=data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=scamgraph_export_{job.export_id}.csv"},
        )
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/audit", response_model=List[AuditEvent])
def query_audit_log(
    action: Optional[AuditActionType] = None,
    limit: int = 50,
    principal: PrincipalContext = Depends(require_permission(Permission.AUDIT_READ)),
):
    """Queries immutable audit trail enforcing tenant isolation."""
    return security_service.query_audit_log(principal=principal, action=action, limit=limit)


@router.post("/disputes")
def submit_dispute(
    req: DisputeSubmission,
    principal: PrincipalContext = Depends(get_current_principal),
):
    """Submits a formal entity reputation dispute."""
    dispute = security_service.submit_entity_dispute(
        principal=principal,
        entity_id=req.entity_id,
        reason=req.reason,
    )
    return {
        "dispute_id": dispute.dispute_id,
        "entity_id": dispute.entity_id,
        "status": dispute.status.value,
    }
