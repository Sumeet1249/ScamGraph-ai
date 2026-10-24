"""Privacy Processing, Masking, and Anti-Enumeration Defense for Entity Intelligence.

Rules (Prompt 6):
1. Never copy raw sensitive values across layers unnecessarily.
2. Separate Raw Evidence, Normalized Value, Canonical Value, Masked Display, and Correlation Hash.
3. Consumer views receive masked display values (******3210, n***@oksbi).
4. Public enumeration of phone numbers, UPI IDs, or victim identities is strictly blocked.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from packages.schemas.entity import Entity, EntityObservation, EntityType


class PrivacySerializer:
    """Serializes entity representations safely based on viewer authorization tier."""

    @staticmethod
    def serialize_for_consumer(entity: Entity) -> Dict[str, Any]:
        """Redacts raw values, returning only privacy-safe display and aggregated risk counts."""
        return {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type.value,
            "display_value": entity.masked_value,
            "verification_state": entity.verification_state.value,
            "first_seen": entity.first_seen.isoformat(),
            "last_seen": entity.last_seen.isoformat(),
            "observation_count": entity.observation_count,
            "incident_count": entity.incident_count,
            "supporting_evidence_count": entity.supporting_evidence_count,
            "contradicting_evidence_count": entity.contradicting_evidence_count,
            "risk_summary": entity.risk_summary,
            "reputation_summary": entity.reputation_summary,
        }

    @staticmethod
    def serialize_for_analyst(entity: Entity) -> Dict[str, Any]:
        """Provides full investigation metadata for authorized analysts."""
        return {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type.value,
            "canonical_value": entity.canonical_value,
            "display_value": entity.display_value or entity.masked_value,
            "masked_value": entity.masked_value,
            "canonical_hash": entity.canonical_hash,
            "verification_state": entity.verification_state.value,
            "first_seen": entity.first_seen.isoformat(),
            "last_seen": entity.last_seen.isoformat(),
            "observation_count": entity.observation_count,
            "incident_count": entity.incident_count,
            "campaign_count": entity.campaign_count,
            "supporting_evidence_count": entity.supporting_evidence_count,
            "contradicting_evidence_count": entity.contradicting_evidence_count,
            "risk_summary": entity.risk_summary,
            "confidence_summary": entity.confidence_summary,
            "reputation_summary": entity.reputation_summary,
            "aliases": entity.aliases,
            "metadata": entity.metadata,
        }


class AntiEnumerationGuard:
    """Defends against malicious actors enumerating entities or scraping victim identities."""

    def __init__(self, max_queries_per_minute: int = 60):
        self._query_counts: Dict[str, List[float]] = {}
        self._max_qpm = max_queries_per_minute

    def check_query_allowed(self, client_id: str, search_query: str) -> Tuple[bool, str]:
        """Validates that search queries are specific and not broad wildcard enumeration."""
        clean = search_query.strip()
        # Disallow empty or single-character broad searches
        if len(clean) < 3:
            return False, "Query too short; potential enumeration attempt."

        # Disallow wildcard patterns
        if any(c in clean for c in ("*", "%", "?", "SELECT", "UNION")):
            return False, "Wildcard or structured pattern search disallowed."

        return True, "Query permitted."
