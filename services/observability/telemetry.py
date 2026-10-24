"""
ScamGraph AI — Production Telemetry, Structured Logging & Redaction V3
Phase 7C / Prompt 23

Implements privacy-safe structured JSON logging, strict sensitive token redaction,
and lightweight in-memory Prometheus-style metrics tracking.
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("scamgraph.observability.telemetry")


class ErrorCode(str, Enum):
    """Canonical error taxonomy."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    MODEL_FAILURE = "MODEL_FAILURE"
    DATABASE_ERROR = "DATABASE_ERROR"
    QUEUE_ERROR = "QUEUE_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ProviderState(str, Enum):
    """Canonical health states for external providers."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class TelemetrySanitizer:
    """
    Centralized privacy filter that strips or masks sensitive tokens from all telemetry streams.
    Ensures OTPs, PINs, passwords, CVVs, card numbers, and raw phone numbers are never leaked.
    """

    OTP_PATTERN = re.compile(r"\b(otp|code|pin|verification)\s*(?:is|:)?\s*(\d{4,8})\b", re.IGNORECASE)
    CARD_PATTERN = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
    CVV_PATTERN = re.compile(r"\b(cvv|cvc|security code)\s*(?:is|:)?\s*(\d{3,4})\b", re.IGNORECASE)
    PHONE_PATTERN = re.compile(r"(?:\+?91|0)?[6-9]\d{9}\b")
    SECRET_KEY_PATTERN = re.compile(r"(api[-_]?key|secret|token|password|auth|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?", re.IGNORECASE)

    SENSITIVE_FIELD_NAMES = {
        "password",
        "pin",
        "otp",
        "cvv",
        "token",
        "secret",
        "auth_token",
        "access_token",
        "api_key",
        "credit_card",
        "pan",
        "aadhaar",
    }

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Mask secrets in free-form string text."""
        if not text:
            return text
        sanitized = cls.OTP_PATTERN.sub(r"\1: [REDACTED_OTP]", text)
        sanitized = cls.CARD_PATTERN.sub("[REDACTED_CARD]", sanitized)
        sanitized = cls.CVV_PATTERN.sub(r"\1: [REDACTED_CVV]", sanitized)
        sanitized = cls.SECRET_KEY_PATTERN.sub(r"\1: [REDACTED_SECRET]", sanitized)
        sanitized = cls.PHONE_PATTERN.sub(lambda m: m.group(0)[:3] + "XXXXXX" + m.group(0)[-2:], sanitized)
        return sanitized

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively scrub sensitive keys and tokens from a dictionary."""
        sanitized: Dict[str, Any] = {}
        for k, v in data.items():
            k_lower = k.lower()
            if any(s in k_lower for s in cls.SENSITIVE_FIELD_NAMES):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = cls.sanitize_dict(v)
            elif isinstance(v, list):
                sanitized[k] = [
                    cls.sanitize_dict(i) if isinstance(i, dict)
                    else (cls.sanitize_text(i) if isinstance(i, str) else i)
                    for i in v
                ]
            elif isinstance(v, str):
                sanitized[k] = cls.sanitize_text(v)
            else:
                sanitized[k] = v
        return sanitized


class StructuredLogger:
    """Emits standardized JSON log records safe for production telemetry ingestion."""

    def __init__(self, service_name: str = "scamgraph-backend", environment: str = "production") -> None:
        self.service_name = service_name
        self.environment = environment

    def format_log(
        self,
        level: str,
        message: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        job_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error_code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        sanitized_msg = TelemetrySanitizer.sanitize_text(message)
        sanitized_extra = TelemetrySanitizer.sanitize_dict(extra) if extra else {}

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "service": self.service_name,
            "environment": self.environment,
            "message": sanitized_msg,
            "request_id": request_id,
            "trace_id": trace_id,
            "job_id": job_id,
            "tenant_id": tenant_id,
            "operation": operation,
            "duration_ms": duration_ms,
            "error_code": error_code,
            "metadata": sanitized_extra,
        }
        return record


class MetricsCollector:
    """
    Lightweight, high-performance in-memory metrics registry.
    Calculates percentiles (p50, p90, p95, p99), rates, error counts,
    provider health states, and cost anomalies.
    """

    def __init__(self) -> None:
        # Request metrics: endpoint -> list of latency ms
        self._latencies: Dict[str, List[float]] = {}
        self._request_counts: Dict[str, int] = {}
        self._error_counts: Dict[str, int] = {}
        
        # Provider health & latencies: provider_name -> (state, list of latencies)
        self._providers: Dict[str, Tuple[ProviderState, List[float]]] = {}
        
        # Cost metrics: provider/operation -> total estimated cost USD
        self._costs: Dict[str, float] = {}
        
        # Queue metrics cache
        self._queue_depth: Dict[str, int] = {}
        self._dead_letter_count: int = 0
        self._oldest_job_age: float = 0.0

    def record_request(self, endpoint_class: str, latency_ms: float, is_error: bool = False) -> None:
        """Record API request completion."""
        if endpoint_class not in self._latencies:
            self._latencies[endpoint_class] = []
            self._request_counts[endpoint_class] = 0
            self._error_counts[endpoint_class] = 0

        self._latencies[endpoint_class].append(latency_ms)
        self._request_counts[endpoint_class] += 1
        if is_error:
            self._error_counts[endpoint_class] += 1

    def record_provider_call(
        self,
        provider: str,
        latency_ms: float,
        state: ProviderState = ProviderState.HEALTHY,
        cost_usd: float = 0.0,
    ) -> None:
        """Record external intelligence provider call (TinyFish, Whisper, OCR, LLM)."""
        if provider not in self._providers:
            self._providers[provider] = (state, [])
        _, lats = self._providers[provider]
        lats.append(latency_ms)
        self._providers[provider] = (state, lats)
        self._costs[provider] = self._costs.get(provider, 0.0) + cost_usd

    def record_queue_metrics(self, queue_depth_by_class: Dict[str, int], dlq_count: int, oldest_age: float) -> None:
        """Update background queue telemetry."""
        self._queue_depth = queue_depth_by_class
        self._dead_letter_count = dlq_count
        self._oldest_job_age = oldest_age

    def get_latency_percentiles(self, endpoint_class: str) -> Dict[str, float]:
        """Compute p50, p90, p95, p99 latencies for an endpoint group."""
        lats = self._latencies.get(endpoint_class, [])
        if not lats:
            return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "count": 0}

        sorted_lats = sorted(lats)
        n = len(sorted_lats)
        def _pct(p: float) -> float:
            k = int(round((p / 100.0) * (n - 1)))
            return sorted_lats[k]

        return {
            "p50": round(_pct(50), 2),
            "p90": round(_pct(90), 2),
            "p95": round(_pct(95), 2),
            "p99": round(_pct(99), 2),
            "count": n,
        }

    def get_provider_status(self, provider: str) -> Tuple[ProviderState, float]:
        """Return provider state and average latency."""
        if provider not in self._providers:
            return ProviderState.UNKNOWN, 0.0
        state, lats = self._providers[provider]
        avg_lat = round(sum(lats) / len(lats), 2) if lats else 0.0
        return state, avg_lat

    def get_total_cost(self, provider_or_op: Optional[str] = None) -> float:
        """Return total estimated provider cost."""
        if provider_or_op:
            return round(self._costs.get(provider_or_op, 0.0), 4)
        return round(sum(self._costs.values()), 4)

    def detect_cost_anomaly(self, provider: str, threshold_usd: float = 5.0) -> bool:
        """Trigger alert if a provider's accumulated run cost spikes unexpectedly."""
        return self._costs.get(provider, 0.0) > threshold_usd


# Singleton instances
_global_logger = StructuredLogger()
_global_metrics = MetricsCollector()


def get_structured_logger() -> StructuredLogger:
    return _global_logger


def get_metrics_collector() -> MetricsCollector:
    return _global_metrics
