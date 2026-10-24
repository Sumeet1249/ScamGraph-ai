"""
ScamGraph AI — Safe Load Testing Harness & Traffic Generator V3
Phase 7D / Prompt 24

Executes reproducible, environment-guarded load scenarios across ScamGraph profiles
with strict safeguards preventing execution against production environments.
"""

from __future__ import annotations

import asyncio
import inspect
import os
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from services.observability.telemetry import MetricsCollector, get_metrics_collector
from services.jobs.queue import JobQueue, get_job_queue
from packages.schemas.jobs import JobType, JobPriority, WorkerClass


class LoadTestSafetyException(Exception):
    """Raised if load tests are run without explicit test environment confirmation."""
    pass


class LoadScenarioResult(BaseModel):
    """Detailed benchmark results from a completed load scenario."""
    scenario_name: str
    target_concurrency: int
    total_requests: int
    duration_seconds: float
    actual_rps: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    error_rate_percent: float
    queue_drain_time_seconds: Optional[float] = None
    is_slo_passing: bool


class SafeLoadRunner:
    """
    Executes controlled traffic mixes across ScamGraph user profiles.
    Strictly verifies safety guard before launching traffic.
    """

    def __init__(self, metrics: Optional[MetricsCollector] = None, queue: Optional[JobQueue] = None) -> None:
        self.metrics = metrics or get_metrics_collector()
        self.queue = queue or get_job_queue()

    def _verify_safety_guard(self) -> None:
        """Enforces that load tests only run in non-production environments."""
        env = os.environ.get("ENV", "test").lower()
        if env in ("production", "prod"):
            raise LoadTestSafetyException("CRITICAL: Load tests are strictly forbidden in production!")

    async def run_scenario(
        self,
        name: str,
        operation_fn: Callable[[], Any],
        concurrency: int = 10,
        iterations_per_worker: int = 10,
        target_slo_p95_ms: float = 300.0,
    ) -> LoadScenarioResult:
        """Run concurrent workload and record empirical percentile latencies."""
        self._verify_safety_guard()

        total_requests = concurrency * iterations_per_worker
        latencies_ms: List[float] = []
        errors = 0

        async def _worker_loop():
            nonlocal errors
            for _ in range(iterations_per_worker):
                start = time.perf_counter()
                try:
                    if inspect.iscoroutinefunction(operation_fn):
                        await operation_fn()
                    else:
                        operation_fn()
                    duration = (time.perf_counter() - start) * 1000.0
                    latencies_ms.append(duration)
                except Exception:
                    errors += 1

        bench_start = time.perf_counter()
        workers = [asyncio.create_task(_worker_loop()) for _ in range(concurrency)]
        await asyncio.gather(*workers)
        total_duration = time.perf_counter() - bench_start

        sorted_lats = sorted(latencies_ms) if latencies_ms else [0.0]
        n = len(sorted_lats)
        def _pct(p: float) -> float:
            k = int(round((p / 100.0) * (n - 1)))
            return sorted_lats[k]

        p50 = round(_pct(50), 2)
        p95 = round(_pct(95), 2)
        p99 = round(_pct(99), 2)
        rps = round(total_requests / max(0.001, total_duration), 2)
        err_pct = round((errors / max(1, total_requests)) * 100.0, 2)

        return LoadScenarioResult(
            scenario_name=name,
            target_concurrency=concurrency,
            total_requests=total_requests,
            duration_seconds=round(total_duration, 3),
            actual_rps=rps,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            error_count=errors,
            error_rate_percent=err_pct,
            is_slo_passing=(p95 <= target_slo_p95_ms and err_pct < 1.0),
        )


# Global singleton
_load_runner = SafeLoadRunner()


def get_load_runner() -> SafeLoadRunner:
    return _load_runner
