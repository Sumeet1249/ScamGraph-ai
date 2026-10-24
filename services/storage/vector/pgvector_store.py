"""PostgreSQL + pgvector VectorStore Implementation (Step 20).

Stores high-dimensional embeddings in PostgreSQL with the pgvector extension.
Enables fast approximate and exact nearest neighbor retrieval with cosine distance (<=>).
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from services.storage.vector.base import VectorStore
from services.storage.vector.models import VectorObjectType, VectorRecord, VectorSearchResult

logger = logging.getLogger("scamgraph.storage.vector.pgvector")

# Table schema DDL with pgvector
PGVECTOR_SCHEMA_SQL = """
-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create semantic embeddings table
CREATE TABLE IF NOT EXISTS semantic_embeddings (
    embedding_id VARCHAR(64) PRIMARY KEY,
    object_type VARCHAR(32) NOT NULL,
    object_id VARCHAR(128) NOT NULL,
    model_name VARCHAR(128) NOT NULL,
    model_version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    embedding vector({dimension}) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb
);

-- 3. HNSW cosine index for sub-millisecond retrieval at scale
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_hnsw 
ON semantic_embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. B-tree indexes for fast filtering
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_type ON semantic_embeddings(object_type);
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_object_id ON semantic_embeddings(object_id);
"""


class PgVectorStore(VectorStore):
    """PostgreSQL pgvector vector store implementation."""

    def __init__(
        self,
        connection_url: Optional[str] = None,
        dimension: int = 384,
        pool: Optional[Any] = None,
    ):
        self.connection_url = connection_url or "postgresql://postgres:postgres@localhost:5432/scamgraph"
        self.dimension = dimension
        self.pool = pool

    @classmethod
    def get_schema_ddl(cls, dimension: int = 384) -> str:
        """Returns the DDL script to initialize pgvector in PostgreSQL."""
        return PGVECTOR_SCHEMA_SQL.format(dimension=dimension)

    async def initialize_schema(self, conn: Optional[Any] = None) -> bool:
        """Executes DDL to ensure pgvector extension and table exist."""
        ddl = self.get_schema_ddl(self.dimension)
        if conn is not None:
            await conn.execute(ddl)
            return True
        logger.info("PgVector schema DDL generated for dimension %d", self.dimension)
        return True

    async def store_embedding(self, record: VectorRecord) -> str:
        """Stores a vector embedding in PostgreSQL."""
        # SQL statement:
        # INSERT INTO semantic_embeddings (embedding_id, object_type, object_id, model_name, model_version, embedding, created_at, metadata)
        # VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        # ON CONFLICT (embedding_id) DO UPDATE SET embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata;
        vec_str = f"[{','.join(str(f) for f in record.embedding)}]"
        query = (
            "INSERT INTO semantic_embeddings "
            "(embedding_id, object_type, object_id, model_name, model_version, embedding, created_at, metadata) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
            "ON CONFLICT (embedding_id) DO UPDATE SET "
            "embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata, model_name = EXCLUDED.model_name;"
        )
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    query,
                    record.embedding_id,
                    record.object_type.value,
                    record.object_id,
                    record.model_name,
                    record.model_version,
                    vec_str,
                    record.created_at,
                    json.dumps(record.metadata),
                )
        return record.embedding_id

    async def get_embedding(self, embedding_id: str) -> Optional[VectorRecord]:
        """Retrieves an embedding record from PostgreSQL."""
        query = (
            "SELECT embedding_id, object_type, object_id, model_name, model_version, "
            "embedding::text, created_at, metadata "
            "FROM semantic_embeddings WHERE embedding_id = $1;"
        )
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, embedding_id)
                if row:
                    raw_vec = row[5]
                    clean_vec = [float(x) for x in raw_vec.strip("[]").split(",")] if raw_vec else []
                    meta = row[7] if isinstance(row[7], dict) else json.loads(row[7] or "{}")
                    return VectorRecord(
                        embedding_id=row[0],
                        object_type=VectorObjectType(row[1]),
                        object_id=row[2],
                        model_name=row[3],
                        model_version=row[4],
                        embedding=clean_vec,
                        created_at=row[6],
                        metadata=meta,
                    )
        return None

    async def find_similar(
        self,
        query_vector: List[float],
        object_type: Optional[VectorObjectType] = None,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Queries pgvector for nearest neighbors by cosine similarity (1 - cosine distance)."""
        vec_str = f"[{','.join(str(f) for f in query_vector)}]"
        query = (
            "SELECT object_id, object_type, 1 - (embedding <=> $1::vector) AS similarity, "
            "model_name, model_version, embedding_id, metadata "
            "FROM semantic_embeddings "
            "WHERE ($2::varchar IS NULL OR object_type = $2) "
            "  AND 1 - (embedding <=> $1::vector) >= $3 "
            "ORDER BY embedding <=> $1::vector ASC "
            "LIMIT $4;"
        )
        results: List[VectorSearchResult] = []
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                type_val = object_type.value if object_type else None
                rows = await conn.fetch(query, vec_str, type_val, threshold, top_k)
                for row in rows:
                    meta = row[6] if isinstance(row[6], dict) else json.loads(row[6] or "{}")
                    results.append(
                        VectorSearchResult(
                            object_id=row[0],
                            object_type=VectorObjectType(row[1]),
                            similarity=round(float(row[2]), 4),
                            model_name=row[3],
                            model_version=row[4],
                            embedding_id=row[5],
                            metadata=meta,
                        )
                    )
        return results

    async def delete_embedding(self, embedding_id: str) -> bool:
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                res = await conn.execute("DELETE FROM semantic_embeddings WHERE embedding_id = $1;", embedding_id)
                return "DELETE 1" in res
        return False

    async def count(self, object_type: Optional[VectorObjectType] = None) -> int:
        if self.pool is not None:
            async with self.pool.acquire() as conn:
                if object_type:
                    val = await conn.fetchval(
                        "SELECT COUNT(*) FROM semantic_embeddings WHERE object_type = $1;",
                        object_type.value,
                    )
                else:
                    val = await conn.fetchval("SELECT COUNT(*) FROM semantic_embeddings;")
                return int(val or 0)
        return 0
