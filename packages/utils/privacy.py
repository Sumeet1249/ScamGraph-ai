"""Privacy preservation utilities: PII display masking and canonical cryptographic hashing.

Rules:
1. Never mutate canonical raw values while masking; mask presentation copies only.
2. Canonical hashing normalizes before hashing.
3. Plain SHA-256 is used for deterministic correlation; keyed HMAC is supported for deployment secrets.
"""

import hashlib
import hmac
import re
from typing import Optional

from packages.utils.normalization import (
    normalize_email,
    normalize_phone,
    normalize_vpa,
)


def mask_phone(phone: str) -> str:
    """Mask phone number for safe display (e.g. 9876543210 -> ******3210)."""
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 4:
        return f"{'*' * (len(digits) - 4)}{digits[-4:]}"
    return "****"


def mask_email(email: str) -> str:
    """Mask email for safe display (e.g. person@example.com -> p***@example.com)."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.strip().rsplit("@", 1)
    if len(local) > 1:
        masked_local = f"{local[0]}***"
    else:
        masked_local = "***"
    return f"{masked_local}@{domain}"


def mask_vpa(vpa: str) -> str:
    """Mask UPI VPA for safe display (e.g. sumeet@oksbi -> s***@oksbi)."""
    if not vpa or "@" not in vpa:
        return "***@***"
    user_handle, bank_handle = vpa.strip().rsplit("@", 1)
    if len(user_handle) > 1:
        masked_user = f"{user_handle[0]}***"
    else:
        masked_user = "***"
    return f"{masked_user}@{bank_handle}"


def mask_bank_account(account_no: str) -> str:
    """Mask bank account or card number (e.g. 123456789012 -> ********9012)."""
    if not account_no:
        return ""
    clean = re.sub(r"\s", "", account_no)
    if len(clean) >= 4:
        return f"{'*' * (len(clean) - 4)}{clean[-4:]}"
    return "****"


def canonical_hash(value: str, secret: Optional[str] = None) -> str:
    """Compute deterministic cryptographic hash of a canonical identifier.
    
    If secret is provided, computes HMAC-SHA256. Otherwise, computes SHA-256.
    """
    if value is None:
        return ""
    normalized_bytes = str(value).strip().encode("utf-8")
    if secret:
        return hmac.new(secret.encode("utf-8"), normalized_bytes, hashlib.sha256).hexdigest()
    return hashlib.sha256(normalized_bytes).hexdigest()
