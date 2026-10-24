"""DBSCAN Campaign Clusterer (Step 15).

Harvested from VECTPHISH concepts.
Groups dense multi-attribute scam embeddings into emergent campaign clusters.
"""

import logging
from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.cluster import DBSCAN

logger = logging.getLogger("graph_engine.campaigns.clusterer")


class CampaignClusterer:
    """Discovers emergent scam campaigns from vector clusters using DBSCAN."""

    def __init__(self, eps: float = 0.35, min_samples: int = 2):
        # eps in cosine distance space (1.0 - cosine_similarity <= 0.35 means >= 65% similarity)
        self.eps = eps
        self.min_samples = min_samples

    def cluster_fingerprints(
        self,
        incident_ids: List[str],
        embeddings: List[List[float]],
    ) -> Dict[str, Any]:
        """Clusters a batch of incident embeddings and assigns campaign cluster IDs."""
        if len(incident_ids) < self.min_samples or not embeddings:
            return {"clusters": {}, "noise_incidents": incident_ids}

        X = np.array(embeddings, dtype=np.float32)

        # Normalize rows to unit vectors
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        X_norm = X / norms

        dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric="cosine")
        labels = dbscan.fit_predict(X_norm)

        clusters: Dict[str, List[str]] = {}
        noise: List[str] = []

        for inc_id, label in zip(incident_ids, labels):
            if label == -1:
                noise.append(inc_id)
            else:
                cluster_name = f"CAMP_DISCOVERED_CLUSTER_{label}"
                clusters.setdefault(cluster_name, []).append(inc_id)

        return {
            "clusters": clusters,
            "noise_incidents": noise,
            "total_clusters": len(clusters),
        }
