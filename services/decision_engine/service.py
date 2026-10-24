"""Unified Decision Service (Phase 4A).

Coordinates Tripartite Decision evaluation across investigation and consumer endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from packages.schemas.unified_decision import TripartiteDecision
from services.decision_engine.config import DecisionConfig, decision_config
from services.decision_engine.fusion import (
    TripartiteDecisionFusionEngine,
    decision_fusion_engine,
)

logger = logging.getLogger("decision_engine.service")


class UnifiedDecisionService:
    """High-level service orchestrating unified risk, confidence, urgency, and action planning."""

    def __init__(
        self,
        config: Optional[DecisionConfig] = None,
        fusion_engine: Optional[TripartiteDecisionFusionEngine] = None,
    ):
        self.config = config or decision_config
        self.fusion = fusion_engine or decision_fusion_engine

    def evaluate(
        self,
        incident_id: Optional[str] = None,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        vpa: Optional[str] = None,
        phone: Optional[str] = None,
        journey_stage: Optional[str] = None,
        tactics_observed: Optional[List[str]] = None,
        known_dna_similarity: Optional[float] = None,
        entity_trust_score: Optional[float] = None,
        counter_evidence_signals: Optional[List[str]] = None,
    ) -> TripartiteDecision:
        """Evaluates all dimensions and yields a calibrated TripartiteDecision."""
        return self.fusion.evaluate_tripartite_decision(
            incident_id=incident_id,
            message_text=message_text,
            url=url,
            vpa=vpa,
            phone=phone,
            journey_stage=journey_stage,
            tactics_observed=tactics_observed,
            known_dna_similarity=known_dna_similarity,
            entity_trust_score=entity_trust_score,
            counter_evidence_signals=counter_evidence_signals,
        )

    def evaluate_incident(self, incident_data: Dict[str, Any]) -> TripartiteDecision:
        """Evaluates an ingested incident dictionary from storage/session."""
        inc_id = incident_data.get("id") or incident_data.get("incident_id")
        text = incident_data.get("text") or incident_data.get("message_text")
        url = incident_data.get("url")
        vpa = incident_data.get("vpa")
        phone = incident_data.get("phone")
        stage = incident_data.get("journey_stage")
        tactics = incident_data.get("tactics", [])
        dna_sim = incident_data.get("dna_similarity")
        trust_score = incident_data.get("trust_score")
        counter_signals = incident_data.get("counter_evidence", [])

        # Extract from entities if present
        for ent in incident_data.get("entities", []):
            val = ent.get("canonical_value") or ent.get("raw_value")
            etype = ent.get("entity_type", "")
            if "UPI" in etype or "VPA" in etype or "PAYMENT" in etype:
                vpa = val
            elif "PHONE" in etype:
                phone = val
            elif "URL" in etype or "DOMAIN" in etype:
                url = val

        return self.evaluate(
            incident_id=inc_id,
            message_text=text,
            url=url,
            vpa=vpa,
            phone=phone,
            journey_stage=stage,
            tactics_observed=tactics,
            known_dna_similarity=dna_sim,
            entity_trust_score=trust_score,
            counter_evidence_signals=counter_signals,
        )


# Global singleton instance
unified_decision_service = UnifiedDecisionService()
