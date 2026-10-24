"""Semantic Similarity & Campaign Correlation Service (Step 15).

Matches incident embeddings against known seed scam templates and clusters.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
from services.pattern_engine.semantic.encoder import semantic_encoder

# Seed Campaign Templates
SEED_CAMPAIGNS: Dict[str, str] = {
    "CAMP_ELECTRICITY_DISCONNECTION": "Electricity power bill unpaid light cutoff tonight 9:30 PM call electricity officer immediately to update.",
    "CAMP_KYC_ACCOUNT_SUSPENSION": "Dear customer bank KYC expired PAN card update immediately or bank account will be blocked.",
    "CAMP_PART_TIME_TASK_FRAUD": "Work from home part time job earn daily 2000 to 5000 like youtube video join telegram group for task deposit.",
    "CAMP_COURIER_PARCEL_HOLD": "India Post courier package delivery on hold address incorrect pay nominal update fee.",
    "CAMP_QR_COLLECT_REFUND_INVERSION": "Scan QR code or approve UPI collect request to receive lottery prize money or instant cashback refund.",
}


class SemanticSimilarityService:
    """Computes cosine similarity and matches active incidents against known scam campaigns."""

    def __init__(self):
        self._cached_embeddings: Dict[str, np.ndarray] = {}
        self._warmup_cache()

    def _warmup_cache(self):
        for camp_id, text in SEED_CAMPAIGNS.items():
            self._cached_embeddings[camp_id] = semantic_encoder.encode(text)

    def match_campaign(self, incident_id: str, query_embedding: List[float]) -> Tuple[Optional[str], float, Optional[EvidenceSignal]]:
        """Matches a query embedding vector against seed campaigns."""
        q_vec = np.array(query_embedding, dtype=np.float32)
        best_camp = None
        best_sim = 0.0

        for camp_id, camp_vec in self._cached_embeddings.items():
            sim = semantic_encoder.cosine_similarity(q_vec, camp_vec)
            if sim > best_sim:
                best_sim = sim
                best_camp = camp_id

        signal = None
        # If similarity exceeds threshold, generate canonical CAMPAIGN EvidenceSignal
        if best_sim >= 0.70 and best_camp:
            signal = EvidenceSignal(
                incident_id=incident_id,
                dimension=SignalDimension.CAMPAIGN,
                signal_type="HIGH_SIMILARITY_TO_ACTIVE_CAMPAIGN",
                severity=SignalSeverity.HIGH if best_sim >= 0.82 else SignalSeverity.MEDIUM,
                confidence=round(best_sim, 2),
                weight=1.7,
                description=f"Incident exhibits {round(best_sim * 100, 1)}% semantic similarity to known campaign '{best_camp}'",
                provenance=ProvenanceRecord(
                    source_service="services/pattern-engine",
                    detector_name="SemanticSimilarityService",
                    target_artifact=best_camp,
                    raw_evidence={"matched_campaign": best_camp, "cosine_similarity": round(best_sim, 4)},
                ),
            )

        return best_camp, round(best_sim, 3), signal


# Global singleton instance
similarity_service = SemanticSimilarityService()
