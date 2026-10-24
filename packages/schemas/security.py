"""Canonical Security, Identity, RBAC, Evidence Security & Governance Schemas (Prompt 21 / Phase 7A)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.enterprise import DataContributionPolicy


# -----------------------------------------------------------------------------
# 1. Identity & Principal Types
# -----------------------------------------------------------------------------

class PrincipalType(str, Enum):
    """Categorized principal class invoking an action."""
    ANONYMOUS = "ANONYMOUS"
    CONSUMER_USER = "CONSUMER_USER"
    ENTERPRISE_USER = "ENTERPRISE_USER"
    SCAMGRAPH_ANALYST = "SCAMGRAPH_ANALYST"
    SCAMGRAPH_ADMIN = "SCAMGRAPH_ADMIN"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    API_CLIENT = "API_CLIENT"


class RoleType(str, Enum):
    """Role-based authorization tiers."""
    CONSUMER = "CONSUMER"
    ORG_VIEWER = "ORG_VIEWER"
    ORG_ANALYST = "ORG_ANALYST"
    ORG_ADMIN = "ORG_ADMIN"
    SCAMGRAPH_ANALYST = "SCAMGRAPH_ANALYST"
    SCAMGRAPH_SENIOR_ANALYST = "SCAMGRAPH_SENIOR_ANALYST"
    SCAMGRAPH_ADMIN = "SCAMGRAPH_ADMIN"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    ANONYMOUS = "ANONYMOUS"


class Permission(str, Enum):
    """Granular action permissions evaluated by AuthorizationService."""
    INCIDENT_READ_OWN = "incident:read_own"
    INCIDENT_READ_ORG = "incident:read_org"
    INCIDENT_REVIEW = "incident:review"
    CAMPAIGN_READ = "campaign:read"
    CAMPAIGN_REVIEW = "campaign:review"
    ENTITY_READ = "entity:read"
    GRAPH_READ = "graph:read"
    EVIDENCE_READ_DERIVED = "evidence:read_derived"
    EVIDENCE_READ_RAW = "evidence:read_raw"
    EVIDENCE_EXPORT = "evidence:export"
    CASE_READ_OWN = "case:read_own"
    CASE_READ_ORG = "case:read_org"
    CASE_WRITE = "case:write"
    REVIEW_WRITE = "review:write"
    ALERT_READ = "alert:read"
    API_KEY_MANAGE = "api_key:manage"
    WEBHOOK_MANAGE = "webhook:manage"
    ORGANIZATION_MANAGE = "organization:manage"
    AUDIT_READ = "audit:read"
    ADMIN_SYSTEM = "admin:system"


class PrincipalContext(BaseModel):
    """Canonical security principal abstraction bound to every request."""
    principal_id: str = Field(default_factory=lambda: generate_id("prn"))
    principal_type: PrincipalType = Field(default=PrincipalType.ANONYMOUS)
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    roles: List[RoleType] = Field(default_factory=lambda: [RoleType.ANONYMOUS])
    permissions: List[Permission] = Field(default_factory=list)
    auth_method: str = Field(default="ANONYMOUS", description="SESSION_TOKEN, API_KEY, BEARER_JWT, ANONYMOUS")
    session_id: Optional[str] = None
    credential_id: Optional[str] = None
    ip_address: Optional[str] = None
    is_authenticated: bool = False
    security_context: Dict[str, Any] = Field(default_factory=dict)

    def has_permission(self, perm: Permission) -> bool:
        """Evaluates if this principal holds the requested permission."""
        return perm in self.permissions or Permission.ADMIN_SYSTEM in self.permissions

    def has_role(self, role: RoleType) -> bool:
        """Evaluates if this principal holds the requested role."""
        return role in self.roles or RoleType.SCAMGRAPH_ADMIN in self.roles


# -----------------------------------------------------------------------------
# 2. User & Session Models
# -----------------------------------------------------------------------------

class User(BaseModel):
    """Persistent consumer, enterprise, or internal identity."""
    user_id: str = Field(default_factory=lambda: generate_id("usr"))
    email: str
    hashed_password: str
    salt: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None


class UserSession(BaseModel):
    """Server-side browser session tracking with rotation & revocation support."""
    session_id: str = Field(default_factory=lambda: generate_id("sess"))
    user_id: str
    token_hash: str
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# -----------------------------------------------------------------------------
# 3. Enterprise Organization & Memberships
# -----------------------------------------------------------------------------

class OrganizationMembership(BaseModel):
    """Enforceable tenant boundary linking users to organizations with roles."""
    membership_id: str = Field(default_factory=lambda: generate_id("mem"))
    org_id: str
    user_id: str
    role: RoleType = Field(default=RoleType.ORG_ANALYST)
    status: str = Field(default="ACTIVE", description="ACTIVE, SUSPENDED, INVITED")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# -----------------------------------------------------------------------------
# 4. Evidence Classification & Secure Access
# -----------------------------------------------------------------------------

class EvidenceSensitivityClass(str, Enum):
    """Explicit sensitivity class governing evidence access."""
    PUBLIC = "PUBLIC"              # Whitelisted domain, official bank IFSC, verified portal
    INTERNAL = "INTERNAL"          # System detector telemetry, normalized tags
    CONFIDENTIAL = "CONFIDENTIAL"  # Redacted chat snippet, masked VPA/phone
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE" # Unmasked chat transcript, payment screenshot, voice audio
    RESTRICTED = "RESTRICTED"      # Identity documents (Aadhaar/PAN), raw banking credentials, OTPs


class EvidenceAccessEvaluation(BaseModel):
    """Decision output determining if principal can access raw vs derived evidence."""
    can_access_derived: bool
    can_access_raw_media: bool
    requires_redaction: bool
    explanation: str
    sensitivity_class: EvidenceSensitivityClass


# -----------------------------------------------------------------------------
# 5. Export Security & Controlled Jobs
# -----------------------------------------------------------------------------

class ExportJobStatus(str, Enum):
    """Lifecycle status of a sensitive evidence export."""
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class ExportJob(BaseModel):
    """Tracked evidence export job with expiring one-time download token."""
    export_id: str = Field(default_factory=lambda: generate_id("exp"))
    requester_id: str
    org_id: Optional[str] = None
    export_type: str = Field(default="CSV", description="CSV, JSON, PDF")
    status: ExportJobStatus = Field(default=ExportJobStatus.REQUESTED)
    download_token: str
    item_count: int = 0
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# -----------------------------------------------------------------------------
# 6. Audit Logging & Security Events
# -----------------------------------------------------------------------------

class AuditActionType(str, Enum):
    """Standardized auditable security-sensitive actions."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    ROLE_CHANGED = "ROLE_CHANGED"
    MEMBER_ADDED = "MEMBER_ADDED"
    MEMBER_REMOVED = "MEMBER_REMOVED"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"
    WEBHOOK_CREATED = "WEBHOOK_CREATED"
    WEBHOOK_UPDATED = "WEBHOOK_UPDATED"
    WEBHOOK_DELETED = "WEBHOOK_DELETED"
    EVIDENCE_VIEWED = "EVIDENCE_VIEWED"
    EVIDENCE_DOWNLOADED = "EVIDENCE_DOWNLOADED"
    EXPORT_REQUESTED = "EXPORT_REQUESTED"
    EXPORT_DOWNLOADED = "EXPORT_DOWNLOADED"
    REVIEW_DECISION = "REVIEW_DECISION"
    ENTITY_MERGE = "ENTITY_MERGE"
    ENTITY_SPLIT = "ENTITY_SPLIT"
    CAMPAIGN_MERGE = "CAMPAIGN_MERGE"
    PRIVACY_SETTING_CHANGED = "PRIVACY_SETTING_CHANGED"
    RETENTION_ACTION = "RETENTION_ACTION"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"
    ADMIN_ACTION = "ADMIN_ACTION"


