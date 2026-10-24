"""Scam Fingerprint Builder (Step 15).

Generates invariant multi-attribute behavioral signatures.
"""

from typing import Any, Dict, List, Optional
from packages.schemas import ScamFingerprint
from services.pattern_engine.semantic.encoder import semantic_encoder


class ScamFingerprintBuilder:
    """Builds invariant behavioral signatures for emerging variant detection."""

    @staticmethod
    def build(
        incident_id: str,
        message_summary: str,
        claimed_identity: Optional[str] = None,
        tactics: Optional[List[str]] = None,
        requested_action: Optional[str] = None,
        stage_sequence: Optional[List[str]] = None,
        temporal_pace_seconds: int = 0,
        url_markers: Optional[List[str]] = None,
        web_behavior: Optional[Dict[str, Any]] = None,
        infrastructure_hash: Optional[Dict[str, Any]] = None,
        payment_profile: Optional[Dict[str, Any]] = None,
    ) -> ScamFingerprint:
        tactics_list = tactics or []

        # Formulate composite semantic prompt capturing core psychological lure
        composite_parts = []
        if claimed_identity:
            composite_parts.append(f"Claimed Identity: {claimed_identity}")
        if tactics_list:
            composite_parts.append(f"Tactics: {', '.join(tactics_list)}")
        if requested_action:
            composite_parts.append(f"Requested Action: {requested_action}")
        composite_parts.append(f"Message: {message_summary}")

        composite_text = " | ".join(composite_parts)
        embedding_vec = semantic_encoder.encode(composite_text)

        return ScamFingerprint(
            incident_id=incident_id,
            semantic_embedding=embedding_vec.tolist(),
            claimed_identity=claimed_identity,
            social_engineering_tactics=tactics_list,
            requested_action=requested_action,
            stage_sequence=stage_sequence or [],
            temporal_pace_seconds=temporal_pace_seconds,
            url_markers=url_markers or [],
            web_behavior=web_behavior or {},
            infrastructure_hash=infrastructure_hash or {},
            payment_profile=payment_profile or {},
        )
