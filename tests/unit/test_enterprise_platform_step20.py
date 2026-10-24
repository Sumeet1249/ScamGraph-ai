"""Comprehensive unit and functional tests for Enterprise Platform V2 (Prompt 20 / Phase 6B)."""

import pytest
import time
from datetime import datetime, timezone

from packages.schemas.enterprise import (
    DataContributionPolicy,
    EnterpriseCheckRequest,
    EnterpriseEntityCheckRequest,
    EnterpriseGuardRequest,
    EnvironmentType,
    GuardActionType,
    WebhookEventType,
)
from packages.sdk_python.scamgraph import (
    AuthenticationError,
    ScamGraphClient,
    verify_webhook_signature,
)
from services.enterprise.service import (
    EnterprisePlatformService,
    enterprise_platform_service,
)


# 1. HINGLISH COERCION CHECK
def test_enterprise_check_hinglish_coercion():
    service = EnterprisePlatformService()
    req = EnterpriseCheckRequest(
        message_text="Sir verification complete karne ke liye abhi 5000 pay karo warna account block ho jayega.",
        vpa="fake.task@oksbi",
        external_reference="REF_CHECK_001",
    )
    res = service.execute_check(req, org_id="org_enterprise_demo")

    assert res.risk_level == "HIGH"
    assert res.risk_score >= 70
    assert "PAYMENT_PRESSURE" in res.reason_codes
    assert res.recommended_action == "PAUSE_BEFORE_PAYMENT"
    assert res.processing_ms >= 0


# 2. UPI PRE-PAYMENT GUARD COERCION
def test_enterprise_guard_upi_coercion():
    service = EnterprisePlatformService()
    req = EnterpriseGuardRequest(
        vpa="fake.cbi.hq@oksbi",
        amount=25000.0,
        message_text="CBI Headquarters se call hai. Turant security deposit pay karo.",
        fast_path=True,
    )
    res = service.execute_guard(req, org_id="org_enterprise_demo")

    assert res.action in (GuardActionType.PAUSE_BEFORE_PAYMENT, GuardActionType.STRONG_WARNING)
    assert res.friction_level >= 4
    assert res.risk_score >= 70
    assert len(res.safe_guidance) >= 1
    assert res.latency_tier == "FAST_PATH"


# 3. LEGITIMATE MERCHANT PAYMENT CONTEXT
def test_enterprise_guard_normal_merchant_context():
    service = EnterprisePlatformService()
    req = EnterpriseGuardRequest(
        vpa="grocery.supermarket@hdfcbank",
        amount=340.0,
        message_text="Payment for daily groceries.",
        fast_path=True,
    )
    res = service.execute_guard(req, org_id="org_enterprise_demo")

    assert res.action == GuardActionType.ALLOW_NORMAL_FLOW
    assert res.friction_level == 0
    assert res.risk_score <= 25


# 4. INSUFFICIENT EVIDENCE HANDLING
def test_enterprise_check_insufficient_evidence():
    service = EnterprisePlatformService()
    req = EnterpriseCheckRequest(
        message_text="",  # Empty text
    )
    res = service.execute_check(req, org_id="org_enterprise_demo")

    assert res.risk_level == "INSUFFICIENT_EVIDENCE"
    assert res.risk_score == 0
    assert res.recommended_action == "ALLOW_NORMAL_FLOW"


# 5. IDEMPOTENCY: CACHE & CONFLICT RESOLUTION
def test_idempotency_cache_and_conflict():
    service = EnterprisePlatformService()
    org_id = "org_enterprise_demo"
    endpoint = "/api/v1/check"
    key = "idem_tx_12345"

    payload_1 = {"message_text": "Pay 5000"}
    payload_2 = {"message_text": "Different payload"}

    # 1. Initially uncached
    cached, data, sc = service.check_idempotency(key, org_id, endpoint, payload_1)
    assert cached is False

    # Store first result
    mock_response = {"check_id": "chk_001", "risk_score": 80}
    service.store_idempotency(key, org_id, endpoint, payload_1, mock_response, status_code=200)

    # 2. Replay with identical payload -> Cache HIT
    cached, replay, sc = service.check_idempotency(key, org_id, endpoint, payload_1)
    assert cached is True
    assert replay["check_id"] == "chk_001"

    # 3. Replay with DIFFERENT payload -> Conflict Error
    with pytest.raises(ValueError, match="Idempotency key"):
        service.check_idempotency(key, org_id, endpoint, payload_2)


# 6. MULTI-TENANT ISOLATION (ORG A CANNOT ACCESS ORG B)
def test_multitenant_isolation():
    service = EnterprisePlatformService()
    org_a = "org_alpha_bank"
    org_b = "org_beta_fintech"

    # Create job for Org A
    job_a = service.create_job(org_id=org_a, artifact_id="art_a")

    # Org A can read its own job
    assert service.get_job(job_a.job_id, requesting_org_id=org_a) is not None

    # Org B is strictly denied access
    assert service.get_job(job_a.job_id, requesting_org_id=org_b) is None


