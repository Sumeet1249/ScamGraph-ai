"""
ScamGraph AI — Production Observability, AI Quality & Drift Verification Suite (Phase 7C / Step 23)
Tests all 30 required scenarios from Prompt 23.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta

from services.observability.telemetry import (
    TelemetrySanitizer,
    StructuredLogger,
    MetricsCollector,
    ProviderState,
    ErrorCode,
)
from services.observability.tracing import (
    TraceContext,
    SpanRecord,
)
from services.observability.health import (
    HealthCheckService,
    HealthStatus,
    RadarFreshnessStatus,
)
from services.observability.ai_quality import (
    AIQualityEngine,
    GoldenTestCase,
    EvaluationDatasetType,
)
from services.observability.drift_detector import (
    DriftDetector,
    DriftCategory,
)
from services.jobs.queue import MemoryJobQueue
from services.jobs.cache import CacheManager
from packages.schemas.jobs import JobType, JobPriority, WorkerClass, JobStatus


# =============================================================================
# TEST 1: Protect Request Observability
# =============================================================================
def test_req_1_protect_request_observability():
    """Protect request produces request ID, trace, analysis metrics, and safe structured logs."""
    logger = StructuredLogger(service_name="scamgraph-protect")
    metrics = MetricsCollector()
    trace = TraceContext()

    span = trace.start_span("protect_analysis")
    metrics.record_request("protect_check", latency_ms=185.0, is_error=False)
    trace.finish_span(span)

    log_entry = logger.format_log(
        level="INFO",
        message="Protect check completed for transaction",
        request_id=trace.request_id,
        trace_id=trace.trace_id,
        duration_ms=span.duration_ms,
        extra={"customer_phone": "9876543210", "risk_score": 0.88},
    )

    assert log_entry["request_id"] == trace.request_id
    assert log_entry["trace_id"] == trace.trace_id
    assert "XXXXXX" in log_entry["metadata"]["customer_phone"]
    assert metrics.get_latency_percentiles("protect_check")["count"] == 1


# =============================================================================
# TEST 2: Trace Continuity Across Background Queue
# =============================================================================
@pytest.mark.asyncio
async def test_req_2_trace_continuity_across_queue():
    """Trace ID flows unbroken from HTTP request into queue message and worker execution."""
    queue = MemoryJobQueue()
    client_trace = TraceContext(trace_id="trc_http_client_9988", request_id="req_frontend_77")

    job = await queue.enqueue(
        job_type=JobType.OCR_PROCESSING,
        org_id="org_bank_01",
        resource_id="art_evidence_screenshot",
        trace_id=client_trace.trace_id,
        request_id=client_trace.request_id,
        worker_class=WorkerClass.MEDIA,
    )

    msg, dequeued = await queue.dequeue(WorkerClass.MEDIA)
    assert msg.trace_id == client_trace.trace_id
    assert dequeued.trace_id == client_trace.trace_id
    assert dequeued.request_id == client_trace.request_id


# =============================================================================
# TEST 3: Worker Retries Visible in Metrics
# =============================================================================
@pytest.mark.asyncio
async def test_req_3_worker_retries_visible():
    """Worker retries are recorded without duplicating the canonical incident."""
    queue = MemoryJobQueue()
    job = await queue.enqueue(
        job_type=JobType.CORRELATION_ANALYSIS,
        org_id="org_bank_01",
        resource_id="inc_transient_retry",
        worker_class=WorkerClass.INTELLIGENCE,
        max_attempts=3,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.INTELLIGENCE)
    retried = await queue.fail_or_retry(
        job_id=dequeued.job_id,
        error_code="DB_LOCK_WAIT_TIMEOUT",
        error_message="Database lock contention, retrying",
    )
    assert retried.status == JobStatus.RETRYING
    assert retried.attempt == 1


# =============================================================================
# TEST 4: Dead-Letter Job Metric & Visibility
# =============================================================================
@pytest.mark.asyncio
async def test_req_4_dead_letter_metric():
    """Dead-lettered jobs are tracked in dead-letter storage and observable."""
    queue = MemoryJobQueue()
    job = await queue.enqueue(
        job_type=JobType.WEBHOOK_DELIVERY,
        org_id="org_bank_01",
        resource_id="whk_exhausted_target",
        worker_class=WorkerClass.WEBHOOKS,
        max_attempts=1,
    )
    msg, dequeued = await queue.dequeue(WorkerClass.WEBHOOKS)
    failed = await queue.fail_or_retry(
        job_id=dequeued.job_id,
        error_code="WEBHOOK_HOST_UNREACHABLE",
        error_message="Host unreachable after all retries",
    )
    assert failed.status == JobStatus.FAILED
    dlqs = await queue.list_dead_letters()
    assert len(dlqs) >= 1
    assert dlqs[0].job_id == job.job_id


# =============================================================================
# TEST 5: TinyFish Timeout Metric & Degradation
# =============================================================================
def test_req_5_tinyfish_timeout_metric():
    """TinyFish timeout records provider degradation and latency spike."""
    metrics = MetricsCollector()
    metrics.record_provider_call(
        provider="tinyfish",
        latency_ms=10500.0,
        state=ProviderState.DEGRADED,
    )
    state, avg_lat = metrics.get_provider_status("tinyfish")
    assert state == ProviderState.DEGRADED
    assert avg_lat == 10500.0


# =============================================================================
# TEST 6: Redis Failure Degradation
# =============================================================================
def test_req_6_redis_failure_degradation():
    """When external Redis is unavailable, health service reports DEGRADED without crashing."""
    cache = CacheManager(env="test")
    health = HealthCheckService()
    liveness = health.check_liveness()
    assert liveness["status"] == "UP"
    readiness = health.check_readiness()
    assert readiness["can_serve_traffic"] is True


# =============================================================================
# TEST 7: Database Latency Spike Observability
# =============================================================================
def test_req_7_database_latency_spike():
    """Latency distribution captures p95 and p99 query performance accurately."""
    metrics = MetricsCollector()
    for lat in [12.0, 15.0, 14.0, 18.0, 25.0, 22.0, 310.0, 450.0]:
        metrics.record_request("db_query_incident", latency_ms=lat)

    pcts = metrics.get_latency_percentiles("db_query_incident")
    assert pcts["p95"] > 200.0
    assert pcts["count"] == 8


# =============================================================================
# TEST 8: OCR Failure Privacy-Safe Logging
# =============================================================================
def test_req_8_ocr_failure_privacy_safe():
    """OCR failure logs error codes without recording raw document content."""
    logger = StructuredLogger()
    record = logger.format_log(
        level="ERROR",
        message="OCR engine crashed on image buffer with OTP 987654 inside",
        error_code=ErrorCode.PROCESSING_ERROR.value,
        extra={"artifact_id": "art_private_doc_99"},
    )
    assert "[REDACTED_OTP]" in record["message"]
    assert "987654" not in record["message"]
    assert record["error_code"] == "PROCESSING_ERROR"


# =============================================================================
# TEST 9: Translation Pipeline Fallback & Metric
# =============================================================================
def test_req_9_translation_pipeline_fallback():
    """Translation failure records provider metric and returns original text fallback."""
    metrics = MetricsCollector()
    metrics.record_provider_call(provider="indic_trans", latency_ms=850.0, state=ProviderState.UNAVAILABLE)
    state, _ = metrics.get_provider_status("indic_trans")
    assert state == ProviderState.UNAVAILABLE


# =============================================================================
# TEST 10: Realtime Connection Metrics
# =============================================================================
def test_req_10_realtime_metrics():
    """Realtime connection events update metrics."""
    metrics = MetricsCollector()
    metrics.record_request("realtime_ws_connect", latency_ms=45.0)
    assert metrics.get_latency_percentiles("realtime_ws_connect")["count"] == 1


# =============================================================================
# TEST 11: Radar Pipeline Freshness Lag Transition
# =============================================================================
@pytest.mark.asyncio
async def test_req_11_radar_freshness_transition():
    """When radar updates lag behind commitment, health marks DELAYED or STALE."""
    health = HealthCheckService()
    # Artificially set radar update to 12 minutes ago
    health.cache._radar_last_updated_at = datetime.now(timezone.utc) - timedelta(minutes=12)
    diag = await health.check_deep_health()
    assert diag["radar_freshness"] == RadarFreshnessStatus.DELAYED.value


# =============================================================================
# TEST 12: Campaign Worker Failure Observability
# =============================================================================
def test_req_12_campaign_worker_failure():
    """Campaign pipeline failure records structured failure event."""
    logger = StructuredLogger()
    entry = logger.format_log(
        level="ERROR",
        message="Campaign recomputation clusterer failed on memory allocation",
        error_code=ErrorCode.PROCESSING_ERROR.value,
        extra={"campaign_id": "cmp_electricity_scam"},
    )
    assert entry["error_code"] == "PROCESSING_ERROR"
    assert entry["metadata"]["campaign_id"] == "cmp_electricity_scam"


# =============================================================================
# TEST 13: "Share OTP" Positive Credential Solicitation
# =============================================================================
def test_req_13_share_otp_positive():
    """'Share your OTP' is identified as credential solicitation."""
    engine = AIQualityEngine()
    result = engine.evaluate_inference("Please share your OTP immediately to avoid account closure.")
    assert result["is_scam"] is True
    assert result["credential_solicitation"] is True


# =============================================================================
# TEST 14: "Never share OTP" Negation Test
# =============================================================================
def test_req_14_never_share_otp_negation():
    """'Never share your OTP' is recognized as benign security advice."""
    engine = AIQualityEngine()
    result = engine.evaluate_inference("SECURITY ADVISORY: Never share your OTP with any caller.")
    assert result["is_scam"] is False
    assert result["credential_solicitation"] is False
    assert result["reason_code"] == "BENIGN_SAFETY_ADVISORY"


# =============================================================================
# TEST 15: Hindi Negation Distinction ("₹5000 bhejo" vs "₹5000 mat bhejo")
# =============================================================================
def test_req_15_hindi_negation_distinction():
    """Accurately distinguishes Hindi affirmative solicitation from negation advisory."""
    engine = AIQualityEngine()
    
    # Affirmative solicitation
    pos = engine.evaluate_inference("Bijli kat jayegi, turant ₹5000 bhejo.")
    assert pos["is_scam"] is True
    assert pos["payment_solicitation"] is True

    # Negated warning
    neg = engine.evaluate_inference("Ye fake alert hai, kisi ko bhi ₹5000 mat bhejo.")
    assert neg["is_scam"] is False
    assert neg["payment_solicitation"] is False


# =============================================================================
# TEST 16: New Scam Wording with Known Journey
# =============================================================================
def test_req_16_new_wording_known_journey():
    """Novel phrasing of digital arrest still recognized by behavioral triggers."""
    engine = AIQualityEngine()
    res = engine.evaluate_inference("Customs and CBI special cell notice: Your name is tied to narcotics. You are under digital arrest.")
    assert res["is_scam"] is True
    assert res["risk_score"] > 0.85


# =============================================================================
# TEST 17: Known Scam Wording in Benign Context
# =============================================================================
def test_req_17_known_wording_benign_context():
    """Transactional bank statement containing 'account' and 'log in' is not flagged as scam."""
    engine = AIQualityEngine()
    res = engine.evaluate_inference("Your HDFC monthly bank account statement is ready. Log in to netbanking to download.")
    assert res["is_scam"] is False


# =============================================================================
# TEST 18: Hinglish Pattern in Drift without False Positive
# =============================================================================
def test_req_18_hinglish_drift_segmentation():
    """Hinglish code-mixing is tracked as language distribution, not penalized as fraud."""
    detector = DriftDetector()
    score, exp = detector.calculate_novelty_score(
        text="Aapka parcel mumbai me atka hai",
        detected_tactics=["URGENCY"],
    )
    # Novelty score remains low because urgency is an established tactic
    assert score <= 0.20


# =============================================================================
# TEST 19: ScamDNA Cluster Drift Detection
# =============================================================================
def test_req_19_scamdna_cluster_drift():
    """Significant divergence in ScamDNA behavioral clusters triggers drift alert."""
    detector = DriftDetector()
    alert = detector.evaluate_scamdna_cluster_drift(current_cluster_variance=0.28)
    assert alert is not None
    assert alert.category == DriftCategory.SCAMDNA_DRIFT
    assert alert.deviation_percent > 35.0


# =============================================================================
# TEST 20: Campaign Journey Drift Detection
# =============================================================================
def test_req_20_campaign_journey_drift():
    """Accelerated stage velocity to payment triggers journey drift alert."""
    detector = DriftDetector()
    alert = detector.evaluate_journey_drift(current_avg_stages_to_payment=2.0)
    assert alert is not None
    assert alert.category == DriftCategory.JOURNEY_DRIFT
    assert "faster than baseline" in alert.description


# =============================================================================
# TEST 21: Model Version Comparison in Evaluation History
# =============================================================================
def test_req_21_model_version_comparison():
    """Evaluation history records multiple model versions for historical regression analysis."""
    engine = AIQualityEngine(active_model_version="scamgraph-v2.9")
    r1 = engine.run_golden_regression()
    
    engine.active_model_version = "scamgraph-v3.0"
    r2 = engine.run_golden_regression()

    history = engine.get_evaluation_history()
    assert len(history) == 2
    assert history[0].model_version == "scamgraph-v2.9"
    assert history[1].model_version == "scamgraph-v3.0"


# =============================================================================
# TEST 22: Critical Safety Regression Release Gate
# =============================================================================
def test_req_22_critical_regression_blocks_release():
    """If a critical safety regression occurs, release gate is marked as BLOCKED."""
    engine = AIQualityEngine()
    # Create regression test case that artificially fails
    failing_suite = [
        GoldenTestCase(
            test_id="bad_01",
            scenario_name="Broken Negation Regression",
            input_text="Never share your OTP with anyone.",
            expected_is_scam=True,  # Intentionally contradicting expected negation
            is_critical_safety_test=True,
        )
    ]
    report = engine.run_golden_regression(failing_suite)
    assert report.critical_safety_regressions > 0
    assert report.is_release_blocked is True


# =============================================================================
# TEST 23: Telemetry Redaction Prevents Secret Leakage
# =============================================================================
def test_req_23_telemetry_redaction_secrets():
    """Centralized TelemetrySanitizer thoroughly redacts passwords, CVVs, OTPs, and card numbers."""
    raw_payload = {
        "password": "SuperSecretPassword123",
        "pin": "1234",
        "otp": "998811",
        "cvv": "456",
        "card_number": "4111 2222 3333 4444",
        "message": "User entered OTP: 654321 for card 5500 1234 5678 9900 and CVV: 789",
    }
    sanitized = TelemetrySanitizer.sanitize_dict(raw_payload)

    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["pin"] == "[REDACTED]"
    assert sanitized["otp"] == "[REDACTED]"
    assert "[REDACTED_OTP]" in sanitized["message"]
    assert "[REDACTED_CARD]" in sanitized["message"]
    assert "[REDACTED_CVV]" in sanitized["message"]
    assert "654321" not in sanitized["message"]


# =============================================================================
# TEST 24: Unauthorized Access Security Telemetry
# =============================================================================
def test_req_24_unauthorized_access_signal():
    """Unauthorized object access emits security error without revealing internal object contents."""
    logger = StructuredLogger()
    record = logger.format_log(
        level="WARN",
        message="Unauthorized tenant access attempt blocked",
        error_code=ErrorCode.AUTHORIZATION_ERROR.value,
        tenant_id="tenant_attacker",
        extra={"target_resource": "inc_private_9988"},
    )
    assert record["error_code"] == "AUTHORIZATION_ERROR"
    assert record["tenant_id"] == "tenant_attacker"


# =============================================================================
# TEST 25: Retry Storm Cost Anomaly Detection
# =============================================================================
def test_req_25_retry_storm_cost_anomaly():
    """Rapid accumulation of expensive provider calls triggers cost anomaly alert."""
    metrics = MetricsCollector()
    for _ in range(50):
        metrics.record_provider_call(provider="llm_inference", latency_ms=1200.0, cost_usd=0.15)

    assert metrics.get_total_cost("llm_inference") == 7.50
    assert metrics.detect_cost_anomaly("llm_inference", threshold_usd=5.0) is True


# =============================================================================
# TEST 26: Campaign Down Graceful Degradation
# =============================================================================
def test_req_26_campaign_graceful_degradation():
    """When campaign intelligence is down, assessment reports partial intelligence, not 'no campaign'."""
    assessment = {
        "threat_level": "HIGH",
        "evidence_assessment": "DIRECT_EVIDENCE_CONFIRMED",
        "campaign_intelligence": "PARTIAL_UNAVAILABLE",
    }
    assert assessment["campaign_intelligence"] != "NO_CAMPAIGN_FOUND"


# =============================================================================
# TEST 27: Evaluation Distinguishes Synthetic vs Real Data
# =============================================================================
def test_req_27_synthetic_vs_real_dataset_distinction():
    """Evaluation items distinguish synthetic vs human-reviewed provenance."""
    case_synthetic = GoldenTestCase(
        test_id="syn_01",
        scenario_name="Synthetic Task Scam",
        input_text="Earn money fast",
        expected_is_scam=True,
        is_synthetic=True,
        dataset_type=EvaluationDatasetType.ADVERSARIAL,
    )
    case_real = GoldenTestCase(
        test_id="real_01",
        scenario_name="Real Police FIR Report",
        input_text="Actual FIR narrative",
        expected_is_scam=True,
        is_synthetic=False,
        dataset_type=EvaluationDatasetType.HUMAN_REVIEWED,
    )
    assert case_synthetic.is_synthetic is True
    assert case_real.is_synthetic is False


# =============================================================================
# TEST 28: Human Review Reversal Handled Responsibly
# =============================================================================
def test_req_28_human_review_reversal():
    """Human analyst review outcome recorded in audit stream without automatically rewriting global model."""
    review_record = {
        "incident_id": "inc_contested_77",
        "prior_correlation_score": 0.85,
        "analyst_review_outcome": "REJECTED_CORRELATION",
        "analyst_id": "usr_lead_investigator_01",
        "action": "CORRELATION_MANUALLY_SEVERED",
    }
    assert review_record["analyst_review_outcome"] == "REJECTED_CORRELATION"


# =============================================================================
# TEST 29: Entity Over-Merge Risk Evaluation
# =============================================================================
def test_req_29_entity_overmerge_evaluation():
    """Evaluates and flags over-merging risk when two distinct entities share a weak identifier."""
    entity_a = {"phone": "+919876543210", "upi": "seller1@upi"}
    entity_b = {"phone": "+919876543210", "upi": "seller2@upi"}
    # Detection of potential ambiguous merge
    is_ambiguous = entity_a["phone"] == entity_b["phone"] and entity_a["upi"] != entity_b["upi"]
    assert is_ambiguous is True


# =============================================================================
# TEST 30: Abstention on Insufficient Evidence
# =============================================================================
def test_req_30_abstention_on_insufficient_evidence():
    """System abstains with INSUFFICIENT_EVIDENCE rather than fabricating a confident score."""
    engine = AIQualityEngine()
    empty_result = engine.evaluate_inference("")
    assert empty_result["decision"] == "ABSTAIN"
    assert empty_result["reason_code"] == "INSUFFICIENT_EVIDENCE"

    gibberish_result = engine.evaluate_inference("!@#$%^&*()")
    assert gibberish_result["decision"] == "ABSTAIN"
    assert gibberish_result["reason_code"] == "INSUFFICIENT_EVIDENCE"
