"""Comprehensive Security, Identity, RBAC, Evidence Security & Governance Tests (Prompt 21 / Phase 7A)."""

import pytest
import time
from datetime import datetime, timezone

from packages.schemas.enterprise import DataContributionPolicy
from packages.schemas.security import (
    AuditActionType,
    ConsentPurpose,
    DisputeStatus,
    EvidenceSensitivityClass,
    ExportJobStatus,
    Permission,
    PrincipalType,
    RoleType,
)
from services.security.service import SecurityService, security_service


# -----------------------------------------------------------------------------
# 1. Identity, Password Security & PBKDF2 Adaptive Hashing
# -----------------------------------------------------------------------------

def test_password_hashing_and_verification():
    service = SecurityService()
    user = service.register_user(
        email="security.test@example.com",
        password="ValidPassword#123",
        full_name="Test User",
    )

    # 1. Password must NEVER be stored in plaintext
    assert user.hashed_password != "ValidPassword#123"
    assert len(user.hashed_password) == 64  # SHA-256 hex length
    assert len(user.salt) == 32            # 16 bytes hex

    # 2. Authenticate with correct password
    session, token = service.authenticate_user("security.test@example.com", "ValidPassword#123")
    assert session is not None
    assert token is not None
    assert session.user_id == user.user_id
    assert not session.is_revoked

    # 3. Authenticate with wrong password fails
    bad_session, bad_token = service.authenticate_user("security.test@example.com", "WrongPassword")
    assert bad_session is None
    assert bad_token is None


def test_brute_force_throttling():
    service = SecurityService()
    service.register_user(
        email="brute.force@example.com",
        password="CorrectPassword#123",
    )

    # Simulate 5 consecutive failed login attempts
    for _ in range(5):
        s, t = service.authenticate_user("brute.force@example.com", "IncorrectPassword")
        assert s is None

    # 6th attempt must be throttled with ValueError
    with pytest.raises(ValueError, match="Too many failed login attempts"):
        service.authenticate_user("brute.force@example.com", "CorrectPassword#123")


def test_session_lifecycle_and_revocation():
    service = SecurityService()
    user = service.register_user(
        email="session.test@example.com",
        password="Password#123",
    )
    session, raw_token = service.authenticate_user("session.test@example.com", "Password#123")
    assert session is not None

    # Resolve principal with active session token
    principal = service.resolve_principal(session_token=raw_token)
    assert principal.is_authenticated is True
    assert principal.user_id == user.user_id

    # Revoke session
    service.revoke_session(session.session_id)

    # Resolve principal after revocation -> falls back to anonymous
    revoked_principal = service.resolve_principal(session_token=raw_token)
    assert revoked_principal.is_authenticated is False
    assert revoked_principal.principal_type == PrincipalType.ANONYMOUS


# -----------------------------------------------------------------------------
# 2. Canonical Principal Resolution (Human vs. Machine)
# -----------------------------------------------------------------------------

def test_principal_resolution_human_vs_machine():
    service = SecurityService()

    # 1. Anonymous request (no credentials)
    anon = service.resolve_principal()
    assert anon.principal_type == PrincipalType.ANONYMOUS
    assert anon.is_authenticated is False
    assert anon.roles == [RoleType.ANONYMOUS]

    # 2. Human Consumer request
    c_session, c_token = service.authenticate_user("victim.consumer@example.com", "ConsumerPass#123")
    consumer_prn = service.resolve_principal(session_token=c_token)
    assert consumer_prn.principal_type == PrincipalType.CONSUMER_USER
    assert consumer_prn.is_authenticated is True
    assert RoleType.CONSUMER in consumer_prn.roles

    # 3. Machine API Client request (using live API key from Prompt 20)
    api_prn = service.resolve_principal(api_key="sg_live_apex_secret_key_889900")
    assert api_prn.principal_type == PrincipalType.API_CLIENT
    assert api_prn.is_authenticated is True
    assert api_prn.organization_id == "org_enterprise_demo"


# -----------------------------------------------------------------------------
# 3. Centralized RBAC & Permissions
# -----------------------------------------------------------------------------

