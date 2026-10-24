"""Campaign Correlation Service (Step 16).

Correlates incidents with known campaign nodes and detected infrastructure clusters.
"""

from typing import Any, Dict, List, Optional
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
from services.graph_engine.neo4j.repository import GraphRepository, graph_repository


class CampaignCorrelationService:
    """Manages graph-based campaign associations and cluster detection."""

    def __init__(self, repo: Optional[GraphRepository] = None):
        self.repo = repo or graph_repository

    async def find_candidate_campaigns(self, incident_id: str) -> List[Dict[str, Any]]:
        """Queries graph for campaigns directly linked or linked via high-degree infrastructure."""
        return await self.repo.find_candidate_campaigns(incident_id)

    async def link_incident_to_campaign(
        self,
        incident_id: str,
        campaign_id: str,
        confidence: float = 0.85,
    ) -> Dict[str, Any]:
        """Creates (:Incident)-[:PART_OF_CAMPAIGN {confidence}]->(:Campaign)."""
        query = """
        MATCH (i:Incident {id: $incident_id})
        MERGE (c:Campaign {id: $campaign_id})
        MERGE (i)-[r:PART_OF_CAMPAIGN]->(c)
        ON CREATE SET r.confidence = $confidence, r.linkedAt = datetime()
        RETURN c.id as campaign_id
        """
        records = await self.repo.client.execute_query(
            query,
            {"incident_id": incident_id, "campaign_id": campaign_id, "confidence": confidence},
        )
        return records[0] if records else {"campaign_id": campaign_id}


# Global instance
campaign_correlation_service = CampaignCorrelationService()