# 7. SANDBOX DETERMINISTIC ISOLATION
def test_sandbox_deterministic_isolation():
    service = EnterprisePlatformService()
    req = EnterpriseCheckRequest(
        message_text="CBI officer demands ₹50,000 security deposit",
        environment=EnvironmentType.SANDBOX,
    )
    res = service.execute_check(req, org_id="org_enterprise_demo")

    assert res.environment == EnvironmentType.SANDBOX
    assert any("SANDBOX_MODE" in w for w in res.warnings)
    assert res.network_signal == "SYNTHETIC_SANDBOX_FIXTURE"


# 8. WEBHOOK SIGNING & REPLAY DEFENSE
def test_webhook_signing_and_replay_protection():
    service = EnterprisePlatformService()
    secret = "whsec_super_secret_test_key_123"
    payload = b'{"event":"high_risk.detected","risk_score":92}'
    timestamp = int(time.time())

    # 1. Sign
    header = service.sign_payload(secret, timestamp, payload)
    assert header.startswith(f"t={timestamp},v1=")

    # 2. Verify valid signature
    assert service.verify_webhook_signature(secret, header, payload, max_age_seconds=300) is True

    # 3. Tampered payload fails
    assert service.verify_webhook_signature(secret, header, b'{"event":"tampered"}', max_age_seconds=300) is False

    # 4. Expired timestamp (> 300s) fails replay
    old_timestamp = timestamp - 400
    old_header = service.sign_payload(secret, old_timestamp, payload)
    assert service.verify_webhook_signature(secret, old_header, payload, max_age_seconds=300) is False


# 9. SSRF DEFENSE: BLOCK LOCALHOST, PRIVATE IP, CLOUD METADATA
def test_ssrf_url_validation_blocks_localhost_and_metadata():
    service = EnterprisePlatformService()

    # Localhost
    safe, r = service.validate_url_ssrf_safe("http://localhost:8080/admin")
    assert safe is False
    assert "SSRF" in r

    # Loopback
    safe, r = service.validate_url_ssrf_safe("http://127.0.0.1:3000/api")
    assert safe is False

    # Private IP RFC1918
    safe, r = service.validate_url_ssrf_safe("http://192.168.1.1/router")
    assert safe is False

    # Cloud Instance Metadata (AWS/GCP/Azure)
    safe, r = service.validate_url_ssrf_safe("http://169.254.169.254/latest/meta-data/")
    assert safe is False
    assert "metadata" in r

    # Dangerous schemes
    safe, r = service.validate_url_ssrf_safe("file:///etc/passwd")
    assert safe is False

    # Public valid URL succeeds
    safe, r = service.validate_url_ssrf_safe("https://legitimate-store.com/checkout")
    assert safe is True
    assert r is None


# 10. DATA CONTRIBUTION POLICY INTEGRATION
def test_data_contribution_policy_isolation():
    service = EnterprisePlatformService()
    # Check default policy is valid
    org = service._organizations["org_enterprise_demo"]
    assert org.data_contribution_policy in (
        DataContributionPolicy.PRIVATE_ONLY,
        DataContributionPolicy.NETWORK_INTELLIGENCE_ALLOWED,
        DataContributionPolicy.AGGREGATE_ALLOWED,
    )


# 11. API KEY LIFECYCLE (CREATE, HASH, AUTHENTICATE, REVOKE)
def test_api_key_lifecycle():
    service = EnterprisePlatformService()
    org_id = "org_enterprise_demo"

    record, raw_secret = service.create_api_key(org_id=org_id, environment=EnvironmentType.LIVE)
    assert raw_secret.startswith("sg_live_")
    # Raw secret must NEVER be stored
    assert record.hashed_secret != raw_secret

    # Authenticate with valid key
    auth = service.authenticate_key(raw_secret)
    assert auth is not None
    assert auth.key_id == record.key_id
    assert auth.last_used_at is not None

    # Revoke key
    revoked = service.revoke_api_key(record.key_id, org_id)
    assert revoked is True

    # Authenticate with revoked key fails
    assert service.authenticate_key(raw_secret) is None


# 12. PYTHON SDK INTEGRATION & WEBHOOK HELPER
def test_python_sdk_integration_and_webhook_helper():
    client = ScamGraphClient(api_key="sg_live_apex_secret_key_889900")
    
    # Check
    res = client.check(message_text="Pay ₹5000 immediately for task verification")
    assert res["risk_level"] == "HIGH"
    assert "check_id" in res

    # Guard
    guard_res = client.guard_check(vpa="vip.desk@oksbi", amount=5000.0)
    assert "action" in guard_res
    assert guard_res["latency_tier"] == "FAST_PATH"

    # Webhook Verify Helper
    secret = "whsec_sdk_test_secret"
    payload = b'{"status":"ok"}'
    ts = int(time.time())
    sig = enterprise_platform_service.sign_payload(secret, ts, payload)
    assert client.verify_webhook(secret, sig, payload) is True