def test_centralized_rbac_permissions():
    service = SecurityService()

    # Consumer permissions
    c_session, c_token = service.authenticate_user("victim.consumer@example.com", "ConsumerPass#123")
    c_prn = service.resolve_principal(session_token=c_token)
    assert c_prn.has_permission(Permission.INCIDENT_READ_OWN)
    assert not c_prn.has_permission(Permission.INCIDENT_REVIEW)
    assert not c_prn.has_permission(Permission.API_KEY_MANAGE)

    # Org Analyst permissions
    oa_session, oa_token = service.authenticate_user("analyst@alphabank.com", "BankAnalyst#999")
    oa_prn = service.resolve_principal(session_token=oa_token)
    assert oa_prn.has_permission(Permission.INCIDENT_READ_ORG)
    assert oa_prn.has_permission(Permission.CAMPAIGN_READ)
    assert not oa_prn.has_permission(Permission.API_KEY_MANAGE)  # Only Org Admin can manage API keys

    # ScamGraph Senior Analyst permissions
    sa_session, sa_token = service.authenticate_user("lead.investigator@scamgraph.ai", "LeadInvestigator#456")
    sa_prn = service.resolve_principal(session_token=sa_token)
    assert sa_prn.has_permission(Permission.INCIDENT_REVIEW)
    assert sa_prn.has_permission(Permission.EVIDENCE_READ_RAW)
    assert sa_prn.has_permission(Permission.EVIDENCE_EXPORT)

    # ScamGraph Admin permissions
    adm_session, adm_token = service.authenticate_user("security.admin@scamgraph.ai", "SuperAdmin#Secret987")
    adm_prn = service.resolve_principal(session_token=adm_token)
    assert adm_prn.has_permission(Permission.ADMIN_SYSTEM)
    assert adm_prn.has_permission(Permission.API_KEY_MANAGE)


# -----------------------------------------------------------------------------
# 4. Resource-Level Authorization & Insecure Direct Object Reference (IDOR)
# -----------------------------------------------------------------------------

def test_consumer_idor_defense():
    service = SecurityService()

    class MockIncident:
        def __init__(self, incident_id: str, owner_id: str):
            self.id = incident_id
            self.owner_id = owner_id

    # Incident belonging to Consumer Rajesh
    incident_rajesh = MockIncident("inc_rajesh_001", "usr_consumer_rajesh")

    # Consumer Rajesh accesses his own incident -> ALLOWED
    c_session, c_token = service.authenticate_user("victim.consumer@example.com", "ConsumerPass#123")
    rajesh_prn = service.resolve_principal(session_token=c_token)
    assert service.authorize(rajesh_prn, Permission.INCIDENT_READ_OWN, resource=incident_rajesh) is True

    # Register Consumer Bob
    service.register_user(email="bob@example.com", password="BobPassword#123", user_id="usr_consumer_bob")
    _, bob_token = service.authenticate_user("bob@example.com", "BobPassword#123")
    bob_prn = service.resolve_principal(session_token=bob_token)

    # Consumer Bob attempts to access Rajesh's incident -> DENIED (IDOR Blocked)
    assert service.authorize(bob_prn, Permission.INCIDENT_READ_OWN, resource=incident_rajesh) is False
    with pytest.raises(PermissionError, match="Access Denied"):
        service.require(bob_prn, Permission.INCIDENT_READ_OWN, resource=incident_rajesh)


def test_enterprise_tenant_isolation():
    service = SecurityService()

    class MockJob:
        def __init__(self, job_id: str, org_id: str):
            self.id = job_id
            self.org_id = org_id

    job_alpha = MockJob("job_alpha_123", "org_alpha_bank")

    # Alpha Bank Analyst accesses Alpha Job -> ALLOWED
    _, alpha_token = service.authenticate_user("analyst@alphabank.com", "BankAnalyst#999")
    alpha_prn = service.resolve_principal(session_token=alpha_token)
    assert service.authorize(alpha_prn, Permission.INCIDENT_READ_ORG, resource=job_alpha) is True

    # Register Beta Fintech Analyst
    service.register_user(email="analyst@betafintech.com", password="BetaAnalyst#123", user_id="usr_beta_analyst")
    service.add_organization_member("org_beta_fintech", "usr_beta_analyst", role=RoleType.ORG_ANALYST)
    _, beta_token = service.authenticate_user("analyst@betafintech.com", "BetaAnalyst#123")
    beta_prn = service.resolve_principal(session_token=beta_token)

    # Beta Fintech Analyst attempts to access Alpha Bank Job -> DENIED (Tenant Isolation Enforced)
    assert service.authorize(beta_prn, Permission.INCIDENT_READ_ORG, resource=job_alpha) is False
    with pytest.raises(PermissionError, match="Access Denied"):
        service.require(beta_prn, Permission.INCIDENT_READ_ORG, resource=job_alpha)


