"""Cross-Victim & Cross-Incident Correlation Engine (Phase 3B).

Provides privacy-safe network intelligence, explainable relationship scoring,
super-node downweighting, and candidate campaign grouping.
"""

from services.correlation_engine.config import CorrelationConfig
from services.correlation_engine.features import CorrelationFeatureExtractor
from services.correlation_engine.retriever import CandidateRetriever
from services.correlation_engine.scorer import CorrelationScorer
from services.correlation_engine.serializer import CorrelationSerializer
from services.correlation_engine.service import (
    CrossIncidentCorrelationService,
    correlation_service,
)

__all__ = [
    "CorrelationConfig",
    "CandidateRetriever",
    "CorrelationFeatureExtractor",
    "CorrelationScorer",
    "CorrelationSerializer",
    "CrossIncidentCorrelationService",
    "correlation_service",
]
