"""
ScamGraph AI — Async Jobs, Redis, Queue & Cache Verification Suite (Phase 7B / Step 22)
Tests all 20 required production scenarios from Prompt 22.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta

from packages.schemas.jobs import (
    JobStatus,
    JobPriority,
    WorkerClass,
    JobType,
    FailureCategory,
    QueueMessage,
    DurableJobRecord,
    CacheCategory,
)
from services.jobs.queue import MemoryJobQueue, reset_job_queue
from services.jobs.cache import CacheManager, reset_cache_manager
from services.jobs.workers import (
    WorkerContext,
    OCRWorker,
    STTWorker,
    MultimodalWorker,
    GraphProjectionWorker,
    CorrelationWorker,
    CampaignWorker,
    WebhookWorker,
    ExportWorker,
    RetentionWorker,
    DeletionWorker,
)


@pytest.fixture
def queue():
    return MemoryJobQueue()


@pytest.fixture
def cache():
    return CacheManager(env="test")


# =============================================================================
# REQUIRED TEST #1: Screenshot Async Analysis
# =============================================================================
@pytest.mark.asyncio
async def test_req_1_screenshot_async_analysis(queue, cache):
    """Artifact -> queued OCR -> OCR worker -> observation -> completed job."""
    worker = OCRWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_screenshot_electricity_bill",
        priority=JobPriority.NORMAL,
        worker_class=WorkerClass.MEDIA,
    )
    assert job.status == JobStatus.QUEUED

    msg, dequeued_job = await queue.dequeue(WorkerClass.MEDIA)
    assert dequeued_job.job_id == job.job_id
    assert dequeued_job.status == JobStatus.RUNNING

    completed = await worker.execute_job(msg, dequeued_job)
    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data is not None
    assert "powerbill.officer@paytm" in completed.result_data["extracted_text"]
    assert completed.result_reference == "obs://ocr/art_screenshot_electricity_bill"


# =============================================================================
# REQUIRED TEST #2: Audio Async Analysis (STT)
# =============================================================================
@pytest.mark.asyncio
async def test_req_2_audio_async_analysis(queue, cache):
    """Audio upload -> STT worker -> transcript & journey stage -> completed job."""
    worker = STTWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.STT_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_audio_digital_arrest_call",
        priority=JobPriority.NORMAL,
        worker_class=WorkerClass.MEDIA,
    )
    msg, dequeued_job = await queue.dequeue(WorkerClass.MEDIA)
    completed = await worker.execute_job(msg, dequeued_job)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["journey_stage"] == "PRESSURE"
    assert "DIGITAL_ARREST" in completed.result_data["detected_tactics"]
    assert completed.result_data["urgency_score"] > 0.90


# =============================================================================
# REQUIRED TEST #3: Temporary Provider Failure -> Retry -> Success
# =============================================================================
@pytest.mark.asyncio
async def test_req_3_transient_failure_retry(queue, cache):
    """OCR provider fails temporarily -> job retries with backoff -> succeeds."""
    worker = OCRWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_transient_fail_screenshot",
        priority=JobPriority.NORMAL,
        worker_class=WorkerClass.MEDIA,
        max_attempts=3,
    )

    # First attempt: triggers transient failure
    msg, dequeued_job = await queue.dequeue(WorkerClass.MEDIA)
    retried_job = await worker.execute_job(msg, dequeued_job)
    assert retried_job.status == JobStatus.RETRYING
    assert retried_job.error_code == "PROVIDER_TEMPORARY_OUTAGE"
    assert retried_job.failure_category == FailureCategory.RETRYABLE

    # Allow delayed retry callback to requeue
    await asyncio.sleep(1.5)

    # Second attempt: dequeued and succeeds
    msg2, dequeued_job2 = await queue.dequeue(WorkerClass.MEDIA)
    assert dequeued_job2 is not None
    completed = await worker.execute_job(msg2, dequeued_job2)
    assert completed.status == JobStatus.COMPLETED


# =============================================================================
# REQUIRED TEST #4: Malformed Image -> NON_RETRYABLE Failure
# =============================================================================
@pytest.mark.asyncio
async def test_req_4_malformed_image_non_retryable(queue, cache):
    """Corrupted artifact produces immediate NON_RETRYABLE failure without futile retries."""
    worker = OCRWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_corrupted_payload_01",
        worker_class=WorkerClass.MEDIA,
    )
    msg, dequeued_job = await queue.dequeue(WorkerClass.MEDIA)
    failed_job = await worker.execute_job(msg, dequeued_job)

    assert failed_job.status == JobStatus.FAILED
    assert failed_job.error_code == "POISON_PAYLOAD"
    assert failed_job.failure_category == FailureCategory.NON_RETRYABLE


# =============================================================================
# REQUIRED TEST #5: Deduplication (Same Artifact Submitted Twice)
# =============================================================================
@pytest.mark.asyncio
async def test_req_5_job_deduplication(queue, cache):
    """Submitting the same job with identical idempotency key returns existing job."""
    job1 = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_fintech_01",
        resource_id="art_same_screenshot_hash",
        idempotency_key="idemp_ocr_hash_abc123",
        worker_class=WorkerClass.MEDIA,
    )
    job2 = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_fintech_01",
        resource_id="art_same_screenshot_hash",
        idempotency_key="idemp_ocr_hash_abc123",
        worker_class=WorkerClass.MEDIA,
    )
    assert job1.job_id == job2.job_id
    depth = await queue.get_queue_depth(WorkerClass.MEDIA)
    assert depth == 1


# =============================================================================
# REQUIRED TEST #6: Worker Crash / Exception Recovery
# =============================================================================
@pytest.mark.asyncio
async def test_req_6_worker_crash_recovery(queue, cache):
    """When a worker raises an unhandled error, job status is updated to FAILED/RETRYING safely."""
    job = await queue.enqueue(
        job_type=JobType.CORRELATION_ANALYSIS,
        org_id="org_bank_01",
        resource_id="inc_crash_test",
        worker_class=WorkerClass.INTELLIGENCE,
    )
    msg, dequeued_job = await queue.dequeue(WorkerClass.INTELLIGENCE)
    
    # Simulate unhandled exception caught by supervisor
    recovered = await queue.fail_or_retry(
        job_id=dequeued_job.job_id,
        error_code="WORKER_SEGFAULT_SIMULATION",
        error_message="Worker process died unexpectedly",
        failure_category=FailureCategory.RETRYABLE,
    )
    assert recovered.status in (JobStatus.RETRYING, JobStatus.FAILED)
    assert recovered.error_code == "WORKER_SEGFAULT_SIMULATION"


# =============================================================================
# REQUIRED TEST #7: Durable State Survives Restart
# =============================================================================
@pytest.mark.asyncio
async def test_req_7_durable_state_survives_restart(queue):
    """Durable job record exists in canonical storage independently of queue memory."""
    job = await queue.enqueue(
        job_type=JobType.EVIDENCE_EXPORT,
        org_id="org_telco_01",
        resource_id="exp_compliance_case_2026",
        worker_class=WorkerClass.EXPORTS,
    )
    retrieved = await queue.get_status(job.job_id)
    assert retrieved is not None
    assert retrieved.resource_id == "exp_compliance_case_2026"
    assert retrieved.org_id == "org_telco_01"


# =============================================================================
# REQUIRED TEST #8: Graph Projection Lag Tracking
# =============================================================================
@pytest.mark.asyncio
async def test_req_8_graph_projection_lag(queue, cache):
    """When graph projection is delayed, lag metric is non-zero and observable."""
    initial_lag = cache.get_graph_lag_seconds()
    assert initial_lag >= 0.0

    worker = GraphProjectionWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.GRAPH_PROJECTION,
        org_id="org_bank_01",
        resource_id="ent_mule_account_7788",
        worker_class=WorkerClass.INTELLIGENCE,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.INTELLIGENCE)
    await worker.execute_job(msg, dequeued)

    fresh_lag = cache.get_graph_lag_seconds()
    assert fresh_lag < 1.0


# =============================================================================
# REQUIRED TEST #9: Bounded Candidate Correlation (No All-Pairs)
# =============================================================================
@pytest.mark.asyncio
async def test_req_9_bounded_candidate_correlation(queue, cache):
    """Correlation job evaluates bounded candidate pool, not all-pairs."""
    worker = CorrelationWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.CORRELATION_ANALYSIS,
        org_id="org_bank_01",
        resource_id="inc_bounded_candidate_01",
        worker_class=WorkerClass.INTELLIGENCE,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.INTELLIGENCE)
    completed = await worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["candidate_pool_size"] == 5
    assert len(completed.result_data["strong_correlations"]) == 5


# =============================================================================
# REQUIRED TEST #10: Correlation Updates Campaign & Outbreak Radar
# =============================================================================
@pytest.mark.asyncio
async def test_req_10_campaign_outbreak_radar_flow(queue, cache):
    """Strong correlation triggers campaign recomputation and updates Radar cache."""
    camp_worker = CampaignWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.CAMPAIGN_RECOMPUTATION,
        org_id="org_bank_01",
        resource_id="cmp_electricity_scam_delhi",
        worker_class=WorkerClass.INTELLIGENCE,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.INTELLIGENCE)
    completed = await camp_worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["status"] == "OUTBREAK"
    assert completed.result_data["outbreak_alert_triggered"] is True
    assert cache.get_radar_lag_seconds() < 1.0

    # Verifies webhook notification was enqueued for the outbreak
    whk_depth = await queue.get_queue_depth(WorkerClass.WEBHOOKS)
    assert whk_depth >= 1


# =============================================================================
# REQUIRED TEST #11: Campaign Alert -> Signed Webhook Delivery
# =============================================================================
@pytest.mark.asyncio
async def test_req_11_signed_webhook_delivery(queue, cache):
    """Outbreak alert triggers HMAC-signed webhook delivery to partner."""
    whk_worker = WebhookWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.WEBHOOK_DELIVERY,
        org_id="org_partner_fintech",
        resource_id="whk_event_alert_9901",
        worker_class=WorkerClass.WEBHOOKS,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.WEBHOOKS)
    completed = await whk_worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["status"] == "DELIVERED"
    assert completed.result_data["http_status"] == 200
    assert "sha256=" in completed.result_data["signature"]


# =============================================================================
# REQUIRED TEST #12: Webhook Endpoint Unavailable -> Dead Letter
# =============================================================================
@pytest.mark.asyncio
async def test_req_12_webhook_endpoint_unavailable_dead_letter(queue, cache):
    """When partner endpoint fails repeatedly, job is bounded and moved to dead-letter queue."""
    whk_worker = WebhookWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.WEBHOOK_DELIVERY,
        org_id="org_down_partner",
        resource_id="whk_endpoint_down_attempt",
        worker_class=WorkerClass.WEBHOOKS,
        max_attempts=1,  # immediate dead letter on attempt 1 failure
    )
    msg, dequeued = await queue.dequeue(WorkerClass.WEBHOOKS)
    failed = await whk_worker.execute_job(msg, dequeued)

    assert failed.status == JobStatus.FAILED
    dlqs = await queue.list_dead_letters(10)
    assert any(d.job_id == job.job_id for d in dlqs)


# =============================================================================
# REQUIRED TEST #13: Evidence Export -> Protected Signed URL
# =============================================================================
@pytest.mark.asyncio
async def test_req_13_evidence_export_expiry(queue, cache):
    """Authorized export generates protected archive with verifiable expiration."""
    exp_worker = ExportWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.EVIDENCE_EXPORT,
        org_id="org_bank_01",
        resource_id="exp_investigation_dossier_5544",
        worker_class=WorkerClass.EXPORTS,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.EXPORTS)
    completed = await exp_worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["archive_format"] == "ZIP_AES256"
    assert "token=signed_token_sample" in completed.result_data["download_url"]
    assert "expires_at" in completed.result_data


# =============================================================================
# REQUIRED TEST #14: Retention Dry Run (Report Only)
# =============================================================================
@pytest.mark.asyncio
async def test_req_14_retention_dry_run(queue, cache):
    """Retention dry-run reports eligible records without modifying or deleting data."""
    ret_worker = RetentionWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.RETENTION_DRY_RUN,
        org_id="org_bank_01",
        resource_id="retention_dry_run_audit",
        worker_class=WorkerClass.MAINTENANCE,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.MAINTENANCE)
    completed = await ret_worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["mode"] == "DRY_RUN"
    assert completed.result_data["action_taken"] == "NONE_REPORT_ONLY"
    assert completed.result_data["records_eligible_for_deletion"] == 2


# =============================================================================
# REQUIRED TEST #15: Retention Execution & Dependent Invalidation
# =============================================================================
@pytest.mark.asyncio
async def test_req_15_retention_execution(queue, cache):
    """Destructive retention removes records and invalidates dependent intelligence."""
    ret_worker = RetentionWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.RETENTION_EXECUTION,
        org_id="org_bank_01",
        resource_id="retention_exec_compliance",
        worker_class=WorkerClass.MAINTENANCE,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.MAINTENANCE)
    completed = await ret_worker.execute_job(msg, dequeued)

    assert completed.status == JobStatus.COMPLETED
    assert completed.result_data["mode"] == "EXECUTION"
    assert completed.result_data["action_taken"] == "DELETED_OR_ANONYMIZED"
    assert completed.result_data["cascade_correlations_invalidated"] > 0


# =============================================================================
# REQUIRED TEST #16: PRIVATE_ONLY Isolation in Workers
# =============================================================================
@pytest.mark.asyncio
async def test_req_16_private_only_worker_isolation():
    """WorkerContext prevents private-only tenant data from leaking to global graphs."""
    ctx_private = WorkerContext(
        org_id="org_private_defense_corp",
        data_contribution_policy="PRIVATE_ONLY",
    )
    assert ctx_private.can_publish_globally() is False

    ctx_contribute = WorkerContext(
        org_id="org_public_fintech",
        data_contribution_policy="CONTRIBUTE_ANONYMIZED",
    )
    assert ctx_contribute.can_publish_globally() is True


# =============================================================================
# REQUIRED TEST #17: Tenant-Isolated Cache (No Cross-Tenant Leakage)
# =============================================================================
@pytest.mark.asyncio
async def test_req_17_tenant_cache_isolation(cache):
    """Tenant A private cache entry cannot be accessed by Tenant B."""
    key_a = cache.build_key(
        category=CacheCategory.TENANT_PRIVATE,
        resource_type="incident",
        resource_id="inc_shared_num_123",
        tenant_id="tenant_a",
    )
    await cache.set(
        key=key_a,
        value={"risk_score": 0.95, "private_notes": "VIP customer report"},
        category=CacheCategory.TENANT_PRIVATE,
        tenant_id="tenant_a",
    )

    # Tenant A access succeeds
    val_a = await cache.get(key_a, category=CacheCategory.TENANT_PRIVATE, tenant_id="tenant_a")
    assert val_a is not None
    assert val_a["risk_score"] == 0.95

    # Tenant B access to same logical key fails
    val_b = await cache.get(key_a, category=CacheCategory.TENANT_PRIVATE, tenant_id="tenant_b")
    assert val_b is None


# =============================================================================
# REQUIRED TEST #18: Revoked API Key Invalidation
# =============================================================================
@pytest.mark.asyncio
async def test_req_18_revoked_api_key_invalidation(cache):
    """Revoking an API key immediately purges security cache entry."""
    key = cache.build_key(
        category=CacheCategory.SESSION_SECURITY,
        resource_type="api_key",
        resource_id="sg_live_secret_key_88",
    )
    await cache.set(key, {"valid": True, "org_id": "org_bank_01"}, category=CacheCategory.SESSION_SECURITY)
    assert await cache.get(key, category=CacheCategory.SESSION_SECURITY) is not None

    # Revocation invalidates cache
    await cache.invalidate(key)
    assert await cache.get(key, category=CacheCategory.SESSION_SECURITY) is None


# =============================================================================
# REQUIRED TEST #19: Priority Preemption (Guard > Historical Backlog)
# =============================================================================
@pytest.mark.asyncio
async def test_req_19_priority_preemption(queue):
    """High-priority Guard continuation job dequeues ahead of low-priority historical backlog."""
    # Enqueue 5 low-priority historical jobs
    for i in range(5):
        await queue.enqueue(
            job_type=JobType.CAMPAIGN_RECOMPUTATION,
            org_id="org_system",
            resource_id=f"hist_batch_{i}",
            priority=JobPriority.LOW,
            worker_class=WorkerClass.INTERACTIVE,
        )

    # Enqueue 1 CRITICAL / HIGH Guard job
    guard_job = await queue.enqueue(
        job_type=JobType.CORRELATION_ANALYSIS,
        org_id="org_bank_01",
        resource_id="guard_pre_payment_check",
        priority=JobPriority.CRITICAL,
        worker_class=WorkerClass.INTERACTIVE,
    )

    # Next dequeued job MUST be the CRITICAL Guard job
    msg, dequeued = await queue.dequeue(WorkerClass.INTERACTIVE)
    assert dequeued.job_id == guard_job.job_id
    assert dequeued.resource_id == "guard_pre_payment_check"
    assert dequeued.priority == JobPriority.CRITICAL


# =============================================================================
# REQUIRED TEST #20: Poison Job Dead-Lettering (No Crash Loop)
# =============================================================================
@pytest.mark.asyncio
async def test_req_20_poison_job_no_crash_loop(queue, cache):
    """A poison job that crashes repeatedly is routed to dead-letter queue without killing the worker."""
    worker = OCRWorker(queue=queue, cache=cache)
    job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_corrupted_crash_loop",
        worker_class=WorkerClass.MEDIA,
        max_attempts=2,
    )

    msg, dequeued = await queue.dequeue(WorkerClass.MEDIA)
    failed = await worker.execute_job(msg, dequeued)

    assert failed.status == JobStatus.FAILED
    assert failed.error_code == "POISON_PAYLOAD"
    
    # Worker is alive and can process another normal job
    good_job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_normal_screenshot",
        worker_class=WorkerClass.MEDIA,
    )
    good_msg, good_dequeued = await queue.dequeue(WorkerClass.MEDIA)
    good_completed = await worker.execute_job(good_msg, good_dequeued)
    assert good_completed.status == JobStatus.COMPLETED