# -----------------------------------------------------------------------------
# 5. Evidence Sensitivity & Derived vs. Raw Media Separation
# -----------------------------------------------------------------------------

def test_evidence_derived_vs_raw_media_separation():
    service = SecurityService()

    # 1. Standard Analyst: Can read derived signals, but raw media is REDACTED
    service.register_user(email="junior.analyst@scamgraph.ai", password="JuniorAnalyst#123", user_id="usr_junior")
    service.add_organization_member("org_scamgraph_internal", "usr_junior", role=RoleType.SCAMGRAPH_ANALYST)
    _, j_token = service.authenticate_user("junior.analyst@scamgraph.ai", "JuniorAnalyst#123")
    junior_prn = service.resolve_principal(session_token=j_token)

    eval_junior = service.evaluate_evidence_access(
        principal=junior_prn,
        sensitivity_class=EvidenceSensitivityClass.HIGHLY_SENSITIVE,
    )
    assert eval_junior.can_access_derived is True
    assert eval_junior.can_access_raw_media is False
    assert eval_junior.requires_redaction is True

    # 2. Senior Analyst: Can read both derived indicators AND unredacted raw media
    _, sa_token = service.authenticate_user("lead.investigator@scamgraph.ai", "LeadInvestigator#456")
    senior_prn = service.resolve_principal(session_token=sa_token)

    eval_senior = service.evaluate_evidence_access(
        principal=senior_prn,
        sensitivity_class=EvidenceSensitivityClass.HIGHLY_SENSITIVE,
    )
    assert eval_senior.can_access_derived is True
    assert eval_senior.can_access_raw_media is True
    assert eval_senior.requires_redaction is False


# -----------------------------------------------------------------------------
# 6. Controlled Export Jobs & CSV Formula Injection Protection
# -----------------------------------------------------------------------------

def test_csv_formula_injection_defense():
    service = SecurityService()
    _, sa_token = service.authenticate_user("lead.investigator@scamgraph.ai", "LeadInvestigator#456")
    senior_prn = service.resolve_principal(session_token=sa_token)

    # Malicious records with spreadsheet formula injection payloads
    records = [
        {"case_id": "case_101", "scam_text": "=cmd|' /C calc'!A0", "phone": "+919876543210"},
        {"case_id": "case_102", "scam_text": "=HYPERLINK(\"http://evil.com\",\"Click\")", "phone": "+918888888888"},
        {"case_id": "case_103", "scam_text": "@SUM(1+1)*cmd", "phone": "-999"},
    ]

    job = service.create_export_job(principal=senior_prn, export_type="CSV", records=records)
    assert job.status == ExportJobStatus.READY

    # Download and inspect CSV
    _, csv_content = service.download_export(job.download_token, senior_prn)

    # Formulas MUST be sanitized by prepending a single quote (')
    assert "'=cmd|' /C calc'!A0" in csv_content
    assert "'=HYPERLINK" in csv_content
    assert "'@SUM" in csv_content
    assert "'-999" in csv_content


# -----------------------------------------------------------------------------
# 7. Consent Ledger (Separating Analysis from Model Training)
# -----------------------------------------------------------------------------

def test_consent_ledger_isolation():
    service = SecurityService()
    subject_id = "usr_consumer_rajesh"

    # 1. Grant consent for SCAM_ANALYSIS
    service.record_consent(subject_id, ConsentPurpose.SCAM_ANALYSIS, granted=True)
    assert service.has_consent(subject_id, ConsentPurpose.SCAM_ANALYSIS) is True

    # 2. MODEL_TRAINING consent must be FALSE by default (never assumed from analysis consent)
    assert service.has_consent(subject_id, ConsentPurpose.MODEL_TRAINING) is False


# -----------------------------------------------------------------------------
# 8. Evidence Deletion & Dependent Intelligence Invalidation
# -----------------------------------------------------------------------------

