"""ScamGraph Python SDK Webhook Verification Helpers."""

import hashlib
import hmac
import time
from typing import Union


def verify_webhook_signature(
    secret: str,
    signature_header: str,
    payload: Union[str, bytes],
    max_age_seconds: int = 300,
) -> bool:
    """Cryptographically verifies incoming webhook signature header against replay attacks.

    Header format: t={timestamp},v1={hex_signature}
    """
    if not secret or not signature_header:
        return False

    payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload

    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(","))
        timestamp = int(parts.get("t", "0"))
        v1_sig = parts.get("v1", "")

        # Replay protection: check age
        current_time = int(time.time())
        if abs(current_time - timestamp) > max_age_seconds:
            return False

        to_sign = f"{timestamp}.".encode("utf-8") + payload_bytes
        expected = hmac.new(
            secret.encode("utf-8"),
            to_sign,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, v1_sig)
    except Exception:
        return False
