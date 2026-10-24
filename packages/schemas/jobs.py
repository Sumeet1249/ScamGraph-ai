"""
ScamGraph AI — Background Jobs, Queues & Cache Schemas V2
Phase 7B / Prompt 22
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class JobStatus(str, Enum):
    """Canonical lifecycle states for all background jobs."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobPriority(str, Enum):
    """Execution priority levels. Higher priority jobs preempt lower priority ones."""
    CRITICAL = "CRITICAL"   # Active rescue / security actions
    HIGH = "HIGH"           # Pre-payment Guard continuation
    NORMAL = "NORMAL"       # Standard multimodal analysis & webhook delivery
    LOW = "LOW"             # Historical recomputation & batch maintenance


class WorkerClass(str, Enum):
    """Dedicated worker queues segregated by compute and operational characteristics."""
    INTERACTIVE = "interactive"     # High-priority Guard / Rescue synchronous follow-ups
    MEDIA = "media"                 # CPU/GPU-heavy OCR and STT transcription
    INTELLIGENCE = "intelligence"   # Fusion, correlation, and campaign clustering
    WEBHOOKS = "webhooks"           # Outbound partner notification I/O
    EXPORTS = "exports"             # Heavy evidence compression & signed URL generation
    MAINTENANCE = "maintenance"     # Retention, pruning, and projection rebuilds


class JobType(str, Enum):
    """Catalog of asynchronous jobs handled across ScamGraph."""
    OCR_PROCESSING = "ocr.processing"
    STT_PROCESSING = "stt.processing"
    MULTIMODAL_FUSION = "multimodal.fusion"
    GRAPH_PROJECTION = "graph.projection"
    GRAPH_REBUILD = "graph.rebuild"
    CORRELATION_ANALYSIS = "correlation.analysis"
    CAMPAIGN_RECOMPUTATION = "campaign.recomputation"
    OUTBREAK_EVALUATION = "campaign.outbreak_evaluation"
    WEBHOOK_DELIVERY = "webhook.delivery"
    EVIDENCE_EXPORT = "evidence.export"
    RETENTION_EXECUTION = "retention.execution"
    RETENTION_DRY_RUN = "retention.dry_run"
    DELETION_CASCADE = "evidence.deletion_cascade"


class FailureCategory(str, Enum):
    """Classification of job failures determining retry behavior."""
    RETRYABLE = "RETRYABLE"                         # Network timeout, transient 5xx, DB lock wait
    NON_RETRYABLE = "NON_RETRYABLE"                 # Corrupted file, permanent 4xx, bad schema
    RATE_LIMITED = "RATE_LIMITED"                   # Provider 429, requires delayed backoff
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE" # Redis/Neo4j offline
    INVALID_INPUT = "INVALID_INPUT"                 # Malformed data, unsupported MIME type
    SECURITY_REJECTED = "SECURITY_REJECTED"         # Tenant unauthorized, policy violation


class QueueMessage(BaseModel):
    """
    Lightweight queue payload transmitted across Redis or in-memory queues.
    SECURITY PRINCIPLE: NEVER store raw secrets, passwords, or full evidence bodies here.
    Store only secure references to authorized resources.
    """
    job_id: str
    job_type: JobType
    worker_class: WorkerClass = WorkerClass.INTELLIGENCE
    priority: JobPriority = JobPriority.NORMAL
    org_id: str
    principal_id: Optional[str] = None
    resource_id: str
    trace_id: str
    request_id: Optional[str] = None
    attempt: int = 1
    max_attempts: int = 3
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DurableJobRecord(BaseModel):
    """
    Canonical source-of-truth job record persisted durably in database storage.
    survives Redis restarts or crashes.
    """
    job_id: str = Field(default_factory=lambda: generate_id("job"))
    job_type: JobType
    org_id: str
    principal_id: Optional[str] = None
    resource_id: str
    status: JobStatus = Field(default=JobStatus.PENDING)
    priority: JobPriority = Field(default=JobPriority.NORMAL)
    worker_class: WorkerClass = Field(default=WorkerClass.INTELLIGENCE)
    attempt: int = 0
    max_attempts: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    failure_category: Optional[FailureCategory] = None
    result_reference: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    worker_metadata: Optional[Dict[str, Any]] = None


class DeadLetterRecord(BaseModel):
    """
    Durable record of a job that exhausted all allowed retry attempts.
    Maintains full observability without exposing raw sensitive payloads.
    """
    dead_letter_id: str = Field(default_factory=lambda: generate_id("dlq"))
    job_id: str
    job_type: JobType
    worker_class: WorkerClass
    org_id: str
    resource_id: str
    attempts: int
    failure_category: FailureCategory
    last_error_code: str
    last_error_summary: str
    queued_at: datetime
    failed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    can_manual_retry: bool = True
    manual_retried_at: Optional[datetime] = None
    manual_retried_by: Optional[str] = None


class CacheCategory(str, Enum):
    """Taxonomy of cached data with distinct sensitivity and invalidation policies."""
    PUBLIC_REFERENCE = "PUBLIC_REFERENCE"       # Known scam catalogs, official bank IFSC/UPI prefixes
    GLOBAL_INTELLIGENCE = "GLOBAL_INTELLIGENCE" # Global campaign graphs, anonymized Outbreak Radar
    TENANT_PRIVATE = "TENANT_PRIVATE"           # Tenant-specific incidents, private rule overrides
    SESSION_SECURITY = "SESSION_SECURITY"       # Rate-limit counters, token blacklists
    COMPUTATION_RESULT = "COMPUTATION_RESULT"   # Intermediate deterministic model inferences


class CacheEntryMetadata(BaseModel):
    """Metadata tracking cache item provenance and freshness."""
    key: str
    category: CacheCategory
    tenant_id: Optional[str] = None
    ttl_seconds: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "v1"
    model_version: Optional[str] = None
    is_stale: bool = False
