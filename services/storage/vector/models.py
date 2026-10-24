"""Vector Storage Models & Schemas (Step 20).

Defines vector database record types and search result schemas for pgvector and in-memory storage.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class VectorObjectType(str, Enum):
    """Supported canonical object types for vector storage and retrieval."""
    MESSAGE = "MESSAGE"
    INCIDENT_SUMMARY = "INCIDENT_SUMMARY"
    PATTERN = "PATTERN"
    CAMPAIGN = "CAMPAIGN"


class VectorRecord(BaseModel):
    """Canonical vector embedding record stored in pgvector or in-memory vector store."""
    embedding_id: str = Field(default_factory=lambda: str(uuid4()), description="Primary key UUID")
    object_type: VectorObjectType = Field(..., description="Target object classification")
    object_id: str = Field(..., description="ID of source entity, message, incident, pattern, or campaign")
    model_name: str = Field(..., description="Model identifier used to produce the vector")
    model_version: str = Field(default="1.0.0", description="Version of the embedding model")
    embedding: List[float] = Field(..., description="Dense float vector embedding")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary queryable payload or provenance")


class VectorSearchResult(BaseModel):
    """Result returned by vector similarity search."""
    object_id: str
    object_type: VectorObjectType
    similarity: float = Field(..., ge=-1.0, le=1.0, description="Cosine similarity score (0.0 to 1.0)")
    model_name: str
    model_version: str = "1.0.0"
    embedding_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
