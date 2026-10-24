"""Entity Correlation Interface for Neo4j Evidence Graph.

Correlates incidents via shared infrastructure, payment entities, and communication channels.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from services.graph_engine.correlation.entity_service import (
    EntityCorrelationReport,
    EntityCorrelationService,
)
from services.graph_engine.neo4j.repository import GraphRepository, graph_repository

logger = logging.getLogger("graph_engine.correlation")


class EntityCorrelation:
    """Convenience interface for performing entity correlation on incidents."""

    def __init__(self, repo: Optional[GraphRepository] = None):
        self.repo = repo or graph_repository
        self.service = EntityCorrelationService(repo=self.repo)

    async def correlate(self, incident_id: str) -> EntityCorrelationReport:
        """Generate correlation report including shared entity counts and evidence signals."""
        return await self.service.correlate_incident(incident_id)

    async def get_related_incidents(self, incident_id: str) -> List[Dict[str, Any]]:
        """Retrieve incidents that share one or more entities with this incident."""
        return await self.repo.find_related_incidents(incident_id)

    async def get_shared_entities(self, incident_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve map of entity types and shared counts."""
        return await self.repo.find_shared_entities(incident_id)


# Default singleton instance
entity_correlation = EntityCorrelation()
