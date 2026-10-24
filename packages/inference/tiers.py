"""Production Inference Tiers and SLA Budgets for ScamGraph AI.

Defines the 4-tier execution hierarchy ensuring fast consumer checks without
unnecessarily invoking expensive GPU or transformer models (Rule 39, 51).
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ml.evaluation.arena.taxonomy import ComputeCostClass


class InferenceTier(str, Enum):
    """Four production execution tiers."""
    TIER_0_DETERMINISTIC = "TIER_0_DETERMINISTIC"   # Regex, normalization, entity extraction, local cache (<1ms)
    TIER_1_FAST_ML = "TIER_1_FAST_ML"               # TF-IDF / character ensemble, E5-small embeddings (<15ms CPU)
    TIER_2_DEEP_INTELLIGENCE = "TIER_2_DEEP_INTEL"  # Transformer reranker, BGE-M3, graph pattern retrieval (15-80ms)
    TIER_3_INVESTIGATION = "TIER_3_INVESTIGATION"   # External evidence, TinyFish, LLM reasoning (>80ms)


class TierSpecification(BaseModel):
    """Operational parameters and SLA budgets per inference tier."""
    tier: InferenceTier
    name: str
    description: str
    target_p95_latency_ms: float
    max_timeout_ms: float
    default_cost: ComputeCostClass
    hardware: str = "CPU"
    supports_batching: bool = True


TIER_SPECIFICATIONS: Dict[InferenceTier, TierSpecification] = {
    InferenceTier.TIER_0_DETERMINISTIC: TierSpecification(
        tier=InferenceTier.TIER_0_DETERMINISTIC,
        name="Deterministic Edge Triage",
        description="Normalization, entity parsing, regex signatures, and instant cache lookups",
        target_p95_latency_ms=1.5,
        max_timeout_ms=5.0,
        default_cost=ComputeCostClass.NEGLIGIBLE,
        hardware="CPU",
        supports_batching=False,
    ),
    InferenceTier.TIER_1_FAST_ML: TierSpecification(
        tier=InferenceTier.TIER_1_FAST_ML,
        name="Fast Consumer ML Tier",
        description="Word + character TF-IDF ensemble and lightweight multilingual-e5-small embeddings",
        target_p95_latency_ms=15.0,
        max_timeout_ms=50.0,
        default_cost=ComputeCostClass.LOW,
        hardware="CPU",
        supports_batching=True,
    ),
    InferenceTier.TIER_2_DEEP_INTELLIGENCE: TierSpecification(
        tier=InferenceTier.TIER_2_DEEP_INTELLIGENCE,
        name="Deep Intelligence Tier",
        description="Multilingual transformer reranker, BGE-M3 journey representation, and graph retrieval",
        target_p95_latency_ms=75.0,
        max_timeout_ms=250.0,
        default_cost=ComputeCostClass.MEDIUM,
        hardware="CPU / Optional GPU",
        supports_batching=True,
    ),
    InferenceTier.TIER_3_INVESTIGATION: TierSpecification(
        tier=InferenceTier.TIER_3_INVESTIGATION,
        name="Analyst Deep Investigation",
        description="TinyFish web crawling, external domain intel, and structured LLM extraction",
        target_p95_latency_ms=1500.0,
        max_timeout_ms=5000.0,
        default_cost=ComputeCostClass.HIGH,
        hardware="Distributed / Async Worker",
        supports_batching=False,
    ),
}