def test_evidence_deletion_cascade_invalidation():
    service = SecurityService()
    _, adm_token = service.authenticate_user("security.admin@scamgraph.ai", "SuperAdmin#Secret987")
    admin_prn = service.resolve_principal(session_token=adm_token)

    # Mock an evidence id connected to graph relationships
    evidence_id = "ev_fake_digital_arrest_notice"

    from services.entity_intelligence.service import entity_intelligence_service
    from packages.schemas.entity import EntityRelationship, EntityRelationshipType

    rel = EntityRelationship(
        source_entity_id="ent_fake_vpa_1",
        target_entity_id="ent_fake_phone_1",
        relationship_type=EntityRelationshipType.APPEARED_WITH,
        evidence_ids=[evidence_id],
    )
    entity_intelligence_service.relationships._relationships[rel.relationship_id] = rel

    # Delete evidence
    res = service.delete_evidence(evidence_id, admin_prn)
    assert res["status"] == "DELETED"
    assert res["invalidated_graph_edges"] >= 1

    # Dependent relationship edge with zero remaining evidence MUST be pruned
    assert rel.relationship_id not in entity_intelligence_service.relationships._relationships


# -----------------------------------------------------------------------------
# 9. Entity Dispute & Reputation Reversal Lifecycle
# -----------------------------------------------------------------------------

def test_entity_dispute_and_reputation_reversal():
    service = SecurityService()

    from services.entity_intelligence.service import entity_intelligence_service
    from packages.schemas.entity import Entity, EntityType, EntityVerificationState

    # Seed an entity incorrectly flagged
    entity = Entity(
        entity_id="ent_disputed_merchant",
        entity_type=EntityType.UPI_VPA,
        canonical_value="legit.local.store@oksbi",
        masked_value="l***@oksbi",
        canonical_hash="hash_legit_store",
        verification_state=EntityVerificationState.VERIFIED_MALICIOUS,
        supporting_evidence_count=5,
    )
    entity_intelligence_service._entities[entity.entity_id] = entity

    # Submit dispute
    c_session, c_token = service.authenticate_user("victim.consumer@example.com", "ConsumerPass#123")
    c_prn = service.resolve_principal(session_token=c_token)
    dispute = service.submit_entity_dispute(c_prn, entity.entity_id, reason="This is an official neighborhood grocery store.")
    assert dispute.status == DisputeStatus.DISPUTED
    assert entity.verification_state == EntityVerificationState.DISPUTED

    # Analyst resolves dispute and reverses false flag
    _, sa_token = service.authenticate_user("lead.investigator@scamgraph.ai", "LeadInvestigator#456")
    senior_prn = service.resolve_principal(session_token=sa_token)
    resolved = service.resolve_entity_dispute(
        principal=senior_prn,
        dispute_id=dispute.dispute_id,
        resolution=DisputeStatus.REVERSED,
        notes="Official merchant trade license verified. Flag reversed.",
    )
    assert resolved.status == DisputeStatus.REVERSED
    assert entity.verification_state == EntityVerificationState.VERIFIED_LEGITIMATE
    assert entity.supporting_evidence_count == 0


# -----------------------------------------------------------------------------
# 10. Immutable Audit Logging with Secret Redaction
# -----------------------------------------------------------------------------

def test_immutable_audit_logging_with_redaction():
    service = SecurityService()

    # Record sensitive event with potential secrets
    event = service.record_audit_event(
        actor_id="usr_admin_root",
        actor_type="ADMIN",
        action=AuditActionType.API_KEY_CREATED,
        resource_type="ApiKey",
        resource_id="key_live_secret_01",
        org_id="org_alpha_bank",
        details={
            "raw_api_key": "sg_live_secret_token_12345",
            "password_hash": "supersecretpassword",
            "key_prefix": "sg_live_apex",
        },
    )

    # Secrets MUST be redacted in audit details
    assert event.details["raw_api_key"] == "[REDACTED]"
    assert event.details["password_hash"] == "[REDACTED]"
    assert event.details["key_prefix"] == "sg_live_apex"

    # Query audit log with Org Admin
    service.add_organization_member("org_alpha_bank", "usr_analyst_pooja", role=RoleType.ORG_ADMIN)
    _, admin_token = service.authenticate_user("analyst@alphabank.com", "BankAnalyst#999")
    org_admin_prn = service.resolve_principal(session_token=admin_token)

    logs = service.query_audit_log(org_admin_prn, action=AuditActionType.API_KEY_CREATED)
    assert len(logs) >= 1
    assert logs[0].resource_id == "key_live_secret_01"
