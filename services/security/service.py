"""Centralized Identity, RBAC, Tenant Isolation & Evidence Security Service for ScamGraph AI V2 (Prompt 21 / Phase 7A).

Implements:
1. Canonical PrincipalContext resolution (Human & Machine)
2. PBKDF2-HMAC adaptive password hashing & session management
3. Enterprise Organization & Membership management
4. Centralized Role-Based Access Control (RBAC) & Permissions
5. Resource-level authorization & Insecure Direct Object Reference (IDOR) defense
6. Evidence sensitivity classification & Derived vs. Raw Media access evaluation
7. Controlled evidence export jobs with CSV Formula Injection sanitization
8. Immutable security audit logging with redacted metadata
9. Consent management (separating analysis, storage, and model training)
10. Cascade intelligence invalidation upon evidence deletion
11. Entity dispute & reputation reversal lifecycle
12. Multi-dimensional rate limiting & brute-force throttling
"""

from __future__ import annotations

import csv
import hashlib
import io
import logging
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from packages.schemas.common import generate_id
from packages.schemas.enterprise import DataContributionPolicy, EnterpriseOrganization, EnvironmentType
from packages.schemas.security import (
    AuditActionType,
    AuditEvent,
    ConsentPurpose,
    ConsentRecord,
    DisputeStatus,
    EntityDisputeRecord,
    EvidenceAccessEvaluation,
    EvidenceSensitivityClass,
    ExportJob,
    ExportJobStatus,
    OrganizationMembership,
    Permission,
    PrincipalContext,
    PrincipalType,
    RoleType,
    User,
    UserSession,
)

logger = logging.getLogger("scamgraph.security.service")


# -----------------------------------------------------------------------------
# Canonical Role-to-Permissions Mapping
# -----------------------------------------------------------------------------

ROLE_PERMISSIONS_MAP: Dict[RoleType, Set[Permission]] = {
    RoleType.ANONYMOUS: set(),
    RoleType.CONSUMER: {
        Permission.INCIDENT_READ_OWN,
        Permission.CASE_READ_OWN,
        Permission.EVIDENCE_READ_DERIVED,
    },
    RoleType.ORG_VIEWER: {
        Permission.INCIDENT_READ_ORG,
        Permission.CASE_READ_ORG,
        Permission.CAMPAIGN_READ,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.ALERT_READ,
    },
    RoleType.ORG_ANALYST: {
        Permission.INCIDENT_READ_ORG,
        Permission.CASE_READ_ORG,
        Permission.CASE_WRITE,
        Permission.REVIEW_WRITE,
        Permission.CAMPAIGN_READ,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.EVIDENCE_READ_RAW,  # Org-scoped raw evidence
        Permission.ALERT_READ,
    },
    RoleType.ORG_ADMIN: {
        Permission.INCIDENT_READ_ORG,
        Permission.CASE_READ_ORG,
        Permission.CASE_WRITE,
        Permission.REVIEW_WRITE,
        Permission.CAMPAIGN_READ,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.EVIDENCE_READ_RAW,
        Permission.EVIDENCE_EXPORT,
        Permission.API_KEY_MANAGE,
        Permission.WEBHOOK_MANAGE,
        Permission.ORGANIZATION_MANAGE,
        Permission.AUDIT_READ,
        Permission.ALERT_READ,
    },
    RoleType.SCAMGRAPH_ANALYST: {
        Permission.INCIDENT_REVIEW,
        Permission.CAMPAIGN_READ,
        Permission.CAMPAIGN_REVIEW,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.CASE_READ_ORG,
        Permission.CASE_WRITE,
        Permission.REVIEW_WRITE,
        Permission.ALERT_READ,
        Permission.AUDIT_READ,
    },
    RoleType.SCAMGRAPH_SENIOR_ANALYST: {
        Permission.INCIDENT_REVIEW,
        Permission.CAMPAIGN_READ,
        Permission.CAMPAIGN_REVIEW,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.EVIDENCE_READ_RAW,  # Cross-tenant investigative access
        Permission.EVIDENCE_EXPORT,
        Permission.CASE_READ_ORG,
        Permission.CASE_WRITE,
        Permission.REVIEW_WRITE,
        Permission.ALERT_READ,
        Permission.AUDIT_READ,
    },
    RoleType.SCAMGRAPH_ADMIN: {
        Permission.INCIDENT_READ_OWN,
        Permission.INCIDENT_READ_ORG,
        Permission.INCIDENT_REVIEW,
        Permission.CAMPAIGN_READ,
        Permission.CAMPAIGN_REVIEW,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.EVIDENCE_READ_RAW,
        Permission.EVIDENCE_EXPORT,
        Permission.CASE_READ_OWN,
        Permission.CASE_READ_ORG,
        Permission.CASE_WRITE,
        Permission.REVIEW_WRITE,
        Permission.ALERT_READ,
        Permission.API_KEY_MANAGE,
        Permission.WEBHOOK_MANAGE,
        Permission.ORGANIZATION_MANAGE,
        Permission.AUDIT_READ,
        Permission.ADMIN_SYSTEM,
    },
    RoleType.SERVICE_ACCOUNT: {
        Permission.INCIDENT_READ_ORG,
        Permission.ENTITY_READ,
        Permission.GRAPH_READ,
        Permission.EVIDENCE_READ_DERIVED,
        Permission.ALERT_READ,
    },
}


