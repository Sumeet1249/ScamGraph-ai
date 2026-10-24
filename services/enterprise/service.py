"""Enterprise Platform Service (Prompt 20 / Phase 6B).

Provides production gateway capabilities: API key management, SSRF protection,
idempotency, sandbox isolation, async job management, and signed webhook dispatching.
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from packages.schemas.common import generate_id
from packages.schemas.enterprise import (
    AnalysisJobRecord,
    AnalysisJobStatus,
    ApiKeyRecord,
    DataContributionPolicy,
    EnterpriseCheckRequest,
    EnterpriseCheckResponse,
    EnterpriseEntityCheckResponse,
    EnterpriseGuardRequest,
    EnterpriseGuardResponse,
    EnterpriseNetworkCheckResponse,
    EnterpriseOrganization,
    EnvironmentType,
    GuardActionType,
    IdempotencyRecord,
    WebhookDeliveryRecord,
    WebhookEndpointRecord,
    WebhookEventPayload,
    WebhookEventType,
)
from services.campaign_engine.service import campaign_service
from services.correlation_engine.service import correlation_service
from services.decision_engine.service import unified_decision_service
from services.entity_intelligence.extractor import EntityExtractor
from services.entity_intelligence.service import entity_intelligence_service
from services.language_intelligence.service import language_intelligence_service

logger = logging.getLogger("enterprise.service")


class EnterprisePlatformService:
    """Core enterprise platform service wrapping canonical ScamGraph intelligence."""

    def __init__(self):
        self._organizations: Dict[str, EnterpriseOrganization] = {}
        self._api_keys: Dict[str, ApiKeyRecord] = {}           # key_id -> record
        self._key_hash_to_id: Dict[str, str] = {}              # hashed_secret -> key_id
        self._idempotency_store: Dict[str, IdempotencyRecord] = {} # key -> record
        self._jobs: Dict[str, AnalysisJobRecord] = {}          # job_id -> record
        self._webhook_endpoints: Dict[str, WebhookEndpointRecord] = {} # endpoint_id -> record
        self._webhook_secrets: Dict[str, str] = {}             # endpoint_id -> raw_secret
        self._deliveries: List[WebhookDeliveryRecord] = []
        self._seed_default_org_and_keys()

    def _seed_default_org_and_keys(self):
        """Seeds default partner organization and test credentials for local dev."""
        org = EnterpriseOrganization(
            org_id="org_enterprise_demo",
            name="Apex Payments & Banking Corp",
            status="ACTIVE",
            data_contribution_policy=DataContributionPolicy.NETWORK_INTELLIGENCE_ALLOWED,
        )
        self._organizations[org.org_id] = org

        # Pre-seed deterministic test keys
        self.create_api_key(
            org_id=org.org_id,
            environment=EnvironmentType.LIVE,
            scopes=["check:write", "guard:write", "entity:read", "campaign:read", "webhook:manage"],
            fixed_secret="sg_live_apex_secret_key_889900",
        )
        self.create_api_key(
            org_id=org.org_id,
            environment=EnvironmentType.SANDBOX,
            scopes=["check:write", "guard:write", "entity:read"],
            fixed_secret="sg_test_apex_sandbox_key_112233",
        )

    # -------------------------------------------------------------------------
    # 1. API Key Authentication & Cryptographic Hashing
    # -------------------------------------------------------------------------
    def _hash_secret(self, secret: str) -> str:
        """Computes SHA-256 hash of API secret."""
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    def create_api_key(
        self,
        org_id: str,
        environment: EnvironmentType = EnvironmentType.LIVE,
        scopes: Optional[List[str]] = None,
        fixed_secret: Optional[str] = None,
    ) -> Tuple[ApiKeyRecord, str]:
        """Generates new API key with secure random secret; stores only hash."""
        prefix = "sg_live_" if environment == EnvironmentType.LIVE else "sg_test_"
        raw_secret = fixed_secret or f"{prefix}{secrets.token_urlsafe(32)}"
        hashed = self._hash_secret(raw_secret)

        record = ApiKeyRecord(
            prefix=prefix,
            hashed_secret=hashed,
            org_id=org_id,
            environment=environment,
            scopes=scopes or ["check:write", "guard:write", "entity:read"],
            status="ACTIVE",
        )
        self._api_keys[record.key_id] = record
        self._key_hash_to_id[hashed] = record.key_id
        return record, raw_secret

    def authenticate_key(self, api_key: str) -> Optional[ApiKeyRecord]:
        """Validates bearer API key and records last_used_at."""
        if not api_key:
            return None
        hashed = self._hash_secret(api_key.strip())
        key_id = self._key_hash_to_id.get(hashed)
        if not key_id:
            return None
        record = self._api_keys.get(key_id)
        if not record or record.status != "ACTIVE":
            return None
        record.last_used_at = datetime.now(timezone.utc)
        return record

    def revoke_api_key(self, key_id: str, org_id: str) -> bool:
        """Revokes an API key belonging to the organization."""
        record = self._api_keys.get(key_id)
        if not record or record.org_id != org_id:
            return False
        record.status = "REVOKED"
        return True

    # -------------------------------------------------------------------------
    # 2. Idempotency Support
    # -------------------------------------------------------------------------
    def check_idempotency(
        self,
        idempotency_key: str,
        org_id: str,
        endpoint: str,
        request_payload: Dict[str, Any],
    ) -> Tuple[bool, Optional[Dict[str, Any]], int]:
        """Checks if idempotency key was previously processed.

        Returns:
            Tuple of (is_cached, cached_response, status_code).
        Raises:
            ValueError: If same key was supplied with differing payload (Conflict).
        """
        composite_key = f"{org_id}:{endpoint}:{idempotency_key}"
        record = self._idempotency_store.get(composite_key)
        if not record:
            return False, None, 200

        # Check expiry (default 24h)
        if datetime.now(timezone.utc) > record.expires_at:
            del self._idempotency_store[composite_key]
            return False, None, 200

        # Check payload fingerprint
        req_hash = hashlib.sha256(json.dumps(request_payload, sort_keys=True).encode()).hexdigest()
        if req_hash != record.request_hash:
            raise ValueError(
                f"Idempotency key '{idempotency_key}' was previously used with a different request payload."
            )

        return True, record.response_payload, record.status_code

    def store_idempotency(
        self,
        idempotency_key: str,
        org_id: str,
        endpoint: str,
        request_payload: Dict[str, Any],
        response_payload: Dict[str, Any],
        status_code: int = 200,
        ttl_seconds: int = 86400,
    ) -> None:
        """Stores response against idempotency key for replay."""
        composite_key = f"{org_id}:{endpoint}:{idempotency_key}"
        now = datetime.now(timezone.utc)
        req_hash = hashlib.sha256(json.dumps(request_payload, sort_keys=True).encode()).hexdigest()

        self._idempotency_store[composite_key] = IdempotencyRecord(
            idempotency_key=idempotency_key,
            org_id=org_id,
            endpoint=endpoint,
            request_hash=req_hash,
            response_payload=response_payload,
            status_code=status_code,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )

    # -------------------------------------------------------------------------
    # 3. SSRF Defense for URL Intelligence
    # -------------------------------------------------------------------------
    def validate_url_ssrf_safe(self, target_url: str) -> Tuple[bool, Optional[str]]:
        """Ensures customer-provided URLs do not target internal networks or cloud metadata.

        Returns:
            Tuple of (is_safe, error_reason)
        """
        if not target_url:
            return True, None

        try:
            parsed = urlparse(target_url)
            scheme = (parsed.scheme or "").lower()
            if scheme not in ("http", "https"):
                return False, f"Unsupported scheme '{scheme}'. Only HTTP and HTTPS are permitted."

            hostname = parsed.hostname
            if not hostname:
                return False, "Malformed URL: missing hostname."

            # Block localhost and common loopback aliases
            lowered = hostname.lower()
            if lowered in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
                return False, "SSRF Defense: Localhost and loopback addresses are blocked."

            # Check if hostname is an IP address
            try:
                ip = ipaddress.ip_address(hostname)
                # Cloud metadata IP
                if str(ip) == "169.254.169.254":
                    return False, "SSRF Defense: Cloud instance metadata endpoint is blocked."
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return False, f"SSRF Defense: IP {hostname} is a private/internal network address."
            except ValueError:
                # Hostname is a domain name
                if lowered.endswith(".internal") or lowered.endswith(".local") or lowered.endswith(".corp"):
                    return False, "SSRF Defense: Internal domain suffix is blocked."

            return True, None
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    # -------------------------------------------------------------------------
    # 4. Canonical Scam Check Execution
    # -------------------------------------------------------------------------
    def execute_check(
        self,
        req: EnterpriseCheckRequest,
        org_id: str,
    ) -> EnterpriseCheckResponse:
        """Executes full multi-signal scam analysis across canonical engines."""
        start_time = time.perf_counter()
        req_id = generate_id("req")
        check_id = generate_id("chk")

        # 1. SSRF Safety Check
        if req.url:
            safe, reason = self.validate_url_ssrf_safe(req.url)
            if not safe:
                return EnterpriseCheckResponse(
                    check_id=check_id,
                    request_id=req_id,
                    risk_level="HIGH",
                    risk_score=90,
                    confidence="HIGH",
                    urgency="CRITICAL",
                    recommended_action="BLOCK_URL_ACCESS",
                    reason_codes=["MALICIOUS_SSRF_TARGET", "INTERNAL_ADDRESS_PROBE"],
                    warnings=[reason or "SSRF probe rejected"],
                    processing_ms=int((time.perf_counter() - start_time) * 1000),
                    environment=req.environment,
                )

        # 2. Sandbox Deterministic Mode
        if req.environment == EnvironmentType.SANDBOX:
            # Deterministic fixtures for partner testing; never mutates production graph
            text = (req.message_text or "").lower()
            is_scam = any(w in text for w in ["cbi", "arrest", "task", "police", "kyc", "otp", "5000"])
            return EnterpriseCheckResponse(
                check_id=check_id,
                request_id=req_id,
                risk_level="HIGH" if is_scam else "LOW",
                risk_score=85 if is_scam else 12,
                confidence="HIGH",
                urgency="HIGH" if is_scam else "LOW",
                recommended_action="PAUSE_BEFORE_PAYMENT" if is_scam else "ALLOW_NORMAL_FLOW",
                reason_codes=["SANDBOX_DETERMINISTIC_MATCH", "PAYMENT_PRESSURE"] if is_scam else ["SANDBOX_SAFE_BASELINE"],
                network_signal="SYNTHETIC_SANDBOX_FIXTURE",
                warnings=["SANDBOX_MODE: Output is synthetic and excluded from global campaign intelligence"],
                processing_ms=int((time.perf_counter() - start_time) * 1000),
                environment=EnvironmentType.SANDBOX,
            )

        # 3. Canonical Pipeline Execution
        combined_text = req.message_text or ""
        feat = language_intelligence_service.extract_behavioral_features(combined_text)
        
        # Check entity intelligence if VPA or phone present
        reputation = "UNKNOWN"
        vpa_to_check = req.vpa
        if not vpa_to_check and req.message_text:
            extracted = EntityExtractor.extract_all(req.message_text)
            for c in extracted:
                if c.entity_type.value in ("UPI_VPA", "PHONE", "URL"):
                    vpa_to_check = c.raw_value
                    break

        entity_suspicious = False
        if vpa_to_check:
            clean_vpa = vpa_to_check.strip().lower()
            for ent in entity_intelligence_service._entities.values():
                if (ent.canonical_value and ent.canonical_value.lower() == clean_vpa) or (ent.display_value and ent.display_value.lower() == clean_vpa):
                    if ent.verification_state.value in ("DISPUTED", "VERIFIED_MALICIOUS") or ent.supporting_evidence_count > 0:
                        entity_suspicious = True
                        reputation = "REPORTED_SUSPICIOUS"
                        break
            if "fake" in clean_vpa or "cbi" in clean_vpa or "scam" in clean_vpa:
                entity_suspicious = True
                reputation = "REPORTED_SUSPICIOUS"

        # Evaluate risk score & level
        tactics = [t.value for t in feat.tactics]
        is_high = "PAYMENT_PRESSURE" in tactics or entity_suspicious or "FEAR" in tactics
        risk_score = 85 if is_high else (55 if tactics else (15 if combined_text else 0))
        risk_level = "HIGH" if risk_score >= 70 else ("MEDIUM" if risk_score >= 40 else ("LOW" if combined_text else "INSUFFICIENT_EVIDENCE"))
        confidence = "HIGH" if (tactics and vpa_to_check) else ("MEDIUM" if tactics else "LOW")
        urgency = "HIGH" if is_high else "LOW"

        action = "PAUSE_BEFORE_PAYMENT" if is_high else ("SHOW_CAUTION" if risk_level == "MEDIUM" else "ALLOW_NORMAL_FLOW")

        return EnterpriseCheckResponse(
            check_id=check_id,
            request_id=req_id,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=confidence,
            urgency=urgency,
            recommended_action=action,
            reason_codes=tactics or (["INSUFFICIENT_EVIDENCE"] if not combined_text else ["SAFE_BASELINE"]),
            journey_summary={"current_stage": "PAYMENT_REQUEST" if is_high else "INITIAL_CONTACT"},
            network_signal="ENTITY_REPORTED_ELSEWHERE" if entity_suspicious else "NO_NETWORK_SIGNAL",
            processing_ms=int((time.perf_counter() - start_time) * 1000),
            environment=req.environment,
        )

    # -------------------------------------------------------------------------
    # 5. Pre-Payment Guard Execution (Fast Path)
    # -------------------------------------------------------------------------
    def execute_guard(
        self,
        req: EnterpriseGuardRequest,
        org_id: str,
    ) -> EnterpriseGuardResponse:
        """Evaluates transaction context before payment authorization with strict SLA."""
        start_time = time.perf_counter()
        req_id = generate_id("req_grd")
        guard_id = generate_id("grd")

        # 1. Sandbox isolation
        if req.environment == EnvironmentType.SANDBOX:
            is_scam = "fake" in req.vpa.lower() or "cbi" in req.vpa.lower() or "scam" in req.vpa.lower()
            return EnterpriseGuardResponse(
                guard_id=guard_id,
                request_id=req_id,
                action=GuardActionType.PAUSE_BEFORE_PAYMENT if is_scam else GuardActionType.ALLOW_NORMAL_FLOW,
                friction_level=4 if is_scam else 0,
                risk_score=85 if is_scam else 10,
                confidence="HIGH",
                payment_proximity="IMMINENT",
                reason_codes=["SANDBOX_VPA_MATCH"] if is_scam else ["SANDBOX_SAFE_MERCHANT"],
                intervention_title="Pause Before Payment" if is_scam else "Normal Transaction",
                intervention_message="Suspicious destination VPA detected in sandbox test." if is_scam else "Normal flow permitted.",
                safe_guidance=["Verify recipient identity"] if is_scam else [],
                network_signal="SYNTHETIC_SANDBOX",
                latency_tier="FAST_PATH",
                processing_ms=int((time.perf_counter() - start_time) * 1000),
                environment=EnvironmentType.SANDBOX,
            )

        # 2. Canonical VPA & Context Inspection
        vpa_clean = req.vpa.strip().lower()
        ent = None
        for e in entity_intelligence_service._entities.values():
            if (e.canonical_value and e.canonical_value.lower() == vpa_clean) or (e.display_value and e.display_value.lower() == vpa_clean):
                ent = e
                break
        
        # Check text context if provided
        tactics = []
        if req.message_text:
            feat = language_intelligence_service.extract_behavioral_features(req.message_text)
            tactics = [t.value for t in feat.tactics]

        entity_risk = ent and (ent.supporting_evidence_count > 0 or ent.verification_state.value == "VERIFIED_MALICIOUS")
        has_pressure = "PAYMENT_PRESSURE" in tactics or "FEAR" in tactics or "URGENCY" in tactics or "AUTHORITY_COERCION" in tactics

        if entity_risk and has_pressure:
            action = GuardActionType.STRONG_WARNING
            friction = 5
            score = 92
            title = "CRITICAL: Known High-Risk Payment Destination"
            msg = f"The VPA '{vpa_clean}' has been flagged in multiple coercive scam reports."
        elif entity_risk or has_pressure:
            action = GuardActionType.PAUSE_BEFORE_PAYMENT
            friction = 4
            score = 78
            title = "Warning: High Risk Coercion Signal Detected"
            msg = "Payment request exhibits behavioral pressure or suspicious recipient patterns."
        else:
            action = GuardActionType.ALLOW_NORMAL_FLOW
            friction = 0
            score = 15
            title = "Low Risk Payment Flow"
            msg = "No anomalous risk indicators observed."

        return EnterpriseGuardResponse(
            guard_id=guard_id,
            request_id=req_id,
            action=action,
            friction_level=friction,
            risk_score=score,
            confidence="HIGH" if entity_risk else "MEDIUM",
            payment_proximity="IMMINENT",
            reason_codes=tactics or (["KNOWN_HIGH_RISK_VPA"] if entity_risk else ["NORMAL_BASELINE"]),
            intervention_title=title,
            intervention_message=msg,
            safe_guidance=[
                "Never send money to an unknown individual claiming to represent authorities.",
                "Verify official claims by contacting the institution via its verified website.",
            ] if friction > 0 else [],
            network_signal="ENTITY_REPORTED_ELSEWHERE" if entity_risk else "NO_NETWORK_SIGNAL",
            latency_tier="FAST_PATH",
            processing_ms=int((time.perf_counter() - start_time) * 1000),
            environment=req.environment,
        )

    # -------------------------------------------------------------------------
    # 6. Entity Intelligence Lookup
    # -------------------------------------------------------------------------
    def check_entity(self, entity_type: str, value: str) -> EnterpriseEntityCheckResponse:
        """Retrieves privacy-safe entity reputation without disclosing victim PII."""
        clean_val = value.strip().lower()
        ent = None
        for e in entity_intelligence_service._entities.values():
            if (e.canonical_value and e.canonical_value.lower() == clean_val) or (e.display_value and e.display_value.lower() == clean_val):
                ent = e
                break

        if ent:
            rep_score = 0.85 if ent.verification_state.value == "VERIFIED_MALICIOUS" else (0.65 if ent.supporting_evidence_count > 0 else 0.2)
            reputation = "HIGH_RISK_MULE" if rep_score >= 0.85 else ("REPORTED_SUSPICIOUS" if rep_score >= 0.60 else "CLEAN")
            bracket = "20+" if ent.incident_count > 20 else ("6-20" if ent.incident_count > 5 else "1-5")
            return EnterpriseEntityCheckResponse(
                entity_type=entity_type.upper(),
                normalized_value=clean_val,
                verification_state="SUSPICIOUS" if rep_score >= 0.60 else "UNVERIFIED",
                network_reputation=reputation,
                incident_count_bracket=bracket,
                confidence=0.88,
                first_seen=ent.first_seen,
                last_seen=ent.last_seen,
            )

        return EnterpriseEntityCheckResponse(
            entity_type=entity_type.upper(),
            normalized_value=clean_val,
            verification_state="UNKNOWN",
            network_reputation="CLEAN",
            incident_count_bracket="0",
            confidence=0.50,
        )

    # -------------------------------------------------------------------------
    # 7. Asynchronous Analysis Jobs
    # -------------------------------------------------------------------------
    def create_job(self, org_id: str, artifact_id: Optional[str] = None) -> AnalysisJobRecord:
        """Creates an asynchronous job for media ingestion or batch processing."""
        job = AnalysisJobRecord(
            org_id=org_id,
            status=AnalysisJobStatus.PROCESSING,
            progress_stage="OCR_PROCESSING",
            artifact_id=artifact_id,
        )
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str, requesting_org_id: str) -> Optional[AnalysisJobRecord]:
        """Retrieves job ensuring multi-tenant isolation boundary (Org A cannot read Org B)."""
        job = self._jobs.get(job_id)
        if not job or job.org_id != requesting_org_id:
            return None
        return job

    def complete_job(self, job_id: str, result_payload: Dict[str, Any]) -> Optional[AnalysisJobRecord]:
        """Marks async job as completed with structured result."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.status = AnalysisJobStatus.COMPLETED
        job.progress_stage = "COMPLETED"
        job.result = result_payload
        job.completed_at = datetime.now(timezone.utc)
        return job

    # -------------------------------------------------------------------------
    # 8. Webhooks: Registration, HMAC-SHA256 Signing & Dispatch
    # -------------------------------------------------------------------------
    def register_webhook(
        self,
        org_id: str,
        url: str,
        event_types: List[WebhookEventType],
    ) -> Tuple[WebhookEndpointRecord, str]:
        """Registers partner webhook endpoint and generates raw secret once."""
        raw_secret = f"whsec_{secrets.token_urlsafe(32)}"
        secret_hash = self._hash_secret(raw_secret)

        endpoint = WebhookEndpointRecord(
            org_id=org_id,
            url=url,
            secret_hash=secret_hash,
            event_types=event_types,
        )
        self._webhook_endpoints[endpoint.endpoint_id] = endpoint
        self._webhook_secrets[endpoint.endpoint_id] = raw_secret
        return endpoint, raw_secret

    def get_webhooks(self, org_id: str) -> List[WebhookEndpointRecord]:
        """Returns registered webhook endpoints for an organization."""
        return [w for w in self._webhook_endpoints.values() if w.org_id == org_id]

    def sign_payload(self, secret: str, timestamp: int, payload_bytes: bytes) -> str:
        """Computes HMAC-SHA256 signature in format t={timestamp},v1={hex_signature}."""
        to_sign = f"{timestamp}.".encode("utf-8") + payload_bytes
        signature = hmac.new(secret.encode("utf-8"), to_sign, hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={signature}"

    def verify_webhook_signature(
        self,
        secret: str,
        header_value: str,
        payload_bytes: bytes,
        max_age_seconds: int = 300,
    ) -> bool:
        """Verifies signature header against replay attacks within time window."""
        try:
            parts = dict(item.split("=", 1) for item in header_value.split(","))
            timestamp = int(parts.get("t", "0"))
            v1_sig = parts.get("v1", "")

            # Replay protection: check age
            current_time = int(time.time())
            if abs(current_time - timestamp) > max_age_seconds:
                return False

            expected = hmac.new(
                secret.encode("utf-8"),
                f"{timestamp}.".encode("utf-8") + payload_bytes,
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected, v1_sig)
        except Exception:
            return False

    def dispatch_event(
        self,
        event_type: WebhookEventType,
        data: Dict[str, Any],
        target_org_id: Optional[str] = None,
    ) -> List[WebhookDeliveryRecord]:
        """Simulates signed dispatch of threat events to registered endpoints."""
        now = datetime.now(timezone.utc)
        payload = WebhookEventPayload(
            event_type=event_type,
            created_at=now,
            data=data,
        )
        payload_bytes = payload.model_dump_json().encode("utf-8")
        timestamp = int(time.time())

        deliveries = []
        for ep in self._webhook_endpoints.values():
            if target_org_id and ep.org_id != target_org_id:
                continue
            if event_type in ep.event_types and ep.status == "ACTIVE":
                secret = self._webhook_secrets.get(ep.endpoint_id, "default_secret")
                sig = self.sign_payload(secret, timestamp, payload_bytes)
                
                delivery = WebhookDeliveryRecord(
                    endpoint_id=ep.endpoint_id,
                    event_id=payload.event_id,
                    status="DELIVERED",
                    attempts=1,
                    last_response_code=200,
                )
                self._deliveries.append(delivery)
                deliveries.append(delivery)

        return deliveries


enterprise_platform_service = EnterprisePlatformService()
