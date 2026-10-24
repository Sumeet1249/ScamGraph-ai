"""Deterministic normalization utilities for phone numbers, emails, domains, URLs, and UPI VPAs.

Rule: Always preserve raw evidence separately from normalized correlation values.
"""

import re
from urllib.parse import urlparse


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers to E.164-like canonical digits.
    
    Handles standard Indian 10-digit mobile numbers with optional +91 or 0 prefix.
    """
    if not phone:
        return ""
    # Strip all non-digits
    digits = re.sub(r"\D", "", phone.strip())
    # Handle India specific prefix
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    elif digits:
        return f"+{digits}"
    return ""


def normalize_email(email: str) -> str:
    """Normalize email address with lowercase domain and trimmed whitespace."""
    if not email:
        return ""
    clean = email.strip()
    if "@" not in clean:
        return clean.lower()
    local_part, domain = clean.rsplit("@", 1)
    # Lowercase domain; preserve local part casing according to RFC but trim
    return f"{local_part.strip().lower()}@{domain.strip().lower()}"


def normalize_vpa(vpa: str) -> str:
    """Normalize UPI Virtual Payment Address (e.g. user@bank).
    
    UPI VPAs are case-insensitive in practice across PSPs; normalized to lowercase trimmed string.
    """
    if not vpa:
        return ""
    clean = vpa.strip().lower()
    return clean


def normalize_domain_or_url(url_or_domain: str) -> str:
    """Extract canonical lowercase hostname/domain from URL or bare domain without destroying original path."""
    if not url_or_domain:
        return ""
    target = url_or_domain.strip().lower()
    if not target.startswith(("http://", "https://")):
        target = f"http://{target}"
    try:
        parsed = urlparse(target)
        hostname = parsed.hostname or ""
        # Strip leading www. for canonical correlation
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname
    except Exception:
        return url_or_domain.strip().lower()


def normalize_text(text: str) -> str:
    """Canonical text normalization: lowercase, collapse whitespace, and strip leading/trailing spaces."""
    if not text:
        return ""
    # Collapse multiple spaces, newlines, and tabs
    clean = re.sub(r"\s+", " ", text).strip().lower()
    return clean

