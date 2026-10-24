"""Common foundational enums, identifiers, and utility types for ScamGraph AI V2."""

from enum import Enum
from typing import Optional
from uuid import uuid4


def generate_id(prefix: str) -> str:
    """Generate a collision-resistant, non-sequential stable ID with a semantic prefix.
    
    Examples:
        generate_id("art") -> "art_9b1deb4d3b7d4e89"
        generate_id("inc") -> "inc_4a7c1b2f90124def"
    """
    clean_prefix = prefix.rstrip("_")
    unique_hex = uuid4().hex[:16]
    return f"{clean_prefix}_{unique_hex}"


class RiskLevelV2(str, Enum):
    """Canonical graded risk assessment levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_legacy(cls, legacy_val: str) -> "RiskLevelV2":
        mapping = {
            "LOW": cls.LOW,
            "MEDIUM": cls.MEDIUM,
            "HIGH": cls.HIGH,
            "CRITICAL": cls.CRITICAL,
            "UNKNOWN": cls.UNKNOWN,
        }
        return mapping.get(str(legacy_val).upper(), cls.UNKNOWN)


class ConfidenceLevelV2(str, Enum):
    """Canonical evidence confidence levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_legacy(cls, legacy_val: str) -> "ConfidenceLevelV2":
        mapping = {
            "LOW": cls.LOW,
            "MEDIUM": cls.MEDIUM,
            "HIGH": cls.HIGH,
            "UNKNOWN": cls.UNKNOWN,
        }
        return mapping.get(str(legacy_val).upper(), cls.UNKNOWN)


class UrgencyLevelV2(str, Enum):
    """Degree of temporal manipulation or immediate victim coercion pressure."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PrivacyClassification(str, Enum):
    """Privacy sensitivity tier for data minimization and PII protection."""
    PUBLIC = "PUBLIC"              # e.g., Public domain, registered bank IFSC, official portal URL
    INTERNAL = "INTERNAL"          # e.g., Internal system correlation ID, detector telemetry
    PERSONAL = "PERSONAL"          # e.g., Raw phone number, victim display name
    SENSITIVE = "SENSITIVE"        # e.g., UPI VPA, detailed chat messages, voice transcripts
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE" # e.g., Bank account tokens, OTPs, PINs, Aadhaar numbers
