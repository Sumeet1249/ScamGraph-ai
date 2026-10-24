"""Unified ScamGraph Risk Engine (Module D).

Orchestrates Smart Registry, Mule Intelligence, Graph Correlation, and Semantic Message NLP
into a calibrated, transparent, and explainable multi-signal assessment.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.graph_correlation import CorrelationNodeType, GraphNode, RiskPropagationRequest
from packages.schemas.mule import MuleEvaluationRequest, MuleRiskBand
from packages.schemas.registry import IdentifierType, ScreenRequest, TypedIdentifier
from packages.schemas.unified_risk import (
    UnifiedAction,
    UnifiedRiskBand,
    UnifiedRiskRequest,
    UnifiedRiskResponse,
)
from services.graph_engine.algorithms.risk_propagation import (
    GraphRiskPropagator,
    get_graph_risk_propagator,
)
from services.graph_engine.correlation.transaction_graph import (
    TransactionGraphEngine,
    get_transaction_graph_engine,
)
from services.investigation.url_analysis.safety import URLAnalyzer
from services.mule_engine.service import (
    MuleIntelligenceService,
    get_mule_intelligence_service,
)
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor
from services.registry.service import (
    SmartRegistryService,
    get_smart_registry_service,
)

logger = logging.getLogger("risk_engine.unified")


class UnifiedScamGraphRiskEngine:
    """Central orchestration layer for ScamGraph AI fraud intelligence."""

    def __init__(
        self,
        registry_service: Optional[SmartRegistryService] = None,
        mule_service: Optional[MuleIntelligenceService] = None,
        graph_engine: Optional[TransactionGraphEngine] = None,
        risk_propagator: Optional[GraphRiskPropagator] = None,
    ):
        self.registry = registry_service or get_smart_registry_service()
        self.mule = mule_service or get_mule_intelligence_service()
        self.graph = graph_engine or get_transaction_graph_engine()
        self.propagator = risk_propagator or get_graph_risk_propagator()

    @staticmethod
    def map_risk_band_and_action(score: float) -> tuple[UnifiedRiskBand, UnifiedAction]:
        """Map aggregate risk score to risk band and recommended review disposition."""
        if score >= 0.85:
            return UnifiedRiskBand.CRITICAL, UnifiedAction.ESCALATE
        elif score >= 0.60:
            return UnifiedRiskBand.HIGH, UnifiedAction.FLAG_FOR_REVIEW
        elif score >= 0.30:
            return UnifiedRiskBand.MEDIUM, UnifiedAction.STEP_UP_VERIFICATION
        return UnifiedRiskBand.LOW, UnifiedAction.ALLOW

    async def assess(self, req: UnifiedRiskRequest) -> UnifiedRiskResponse:
        """Perform comprehensive unified assessment across all 4 intelligence layers."""
        entity_id = req.entity_id or f"ent_{uuid4().hex[:10]}"
        correlation_id = req.correlation_id or f"corr_{uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        reason_codes: List[str] = []
        evidence_items: List[Dict[str, Any]] = []
        contributing_signals: Dict[str, Any] = {}
        degraded_components: List[str] = []

        sub_scores: Dict[str, float] = {}
        sub_weights: Dict[str, float] = {}

        # ---------------------------------------------------------------------
        # Layer 1: Smart Registry Screening
        # ---------------------------------------------------------------------
        screen_idents: List[TypedIdentifier] = []
        if req.phone:
            screen_idents.append(TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value=req.phone))
        if req.vpa:
            screen_idents.append(TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value=req.vpa))
        if req.url:
            screen_idents.append(TypedIdentifier(identifier_type=IdentifierType.URL_DOMAIN, raw_value=req.url))
        if req.bank_account:
            screen_idents.append(TypedIdentifier(identifier_type=IdentifierType.BANK_ACCOUNT, raw_value=req.bank_account))
        if req.device_id:
            screen_idents.append(TypedIdentifier(identifier_type=IdentifierType.DEVICE_ID, raw_value=req.device_id))

        registry_score = 0.0
        if screen_idents:
            try:
                screen_res = await self.registry.screen_identifiers(
                    ScreenRequest(caller_org=req.caller_org, identifiers=screen_idents, correlation_id=correlation_id)
                )
                registry_score = screen_res.highest_risk_score
                contributing_signals["registry"] = {
                    "total_hits": screen_res.total_hits,
                    "has_confirmed": screen_res.has_confirmed_hit,
                    "has_disputed": screen_res.has_disputed_hit,
                    "has_revoked": screen_res.has_revoked_hit,
                    "score": registry_score,
                    "matches": [m.model_dump() for m in screen_res.matches],
                }
                for m in screen_res.matches:
                    reason_codes.append(m.reason_code)
                    evidence_items.append({
                        "source": "SMART_REGISTRY",
                        "type": m.category,
                        "report_id": m.report_id,
                        "reporting_source": m.reporting_source,
                        "confidence": m.confidence,
                        "is_disputed": m.is_disputed,
                        "is_revoked": m.is_revoked,
                    })
                sub_scores["registry"] = registry_score
                sub_weights["registry"] = 0.35
            except Exception as e:
                logger.error(f"Registry screening error: {e}")
                degraded_components.append("SMART_REGISTRY")
        else:
            degraded_components.append("SMART_REGISTRY_NO_IDENTIFIERS")

        # ---------------------------------------------------------------------
        # Layer 2: Mule Intelligence Engine
        # ---------------------------------------------------------------------
        if req.transactions:
            try:
                mule_res = await self.mule.evaluate_account(
                    MuleEvaluationRequest(
                        account_id=req.bank_account or req.vpa or entity_id,
                        transactions=req.transactions,
                        account_age_days=req.account_age_days,
                        historical_avg_daily_volume=req.historical_avg_daily_volume,
                        has_registry_match=registry_score >= 0.80,
                    )
                )
                sub_scores["mule"] = mule_res.risk_score
                sub_weights["mule"] = 0.30
                contributing_signals["mule_intelligence"] = {
                    "score": mule_res.risk_score,
                    "band": mule_res.risk_band.value,
                    "rules_score": mule_res.rules_engine_score,
                    "ml_score": mule_res.ml_model_score,
                    "action": mule_res.recommended_action.value,
                    "top_rules": [r.model_dump() for r in mule_res.top_contributing_rules],
                }
                for r in mule_res.top_contributing_rules:
                    reason_codes.append(f"MULE_{r.rule_id}")
                    evidence_items.append({
                        "source": "MULE_INTELLIGENCE",
                        "rule": r.name,
                        "severity": r.severity,
                        "description": r.description,
                    })
            except Exception as e:
                logger.error(f"Mule intelligence error: {e}")
                degraded_components.append("MULE_INTELLIGENCE")
        else:
            degraded_components.append("MULE_INTELLIGENCE_NO_TRANSACTIONS")

        # ---------------------------------------------------------------------
        # Layer 3: Graph Correlation & Risk Propagation
        # ---------------------------------------------------------------------
        graph_score = 0.0
        graph_seeds: List[str] = []
        if screen_idents:
            for ident in screen_idents:
                node = self.graph.get_node(ident.raw_value)
                if node:
                    graph_seeds.append(ident.raw_value)

        if graph_seeds:
            try:
                prop_res = self.propagator.propagate_risk(
                    RiskPropagationRequest(seed_node_ids=graph_seeds, decay_factor=0.5, max_hops=3)
                )
                max_prop = max((n.total_risk for n in prop_res.nodes), default=0.0)
                graph_score = max_prop
                sub_scores["graph"] = graph_score
                sub_weights["graph"] = 0.20
                contributing_signals["graph_correlation"] = {
                    "score": graph_score,
                    "affected_nodes_count": prop_res.affected_nodes_count,
                    "seeds": graph_seeds,
                }
                if graph_score > 0.4:
                    reason_codes.append("GRAPH_TOPOLOGICAL_RISK_PROPAGATION")
                    evidence_items.append({
                        "source": "GRAPH_CORRELATION",
                        "propagated_risk": graph_score,
                        "hops": 1,
                        "seeds": graph_seeds,
                    })
            except Exception as e:
                logger.error(f"Graph propagation error: {e}")
                degraded_components.append("GRAPH_CORRELATION")
        else:
            degraded_components.append("GRAPH_CORRELATION_UNPOPULATED")

        # ---------------------------------------------------------------------
        # Layer 4: Semantic NLP & URL Analysis (Existing Models)
        # ---------------------------------------------------------------------
        message_score = 0.0
        msg_signals_found = []
        if req.message_text:
            text_signals = SemanticSignalExtractor.extract_signals(entity_id, req.message_text)
            if text_signals:
                message_score = max((s.confidence * (s.weight / 2.0) for s in text_signals), default=0.0)
                message_score = min(1.0, round(message_score, 3))
                msg_signals_found.extend([s.signal_type for s in text_signals])
                for s in text_signals:
                    reason_codes.append(f"MSG_{s.signal_type}")
                    evidence_items.append({
                        "source": "SEMANTIC_NLP",
                        "signal_type": s.signal_type,
                        "severity": s.severity.value,
                        "description": s.description,
                    })

        url_score = 0.0
        if req.url:
            url_res = URLAnalyzer.analyze_lexical_risk(entity_id, req.url)
            url_sigs = url_res.get("signals", [])
            if url_sigs:
                url_score = max((s.confidence * (s.weight / 2.0) for s in url_sigs), default=0.0)
                url_score = min(1.0, round(url_score, 3))
                for s in url_sigs:
                    reason_codes.append(f"URL_{s.signal_type}")
                    evidence_items.append({
                        "source": "URL_ANALYSIS",
                        "signal_type": s.signal_type,
                        "severity": s.severity.value,
                        "description": s.description,
                    })

        nlp_combined = max(message_score, url_score)
        if nlp_combined > 0:
            sub_scores["nlp_url"] = nlp_combined
            sub_weights["nlp_url"] = 0.15
            contributing_signals["semantic_nlp_url"] = {
                "score": nlp_combined,
                "message_score": message_score,
                "url_score": url_score,
                "detected_signals": msg_signals_found,
            }
        else:
            if not req.message_text and not req.url:
                degraded_components.append("SEMANTIC_NLP_URL_NO_INPUT")

        # ---------------------------------------------------------------------
        # Multi-Signal Fusion & Weight Normalization
        # ---------------------------------------------------------------------
        if sub_scores and sub_weights:
            total_active_weight = sum(sub_weights.values())
            # Normalize active weights to sum to 1.0
            normalized_score = sum(
                sub_scores[k] * (sub_weights[k] / total_active_weight)
                for k in sub_scores
            )
            # If an active confirmed registry match exists, floor risk at registry score
            if registry_score >= 0.85:
                normalized_score = max(normalized_score, registry_score)

            final_overall_score = min(1.0, round(normalized_score, 3))
        else:
            # Fallback if absolutely no valid signals were provided
            final_overall_score = 0.05
            reason_codes.append("INSUFFICIENT_EVIDENCE")

        risk_band, recommended_action = self.map_risk_band_and_action(final_overall_score)

        # De-duplicate reason codes preserving order
        unique_reasons = list(dict.fromkeys(reason_codes))

        is_degraded = len(degraded_components) > 0
        uncertainty_info = {
            "is_degraded": is_degraded,
            "degraded_components": degraded_components,
            "active_signal_layers": list(sub_scores.keys()),
            "data_confidence": "HIGH" if len(sub_scores) >= 3 else ("MEDIUM" if len(sub_scores) >= 2 else "LOW"),
            "corroborated": len(sub_scores) >= 2,
        }

        return UnifiedRiskResponse(
            entity_id=entity_id,
            overall_risk_score=final_overall_score,
            risk_band=risk_band,
            recommended_action=recommended_action,
            reason_codes=unique_reasons,
            contributing_signals=contributing_signals,
            supporting_evidence=evidence_items,
            uncertainty_and_data_quality=uncertainty_info,
            is_degraded=is_degraded,
            degraded_components=degraded_components,
            model_versions={
                "unified_engine": "v1.0.0",
                "smart_registry": "v1.0.0",
                "mule_intelligence": "v1.0.0",
                "graph_correlation": "v1.0.0",
                "semantic_nlp": "v1.0.0",
            },
            scored_at=now,
            correlation_id=correlation_id,
        )


# Global instance
unified_risk_engine = UnifiedScamGraphRiskEngine()


def get_unified_risk_engine() -> UnifiedScamGraphRiskEngine:
    """Dependency provider."""
    return unified_risk_engine
