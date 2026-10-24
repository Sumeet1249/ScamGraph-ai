# ScamGraph AI — Pretrained Multilingual Semantic Intelligence & pgvector (Step 20)

## 1. Overview

ScamGraph Semantic Intelligence V1 introduces our first **pretrained AI embedding and vector indexing layer**. 

### Foundational Principle:
> **Embeddings are NOT scam classifiers.**
> Similarity scores represent probabilistic retrieval evidence, paraphrase resistance, and historical incident alignment — **never** standalone fraud probabilities or automated judicial verdicts (strictly enforcing **Constitutional Rule 10**).

---

## 2. Pretrained Model Architecture & Trade-Offs

ScamGraph utilizes a pluggable, configurable local Hugging Face transformer pipeline through the [SemanticEncoder](file:///s:/ScamGraph-AI/ml/embeddings/encoder.py) interface.

### Model Comparison Matrix

| Attribute | **intfloat/multilingual-e5-small** *(Default)* | **BAAI/bge-m3** *(Advanced)* |
| :--- | :--- | :--- |
| **Embedding Dimension** | **384** | **1024** |
| **Max Token Context** | 512 tokens | 8,192 tokens |
| **Model Disk Size** | **~470 MB** | ~2.2 GB |
| **CPU Inference Latency** | **Fast (~10–25 ms per message)** | Slower (~80–180 ms per message) |
| **RAM / VRAM Footprint** | ~600 MB | ~3.5 GB |
| **Multilingual Coverage** | 100+ languages (English, Hindi, Hinglish, regional scripts) | 100+ languages (dense + sparse multi-granularity) |
| **Primary Use Case** | **Low-latency live hackathon demos, local CPU execution** | Heavy batch forensics, long legal document / chat history indexing |

### Configuration

The active model is dynamically selected via environment variable or application settings:
```bash
# Default (lightweight, highly reliable for local dev & hackathon demos)
export SCAMGRAPH_EMBEDDING_MODEL="intfloat/multilingual-e5-small"

# Advanced (for GPU environments or long-context retrieval)
export SCAMGRAPH_EMBEDDING_MODEL="BAAI/bge-m3"
```

---

## 3. Normalized Semantic Representations

To prevent vector distortion and garbage-in-garbage-out retrieval, **ScamGraph strictly forbids embedding raw, arbitrary JSON payloads**.

Before encoding, entities, messages, incidents, and attack patterns are converted into canonical normalized key-value text via [SemanticRepresentationBuilder](file:///s:/ScamGraph-AI/ml/embeddings/representation.py):

```text
claimed_identity: State Bank of India
intent: account verification
tactics: impersonation, urgency
requested_action: open URL
financial_context: true
journey_stage: suspicious_link
context: Dear customer, your SBI account KYC is expired. Update immediately at https://sbi-kyc.info
```

This ensures semantic vectors encode **behavioral invariants and psychological coercion patterns**, rather than superficial formatting or ephemeral phone numbers/URLs.

---

## 4. PostgreSQL + pgvector Storage

Vector records are persisted using the [VectorStore](file:///s:/ScamGraph-AI/services/storage/vector/base.py) abstraction, implemented via [PgVectorStore](file:///s:/ScamGraph-AI/services/storage/vector/pgvector_store.py) for PostgreSQL and [InMemoryVectorStore](file:///s:/ScamGraph-AI/services/storage/vector/in_memory.py) for zero-dependency local testing.

### Target Object Types
- `MESSAGE`: Multi-channel communication lures (SMS, WhatsApp, Telegram, Call transcripts)
- `INCIDENT_SUMMARY`: Normalized timeline and evidence summary of an ongoing incident
- `PATTERN`: Declarative canonical scam pattern definitions (KYC, Electricity, Task Scam, Digital Arrest)
- `CAMPAIGN`: High-level syndicated scam cluster signatures

### Schema DDL

```sql
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
    embedding vector(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- 3. HNSW cosine distance index
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_hnsw 
ON semantic_embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. B-tree indexes for fast filtering
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_type ON semantic_embeddings(object_type);
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_object_id ON semantic_embeddings(object_id);
```

### Retrieval Query
```sql
SELECT object_id, object_type, 1 - (embedding <=> $1::vector) AS similarity,
       model_name, model_version, embedding_id, metadata
FROM semantic_embeddings
WHERE ($2::varchar IS NULL OR object_type = $2)
  AND 1 - (embedding <=> $1::vector) >= $3
ORDER BY embedding <=> $1::vector ASC
LIMIT $4;
```

---

## 5. Performance & Caching

1. **Embedding Cache (`EmbeddingCache`)**: In-memory LRU cache keyed by `model_name:sha256(text)` ensures identical messages, static pattern templates, and historical campaign lures are encoded exactly once.
2. **Deterministic Fallback**: If network connectivity is lost or heavy Hugging Face weights fail to initialize, a deterministic n-gram hash projection activates automatically, preserving test reproducibility and preventing server crashes.

---

## 6. Operational Invariants & Limitations

1. **Similarity $\neq$ Fraud Probability**:
   - A cosine similarity of $0.92$ to a known bank KYC scam means the message uses highly similar vocabulary and coercive urgency.
   - It is ingested as an `EvidenceSignal` under `SignalDimension.SEMANTIC`.
   - The Intervention Engine requires cross-dimensional corroboration (e.g. unverified VPA, typosquatted domain, or credential form) before taking disruptive actions.
2. **No Fine-Tuning at this Stage**:
   - Pretrained representations provide zero-shot multilingual paraphrase resistance.
   - Supervised contrastive fine-tuning on Indian financial fraud corpora is reserved for post-hackathon iteration.