class SecurityService:
    """Core enterprise identity, RBAC, tenant isolation, and evidence protection service."""

    def __init__(self):
        # Repositories / In-memory data structures
        self._users: Dict[str, User] = {}                         # user_id -> User
        self._user_email_index: Dict[str, str] = {}               # email.lower() -> user_id
        self._sessions: Dict[str, UserSession] = {}               # session_id -> UserSession
        self._token_to_session: Dict[str, str] = {}               # hashed_token -> session_id
        
        self._organizations: Dict[str, EnterpriseOrganization] = {} # org_id -> Organization
        self._memberships: Dict[str, OrganizationMembership] = {} # membership_id -> Membership
        self._user_memberships: Dict[str, List[str]] = {}         # user_id -> [membership_id]
        self._org_memberships: Dict[str, List[str]] = {}          # org_id -> [membership_id]

        self._export_jobs: Dict[str, ExportJob] = {}              # export_id -> ExportJob
        self._export_tokens: Dict[str, str] = {}                  # download_token -> export_id
        self._export_data: Dict[str, str] = {}                    # export_id -> sanitized_csv_string

        self._audit_log: List[AuditEvent] = []                    # Immutable chronological audit log
        self._consents: Dict[str, Dict[ConsentPurpose, ConsentRecord]] = {} # subject_id -> {purpose: ConsentRecord}
        self._disputes: Dict[str, EntityDisputeRecord] = {}       # dispute_id -> EntityDisputeRecord

        # Rate limiting & brute force tracking
        self._rate_limits: Dict[str, List[float]] = {}            # key -> list of timestamps
        self._failed_logins: Dict[str, List[float]] = {}          # identifier -> list of failed timestamps

        # Initialize standard test principals & seed organizations
        self._init_defaults()

    def _init_defaults(self):
        """Seeds default organizations and admin/analyst users for verification."""
        # 1. Demo Enterprise Organization A (Bank)
        org_a = EnterpriseOrganization(
            org_id="org_alpha_bank",
            name="Alpha Federal Bank",
            status="ACTIVE",
            data_contribution_policy=DataContributionPolicy.NETWORK_INTELLIGENCE_ALLOWED,
        )
        self._organizations[org_a.org_id] = org_a

        # 2. Demo Enterprise Organization B (Fintech / Competitor)
        org_b = EnterpriseOrganization(
            org_id="org_beta_fintech",
            name="Beta FastPay UPI",
            status="ACTIVE",
            data_contribution_policy=DataContributionPolicy.PRIVATE_ONLY,
        )
        self._organizations[org_b.org_id] = org_b

        # 3. Seed Consumer User
        self.register_user(
            email="victim.consumer@example.com",
            password="ConsumerPass#123",
            full_name="Rajesh Sharma",
            user_id="usr_consumer_rajesh",
        )

        # 4. Seed Org A Analyst
        u_analyst = self.register_user(
            email="analyst@alphabank.com",
            password="BankAnalyst#999",
            full_name="Pooja Mehta",
            user_id="usr_analyst_pooja",
        )
        self.add_organization_member(
            org_id=org_a.org_id,
            user_id=u_analyst.user_id,
            role=RoleType.ORG_ANALYST,
        )

        # 5. Seed ScamGraph Senior Analyst
        u_sg_analyst = self.register_user(
            email="lead.investigator@scamgraph.ai",
            password="LeadInvestigator#456",
            full_name="Vikramaditya Rao",
            user_id="usr_sg_analyst_vikram",
        )
        # Assign global senior analyst role
        self.add_organization_member(
            org_id="org_scamgraph_internal",
            user_id=u_sg_analyst.user_id,
            role=RoleType.SCAMGRAPH_SENIOR_ANALYST,
        )

        # 6. Seed ScamGraph System Admin
        u_admin = self.register_user(
            email="security.admin@scamgraph.ai",
            password="SuperAdmin#Secret987",
            full_name="Root Security Administrator",
            user_id="usr_admin_root",
        )
        self.add_organization_member(
            org_id="org_scamgraph_internal",
            user_id=u_admin.user_id,
            role=RoleType.SCAMGRAPH_ADMIN,
        )

    # -------------------------------------------------------------------------
    # 1. Identity & Password Security (PBKDF2-HMAC Adaptive Hashing)
    # -------------------------------------------------------------------------

    def _hash_password(self, password: str, salt: str) -> str:
        """Computes secure adaptive PBKDF2-HMAC-SHA256 with 100,000 iterations."""
        pwd_bytes = password.encode("utf-8")
        salt_bytes = bytes.fromhex(salt)
        derived = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, 100_000)
        return derived.hex()

    def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> User:
        """Registers a new identity with salted adaptive password hashing."""
        clean_email = email.strip().lower()
        if clean_email in self._user_email_index:
            raise ValueError(f"User with email '{clean_email}' already exists.")

        salt = secrets.token_hex(16)
        hashed_pwd = self._hash_password(password, salt)

        uid = user_id or generate_id("usr")
        user = User(
            user_id=uid,
            email=clean_email,
            hashed_password=hashed_pwd,
            salt=salt,
            full_name=full_name,
            phone=phone,
            is_active=True,
            is_verified=True,
        )

        self._users[user.user_id] = user
        self._user_email_index[clean_email] = user.user_id
        self._user_memberships[user.user_id] = []

        self.record_audit_event(
            actor_id=user.user_id,
            actor_type="CONSUMER_USER",
            action=AuditActionType.MEMBER_ADDED,
            resource_type="User",
            resource_id=user.user_id,
            details={"email": clean_email, "full_name": full_name},
        )
        return user

    def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Optional[UserSession], Optional[str]]:
        """Authenticates user with brute-force defense, returning session and raw token."""
        clean_email = email.strip().lower()
        now = time.time()

        # Check brute force throttling (max 5 failed attempts in 5 minutes)
        attempts = self._failed_logins.get(clean_email, [])
        recent_failures = [t for t in attempts if now - t < 300]
        if len(recent_failures) >= 5:
            self.record_audit_event(
                actor_id=clean_email,
                actor_type="UNAUTHENTICATED",
                action=AuditActionType.LOGIN_FAILURE,
                resource_type="UserSession",
                resource_id="none",
                result="DENIED",
                ip_address=ip_address,
                details={"reason": "BRUTE_FORCE_THROTTLED"},
            )
            raise ValueError("Too many failed login attempts. Please wait 5 minutes before retrying.")

        user_id = self._user_email_index.get(clean_email)
        if not user_id:
            self._failed_logins.setdefault(clean_email, []).append(now)
            return None, None

        user = self._users.get(user_id)
        if not user or not user.is_active:
            return None, None

        computed_hash = self._hash_password(password, user.salt)
        if not secrets.compare_digest(computed_hash, user.hashed_password):
            self._failed_logins.setdefault(clean_email, []).append(now)
            self.record_audit_event(
                actor_id=user.user_id,
                actor_type="User",
                action=AuditActionType.LOGIN_FAILURE,
                resource_type="UserSession",
                resource_id=user.user_id,
                result="FAILED",
                ip_address=ip_address,
                details={"reason": "INVALID_PASSWORD"},
            )
            return None, None

        # Reset failed login counter on success
        self._failed_logins.pop(clean_email, None)

        # Generate secure random session token (token displayed/issued once)
        raw_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        session = UserSession(
            user_id=user.user_id,
            token_hash=hashed_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self._sessions[session.session_id] = session
        self._token_to_session[hashed_token] = session.session_id
        user.last_login_at = datetime.now(timezone.utc)

        self.record_audit_event(
            actor_id=user.user_id,
            actor_type="User",
            action=AuditActionType.LOGIN,
            resource_type="UserSession",
            resource_id=session.session_id,
            ip_address=ip_address,
            details={"session_id": session.session_id},
        )

        return session, raw_token

    def revoke_session(self, session_id: str, actor_id: Optional[str] = None) -> bool:
        """Revokes an active session immediately."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.is_revoked = True
        self._token_to_session.pop(session.token_hash, None)

        self.record_audit_event(
            actor_id=actor_id or session.user_id,
            actor_type="User",
            action=AuditActionType.LOGOUT,
            resource_type="UserSession",
            resource_id=session_id,
            details={"revoked": True},
        )
        return True

    # -------------------------------------------------------------------------
    # 2. Enterprise Organization & Membership Management
    # -------------------------------------------------------------------------

    def create_organization(
        self,
        name: str,
        policy: DataContributionPolicy = DataContributionPolicy.NETWORK_INTELLIGENCE_ALLOWED,
        actor_id: Optional[str] = None,
    ) -> EnterpriseOrganization:
        """Creates an enterprise organization boundary."""
        org = EnterpriseOrganization(
            name=name,
            data_contribution_policy=policy,
        )
        self._organizations[org.org_id] = org
        self._org_memberships[org.org_id] = []

        self.record_audit_event(
            actor_id=actor_id or "system",
            actor_type="ADMIN",
            action=AuditActionType.ADMIN_ACTION,
            resource_type="EnterpriseOrganization",
            resource_id=org.org_id,
            details={"name": name, "policy": policy.value},
        )
        return org

    def add_organization_member(
        self,
        org_id: str,
        user_id: str,
        role: RoleType = RoleType.ORG_ANALYST,
        actor_id: Optional[str] = None,
    ) -> OrganizationMembership:
        """Binds a user to an organization with a specific RBAC role."""
        if org_id not in self._organizations and org_id != "org_scamgraph_internal":
            raise ValueError(f"Organization '{org_id}' not found.")
        if user_id not in self._users:
            raise ValueError(f"User '{user_id}' not found.")

        membership = OrganizationMembership(
            org_id=org_id,
            user_id=user_id,
            role=role,
            status="ACTIVE",
        )
        self._memberships[membership.membership_id] = membership
        self._user_memberships.setdefault(user_id, []).append(membership.membership_id)
        self._org_memberships.setdefault(org_id, []).append(membership.membership_id)

        self.record_audit_event(
            actor_id=actor_id or "system",
            actor_type="ADMIN",
            action=AuditActionType.MEMBER_ADDED,
            resource_type="OrganizationMembership",
            resource_id=membership.membership_id,
            org_id=org_id,
            details={"user_id": user_id, "role": role.value},
        )
        return membership

    def remove_organization_member(
        self,
        org_id: str,
        user_id: str,
        actor_id: Optional[str] = None,
    ) -> bool:
        """Removes a user's membership from an organization."""
        m_ids = self._user_memberships.get(user_id, [])
        target_m_id = None
        for mid in m_ids:
            mem = self._memberships.get(mid)
            if mem and mem.org_id == org_id:
                target_m_id = mid
                break

        if not target_m_id:
            return False

        self._memberships.pop(target_m_id, None)
        self._user_memberships[user_id].remove(target_m_id)
        if target_m_id in self._org_memberships.get(org_id, []):
            self._org_memberships[org_id].remove(target_m_id)

        self.record_audit_event(
            actor_id=actor_id or "system",
            actor_type="ADMIN",
            action=AuditActionType.MEMBER_REMOVED,
            resource_type="OrganizationMembership",
            resource_id=target_m_id,
            org_id=org_id,
            details={"user_id": user_id},
        )
        return True

    # -------------------------------------------------------------------------
    # 3. Canonical PrincipalContext Resolution (Human vs. Machine)
    # -------------------------------------------------------------------------

    def resolve_principal(
        self,
        session_token: Optional[str] = None,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> PrincipalContext:
        """Resolves request credentials into an immutable, authenticated PrincipalContext."""
        # 1. Machine API Client Resolution (via Prompt 20 API Key)
        if api_key and api_key.strip():
            from services.enterprise.service import enterprise_platform_service
            auth_rec = enterprise_platform_service.authenticate_key(api_key.strip())
            if auth_rec:
                perms: List[Permission] = []
                for s in auth_rec.scopes:
                    if s == "check:write":
                        perms.extend([Permission.INCIDENT_READ_ORG, Permission.CASE_READ_ORG])
                    elif s == "guard:write":
                        perms.extend([Permission.INCIDENT_READ_ORG, Permission.ENTITY_READ])
                    elif s == "entity:read":
                        perms.append(Permission.ENTITY_READ)
                    elif s == "campaign:read":
                        perms.append(Permission.CAMPAIGN_READ)
                    elif s == "webhook:manage":
                        perms.append(Permission.WEBHOOK_MANAGE)

                return PrincipalContext(
                    principal_id=auth_rec.key_id,
                    principal_type=PrincipalType.API_CLIENT,
                    organization_id=auth_rec.org_id,
                    roles=[RoleType.ORG_ANALYST],
                    permissions=perms,
                    auth_method="API_KEY",
                    credential_id=auth_rec.key_id,
                    ip_address=ip_address,
                    is_authenticated=True,
                )

        # 2. Human Session Token Resolution (Browser Cookie / Header)
        raw_token = session_token or bearer_token
        if raw_token and raw_token.strip():
            hashed_token = hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()
            session_id = self._token_to_session.get(hashed_token)
            if session_id:
                session = self._sessions.get(session_id)
                if session and not session.is_revoked and session.expires_at > datetime.now(timezone.utc):
                    user = self._users.get(session.user_id)
                    if user and user.is_active:
                        # Collect user's roles & permissions across memberships
                        mem_ids = self._user_memberships.get(user.user_id, [])
                        roles: List[RoleType] = []
                        perms: Set[Permission] = set()
                        active_org_id: Optional[str] = None

                        for mid in mem_ids:
                            mem = self._memberships.get(mid)
                            if mem and mem.status == "ACTIVE":
                                roles.append(mem.role)
                                perms.update(ROLE_PERMISSIONS_MAP.get(mem.role, set()))
                                if not active_org_id:
                                    active_org_id = mem.org_id

                        # Default consumer role if no explicit org membership
                        if not roles:
                            roles = [RoleType.CONSUMER]
                            perms.update(ROLE_PERMISSIONS_MAP[RoleType.CONSUMER])

                        # Determine principal type
                        if RoleType.SCAMGRAPH_ADMIN in roles:
                            ptype = PrincipalType.SCAMGRAPH_ADMIN
                        elif RoleType.SCAMGRAPH_ANALYST in roles or RoleType.SCAMGRAPH_SENIOR_ANALYST in roles:
                            ptype = PrincipalType.SCAMGRAPH_ANALYST
                        elif any(r in (RoleType.ORG_ADMIN, RoleType.ORG_ANALYST, RoleType.ORG_VIEWER) for r in roles):
                            ptype = PrincipalType.ENTERPRISE_USER
                        else:
                            ptype = PrincipalType.CONSUMER_USER

                        return PrincipalContext(
                            principal_id=user.user_id,
                            principal_type=ptype,
                            user_id=user.user_id,
                            organization_id=active_org_id,
                            roles=roles,
                            permissions=list(perms),
                            auth_method="SESSION_TOKEN",
                            session_id=session.session_id,
                            ip_address=ip_address,
                            is_authenticated=True,
                        )

        # 3. Anonymous Fallback (for public unauthenticated Protect checks)
        return PrincipalContext(
            principal_id="anon_" + secrets.token_hex(6),
            principal_type=PrincipalType.ANONYMOUS,
            roles=[RoleType.ANONYMOUS],
            permissions=[],
            auth_method="ANONYMOUS",
            ip_address=ip_address,
            is_authenticated=False,
        )

    # -------------------------------------------------------------------------
    # 4. Central Authorization & Resource-Level IDOR Defense
    # -------------------------------------------------------------------------

    def authorize(
        self,
        principal: PrincipalContext,
        permission: Permission,
        resource: Optional[Any] = None,
    ) -> bool:
        """Evaluates centralized RBAC permissions and enforces strict resource boundary checks."""
        # 1. Base permission check
        if not principal.has_permission(permission):
            return False

        # 2. System Admins bypass resource ownership checks
        if principal.has_role(RoleType.SCAMGRAPH_ADMIN) or Permission.ADMIN_SYSTEM in principal.permissions:
            return True

        # 3. Resource Ownership & Tenant Isolation Enforcement (IDOR Protection)
        if resource is not None:
            # Check Consumer Ownership (e.g. incident, rescue case)
            resource_owner = getattr(resource, "owner_id", None) or getattr(resource, "user_id", None)
            if resource_owner and principal.user_id:
                if resource_owner != principal.user_id:
                    # If user is not the owner, only internal ScamGraph Analysts may inspect it
                    if not principal.has_role(RoleType.SCAMGRAPH_ANALYST) and not principal.has_role(RoleType.SCAMGRAPH_SENIOR_ANALYST):
                        return False

            # Check Enterprise Tenant Boundary (e.g. job, private evidence, org case)
            resource_org = getattr(resource, "org_id", None) or getattr(resource, "organization_id", None)
            if resource_org and principal.organization_id:
                if resource_org != principal.organization_id:
                    # Cross-tenant access is strictly denied; even an Org Admin cannot cross boundaries
                    if not principal.has_role(RoleType.SCAMGRAPH_ANALYST) and not principal.has_role(RoleType.SCAMGRAPH_SENIOR_ANALYST):
                        return False

            # Check Raw Media Access Authorization
            if permission == Permission.EVIDENCE_READ_RAW:
                # Consumers can only view raw media of their OWN incidents
                if principal.principal_type == PrincipalType.CONSUMER_USER:
                    return resource_owner == principal.user_id
                # Org analysts can view raw media only within their OWN organization
                if principal.principal_type == PrincipalType.ENTERPRISE_USER:
                    return resource_org == principal.organization_id
                # Normal ScamGraph Analysts do NOT have raw media permission (only Senior Analysts do)
                if RoleType.SCAMGRAPH_SENIOR_ANALYST not in principal.roles:
                    return False

        return True

    def require(
        self,
        principal: PrincipalContext,
        permission: Permission,
        resource: Optional[Any] = None,
        action_name: Optional[str] = None,
    ) -> None:
        """Enforces authorization, raising PermissionError on violation and recording an audit trail."""
        allowed = self.authorize(principal, permission, resource)
        if not allowed:
            self.record_audit_event(
                actor_id=principal.principal_id,
                actor_type=principal.principal_type.value,
                action=AuditActionType.ADMIN_ACTION,
                resource_type=type(resource).__name__ if resource else "Permission",
                resource_id=getattr(resource, "id", None) or getattr(resource, "artifact_id", None) or permission.value,
                org_id=principal.organization_id,
                result="DENIED",
                details={"permission": permission.value, "attempted_action": action_name or "access"},
            )
            raise PermissionError(f"Access Denied: Principal lacks permission '{permission.value}' for resource.")

    # -------------------------------------------------------------------------
    # 5. Evidence Sensitivity & Derived vs. Raw Media Separation
    # -------------------------------------------------------------------------

    def evaluate_evidence_access(
        self,
        principal: PrincipalContext,
        sensitivity_class: EvidenceSensitivityClass,
        resource_owner_id: Optional[str] = None,
        resource_org_id: Optional[str] = None,
    ) -> EvidenceAccessEvaluation:
        """Evaluates whether principal may access derived indicators vs. raw binary media."""
        # Derived access is broadly available to analysts and authorized viewers
        can_derived = principal.has_permission(Permission.EVIDENCE_READ_DERIVED)

        # Raw media access requires specific permission and strict ownership/role verification
        can_raw = False
        requires_redaction = False

        if principal.has_role(RoleType.SCAMGRAPH_ADMIN):
            can_raw = True
            can_derived = True
        elif principal.has_role(RoleType.SCAMGRAPH_SENIOR_ANALYST):
            can_raw = True
            can_derived = True
        elif principal.principal_type == PrincipalType.CONSUMER_USER and resource_owner_id == principal.user_id:
            can_raw = True
            can_derived = True
        elif principal.principal_type == PrincipalType.ENTERPRISE_USER and resource_org_id == principal.organization_id:
            can_raw = principal.has_permission(Permission.EVIDENCE_READ_RAW)
        elif principal.has_role(RoleType.SCAMGRAPH_ANALYST):
            # Standard analysts see derived text only; raw media is redacted
            can_raw = False
            requires_redaction = sensitivity_class in (
                EvidenceSensitivityClass.HIGHLY_SENSITIVE,
                EvidenceSensitivityClass.RESTRICTED,
            )

        explanation = "Full raw media access granted." if can_raw else (
            "Derived indicators available; raw media restricted." if can_derived else "Access denied."
        )

        return EvidenceAccessEvaluation(
            can_access_derived=can_derived,
            can_access_raw_media=can_raw,
            requires_redaction=requires_redaction,
            explanation=explanation,
            sensitivity_class=sensitivity_class,
        )

    # -------------------------------------------------------------------------
    # 6. Controlled Export Jobs & CSV Formula Injection Protection
    # -------------------------------------------------------------------------

    def create_export_job(
        self,
        principal: PrincipalContext,
        export_type: str = "CSV",
        records: Optional[List[Dict[str, Any]]] = None,
    ) -> ExportJob:
        """Generates a controlled export job with CSV formula injection sanitization."""
        self.require(principal, Permission.EVIDENCE_EXPORT, action_name="create_export_job")

        records_to_export = records or []
        token = secrets.token_urlsafe(24)

        job = ExportJob(
            requester_id=principal.principal_id,
            org_id=principal.organization_id,
            export_type=export_type.upper(),
            status=ExportJobStatus.READY,
            download_token=token,
            item_count=len(records_to_export),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            completed_at=datetime.now(timezone.utc),
        )

        # Sanitize CSV values against spreadsheet formula execution (=, +, -, @, \t, \r)
        output = io.StringIO()
        if records_to_export:
            fieldnames = list(records_to_export[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for row in records_to_export:
                sanitized_row = {}
                for k, v in row.items():
                    val_str = str(v) if v is not None else ""
                    # If value starts with a dangerous formula prefix, prepend single quote (')
                    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
                        sanitized_row[k] = "'" + val_str
                    else:
                        sanitized_row[k] = val_str
                writer.writerow(sanitized_row)

        self._export_jobs[job.export_id] = job
        self._export_tokens[token] = job.export_id
        self._export_data[job.export_id] = output.getvalue()

        self.record_audit_event(
            actor_id=principal.principal_id,
            actor_type=principal.principal_type.value,
            action=AuditActionType.EXPORT_REQUESTED,
            resource_type="ExportJob",
            resource_id=job.export_id,
            org_id=principal.organization_id,
            details={"export_type": export_type, "item_count": len(records_to_export)},
        )
        return job

    def download_export(
        self,
        download_token: str,
        principal: PrincipalContext,
    ) -> Tuple[ExportJob, str]:
        """Downloads sanitized export file verifying expiration and tenant boundary."""
        export_id = self._export_tokens.get(download_token)
        if not export_id:
            raise ValueError("Invalid or expired download token.")

        job = self._export_jobs.get(export_id)
        if not job or job.status != ExportJobStatus.READY:
            raise ValueError("Export job is not ready or has been revoked.")

        if job.expires_at < datetime.now(timezone.utc):
            job.status = ExportJobStatus.EXPIRED
            raise ValueError("Export download token has expired.")

        # Enforce tenant isolation on export download
        if job.org_id and principal.organization_id and job.org_id != principal.organization_id:
            if not principal.has_role(RoleType.SCAMGRAPH_ADMIN):
                raise PermissionError("Cross-tenant export download is prohibited.")

        self.record_audit_event(
            actor_id=principal.principal_id,
            actor_type=principal.principal_type.value,
            action=AuditActionType.EXPORT_DOWNLOADED,
            resource_type="ExportJob",
            resource_id=job.export_id,
            org_id=principal.organization_id,
            details={"export_type": job.export_type},
        )
        return job, self._export_data.get(job.export_id, "")

    # -------------------------------------------------------------------------
    # 7. Consent Management Ledger (Analysis vs. Training Separation)
    # -------------------------------------------------------------------------

    def record_consent(
        self,
        subject_id: str,
        purpose: ConsentPurpose,
        granted: bool,
        policy_version: str = "v2.0",
        actor_id: Optional[str] = None,
    ) -> ConsentRecord:
        """Records explicit user consent per purpose. Analysis != Model Training."""
        rec = ConsentRecord(
            subject_id=subject_id,
            purpose=purpose,
            granted=granted,
            policy_version=policy_version,
        )
        self._consents.setdefault(subject_id, {})[purpose] = rec

        self.record_audit_event(
            actor_id=actor_id or subject_id,
            actor_type="User",
            action=AuditActionType.PRIVACY_SETTING_CHANGED,
            resource_type="ConsentRecord",
            resource_id=rec.consent_id,
            details={"purpose": purpose.value, "granted": granted, "version": policy_version},
        )
        return rec

    def has_consent(self, subject_id: str, purpose: ConsentPurpose) -> bool:
        """Evaluates if specific consent has been granted by the data subject."""
        user_consents = self._consents.get(subject_id, {})
        record = user_consents.get(purpose)
        return record.granted if record else False

    # -------------------------------------------------------------------------
    # 8. Evidence Deletion & Dependent Intelligence Invalidation
    # -------------------------------------------------------------------------

    def delete_evidence(
        self,
        evidence_id: str,
        principal: PrincipalContext,
        evidence_owner_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deletes raw evidence and cascade-invalidates dependent graph/ScamDNA claims."""
        # Verify ownership / admin privilege
        if principal.principal_type == PrincipalType.CONSUMER_USER:
            if evidence_owner_id and evidence_owner_id != principal.user_id:
                raise PermissionError("Cannot delete evidence belonging to another user.")
        elif not principal.has_role(RoleType.SCAMGRAPH_ADMIN):
            self.require(principal, Permission.ADMIN_SYSTEM, action_name="delete_evidence")

        # Invalidate downstream graph connections & reputation references
        from services.entity_intelligence.service import entity_intelligence_service
        from services.correlation_engine.service import correlation_service

        invalidated_edges = 0
        invalidated_correlations = 0

        # 1. Clean entity relationships containing this evidence
        for rel in list(entity_intelligence_service.relationships._relationships.values()):
            if evidence_id in rel.evidence_ids:
                rel.evidence_ids.remove(evidence_id)
                invalidated_edges += 1
                if not rel.evidence_ids:
                    # Remove edge if zero supporting evidence remains
                    entity_intelligence_service.relationships._relationships.pop(rel.relationship_id, None)

        # 2. Invalidate correlations referencing this evidence
        if hasattr(correlation_service, "_materialized_correlations"):
            for corr in list(correlation_service._materialized_correlations.values()):
                if hasattr(corr, "evidence_ids") and evidence_id in corr.evidence_ids:
                    corr.evidence_ids.remove(evidence_id)
                    invalidated_correlations += 1

        self.record_audit_event(
            actor_id=principal.principal_id,
            actor_type=principal.principal_type.value,
            action=AuditActionType.EVIDENCE_DELETED,
            resource_type="Evidence",
            resource_id=evidence_id,
            org_id=principal.organization_id,
            details={
                "invalidated_edges": invalidated_edges,
                "invalidated_correlations": invalidated_correlations,
            },
        )

        return {
            "evidence_id": evidence_id,
            "status": "DELETED",
            "invalidated_graph_edges": invalidated_edges,
            "invalidated_correlations": invalidated_correlations,
        }

    # -------------------------------------------------------------------------
    # 9. Entity Dispute & Reputation Reversal Lifecycle
    # -------------------------------------------------------------------------

    def submit_entity_dispute(
        self,
        principal: PrincipalContext,
        entity_id: str,
        reason: str,
    ) -> EntityDisputeRecord:
        """Submits a formal dispute against an entity reputation flag."""
        dispute = EntityDisputeRecord(
            entity_id=entity_id,
            disputer_id=principal.principal_id,
            reason=reason,
            status=DisputeStatus.DISPUTED,
        )
        self._disputes[dispute.dispute_id] = dispute

        # Immediately mark entity verification state as DISPUTED
        from services.entity_intelligence.service import entity_intelligence_service
        ent = entity_intelligence_service._entities.get(entity_id)
        if ent:
            from packages.schemas.entity import EntityVerificationState
            ent.verification_state = EntityVerificationState.DISPUTED

        self.record_audit_event(
            actor_id=principal.principal_id,
            actor_type=principal.principal_type.value,
            action=AuditActionType.REVIEW_DECISION,
            resource_type="EntityDispute",
            resource_id=dispute.dispute_id,
            details={"entity_id": entity_id, "status": DisputeStatus.DISPUTED.value},
        )
        return dispute

    def resolve_entity_dispute(
        self,
        principal: PrincipalContext,
        dispute_id: str,
        resolution: DisputeStatus,
        notes: str,
    ) -> EntityDisputeRecord:
        """Resolves an entity dispute (reversing false flags or confirming scam attribution)."""
        self.require(principal, Permission.REVIEW_WRITE, action_name="resolve_entity_dispute")

        dispute = self._disputes.get(dispute_id)
        if not dispute:
            raise ValueError(f"Dispute '{dispute_id}' not found.")

        dispute.status = resolution
        dispute.resolved_at = datetime.now(timezone.utc)
        dispute.resolution_notes = notes

        from services.entity_intelligence.service import entity_intelligence_service
        ent = entity_intelligence_service._entities.get(dispute.entity_id)
        if ent:
            from packages.schemas.entity import EntityVerificationState
            if resolution == DisputeStatus.REVERSED:
                # Clear malicious flag upon substantiated reversal
                ent.verification_state = EntityVerificationState.VERIFIED_LEGITIMATE
                ent.supporting_evidence_count = 0
            elif resolution == DisputeStatus.CONFIRMED:
                ent.verification_state = EntityVerificationState.VERIFIED_MALICIOUS

        self.record_audit_event(
            actor_id=principal.principal_id,
            actor_type=principal.principal_type.value,
            action=AuditActionType.REVIEW_DECISION,
            resource_type="EntityDispute",
            resource_id=dispute_id,
            details={"resolution": resolution.value, "notes": notes},
        )
        return dispute

    # -------------------------------------------------------------------------
    # 10. Immutable Audit Logging & Redaction
    # -------------------------------------------------------------------------

    def record_audit_event(
        self,
        actor_id: str,
        actor_type: str,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        org_id: Optional[str] = None,
        result: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        """Appends an immutable audit event with automatic secret redaction."""
        # Redact any passwords, secrets, tokens, or raw keys in details
        clean_details: Dict[str, Any] = {}
        if details:
            for k, v in details.items():
                lowered = k.lower()
                if (any(sec in lowered for sec in ("password", "secret", "token", "api_key", "cookie")) or "raw_api_key" in lowered or lowered == "raw_key") and not lowered.endswith("_prefix"):
                    clean_details[k] = "[REDACTED]"
                else:
                    clean_details[k] = v

        event = AuditEvent(
            actor_id=actor_id,
            actor_type=actor_type,
            org_id=org_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            ip_address=ip_address,
            details=clean_details,
        )
        self._audit_log.append(event)
        return event

    def query_audit_log(
        self,
        principal: PrincipalContext,
        action: Optional[AuditActionType] = None,
        limit: int = 50,
    ) -> List[AuditEvent]:
        """Queries the audit log enforcing tenant isolation and AUDIT_READ permission."""
        self.require(principal, Permission.AUDIT_READ, action_name="query_audit_log")

        results: List[AuditEvent] = []
        is_sg_admin = principal.has_role(RoleType.SCAMGRAPH_ADMIN) or principal.has_role(RoleType.SCAMGRAPH_SENIOR_ANALYST)

        for ev in reversed(self._audit_log):
            # Tenant filtering: Org Admins only see their own organization's events
            if not is_sg_admin:
                if ev.org_id != principal.organization_id:
                    continue

            if action and ev.action != action:
                continue

            results.append(ev)
            if len(results) >= limit:
                break

        return results


# Global singleton instance
security_service = SecurityService()
