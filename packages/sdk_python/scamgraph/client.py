"""Official ScamGraph Python SDK Client."""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from packages.sdk_python.scamgraph.errors import (
    AuthenticationError,
    ConflictError,
    RateLimitError,
    ScamGraphAPIError,
    ServiceUnavailableError,
    ValidationError,
)
from packages.sdk_python.scamgraph.webhooks import verify_webhook_signature


class ScamGraphClient:
    """Official enterprise client for ScamGraph AI Fraud Intelligence Platform."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001/api/v1/",
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
    ):
        if not api_key:
            raise AuthenticationError("API key must be provided to initialize ScamGraphClient.")
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout_seconds
        self.max_retries = max_retries

    def _headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "scamgraph-python-sdk/2.0.0",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def check(
        self,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        phone: Optional[str] = None,
        vpa: Optional[str] = None,
        external_reference: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        environment: str = "LIVE",
    ) -> Dict[str, Any]:
        """Performs multi-signal scam analysis across canonical intelligence engines."""
        from services.enterprise.service import enterprise_platform_service
        from packages.schemas.enterprise import EnterpriseCheckRequest, EnvironmentType

        auth_record = enterprise_platform_service.authenticate_key(self.api_key)
        if not auth_record:
            raise AuthenticationError("Invalid or revoked API key.")

        req = EnterpriseCheckRequest(
            message_text=message_text,
            url=url,
            phone=phone,
            vpa=vpa,
            external_reference=external_reference,
            environment=EnvironmentType.SANDBOX if environment.upper() == "SANDBOX" else EnvironmentType.LIVE,
        )
        res = enterprise_platform_service.execute_check(req, org_id=auth_record.org_id)
        return res.model_dump()

    def guard_check(
        self,
        vpa: str,
        amount: Optional[float] = None,
        message_text: Optional[str] = None,
        qr_payload: Optional[str] = None,
        external_reference: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        fast_path: bool = True,
        environment: str = "LIVE",
    ) -> Dict[str, Any]:
        """Evaluates recipient VPA and transaction context before payment completion."""
        from services.enterprise.service import enterprise_platform_service
        from packages.schemas.enterprise import EnterpriseGuardRequest, EnvironmentType

        auth_record = enterprise_platform_service.authenticate_key(self.api_key)
        if not auth_record:
            raise AuthenticationError("Invalid or revoked API key.")

        req = EnterpriseGuardRequest(
            vpa=vpa,
            amount=amount,
            message_text=message_text,
            qr_payload=qr_payload,
            external_reference=external_reference,
            fast_path=fast_path,
            environment=EnvironmentType.SANDBOX if environment.upper() == "SANDBOX" else EnvironmentType.LIVE,
        )
        res = enterprise_platform_service.execute_guard(req, org_id=auth_record.org_id)
        return res.model_dump()

    def check_entity(self, entity_type: str, value: str) -> Dict[str, Any]:
        """Queries privacy-safe entity reputation."""
        from services.enterprise.service import enterprise_platform_service
        return enterprise_platform_service.check_entity(entity_type=entity_type, value=value).model_dump()

    @staticmethod
    def verify_webhook(secret: str, signature_header: str, payload: bytes, max_age: int = 300) -> bool:
        """Helper to verify webhook signatures."""
        return verify_webhook_signature(secret, signature_header, payload, max_age_seconds=max_age)
