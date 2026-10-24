"""ScamGraph AI Graph Engine package."""

from services.graph_engine.algorithms.graph_analytics import (
    GraphAnalyticsService,
    graph_analytics_service,
)
from services.graph_engine.correlation.entity_correlation import (
    EntityCorrelation,
    entity_correlation,
)
from services.graph_engine.models.graph_models import (
    GraphCorrelationResult,
    GraphEntityNode,
    GraphNodeType,
    GraphRelationshipType,
    GraphSyncResult,
    IncidentNode,
    RelationshipProvenance,
)
from services.graph_engine.neo4j.client import Neo4jClient, neo4j_client
from services.graph_engine.neo4j.migrations import apply_migrations
from services.graph_engine.neo4j.repository import (
    GraphRepository,
    Neo4jGraphRepository,
    graph_repository,
)
from services.graph_engine.normalization.entity_normalizer import (
    EntityNormalizer,
    entity_normalizer,
)
from services.graph_engine.sync.graph_sync_service import (
    GraphSyncService,
    graph_sync_service,
)

__all__ = [
    "Neo4jClient",
    "neo4j_client",
    "GraphRepository",
    "Neo4jGraphRepository",
    "graph_repository",
    "apply_migrations",
    "EntityNormalizer",
    "entity_normalizer",
    "EntityCorrelation",
    "entity_correlation",
    "GraphSyncService",
    "graph_sync_service",
    "GraphAnalyticsService",
    "graph_analytics_service",
    "GraphNodeType",
    "GraphRelationshipType",
    "RelationshipProvenance",
    "IncidentNode",
    "GraphEntityNode",
    "GraphSyncResult",
    "GraphCorrelationResult",
]
