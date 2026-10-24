"""Model Task Taxonomy and Computational Cost Classes for ScamGraph AI.

Establishes formal boundaries so that specialist models are evaluated and routed
for specific tasks rather than assuming a single monolithic model handles everything.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModelTask(str, Enum):
    """Explicit AI tasks within the ScamGraph intelligence pipeline."""
    MESSAGE_SCAM_CLASSIFICATION = "MESSAGE_SCAM_CLASSIFICATION"
    SEMANTIC_EMBEDDING = "SEMANTIC_EMBEDDING"
    LANGUAGE_IDENTIFICATION = "LANGUAGE_IDENTIFICATION"
    ENTITY_EXTRACTION = "ENTITY_EXTRACTION"
    TACTIC_CLASSIFICATION = "TACTIC_CLASSIFICATION"
    SCAM_FAMILY_CLASSIFICATION = "SCAM_FAMILY_CLASSIFICATION"
    JOURNEY_STAGE_CLASSIFICATION = "JOURNEY_STAGE_CLASSIFICATION"
    RELATED_INCIDENT_RETRIEVAL = "RELATED_INCIDENT_RETRIEVAL"
    CAMPAIGN_RETRIEVAL = "CAMPAIGN_RETRIEVAL"
    EXPLANATION_GENERATION = "EXPLANATION_GENERATION"
    EVIDENCE_EXTRACTION = "EVIDENCE_EXTRACTION"


class ComputeCostClass(str, Enum):
    """Normalized computational cost tiers for operations (Rule 87)."""
    NEGLIGIBLE = "NEGLIGIBLE"        # CPU <1ms: regex, normalization, hash lookup
    LOW = "LOW"                      # CPU <15ms: TF-IDF, Logistic Regression, small embeddings
    MEDIUM = "MEDIUM"                # CPU/GPU 15-80ms: small multilingual transformer, BGE-M3
    HIGH = "HIGH"                    # GPU/CPU >80ms: large transformer, graph clustering
    EXTERNAL_PAID = "EXTERNAL_PAID"  # Commercial API calls, TinyFish, paid search


class TaskSpecification(BaseModel):
    """Metadata describing requirements for an AI task."""
    task: ModelTask
    description: str
    target_latency_ms: float
    recommended_cost: ComputeCostClass
    evaluation_metric: str
    required_inputs: List[str]
    output_schema: str
