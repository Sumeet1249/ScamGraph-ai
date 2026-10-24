"""Advanced Deterministic Entity Normalizers for ScamGraph AI V2 (Prompt 6).

Implements strict canonical normalization, IDNA/Punycode handling, format validation status,
and non-destructive preservation of raw evidence.
"""

from __future__ import annotations

import re
import unicodedata
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
from pydantic import BaseModel, Field

from packages.schemas.entity import EntityType


class FormatValidationStatus(str, Enum):
    """Syntactic validity of an entity format (Rule: Format Validity != Fraud!)."""
    VALID = "VALID"
    POSSIBLY_VALID = "POSSIBLY_VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class NormalizedEntityResult(BaseModel):
    """Result of normalizing an atomic identifier."""
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    display_value: str
    canonical_hash: str
    validation_status: FormatValidationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityNormalizer:
    """Multi-type canonical normalizer for Indian and international identifiers."""

    # -------------------------------------------------------------------------
    # 1. PHONE NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_phone(raw_phone: str) -> NormalizedEntityResult:
        """Normalizes phone numbers, specifically handling Indian mobile number conventions.
        
        Rules:
        - 10 digits starting with 6, 7, 8, 9 is standard Indian mobile.
        - Strips spaces, dashes, dots, parentheses.
        - Strips leading zero or +91 / 91 prefix.
        - Never silently invents a country code for ambiguous international numbers.
        """
        from packages.utils.privacy import canonical_hash, mask_phone

        raw_clean = str(raw_phone or "").strip()
        digits = re.sub(r"\D", "", raw_clean)

        status = FormatValidationStatus.UNKNOWN
        normalized = ""
        confidence = 0.5
        extra: Dict[str, Any] = {}

        if not digits:
            status = FormatValidationStatus.INVALID
            confidence = 1.0
        elif len(digits) == 10 and digits[0] in "6789":
            normalized = f"+91{digits}"
            status = FormatValidationStatus.VALID
            confidence = 1.0
            extra["country"] = "IN"
            extra["is_indian_mobile"] = True
        elif len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
            normalized = f"+91{digits[1:]}"
            status = FormatValidationStatus.VALID
            confidence = 1.0
            extra["country"] = "IN"
            extra["is_indian_mobile"] = True
        elif len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
            normalized = f"+91{digits[2:]}"
            status = FormatValidationStatus.VALID
            confidence = 1.0
            extra["country"] = "IN"
            extra["is_indian_mobile"] = True
        elif raw_clean.startswith("+") and len(digits) >= 8:
            # Explicit international number with plus
            normalized = f"+{digits}"
            status = FormatValidationStatus.POSSIBLY_VALID
            confidence = 0.85
            extra["is_international"] = True
        elif len(digits) >= 10:
            # Ambiguous without plus - do not guess country
            normalized = digits
            status = FormatValidationStatus.POSSIBLY_VALID
            confidence = 0.60
            extra["ambiguous_country"] = True
        else:
            normalized = digits
            status = FormatValidationStatus.INVALID
            confidence = 0.90

        if extra.get("is_indian_mobile") and len(digits) >= 10:
            display = f"******{digits[-4:]}"
        else:
            display = mask_phone(normalized or raw_clean)
        hash_val = canonical_hash(normalized or raw_clean)

        return NormalizedEntityResult(
            entity_type=EntityType.PHONE,
            raw_value=raw_clean,
            normalized_value=normalized,
            display_value=display,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 2. EMAIL NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_email(raw_email: str) -> NormalizedEntityResult:
        """Normalizes email addresses with lowercase domain, Unicode NFC, and whitespace trimming."""
        from packages.utils.privacy import canonical_hash, mask_email

        raw_clean = unicodedata.normalize("NFC", str(raw_email or "").strip())
        status = FormatValidationStatus.UNKNOWN
        confidence = 0.5
        normalized = ""
        extra: Dict[str, Any] = {}

        email_regex = r"^([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$"
        match = re.match(email_regex, raw_clean)

        if match:
            local_part = match.group(1).strip().lower()
            domain_part = match.group(2).strip().lower()
            normalized = f"{local_part}@{domain_part}"
            status = FormatValidationStatus.VALID
            confidence = 1.0
            extra["domain"] = domain_part
        elif "@" in raw_clean:
            parts = raw_clean.rsplit("@", 1)
            normalized = f"{parts[0].strip().lower()}@{parts[1].strip().lower()}"
            status = FormatValidationStatus.POSSIBLY_VALID
            confidence = 0.70
        else:
            normalized = raw_clean.lower()
            status = FormatValidationStatus.INVALID
            confidence = 0.95

        display = mask_email(normalized or raw_clean)
        hash_val = canonical_hash(normalized or raw_clean)

        return NormalizedEntityResult(
            entity_type=EntityType.EMAIL,
            raw_value=raw_clean,
            normalized_value=normalized,
            display_value=display,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 3. DOMAIN & IDNA/PUNYCODE NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_domain(raw_domain: str) -> NormalizedEntityResult:
        """Normalizes domains with IDNA/Punycode handling, subdomain separation, and root domain parsing."""
        from packages.utils.privacy import canonical_hash

        raw_clean = unicodedata.normalize("NFKC", str(raw_domain or "").strip())
        display = raw_clean
        extra: Dict[str, Any] = {}

        # Strip protocol or slashes if accidentally included
        cleaned = raw_clean.lower()
        if "://" in cleaned:
            cleaned = urlparse(cleaned).netloc or cleaned
        if "/" in cleaned:
            cleaned = cleaned.split("/")[0]
        if ":" in cleaned:
            cleaned = cleaned.split(":")[0]
        cleaned = cleaned.rstrip(".")

        # Strip www. for canonical representation
        if cleaned.startswith("www."):
            cleaned = cleaned[4:]

        # IDNA encoding (detects Unicode homoglyphs / punycode)
        punycode = ""
        try:
            punycode = cleaned.encode("idna").decode("ascii")
            if punycode != cleaned:
                extra["has_punycode_homoglyph"] = True
                extra["punycode"] = punycode
        except Exception:
            extra["idna_error"] = True

        # Extract root domain / TLD
        parts = cleaned.split(".")
        if len(parts) >= 2:
            extra["tld"] = parts[-1]
            extra["root_domain"] = f"{parts[-2]}.{parts[-1]}"
            if len(parts) > 2:
                extra["subdomain"] = ".".join(parts[:-2])
            status = FormatValidationStatus.VALID
            confidence = 0.95
        else:
            status = FormatValidationStatus.POSSIBLY_VALID
            confidence = 0.50

        hash_val = canonical_hash(cleaned)

        return NormalizedEntityResult(
            entity_type=EntityType.DOMAIN,
            raw_value=raw_clean,
            normalized_value=cleaned,
            display_value=display,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 4. URL NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_url(raw_url: str) -> NormalizedEntityResult:
        """Normalizes URLs with deterministic query parameter sorting, fragment removal, and port stripping."""
        from packages.utils.privacy import canonical_hash

        raw_clean = str(raw_url or "").strip()
        url_to_parse = raw_clean
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url_to_parse):
            url_to_parse = f"https://{url_to_parse}"

        extra: Dict[str, Any] = {}
        try:
            parsed = urlparse(url_to_parse)
            scheme = (parsed.scheme or "https").lower()
            netloc = (parsed.netloc or "").lower()

            # Strip default ports
            if scheme == "http" and netloc.endswith(":80"):
                netloc = netloc[:-3]
            elif scheme == "https" and netloc.endswith(":443"):
                netloc = netloc[:-4]

            # Strip www from netloc for canonical match
            canonical_netloc = netloc[4:] if netloc.startswith("www.") else netloc

            # Path normalization
            path = parsed.path or "/"
            path = re.sub(r"/+", "/", path)
            if len(path) > 1 and path.endswith("/"):
                path = path.rstrip("/")

            # Sorted query parameters
            query_str = ""
            if parsed.query:
                qs = parse_qs(parsed.query, keep_blank_values=True)
                sorted_qs = sorted(qs.items())
                pairs = []
                for k, vals in sorted_qs:
                    for v in sorted(vals):
                        pairs.append((k, v))
                query_str = f"?{urlencode(pairs)}"

            normalized = f"{scheme}://{canonical_netloc}{path}{query_str}"
            status = FormatValidationStatus.VALID
            confidence = 1.0
            extra["host_domain"] = canonical_netloc
        except Exception as e:
            normalized = raw_clean.lower()
            status = FormatValidationStatus.INVALID
            confidence = 0.5
            extra["error"] = str(e)

        hash_val = canonical_hash(normalized)

        return NormalizedEntityResult(
            entity_type=EntityType.URL,
            raw_value=raw_clean,
            normalized_value=normalized,
            display_value=raw_clean,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 5. UPI VPA NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_upi_vpa(raw_vpa: str) -> NormalizedEntityResult:
        """Normalizes UPI VPAs (e.g., user@oksbi, payment@paytm).
        
        Rule: Never claim ownership from VPA text alone (policehelp@upi does not prove police ownership).
        """
        from packages.utils.privacy import canonical_hash, mask_vpa

        raw_clean = str(raw_vpa or "").strip()
        cleaned = raw_clean.lower()
        extra: Dict[str, Any] = {}

        if "@" in cleaned:
            parts = cleaned.rsplit("@", 1)
            handle = parts[0].strip()
            psp = parts[1].strip()
            normalized = f"{handle}@{psp}"
            extra["handle"] = handle
            extra["psp"] = psp

            # Check if PSP is a known Indian banking PSP handle
            known_psps = {"okaxis", "okhdfcbank", "okicici", "oksbi", "paytm", "apl", "ybl", "ibl", "axl"}
            if psp in known_psps or len(psp) >= 3:
                status = FormatValidationStatus.VALID
                confidence = 1.0
            else:
                status = FormatValidationStatus.POSSIBLY_VALID
                confidence = 0.75
        else:
            normalized = cleaned
            status = FormatValidationStatus.INVALID
            confidence = 0.95

        display = mask_vpa(normalized)
        hash_val = canonical_hash(normalized)

        return NormalizedEntityResult(
            entity_type=EntityType.UPI_VPA,
            raw_value=raw_clean,
            normalized_value=normalized,
            display_value=display,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 6. TELEGRAM & SOCIAL HANDLE NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_telegram_handle(raw_handle: str) -> NormalizedEntityResult:
        """Normalizes Telegram handle, stripping @, t.me/ prefixes, and lowercasing."""
        from packages.utils.privacy import canonical_hash

        raw_clean = str(raw_handle or "").strip()
        cleaned = raw_clean.lower()

        # Handle t.me/ prefixes
        if "t.me/" in cleaned:
            cleaned = cleaned.split("t.me/")[-1].split("/")[0]
        elif cleaned.startswith("@"):
            cleaned = cleaned[1:]

        cleaned = cleaned.strip()

        extra: Dict[str, Any] = {
            "platform": "TELEGRAM",
            "profile_url": f"https://t.me/{cleaned}" if cleaned else "",
        }

        # Telegram usernames are 5-32 alphanumeric + underscores
        if re.match(r"^[a-zA-Z0-9_]{5,32}$", cleaned):
            status = FormatValidationStatus.VALID
            confidence = 1.0
        elif cleaned:
            status = FormatValidationStatus.POSSIBLY_VALID
            confidence = 0.70
        else:
            status = FormatValidationStatus.INVALID
            confidence = 1.0

        normalized = f"@{cleaned}" if cleaned else ""
        display = f"@{cleaned}" if cleaned else ""
        hash_val = canonical_hash(normalized)

        return NormalizedEntityResult(
            entity_type=EntityType.TELEGRAM_HANDLE,
            raw_value=raw_clean,
            normalized_value=normalized,
            display_value=display,
            canonical_hash=hash_val,
            validation_status=status,
            confidence=confidence,
            extra_metadata=extra,
        )

    # -------------------------------------------------------------------------
    # 7. BRAND / ORGANIZATION NORMALIZATION
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_brand(raw_brand: str) -> NormalizedEntityResult:
        """Normalizes brand references and maps common aliases to canonical Indian entity names."""
        from packages.utils.privacy import canonical_hash

        raw_clean = str(raw_brand or "").strip()
        cleaned = raw_clean.lower()

        brand_alias_map = {
            "sbi": ("State Bank of India", "SBI", "BANK"),
            "state bank": ("State Bank of India", "SBI", "BANK"),
            "yono": ("SBI YONO", "YONO", "BANK_APP"),
            "hdfc": ("HDFC Bank", "HDFC", "BANK"),
            "hdfcbank": ("HDFC Bank", "HDFC", "BANK"),
            "icici": ("ICICI Bank", "ICICI", "BANK"),
            "imobile": ("ICICI iMobile", "ICICI", "BANK_APP"),
            "pnb": ("Punjab National Bank", "PNB", "BANK"),
            "paytm": ("Paytm Payments Bank", "PAYTM", "FINTECH"),
            "gpay": ("Google Pay", "GPAY", "PSP"),
            "google pay": ("Google Pay", "GPAY", "PSP"),
            "phonepe": ("PhonePe", "PHONEPE", "PSP"),
            "cbi": ("Central Bureau of Investigation", "CBI", "LAW_ENFORCEMENT"),
            "police": ("Police Department", "POLICE", "LAW_ENFORCEMENT"),
            "electricity": ("State Electricity Board / DISCOM", "DISCOM", "UTILITY"),
            "discom": ("State Electricity Board / DISCOM", "DISCOM", "UTILITY"),
            "bijli vibhag": ("State Electricity Board / DISCOM", "DISCOM", "UTILITY"),
            "income tax": ("Income Tax Department India", "INCOME_TAX", "GOVERNMENT"),
            "trai": ("Telecom Regulatory Authority of India", "TRAI", "REGULATOR"),
        }

        canonical_name = raw_clean
        ticker = ""
        category = "UNKNOWN"

        for alias, (full_name, t, cat) in brand_alias_map.items():
            if alias in cleaned:
                canonical_name = full_name
                ticker = t
                category = cat
                break

        hash_val = canonical_hash(canonical_name.lower())

        return NormalizedEntityResult(
            entity_type=EntityType.BRAND,
            raw_value=raw_clean,
            normalized_value=canonical_name,
            display_value=canonical_name,
            canonical_hash=hash_val,
            validation_status=FormatValidationStatus.VALID,
            confidence=0.95,
            extra_metadata={"ticker": ticker, "category": category},
        )
