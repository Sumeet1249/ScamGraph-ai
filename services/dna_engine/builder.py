"""ScamDNA V3 Builder.

Constructs unified 8-dimensional ScamDNA instances from incidents, journeys,
tactic intelligence, entity intelligence, payment context, and temporal features.
Enforces strict privacy boundaries (zero raw PII or secret credentials in DNA).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from ml.embeddings.encoder import semantic_encoder
from packages.schemas.dna import (
    DNADimension,
    DNADimensionType,
    DNAQuality,
    ScamDNA,
)
from packages.schemas.journey import JourneyStage, ScamJourney

logger = logging.getLogger("dna_engine.builder")


class ScamDNABuilder:
    """Builds canonical ScamDNA V3 representations from multi-source intelligence."""

    ENGINE_VERSION = "3.0.0"

    @classmethod
    def build(
        cls,
        incident_id: str,
        journey: Optional[ScamJourney] = None,
        tactics: Optional[List[str]] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
        payment_context: Optional[Dict[str, Any]] = None,
        infrastructure: Optional[Dict[str, Any]] = None,
        temporal_context: Optional[Dict[str, Any]] = None,
        graph_context: Optional[Dict[str, Any]] = None,
        message_text: Optional[str] = None,
        message_summary: Optional[str] = None,
        requested_actions: Optional[List[str]] = None,
        family_hypotheses: Optional[Dict[str, float]] = None,
        evidence_ids: Optional[List[str]] = None,
    ) -> ScamDNA:
        """Constructs an 8-dimensional ScamDNA instance supporting partial inputs."""
        dimensions: Dict[str, DNADimension] = {}
        all_evidence = list(evidence_ids or [])

        # ---------------------------------------------------------------------
        # 1. Semantic DNA
        # ---------------------------------------------------------------------
        text_for_embedding = message_text or message_summary or ""
        embedding: Optional[List[float]] = None
        if text_for_embedding:
            try:
                emb = semantic_encoder.encode(text_for_embedding[:512])
                embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            except Exception as e:
                logger.warning(f"Failed to generate semantic embedding for incident {incident_id}: {e}")

        semantic_actions = list(requested_actions or [])
        semantic_features = {
            "intent_summary": message_summary or (text_for_embedding[:100] if text_for_embedding else ""),
            "requested_actions": semantic_actions,
            "has_embedding": embedding is not None,
        }
        dimensions[DNADimensionType.SEMANTIC.value] = DNADimension(
            dimension=DNADimensionType.SEMANTIC,
            available=bool(text_for_embedding or semantic_actions),
            quality=DNAQuality.HIGH if embedding else (DNAQuality.MEDIUM if semantic_actions else DNAQuality.LOW),
            confidence=0.85 if embedding else (0.60 if semantic_actions else 0.30),
            features=semantic_features,
            vector_embedding=embedding,
            engine_version=cls.ENGINE_VERSION,
        )

        # ---------------------------------------------------------------------
        # 2. Journey DNA
        # ---------------------------------------------------------------------
        if journey and journey.stage_history:
            stage_seq = [s.value if hasattr(s, "value") else str(s) for s in journey.stage_history]
            curr_stage = journey.current_stage.value if hasattr(journey.current_stage, "value") else str(journey.current_stage)
            if curr_stage == "CONTACT" and len(stage_seq) > 1:
                curr_stage = stage_seq[-1]

            has_boundary = bool(
                journey.monetization_boundary_event_id
                or any(s in ("INITIAL_PAYMENT", "PAYMENT_ESCALATION", "RECOVERY_FEE", "CREDENTIAL_REQUEST") for s in stage_seq)
                or (payment_context and (payment_context.get("deposit_requested") or payment_context.get("amount", 0) > 0))
            )
            journey_features = {
                "stage_sequence": stage_seq,
                "current_stage": curr_stage,
                "stage_count": len(stage_seq),
                "monetization_boundary_crossed": has_boundary,
                "monetization_status": journey.monetization_status.value if hasattr(journey.monetization_status, "value") else str(journey.monetization_status),
                "loss_status": journey.loss_status.value if hasattr(journey.loss_status, "value") else str(journey.loss_status),
                "pre_loss_warning_issued": journey.pre_loss_warning_issued,
            }
            dimensions[DNADimensionType.JOURNEY.value] = DNADimension(
                dimension=DNADimensionType.JOURNEY,
                available=True,
                quality=DNAQuality.VERY_HIGH if len(stage_seq) >= 3 else DNAQuality.HIGH,
                confidence=journey.current_stage_confidence,
                features=journey_features,
                evidence_ids=journey.evidence_ids,
                engine_version=cls.ENGINE_VERSION,
            )
            all_evidence.extend(journey.evidence_ids)
        else:
            dimensions[DNADimensionType.JOURNEY.value] = DNADimension(
                dimension=DNADimensionType.JOURNEY,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 3. Tactic DNA
        # ---------------------------------------------------------------------
        tactic_list = [t.upper() for t in (tactics or [])]
        if tactic_list:
            dimensions[DNADimensionType.TACTIC.value] = DNADimension(
                dimension=DNADimensionType.TACTIC,
                available=True,
                quality=DNAQuality.HIGH if len(tactic_list) >= 2 else DNAQuality.MEDIUM,
                confidence=0.80,
                features={
                    "tactics": tactic_list,
                    "tactic_count": len(tactic_list),
                    "primary_tactic": tactic_list[0] if tactic_list else None,
                    "has_isolation": "ISOLATION" in tactic_list or "SECRECY" in tactic_list,
                    "has_pressure": "PAYMENT_PRESSURE" in tactic_list or "URGENCY" in tactic_list,
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.TACTIC.value] = DNADimension(
                dimension=DNADimensionType.TACTIC,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 4. Infrastructure DNA (Privacy-Safe: structural traits only)
        # ---------------------------------------------------------------------
        infra_dict = infrastructure or {}
        channels_observed: List[str] = []
        if journey and journey.channels:
            channels_observed = list(journey.channels)
        elif "channels" in infra_dict:
            channels_observed = list(infra_dict["channels"])

        has_infra = bool(channels_observed or infra_dict.get("domain_traits") or infra_dict.get("url_traits"))
        if has_infra:
            dimensions[DNADimensionType.INFRASTRUCTURE.value] = DNADimension(
                dimension=DNADimensionType.INFRASTRUCTURE,
                available=True,
                quality=DNAQuality.MEDIUM,
                confidence=0.75,
                features={
                    "channels": channels_observed,
                    "channel_progression": " > ".join(channels_observed) if channels_observed else "",
                    "has_platform_migration": len(set(channels_observed)) > 1,
                    "domain_suspicion": infra_dict.get("domain_suspicion", "UNKNOWN"),
                    "uses_private_channel": any(c in ("TELEGRAM", "WHATSAPP") for c in channels_observed),
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.INFRASTRUCTURE.value] = DNADimension(
                dimension=DNADimensionType.INFRASTRUCTURE,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 5. Payment DNA (Behavioral progression, no raw secrets)
        # ---------------------------------------------------------------------
        pay_dict = payment_context or {}
        has_payment = bool(pay_dict) or (journey and journey.monetization_status.value != "NO_PAYMENT_SIGNAL")
        if has_payment:
            prior_reward = pay_dict.get("prior_reward", False)
            deposit_req = pay_dict.get("deposit_requested", False) or pay_dict.get("amount", 0) > 0
            escalation = pay_dict.get("is_escalated", False)
            fee_after_block = pay_dict.get("fee_after_block", False)
            
            progression_traits = []
            if prior_reward:
                progression_traits.append("SMALL_REWARD")
            if deposit_req:
                progression_traits.append("INITIAL_DEPOSIT")
            if escalation:
                progression_traits.append("ESCALATED_DEPOSIT")
            if fee_after_block:
                progression_traits.append("UNFREEZE_FEE")

            dimensions[DNADimensionType.PAYMENT.value] = DNADimension(
                dimension=DNADimensionType.PAYMENT,
                available=True,
                quality=DNAQuality.HIGH if progression_traits else DNAQuality.MEDIUM,
                confidence=0.85 if progression_traits else 0.60,
                features={
                    "payment_progression": progression_traits,
                    "progression_signature": " > ".join(progression_traits) if progression_traits else "PAYMENT_REQUESTED",
                    "payment_channel_type": pay_dict.get("channel_type", "UPI_VPA"),
                    "recipient_psp_category": pay_dict.get("psp_category", "PERSONAL_HANDLE"),
                    "relative_escalation_ratio": pay_dict.get("escalation_ratio", 1.0),
                    "fee_after_block": fee_after_block,
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.PAYMENT.value] = DNADimension(
                dimension=DNADimensionType.PAYMENT,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 6. Identity DNA (Claimed category & switching patterns, no victim PII)
        # ---------------------------------------------------------------------
        ent_list = entities or []
        claimed_org = None
        impersonated_cat = "NONE"
        for ent in ent_list:
            if ent.get("entity_type") in ("BRAND", "ORGANIZATION"):
                claimed_org = ent.get("canonical_value") or ent.get("masked_value")
                # Classify category
                org_low = str(claimed_org).lower()
                if any(k in org_low for k in ("police", "cbi", "investigation", "bureau", "trai", "customs", "cyber", "court", "enforcement", "ed")):
                    impersonated_cat = "LAW_ENFORCEMENT"
                elif any(k in org_low for k in ("bank", "sbi", "hdfc", "icici", "rbi")):
                    impersonated_cat = "BANK"
                elif any(k in org_low for k in ("telegram", "youtube", "amazon", "flipkart", "part-time", "job")):
                    impersonated_cat = "TASK_JOB_PLATFORM"
                elif any(k in org_low for k in ("electricity", "discom", "power")):
                    impersonated_cat = "UTILITY"
                else:
                    impersonated_cat = "COMMERCIAL_BRAND"
                break

        has_identity = claimed_org is not None or impersonated_cat != "NONE"
        if has_identity:
            dimensions[DNADimensionType.IDENTITY.value] = DNADimension(
                dimension=DNADimensionType.IDENTITY,
                available=True,
                quality=DNAQuality.HIGH if impersonated_cat != "NONE" else DNAQuality.MEDIUM,
                confidence=0.80,
                features={
                    "impersonated_category": impersonated_cat,
                    "claimed_brand_masked": str(claimed_org)[:15] if claimed_org else None,
                    "authority_role_present": impersonated_cat == "LAW_ENFORCEMENT",
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.IDENTITY.value] = DNADimension(
                dimension=DNADimensionType.IDENTITY,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 7. Temporal DNA
        # ---------------------------------------------------------------------
        temp_dict = temporal_context or {}
        time_gaps = temp_dict.get("time_gaps", [])
        duration_sec = temp_dict.get("duration_seconds", 0)
        has_temporal = bool(time_gaps or duration_sec > 0)
        if has_temporal:
            dimensions[DNADimensionType.TEMPORAL.value] = DNADimension(
                dimension=DNADimensionType.TEMPORAL,
                available=True,
                quality=DNAQuality.MEDIUM,
                confidence=0.70,
                features={
                    "duration_seconds": duration_sec,
                    "time_gaps": time_gaps[:10],
                    "temporal_pace": "RAPID_PRESSURE" if duration_sec < 900 else "PATIENT_GROOMING",
                    "accelerating_pressure": len(time_gaps) >= 2 and time_gaps[-1] < time_gaps[0],
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.TEMPORAL.value] = DNADimension(
                dimension=DNADimensionType.TEMPORAL,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # 8. Graph DNA (Structural topology features)
        # ---------------------------------------------------------------------
        grp_dict = graph_context or {}
        has_graph = bool(grp_dict)
        if has_graph:
            dimensions[DNADimensionType.GRAPH.value] = DNADimension(
                dimension=DNADimensionType.GRAPH,
                available=True,
                quality=DNAQuality.MEDIUM,
                confidence=0.75,
                features={
                    "degree_centrality_tier": grp_dict.get("degree_tier", "LOW"),
                    "shared_entity_count": grp_dict.get("shared_entity_count", 0),
                    "community_cluster_id": grp_dict.get("community_id"),
                    "infrastructure_connectivity": grp_dict.get("infra_connectivity", "DISCONNECTED"),
                },
                engine_version=cls.ENGINE_VERSION,
            )
        else:
            dimensions[DNADimensionType.GRAPH.value] = DNADimension(
                dimension=DNADimensionType.GRAPH,
                available=False,
                quality=DNAQuality.LOW,
                confidence=0.0,
                features={},
                engine_version=cls.ENGINE_VERSION,
            )

        # ---------------------------------------------------------------------
        # Assemble Metadata & Canonical Signature
        # ---------------------------------------------------------------------
        available_dims = [k for k, d in dimensions.items() if d.available]
        missing_dims = [k for k, d in dimensions.items() if not d.available]

        # Overall DNA quality & confidence
        if len(available_dims) >= 6:
            overall_quality = DNAQuality.VERY_HIGH if dimensions[DNADimensionType.JOURNEY.value].available else DNAQuality.HIGH
            overall_conf = 0.88
        elif len(available_dims) >= 4:
            overall_quality = DNAQuality.MEDIUM
            overall_conf = 0.72
        elif len(available_dims) >= 2:
            overall_quality = DNAQuality.LOW
            overall_conf = 0.50
        else:
            overall_quality = DNAQuality.LOW
            overall_conf = 0.25

        # Canonical explainable signature
        family_str = journey.scam_family if journey else "UNKNOWN"
        journey_str = " > ".join(dimensions[DNADimensionType.JOURNEY.value].features.get("stage_sequence", []))
        tactics_str = "+".join(dimensions[DNADimensionType.TACTIC.value].features.get("tactics", []))
        payment_str = dimensions[DNADimensionType.PAYMENT.value].features.get("progression_signature", "NONE")
        channels_str = dimensions[DNADimensionType.INFRASTRUCTURE.value].features.get("channel_progression", "NONE")

        sig_parts = [f"family:{family_str}"]
        if journey_str:
            sig_parts.append(f"journey:{journey_str}")
        if tactics_str:
            sig_parts.append(f"tactics:{tactics_str}")
        if payment_str != "NONE":
            sig_parts.append(f"payment:{payment_str}")
        if channels_str != "NONE":
            sig_parts.append(f"channels:{channels_str}")
        canonical_signature = " | ".join(sig_parts)

        # Family distribution
        f_hyp = family_hypotheses or (journey.family_hypotheses if journey and journey.family_hypotheses else None)
        if not f_hyp and journey and journey.scam_family and journey.scam_family != "UNKNOWN":
            f_hyp = {journey.scam_family: 1.0}
        f_hyp = f_hyp or {"UNKNOWN": 1.0}

        now = datetime.now(timezone.utc)
        return ScamDNA(
            dna_id=f"dna_{uuid4().hex[:12]}",
            schema_version="3.0",
            incident_id=incident_id,
            family_hypotheses=f_hyp,
            dimensions=dimensions,
            available_dimensions=available_dims,
            missing_dimensions=missing_dims,
            quality=overall_quality,
            confidence=round(overall_conf, 2),
            canonical_signature=canonical_signature,
            created_at=now,
            updated_at=now,
            engine_version=cls.ENGINE_VERSION,
            source_versions={
                "journey_engine": "1.0.0",
                "tactic_engine": "1.0.0",
                "entity_intelligence": "2.0.0",
            },
            evidence_ids=list(set(all_evidence)),
        )
