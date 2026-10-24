"""Hardware & Performance Resource Profiler for ScamGraph AI Models.

Measures operational latency, batch throughput, memory delta, and artifact storage footprint
without fabricating unmeasured GPU metrics (Rule 77).
"""

from __future__ import annotations

import logging
import os
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger("scamgraph.arena.resources")


class ResourceProfile(BaseModel):
    """Execution resource metrics for a model or pipeline component."""
    model_id: str
    load_time_sec: float
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_items_per_sec: float
    peak_memory_mb: float
    artifact_size_mb: float
    hardware_runtime: str = "CPU"


class ResourceProfiler:
    """Profiles execution time, batch throughput, and memory consumption."""

    @staticmethod
    def profile_latency(
        predict_fn: Callable[[List[str]], Any],
        sample_texts: List[str],
        warmup_runs: int = 3,
    ) -> Dict[str, float]:
        """Profiles single-item latency and batch throughput."""
        if not sample_texts:
            return {
                "mean_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "throughput_items_per_sec": 0.0,
            }

        # 1. Warmup
        for _ in range(warmup_runs):
            predict_fn([sample_texts[0]])

        # 2. Single item latencies
        latencies: List[float] = []
        for text in sample_texts:
            t0 = time.perf_counter()
            predict_fn([text])
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

        arr = np.array(latencies)

        # 3. Batch throughput
        t_batch_start = time.perf_counter()
        predict_fn(sample_texts)
        t_batch_dur = max(time.perf_counter() - t_batch_start, 1e-6)
        throughput = len(sample_texts) / t_batch_dur

        return {
            "mean_latency_ms": round(float(np.mean(arr)), 3),
            "p50_latency_ms": round(float(np.percentile(arr, 50)), 3),
            "p95_latency_ms": round(float(np.percentile(arr, 95)), 3),
            "p99_latency_ms": round(float(np.percentile(arr, 99)), 3),
            "throughput_items_per_sec": round(float(throughput), 1),
        }

    @staticmethod
    def profile_memory_and_load(
        load_fn: Callable[[], Any],
        artifact_paths: Optional[List[str]] = None,
    ) -> Tuple[Any, float, float, float]:
        """Measures load time (sec), peak memory allocated (MB), and artifact disk footprint (MB)."""
        tracemalloc.start()
        t0 = time.perf_counter()
        instance = load_fn()
        load_time = time.perf_counter() - t0
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = round(peak / (1024 * 1024), 2)

        # Artifact disk footprint
        artifact_mb = 0.0
        if artifact_paths:
            total_bytes = 0
            for p in artifact_paths:
                path_obj = Path(p)
                if path_obj.exists():
                    total_bytes += path_obj.stat().st_size
            artifact_mb = round(total_bytes / (1024 * 1024), 2)

        return instance, round(load_time, 3), peak_mb, artifact_mb