class AuditEvent(BaseModel):
    """Canonical immutable audit log entry."""
    audit_id: str = Field(default_factory=lambda: generate_id("aud"))
    actor_id: str
    actor_type: str
    org_id: Optional[str] = None
    action: AuditActionType
    resource_type: str
    resource_id: str
    result: str = Field(default="SUCCESS", description="SUCCESS, DENIED, FAILED")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# 7. Consent, Retention & Entity Disputes
# -----------------------------------------------------------------------------

class ConsentPurpose(str, Enum):
    """Specific processing purposes requiring discrete user consent."""
    SCAM_ANALYSIS = "SCAM_ANALYSIS"
    EVIDENCE_STORAGE = "EVIDENCE_STORAGE"
    NETWORK_INTELLIGENCE_CONTRIBUTION = "NETWORK_INTELLIGENCE_CONTRIBUTION"
    MODEL_TRAINING = "MODEL_TRAINING"
    AUDIO_PROCESSING = "AUDIO_PROCESSING"
    CASE_EXPORT = "CASE_EXPORT"


class ConsentRecord(BaseModel):
    """Audit record capturing explicit user consent per purpose."""
    consent_id: str = Field(default_factory=lambda: generate_id("cst"))
    subject_id: str
    purpose: ConsentPurpose
    granted: bool
    policy_version: str = "v2.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DisputeStatus(str, Enum):
    """Lifecycle states of an entity misattribution dispute."""
    DISPUTED = "DISPUTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    REVERSED = "REVERSED"


class EntityDisputeRecord(BaseModel):
    """Formal audit record tracking an entity reputation dispute."""
    dispute_id: str = Field(default_factory=lambda: generate_id("dsp"))
    entity_id: str
    disputer_id: str
    status: DisputeStatus = Field(default=DisputeStatus.DISPUTED)
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
