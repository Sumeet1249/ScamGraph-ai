"""
ScamGraph AI — Distributed Tracing & Context Propagation V3
Phase 7C / Prompt 23

Ensures trace context (trace_id, request_id, span_id, job_id, org_id)
flows seamlessly across HTTP API requests, message queues, and background workers.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class SpanRecord(BaseModel):
    """Execution span within a distributed trace."""
    span_id: str = Field(default_factory=lambda: generate_id("spn"))
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    service: str = "scamgraph"
    start_time_epoch_ms: float = Field(default_factory=lambda: time.time() * 1000)
    end_time_epoch_ms: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "OK"  # OK, ERROR
    error_message: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TraceContext:
    """Carries ambient correlation and tracing context across async boundaries."""

    def __init__(
        self,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        job_id: Optional[str] = None,
        org_id: Optional[str] = None,
        principal_id: Optional[str] = None,
    ) -> None:
        self.trace_id = trace_id or generate_id("trc")
        self.request_id = request_id or generate_id("req")
        self.job_id = job_id
        self.org_id = org_id or "org_anonymous"
        self.principal_id = principal_id
        self.spans: List[SpanRecord] = []

    def start_span(self, name: str, parent_span_id: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> SpanRecord:
        """Create and begin timing a new operation span."""
        span = SpanRecord(
            trace_id=self.trace_id,
            parent_span_id=parent_span_id,
            name=name,
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def finish_span(self, span: SpanRecord, status: str = "OK", error: Optional[str] = None) -> None:
        """Complete timing a span."""
        span.end_time_epoch_ms = time.time() * 1000
        span.duration_ms = round(span.end_time_epoch_ms - span.start_time_epoch_ms, 2)
        span.status = status
        span.error_message = error

    def to_header_dict(self) -> Dict[str, str]:
        """Serialize trace context into standard HTTP headers."""
        headers = {
            "x-trace-id": self.trace_id,
            "x-request-id": self.request_id,
            "x-tenant-id": self.org_id,
        }
        if self.job_id:
            headers["x-job-id"] = self.job_id
        return headers

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> TraceContext:
        """Extract trace context from incoming request headers."""
        return cls(
            trace_id=headers.get("x-trace-id"),
            request_id=headers.get("x-request-id"),
            job_id=headers.get("x-job-id"),
            org_id=headers.get("x-tenant-id"),
        )
