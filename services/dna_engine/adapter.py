"""ScamFingerprintV2 <-> ScamDNA V3 Bidirectional Adapter.

Ensures zero breaking changes for existing components expecting ScamFingerprintV2,
while upgrading downstream logic to benefit from 8-dimensional ScamDNA V3 features.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.dna import (
    DNADimension,
    DNADimensionType,
    DNAQuality,
    ScamDNA,
)
from packages.schemas.fingerprint import ScamFingerprintV2


class ScamFingerprintV2Adapter:
    """Bidirectional conversion between ScamFingerprintV2 and ScamDNA V3."""

    @staticmethod
    def to_dna(fp: ScamFingerprintV2) -> ScamDNA:
        """Converts a legacy ScamFingerprintV2 into a canonical ScamDNA V3."""
        dimensions: Dict[str, DNADimension] = {}

        # 1. Semantic
        has_semantic = bool(fp.semantic_embedding or fp.semantic_features or fp.requested_actions)
        dimensions[DNADimensionType.SEMANTIC.value] = DNADimension(
            dimension=DNADimensionType.SEMANTIC,
            available=has_semantic,
            quality=DNAQuality.HIGH if fp.semantic_embedding else DNAQuality.MEDIUM,
            confidence=0.85 if fp.semantic_embedding else 0.50,
            features={
                "intent_summary": fp.semantic_features.get("composite_text", ""),
                "requested_actions": fp.requested_actions,
            },
            vector_embedding=fp.semantic_embedding,
            vector_reference=fp.semantic_vector_reference,
            engine_version="3.0.0-compat",
        )

        # 2. Journey
        has_journey = bool(fp.ordered_event_sequence)
        dimensions[DNADimensionType.JOURNEY.value] = DNADimension(
            dimension=DNADimensionType.JOURNEY,
            available=has_journey,
            quality=DNAQuality.HIGH if len(fp.ordered_event_sequence) >= 3 else DNAQuality.MEDIUM,
            confidence=0.75 if has_journey else 0.0,
            features={
                "stage_sequence": fp.ordered_event_sequence,
                "stage_count": len(fp.ordered_event_sequence),
                "current_stage": fp.ordered_event_sequence[-1] if fp.ordered_event_sequence else "UNKNOWN",
            },
            engine_version="3.0.0-compat",
        )

        # 3. Tactic
        has_tactics = bool(fp.social_engineering_tactics)
        dimensions[DNADimensionType.TACTIC.value] = DNADimension(
            dimension=DNADimensionType.TACTIC,
            available=has_tactics,
            quality=DNAQuality.HIGH if has_tactics else DNAQuality.LOW,
            confidence=0.80 if has_tactics else 0.0,
            features={
                "tactics": [t.upper() for t in fp.social_engineering_tactics],
                "tactic_count": len(fp.social_engineering_tactics),
            },
            engine_version="3.0.0-compat",
        )

        # 4. Infrastructure
        has_infra = bool(fp.URL_features or fp.infrastructure_entities or fp.TinyFish_observations)
        dimensions[DNADimensionType.INFRASTRUCTURE.value] = DNADimension(
            dimension=DNADimensionType.INFRASTRUCTURE,
            available=has_infra,
            quality=DNAQuality.MEDIUM,
            confidence=0.70 if has_infra else 0.0,
            features={
                "url_traits": fp.URL_features,
                "entities": fp.infrastructure_entities,
                "dom_observations": fp.TinyFish_observations,
            },
            engine_version="3.0.0-compat",
        )

        # 5. Payment
        has_payment = bool(fp.payment_entities)
        dimensions[DNADimensionType.PAYMENT.value] = DNADimension(
            dimension=DNADimensionType.PAYMENT,
            available=has_payment,
            quality=DNAQuality.MEDIUM,
            confidence=0.70 if has_payment else 0.0,
            features=fp.payment_entities,
            engine_version="3.0.0-compat",
        )

        # 6. Identity
        has_identity = bool(fp.claimed_identity)
        dimensions[DNADimensionType.IDENTITY.value] = DNADimension(
            dimension=DNADimensionType.IDENTITY,
            available=has_identity,
            quality=DNAQuality.MEDIUM,
            confidence=0.75 if has_identity else 0.0,
            features={"claimed_identity": fp.claimed_identity},
            engine_version="3.0.0-compat",
        )

        # 7. Temporal
        has_temporal = bool(fp.event_time_gaps)
        dimensions[DNADimensionType.TEMPORAL.value] = DNADimension(
            dimension=DNADimensionType.TEMPORAL,
            available=has_temporal,
            quality=DNAQuality.MEDIUM,
            confidence=0.65 if has_temporal else 0.0,
            features={
                "time_gaps": fp.event_time_gaps,
                "duration_seconds": sum(fp.event_time_gaps),
            },
            engine_version="3.0.0-compat",
        )

        # 8. Graph
        has_graph = bool(fp.graph_community or fp.graph_features)
        dimensions[DNADimensionType.GRAPH.value] = DNADimension(
            dimension=DNADimensionType.GRAPH,
            available=has_graph,
            quality=DNAQuality.MEDIUM,
            confidence=0.70 if has_graph else 0.0,
            features={
                "community_id": fp.graph_community,
                "graph_traits": fp.graph_features,
            },
            engine_version="3.0.0-compat",
        )

        available_dims = [k for k, d in dimensions.items() if d.available]
        missing_dims = [k for k, d in dimensions.items() if not d.available]

        return ScamDNA(
            dna_id=f"dna_{fp.fingerprint_id[-12:]}" if fp.fingerprint_id else f"dna_{uuid4().hex[:12]}",
            schema_version="3.0-compat",
            incident_id=fp.incident_id,
            family_hypotheses={"LEGACY_V2": 1.0},
            dimensions=dimensions,
            available_dimensions=available_dims,
            missing_dimensions=missing_dims,
            quality=DNAQuality.HIGH if len(available_dims) >= 5 else DNAQuality.MEDIUM,
            confidence=0.75,
            canonical_signature=f"legacy_v2:{fp.fingerprint_id}",
            created_at=fp.created_at,
            updated_at=datetime.now(timezone.utc),
            engine_version="3.0.0-compat",
            source_versions={"fingerprint_v2": "2.0.0"},
        )

    @staticmethod
    def to_fingerprint_v2(dna: ScamDNA) -> ScamFingerprintV2:
        """Converts a ScamDNA V3 instance back into a backward-compatible ScamFingerprintV2."""
        sem_dim = dna.dimensions.get(DNADimensionType.SEMANTIC.value)
        jrn_dim = dna.dimensions.get(DNADimensionType.JOURNEY.value)
        tac_dim = dna.dimensions.get(DNADimensionType.TACTIC.value)
        inf_dim = dna.dimensions.get(DNADimensionType.INFRASTRUCTURE.value)
        pay_dim = dna.dimensions.get(DNADimensionType.PAYMENT.value)
        idt_dim = dna.dimensions.get(DNADimensionType.IDENTITY.value)
        tmp_dim = dna.dimensions.get(DNADimensionType.TEMPORAL.value)
        grp_dim = dna.dimensions.get(DNADimensionType.GRAPH.value)

        return ScamFingerprintV2(
            fingerprint_id=dna.dna_id,
            incident_id=dna.incident_id,
            semantic_embedding=sem_dim.vector_embedding if sem_dim else None,
            semantic_vector_reference=sem_dim.vector_reference if sem_dim else None,
            semantic_features=sem_dim.features if sem_dim else {},
            ordered_event_sequence=jrn_dim.features.get("stage_sequence", []) if jrn_dim else [],
            event_time_gaps=tmp_dim.features.get("time_gaps", []) if tmp_dim else [],
            social_engineering_tactics=tac_dim.features.get("tactics", []) if tac_dim else [],
            claimed_identity=idt_dim.features.get("claimed_identity") if idt_dim else None,
            requested_actions=sem_dim.features.get("requested_actions", []) if sem_dim else [],
            pattern_matches=list(dna.family_hypotheses.keys()) if dna.family_hypotheses else [],
            URL_features=inf_dim.features.get("url_traits", {}) if inf_dim else {},
            TinyFish_observations=inf_dim.features.get("dom_observations", {}) if inf_dim else {},
            infrastructure_entities=inf_dim.features.get("entities", {}) if inf_dim else {},
            payment_entities=pay_dim.features if pay_dim else {},
            graph_community=grp_dim.features.get("community_id") if grp_dim else None,
            graph_features=grp_dim.features.get("graph_traits", {}) if grp_dim else {},
            created_at=dna.created_at,
        )
