"""In-Memory Vector Store Implementation (Step 20).

Thread-safe, high-speed vector store implementing VectorStore for local testing and dev.
Uses numpy cosine similarity.
"""

import asyncio
from typing import Dict, List, Optional
import numpy as np

from services.storage.vector.base import VectorStore
from services.storage.vector.models import VectorObjectType, VectorRecord, VectorSearchResult


class InMemoryVectorStore(VectorStore):
    """In-memory implementation of VectorStore using numpy cosine similarity."""

    def __init__(self):
        self._records: Dict[str, VectorRecord] = {}
        self._lock = asyncio.Lock()

    async def store_embedding(self, record: VectorRecord) -> str:
        async with self._lock:
            self._records[record.embedding_id] = record
            return record.embedding_id

    async def get_embedding(self, embedding_id: str) -> Optional[VectorRecord]:
        async with self._lock:
            rec = self._records.get(embedding_id)
            return rec.model_copy() if rec else None

    async def find_similar(
        self,
        query_vector: List[float],
        object_type: Optional[VectorObjectType] = None,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        q = np.array(query_vector, dtype=np.float32)
        norm_q = np.linalg.norm(q)
        if norm_q == 0.0:
            return []

        candidates: List[VectorSearchResult] = []
        async with self._lock:
            for rec in self._records.values():
                if object_type is not None and rec.object_type != object_type:
                    continue

                v = np.array(rec.embedding, dtype=np.float32)
                norm_v = np.linalg.norm(v)
                if norm_v == 0.0:
                    continue

                sim = float(np.dot(q, v) / (norm_q * norm_v))
                if sim >= threshold:
                    candidates.append(
                        VectorSearchResult(
                            object_id=rec.object_id,
                            object_type=rec.object_type,
                            similarity=round(sim, 4),
                            model_name=rec.model_name,
                            model_version=rec.model_version,
                            embedding_id=rec.embedding_id,
                            metadata=dict(rec.metadata),
                        )
                    )

        # Sort descending by similarity
        candidates.sort(key=lambda x: x.similarity, reverse=True)
        return candidates[:top_k]

    async def delete_embedding(self, embedding_id: str) -> bool:
        async with self._lock:
            if embedding_id in self._records:
                del self._records[embedding_id]
                return True
            return False

    async def count(self, object_type: Optional[VectorObjectType] = None) -> int:
        async with self._lock:
            if object_type is None:
                return len(self._records)
            return sum(1 for r in self._records.values() if r.object_type == object_type)

    def clear(self) -> None:
        self._records.clear()
