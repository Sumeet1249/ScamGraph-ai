"""Canonical Domain Enums for ScamGraph AI (Step 10).

Defines standard vocabulary shared across TinyFish, ML, Neo4j, URL Intelligence,
and Semantic Signal Processing.
"""

from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ASSESSED = "ASSESSED"
    CLOSED = "CLOSED"


class EventType(str, Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    CALL_REPORTED = "CALL_REPORTED"
    URL_RECEIVED = "URL_RECEIVED"
    URL_OPENED = "URL_OPENED"
    CREDENTIAL_REQUEST = "CREDENTIAL_REQUEST"
    OTP_REQUEST = "OTP_REQUEST"
    QR_RECEIVED = "QR_RECEIVED"
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    PAYMENT_INTENT = "PAYMENT_INTENT"
    PAYMENT_REPORTED = "PAYMENT_REPORTED"
    OTHER = "OTHER"


class EntityType(str, Enum):
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    URL = "URL"
    DOMAIN = "DOMAIN"
    IP = "IP"
    ASN = "ASN"
    BRAND = "BRAND"
    PAYMENT_ENTITY = "PAYMENT_ENTITY"
    CERTIFICATE = "CERTIFICATE"
    NAMESERVER = "NAMESERVER"


class EvidenceSource(str, Enum):
    USER_INPUT = "USER_INPUT"
    MESSAGE_ANALYZER = "MESSAGE_ANALYZER"
    URL_ANALYZER = "URL_ANALYZER"
    TINYFISH = "TINYFISH"
    DNS = "DNS"
    RDAP = "RDAP"
    TLS = "TLS"
    THREAT_INTELLIGENCE = "THREAT_INTELLIGENCE"
    GRAPH_ENGINE = "GRAPH_ENGINE"
    PATTERN_ENGINE = "PATTERN_ENGINE"
    PAYMENT_MODEL = "PAYMENT_MODEL"
    SIMULATOR = "SIMULATOR"


class InterventionType(str, Enum):
    NONE = "NONE"
    PASSIVE = "PASSIVE"
    CAUTION = "CAUTION"
    STRONG_WARNING = "STRONG_WARNING"
    PRE_PAYMENT_INTERVENTION = "PRE_PAYMENT_INTERVENTION"


class MatchLevel(str, Enum):
    NONE = "NONE"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
