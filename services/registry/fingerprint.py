"""Identifier Normalization & Keyed HMAC-SHA-256 Fingerprinting.

Implements privacy-preserving exact matching resistant to dictionary and enumeration attacks.
Supports canonical normalization by identifier type, explicit key versioning, and controlled key rotation.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from packages.schemas.registry import CanonicalFingerprint, IdentifierType

# Default secret keys for HMAC fingerprinting (overridden by environment variables outside source control)
# Key rotation: ACTIVE_VERSION is used to generate new fingerprints; RETIRED_VERSIONS are supported for matching.
ACTIVE_KEY_VERSION: str = os.getenv("SCAMGRAPH_REGISTRY_KEY_VERSION", "v1")
SECRET_KEYS: Dict[str, bytes] = {
    "v1": os.getenv("SCAMGRAPH_REGISTRY_SECRET_V1", "scamgraph_registry_secret_v1_secure_key_2026").encode("utf-8"),
    "v0": os.getenv("SCAMGRAPH_REGISTRY_SECRET_V0", "scamgraph_registry_secret_v0_legacy_key").encode("utf-8"),
}


class IdentifierNormalizer:
    """Type-specific canonical normalization and validation for exact fingerprinting."""

    @staticmethod
    def normalize_phone(raw: str, default_country_code: str = "+91") -> str:
        """Canonicalize phone number into E.164 standard.
        
        Handles leading zeros, spaces, dashes, parentheses, and Indian 10-digit numbers.
        Raises ValueError if raw input is malformed or invalid.
        """
        if not raw or not raw.strip():
            raise ValueError("Phone number cannot be empty.")
            
        clean = re.sub(r"[\s\-\(\)\.]", "", raw.strip())
        
        # Check for invalid non-digit characters (other than leading +)
        digits_only = clean.lstrip("+")
        if not digits_only.isdigit():
            raise ValueError(f"Phone number contains non-digit characters: {raw}")
            
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError(f"Phone number length {len(digits_only)} out of valid E.164 range (7-15 digits): {raw}")

        if clean.startswith("00"):
            clean = "+" + clean[2:]
        elif clean.startswith("0") and len(clean) == 11:
            clean = default_country_code + clean[1:]
        elif not clean.startswith("+"):
            if len(clean) == 10 and clean.isdigit():
                clean = default_country_code + clean
            else:
                clean = default_country_code + clean.lstrip("+")
        return clean

    @staticmethod
    def normalize_upi_vpa(raw: str) -> str:
        """Canonicalize UPI VPA.
        
        Preserves username and PSP handle, normalizes to lowercase, removes whitespace.
        Never blindly strips dots like email normalizers do.
        """
        if not raw or not raw.strip():
            raise ValueError("UPI VPA cannot be empty.")
            
        clean = raw.strip().lower()
        # Remove upi://pay?pa= prefix if QR payload was passed
        if "pa=" in clean:
            match = re.search(r"pa=([^&]+)", clean)
            if match:
                clean = match.group(1).lower()

        if "@" not in clean:
            raise ValueError(f"Invalid UPI VPA: missing '@' delimiter in '{raw}'")
            
        parts = clean.split("@")
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            raise ValueError(f"Invalid UPI VPA structure: '{raw}'")

        return f"{parts[0].strip()}@{parts[1].strip()}"

    @staticmethod
    def normalize_bank_account(raw: str) -> str:
        """Canonicalize bank account as IFSC:ACCOUNT_NUMBER without stripping leading zeros."""
        if not raw or not raw.strip():
            raise ValueError("Bank account cannot be empty.")
            
        clean = raw.strip().upper()
        # Remove hyphens or spaces
        clean = re.sub(r"[\s\-]", "", clean)
        
        if len(clean) < 6:
            raise ValueError(f"Bank account identifier '{raw}' is too short to be valid.")
            
        return clean

    @staticmethod
    def normalize_device_id(raw: str) -> str:
        """Canonicalize Device ID / IMEI / Android ID."""
        if not raw or not raw.strip():
            raise ValueError("Device ID cannot be empty.")
        clean = raw.strip().lower()
        clean = re.sub(r"[\s\-\:]", "", clean)
        return clean

    @staticmethod
    def normalize_ip_address(raw: str) -> str:
        """Canonicalize IPv4 or IPv6 address."""
        if not raw or not raw.strip():
            raise ValueError("IP address cannot be empty.")
        clean = raw.strip()
        # Strip port if provided
        if ":" in clean and not clean.startswith("["):
            parts = clean.split(":")
            if len(parts) == 2 and "." in parts[0]:
                clean = parts[0]
        return clean

    @staticmethod
    def normalize_url_domain(raw: str) -> str:
        """Canonicalize URL / Domain, preserving security-relevant scheme, host, and path."""
        if not raw or not raw.strip():
            raise ValueError("URL / Domain cannot be empty.")
            
        clean = raw.strip().lower()
        if clean.startswith("http://") or clean.startswith("https://"):
            parsed = urlparse(clean)
            scheme = parsed.scheme
            host = parsed.netloc or parsed.path.split("/")[0]
            path = parsed.path.rstrip("/")
            try:
                host = host.encode("idna").decode("ascii")
            except Exception:
                pass
            return f"{scheme}://{host}{path}"
        else:
            parts = clean.split("/", 1)
            host = parts[0]
            path = ("/" + parts[1].rstrip("/")) if len(parts) > 1 and parts[1].strip() else ""
            try:
                host = host.encode("idna").decode("ascii")
            except Exception:
                pass
            return f"{host}{path}"

    @staticmethod
    def normalize_email(raw: str) -> str:
        """Canonicalize email address."""
        if not raw or not raw.strip():
            raise ValueError("Email cannot be empty.")
        clean = raw.strip().lower()
        if "@" not in clean:
            raise ValueError(f"Invalid email: missing '@' in '{raw}'")
            
        parts = clean.split("@", 1)
        local, domain = parts[0].strip(), parts[1].strip()
        if not local or not domain:
            raise ValueError(f"Invalid email structure: '{raw}'")
            
        # For gmail.com, remove dots in local part
        if domain == "gmail.com":
            local = local.replace(".", "")
        return f"{local}@{domain}"

    @staticmethod
    def normalize_transaction_ref(raw: str) -> str:
        """Canonicalize transaction reference token (UTR, RRN, IMPS ref)."""
        if not raw or not raw.strip():
            raise ValueError("Transaction reference cannot be empty.")
        clean = re.sub(r"[\s\-\:\/]", "", raw.strip().upper())
        if len(clean) < 6:
            raise ValueError(f"Transaction reference '{raw}' is too short (min 6 chars).")
        return clean

    @classmethod
    def normalize(cls, identifier_type: IdentifierType, raw_value: str) -> str:
        """Dispatch to appropriate canonical normalizer with alias resolution."""
        # Resolve aliases
        t = identifier_type
        if t in (IdentifierType.PHONE, IdentifierType.PHONE_NUMBER):
            return cls.normalize_phone(raw_value)
        elif t in (IdentifierType.UPI_VPA, IdentifierType.UPI_ID):
            return cls.normalize_upi_vpa(raw_value)
        elif t == IdentifierType.BANK_ACCOUNT:
            return cls.normalize_bank_account(raw_value)
        elif t == IdentifierType.DEVICE_ID:
            return cls.normalize_device_id(raw_value)
        elif t == IdentifierType.IP_ADDRESS:
            return cls.normalize_ip_address(raw_value)
        elif t in (IdentifierType.URL_DOMAIN, IdentifierType.URL, IdentifierType.DOMAIN):
            return cls.normalize_url_domain(raw_value)
        elif t == IdentifierType.EMAIL:
            return cls.normalize_email(raw_value)
        elif t == IdentifierType.TRANSACTION_REF:
            return cls.normalize_transaction_ref(raw_value)
        return raw_value.strip().lower()


class RegistryFingerprinter:
    """Computes keyed HMAC-SHA-256 fingerprints for privacy-preserving exact screening."""

    @classmethod
    def compute_hmac(cls, key: bytes, type_str: str, canonical_val: str) -> str:
        """Deterministic keyed HMAC-SHA-256 over length-delimited payload."""
        payload = f"{type_str}:{canonical_val}".encode("utf-8")
        return hmac.new(key, payload, hashlib.sha256).hexdigest()

    @classmethod
    def generate_fingerprint(
        cls,
        identifier_type: IdentifierType,
        raw_value: str,
        key_version: Optional[str] = None,
    ) -> CanonicalFingerprint:
        """Generate a versioned HMAC-SHA-256 fingerprint from a typed raw identifier."""
        version = key_version or ACTIVE_KEY_VERSION
        secret = SECRET_KEYS.get(version)
        if not secret:
            secret = SECRET_KEYS.get("v1", b"scamgraph_default_key")

        # Canonicalize
        canonical_value = IdentifierNormalizer.normalize(identifier_type, raw_value)
        
        # Primary type value for hashing
        type_str = identifier_type.value
        digest = cls.compute_hmac(secret, type_str, canonical_value)
        fingerprint_str = f"hmac_{version}_{digest}"

        # Masked preview
        masked_preview = cls.mask_value(identifier_type, canonical_value)

        return CanonicalFingerprint(
            identifier_type=identifier_type,
            fingerprint=fingerprint_str,
            key_version=version,
            normalized_preview=masked_preview,
        )

    @classmethod
    def constant_time_matches(cls, fp_candidate: str, fp_target: str) -> bool:
        """Constant-time comparison to prevent timing attacks."""
        return hmac.compare_digest(fp_candidate.encode("utf-8"), fp_target.encode("utf-8"))

    @classmethod
    def generate_all_version_fingerprints(
        cls,
        identifier_type: IdentifierType,
        raw_value: str,
    ) -> List[str]:
        """Generate candidate fingerprints across all active and retired keys for migration search."""
        canonical_val = IdentifierNormalizer.normalize(identifier_type, raw_value)
        type_str = identifier_type.value
        candidates = []
        for v, secret in SECRET_KEYS.items():
            digest = cls.compute_hmac(secret, type_str, canonical_val)
            candidates.append(f"hmac_{v}_{digest}")
        return candidates

    @classmethod
    def mask_value(cls, identifier_type: IdentifierType, canonical: str) -> str:
        """Create privacy-preserving masked preview for admin review without logging raw PII."""
        t = identifier_type
        if t in (IdentifierType.PHONE, IdentifierType.PHONE_NUMBER):
            if len(canonical) >= 6:
                return f"{canonical[:4]}****{canonical[-2:]}"
        elif t in (IdentifierType.UPI_VPA, IdentifierType.UPI_ID):
            if "@" in canonical:
                handle, psp = canonical.split("@", 1)
                prefix = handle[:2] if len(handle) >= 2 else handle
                return f"{prefix}***@{psp}"
        elif t == IdentifierType.BANK_ACCOUNT:
            if ":" in canonical:
                ifsc, acc = canonical.split(":", 1)
                return f"{ifsc}:****{acc[-4:] if len(acc) >= 4 else acc}"
            return f"****{canonical[-4:] if len(canonical) >= 4 else canonical}"
        elif t == IdentifierType.EMAIL:
            if "@" in canonical:
                user, dom = canonical.split("@", 1)
                return f"{user[:2]}***@{dom}"
        elif t == IdentifierType.TRANSACTION_REF:
            return f"{canonical[:3]}****{canonical[-3:] if len(canonical) >= 6 else ''}"
        return canonical[:3] + "***" if len(canonical) > 3 else "***"
