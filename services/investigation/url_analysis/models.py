"""Data models for URL Safety and Infrastructure Intelligence (Step 16)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.api.app.domain.models import Entity, Evidence


class NormalizedURL(BaseModel):
    """Standardized representation of an inspected URL."""
    original_url: str
    normalized_url: str
    scheme: str
    hostname: str
    port: Optional[int] = None
    path: str = "/"
    query: Optional[str] = None
    registered_domain: str
    is_ip_host: bool = False


class SafetyResult(BaseModel):
    """Structured security outcome from URL safety validation."""
    is_safe: bool
    resolved_ips: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    blocked_range: Optional[str] = None
    is_private: bool = False
    is_loopback: bool = False
    is_metadata_endpoint: bool = False


class URLFeatureSet(BaseModel):
    """Deterministic lexical features extracted from a URL for ML consumption."""
    url_length: int
    hostname_length: int
    path_length: int
    number_of_dots: int
    number_of_hyphens: int
    number_of_digits: int
    subdomain_count: int
    has_ip_hostname: bool
    has_punycode: bool
    https_scheme: bool
    hostname_entropy: float
    suspicious_token_count: int
    encoded_character_count: int
    query_parameter_count: int


class URLInvestigationResult(BaseModel):
    """Consolidated outcome of the URL investigation pipeline."""
    investigation_id: str
    status: str  # "completed", "partial", "rejected"
    normalized_url: Optional[NormalizedURL] = None
    safety: SafetyResult
    features: Optional[URLFeatureSet] = None
    entities: List[Entity] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    partial_results: bool = False
    duration_ms: float = 0.0
    ml_prediction: Optional[Dict[str, Any]] = None
