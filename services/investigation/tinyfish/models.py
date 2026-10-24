"""Models and interfaces for WebInvestigator and TinyFish (Step 17)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.api.app.domain.models import Entity, Evidence


class TinyFishObservationData(BaseModel):
    """Structured observable facts extracted by TinyFish."""
    page_title: Optional[str] = None
    claimed_brands: List[str] = Field(default_factory=list)
    login_fields: List[str] = Field(default_factory=list)
    credential_fields: List[str] = Field(default_factory=list)
    otp_fields: List[str] = Field(default_factory=list)
    payment_fields: List[str] = Field(default_factory=list)
    personal_information_fields: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    email_addresses: List[str] = Field(default_factory=list)
    payment_identifiers: List[str] = Field(default_factory=list)
    linked_domains: List[str] = Field(default_factory=list)
    redirects: List[Dict[str, Any]] = Field(default_factory=list)
    urgency_claims: List[str] = Field(default_factory=list)
    financial_claims: List[str] = Field(default_factory=list)
    brand_impersonation_observations: List[str] = Field(default_factory=list)
    observable_actions: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class WebInvestigationResult(BaseModel):
    """Standardized output from any WebInvestigator provider."""
    provider: str = "TINYFISH"
    status: str  # "completed", "unavailable", "partial", "rejected"
    inspected_url: str
    observables: Optional[TinyFishObservationData] = None
    evidence: List[Evidence] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    duration_ms: float = 0.0


class WebInvestigator(ABC):
    """Abstract interface for external web page investigation providers."""

    @abstractmethod
    async def investigate(
        self,
        incident_id: str,
        target_url: str,
    ) -> WebInvestigationResult:
        """Inspects an external landing page and returns factual observations."""
        pass
