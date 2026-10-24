"""VectorStore Interface Abstraction (Step 20).

Defines the storage-agnostic interface for vector indexing, storage, and similarity search.
Implementations:
- PgVectorStore (PostgreSQL + pgvector)
- InMemoryVectorStore (isolated testing and local execution)
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from services.storage.vector.models import VectorObjectType, VectorRecord, VectorSearchResult


class VectorStore(ABC):
    """Abstract interface for vector storage and cosine similarity retrieval."""

    @abstractmethod
    async def store_embedding(self, record: VectorRecord) -> str:
        """Stores a vector embedding record and returns its embedding_id."""
        pass

    @abstractmethod
    async def get_embedding(self, embedding_id: str) -> Optional[VectorRecord]:
        """Retrieves a vector embedding by its unique embedding_id."""
        pass

    @abstractmethod
    async def find_similar(
        self,
        query_vector: List[float],
        object_type: Optional[VectorObjectType] = None,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Finds closest records to query_vector using cosine similarity."""
        pass

    @abstractmethod
    async def delete_embedding(self, embedding_id: str) -> bool:
        """Deletes an embedding record by ID."""
        pass

    @abstractmethod
    async def count(self, object_type: Optional[VectorObjectType] = None) -> int:
        """Returns total records stored, optionally filtered by object_type."""
        pass
