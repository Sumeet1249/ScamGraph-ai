"""Deterministic Entity Extractor for ScamGraph AI V2 (Prompt 6).

Extracts phones, emails, URLs, domains, UPI VPAs, Telegram handles, and brands
with exact character spans, extraction confidence, and preliminary roles.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from packages.schemas.entity import EntityObservationRole, EntityType
from services.entity_intelligence.normalizer import EntityNormalizer, NormalizedEntityResult


class ExtractedEntityCandidate(BaseModel):
    """An entity detected in raw text before full database resolution."""
    entity_type: EntityType
    raw_value: str
    normalized_result: NormalizedEntityResult
    span_start: int
    span_end: int
    suggested_role: EntityObservationRole = EntityObservationRole.UNKNOWN
    extraction_confidence: float = 1.0


class EntityExtractor:
    """Multi-regex deterministic entity extractor with context-aware role suggestion."""

    # Regex patterns
    URL_REGEX = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+|[a-zA-Z0-9-]+\.(?:top|xyz|in|cc|online|site|app|live|vip|club|click|work)/[^\s<>\"']*")
    EMAIL_REGEX = re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
    UPI_REGEX = re.compile(r"\b[a-zA-Z0-9_.+-]+@(oksbi|okhdfcbank|okicici|okaxis|paytm|apl|ybl|ibl|axl|upi)\b", re.IGNORECASE)
    TELEGRAM_REGEX = re.compile(r"(?:https?://)?(?:www\.)?t\.me/([a-zA-Z0-9_]{5,32})|@([a-zA-Z0-9_]{5,32})", re.IGNORECASE)
    INDIAN_PHONE_REGEX = re.compile(r"(?:\+91[\s-]?)?[6789]\d{9}\b|\b0[6789]\d{9}\b")
    IFSC_REGEX = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")

    BRAND_PATTERNS = {
        "SBI": re.compile(r"\b(sbi|state bank|yono)\b", re.IGNORECASE),
        "HDFC": re.compile(r"\b(hdfc|hdfcbank)\b", re.IGNORECASE),
        "ICICI": re.compile(r"\b(icici|imobile)\b", re.IGNORECASE),
        "POLICE": re.compile(r"\b(police|cbi|crime branch|cyber cell|high court)\b", re.IGNORECASE),
        "ELECTRICITY": re.compile(r"\b(electricity|discom|bijli vibhag)\b", re.IGNORECASE),
        "TELECOM": re.compile(r"\b(trai|airtel|jio|vi-india)\b", re.IGNORECASE),
    }

    @classmethod
    def extract_all(cls, text: str) -> List[ExtractedEntityCandidate]:
        """Extracts all entities present in a text string."""
        if not text:
            return []

        candidates: List[ExtractedEntityCandidate] = []
        lower = text.lower()

        # 1. URLs
        for m in cls.URL_REGEX.finditer(text):
            raw = m.group(0)
            norm = EntityNormalizer.normalize_url(raw)
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.URL,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.REDIRECT_TARGET,
                extraction_confidence=0.98,
            ))
            # Also extract host domain as a separate DOMAIN entity
            host = norm.extra_metadata.get("host_domain")
            if host:
                norm_domain = EntityNormalizer.normalize_domain(host)
                candidates.append(ExtractedEntityCandidate(
                    entity_type=EntityType.DOMAIN,
                    raw_value=host,
                    normalized_result=norm_domain,
                    span_start=m.start(),
                    span_end=m.end(),
                    suggested_role=EntityObservationRole.HOST,
                    extraction_confidence=0.95,
                ))

        # 2. UPI VPAs
        for m in cls.UPI_REGEX.finditer(text):
            raw = m.group(0)
            norm = EntityNormalizer.normalize_upi_vpa(raw)
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.UPI_VPA,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.PAYMENT_RECIPIENT,
                extraction_confidence=0.99,
            ))

        # 3. Emails
        for m in cls.EMAIL_REGEX.finditer(text):
            raw = m.group(0)
            # Skip if it was already captured as a UPI VPA
            if any(c.entity_type == EntityType.UPI_VPA and c.raw_value.lower() == raw.lower() for c in candidates):
                continue
            norm = EntityNormalizer.normalize_email(raw)
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.EMAIL,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.CONTACT_POINT,
                extraction_confidence=0.95,
            ))

        # 4. Telegram Handles
        for m in cls.TELEGRAM_REGEX.finditer(text):
            raw = m.group(0)
            norm = EntityNormalizer.normalize_telegram_handle(raw)
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.TELEGRAM_HANDLE,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.SOCIAL_PROFILE,
                extraction_confidence=0.95,
            ))

        # 5. Phone numbers
        for m in cls.INDIAN_PHONE_REGEX.finditer(text):
            raw = m.group(0)
            norm = EntityNormalizer.normalize_phone(raw)
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.PHONE,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.CONTACT_POINT,
                extraction_confidence=0.95,
            ))

        # 6. IFSC Codes
        for m in cls.IFSC_REGEX.finditer(text):
            raw = m.group(0)
            from packages.utils.privacy import canonical_hash
            norm = NormalizedEntityResult(
                entity_type=EntityType.IFSC,
                raw_value=raw,
                normalized_value=raw.upper(),
                display_value=raw.upper(),
                canonical_hash=canonical_hash(raw.upper()),
                validation_status=norm.validation_status.VALID,
                confidence=1.0,
            )
            candidates.append(ExtractedEntityCandidate(
                entity_type=EntityType.IFSC,
                raw_value=raw,
                normalized_result=norm,
                span_start=m.start(),
                span_end=m.end(),
                suggested_role=EntityObservationRole.PAYMENT_RECIPIENT,
                extraction_confidence=0.98,
            ))

        # 7. Brands / Claimed Organizations
        for brand_key, pattern in cls.BRAND_PATTERNS.items():
            for m in pattern.finditer(text):
                raw = m.group(0)
                norm = EntityNormalizer.normalize_brand(raw)
                role = EntityObservationRole.CLAIMED_AUTHORITY if brand_key in ("POLICE", "CBI", "ELECTRICITY") else EntityObservationRole.BRAND_REFERENCE
                candidates.append(ExtractedEntityCandidate(
                    entity_type=EntityType.BRAND,
                    raw_value=raw,
                    normalized_result=norm,
                    span_start=m.start(),
                    span_end=m.end(),
                    suggested_role=role,
                    extraction_confidence=0.90,
                ))

        return candidates
