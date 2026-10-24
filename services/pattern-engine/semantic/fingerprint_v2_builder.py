"""ScamFingerprintV2 Builder (Step 25).

Constructs unified ScamFingerprintV2 instances from raw incident telemetry,
event sequences, evidence signals, and pattern engine outputs.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ml.embeddings.encoder import semantic_encoder
from packages.schemas.fingerprint import ScamFingerprintV2

logger = logging.getLogger("pattern_engine.fingerprint_v2_builder")


class ScamFingerprintV2Builder:
    """Builds multi-dimensional ScamFingerprintV2 representations."""

    @staticmethod
    def build(
        incident_id: str,
        events: Optional[List[Any]] = None,
        claimed_identity: Optional[str] = None,
        social_engineering_tactics: Optional[List[str]] = None,
        requested_actions: Optional[List[str]] = None,
        pattern_matches: Optional[List[str]] = None,
        url_features: Optional[Dict[str, Any]] = None,
        tinyfish_observations: Optional[Dict[str, Any]] = None,
        infrastructure_entities: Optional[Dict[str, Any]] = None,
        payment_entities: Optional[Dict[str, Any]] = None,
        graph_community: Optional[str] = None,
        graph_features: Optional[Dict[str, Any]] = None,
        message_summary: Optional[str] = None,
    ) -> ScamFingerprintV2:
        # Extract ordered event sequence and time deltas
        ordered_sequence: List[str] = []
        time_gaps: List[int] = []

        if events:
            prev_ts = None
            for ev in events:
                if isinstance(ev, dict):
                    etype = str(ev.get("event_type") or ev.get("type") or "UNKNOWN").upper()
                    ts_offset = ev.get("timestamp_offset_seconds")
                else:
                    etype = str(getattr(ev, "event_type", getattr(ev, "type", "UNKNOWN"))).upper()
                    ts_offset = getattr(ev, "timestamp_offset_seconds", None)

                ordered_sequence.append(etype)
                if ts_offset is not None:
                    if prev_ts is not None and ts_offset >= prev_ts:
                        time_gaps.append(int(ts_offset - prev_ts))
                    prev_ts = ts_offset

        tactics_list = social_engineering_tactics or []
        actions_list = requested_actions or []

        # Formulate composite semantic description
        composite_parts = []
        if claimed_identity:
            composite_parts.append(f"Identity: {claimed_identity}")
        if tactics_list:
            composite_parts.append(f"Tactics: {', '.join(tactics_list)}")
        if actions_list:
            composite_parts.append(f"Actions: {', '.join(actions_list)}")
        if message_summary:
            composite_parts.append(f"Summary: {message_summary}")

        composite_text = " | ".join(composite_parts) if composite_parts else f"Incident {incident_id}"

        # Generate embedding
        embedding: List[float] = []
        try:
            emb = semantic_encoder.encode(composite_text)
            embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for fingerprint {incident_id}: {e}")

        return ScamFingerprintV2(
            incident_id=incident_id,
            semantic_embedding=embedding,
            semantic_features={
                "message_summary": message_summary or "",
                "composite_text": composite_text,
            },
            ordered_event_sequence=ordered_sequence,
            event_time_gaps=time_gaps,
            social_engineering_tactics=tactics_list,
            claimed_identity=claimed_identity,
            requested_actions=actions_list,
            pattern_matches=pattern_matches or [],
            URL_features=url_features or {},
            TinyFish_observations=tinyfish_observations or {},
            infrastructure_entities=infrastructure_entities or {},
            payment_entities=payment_entities or {},
            graph_community=graph_community,
            graph_features=graph_features or {},
        )
