"""
ScamGraph AI — Backpressure, Load Shedding & Degradation Engine V3
Phase 7D / Prompt 24

Protects system availability during severe traffic surges by gracefully shedding
non-essential background enrichments while strictly preserving safety-critical
user flows (Protect, Pre-Payment Guard, and Rescue).
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, Field

from packages.schemas.jobs import JobPriority

logger = logging.getLogger("scamgraph.scalability.backpressure")


class DegradationLevel(str, Enum):
    """System degradation tiers under capacity pressure."""
    NORMAL = "NORMAL"                               # All services operating nominally
    DEGRADED_ENRICHMENT = "DEGRADED_ENRICHMENT"     # Defer deep external scraping & heavy multimodal VLM
    DEGRADED_INTELLIGENCE = "DEGRADED_INTELLIGENCE" # Defer campaign recomputation & global graph projection
    CRITICAL_SAFETY_ONLY = "CRITICAL_SAFETY_ONLY"   # Only serve Protect fast path, Guard, and Rescue P0/P1


class AdmissionDecision(BaseModel):
    """Decision returned by admission controller for an incoming workload."""
    admitted: bool
    priority: JobPriority
    degradation_level: DegradationLevel
    reason: str
    suggested_retry_after_seconds: Optional[int] = None


class BackpressureController:
    """
    Evaluates real-time queue depth, oldest job age, and concurrency pressure
    to enforce dynamic admission control and load shedding.
    """

    def __init__(
        self,
        max_normal_queue_depth: int = 50,
        max_degraded_queue_depth: int = 150,
        critical_queue_depth: int = 300,
        max_oldest_job_age_seconds: float = 600.0,
    ) -> None:
        self.max_normal_queue_depth = max_normal_queue_depth
        self.max_degraded_queue_depth = max_degraded_queue_depth
        self.critical_queue_depth = critical_queue_depth
        self.max_oldest_job_age_seconds = max_oldest_job_age_seconds
        self.current_degradation_level = DegradationLevel.NORMAL

    def evaluate_system_load(self, queue_depth: int, oldest_job_age_seconds: float) -> DegradationLevel:
        """Determine degradation mode based on observable backpressure signals."""
        if queue_depth >= self.critical_queue_depth or oldest_job_age_seconds > self.max_oldest_job_age_seconds:
            self.current_degradation_level = DegradationLevel.CRITICAL_SAFETY_ONLY
        elif queue_depth >= self.max_degraded_queue_depth or oldest_job_age_seconds > (self.max_oldest_job_age_seconds / 2):
            self.current_degradation_level = DegradationLevel.DEGRADED_INTELLIGENCE
        elif queue_depth >= self.max_normal_queue_depth:
            self.current_degradation_level = DegradationLevel.DEGRADED_ENRICHMENT
        else:
            self.current_degradation_level = DegradationLevel.NORMAL

        return self.current_degradation_level

    def evaluate_admission(
        self,
        priority: JobPriority,
        is_user_facing: bool = True,
    ) -> AdmissionDecision:
        """
        Admit or reject workload based on priority class and current degradation tier.
        Safety-critical P0 (CRITICAL) and P1 (HIGH) flows are NEVER shed.
        """
        level = self.current_degradation_level

        if level == DegradationLevel.NORMAL:
            return AdmissionDecision(
                admitted=True,
                priority=priority,
                degradation_level=level,
                reason="System healthy; nominal admission",
            )

        elif level == DegradationLevel.DEGRADED_ENRICHMENT:
            if priority == JobPriority.LOW and not is_user_facing:
                return AdmissionDecision(
                    admitted=False,
                    priority=priority,
                    degradation_level=level,
                    reason="Low priority batch work shed under enrichment degradation",
                    suggested_retry_after_seconds=30,
                )
            return AdmissionDecision(admitted=True, priority=priority, degradation_level=level, reason="Admitted")

        elif level == DegradationLevel.DEGRADED_INTELLIGENCE:
            if priority in (JobPriority.LOW, JobPriority.NORMAL) and not is_user_facing:
                return AdmissionDecision(
                    admitted=False,
                    priority=priority,
                    degradation_level=level,
                    reason="Intelligence maintenance shed under queue pressure",
                    suggested_retry_after_seconds=60,
                )
            return AdmissionDecision(admitted=True, priority=priority, degradation_level=level, reason="Admitted")

        elif level == DegradationLevel.CRITICAL_SAFETY_ONLY:
            # Under critical pressure, ONLY CRITICAL (Guard) and HIGH (Rescue / Protect) are admitted
            if priority in (JobPriority.CRITICAL, JobPriority.HIGH):
                return AdmissionDecision(
                    admitted=True,
                    priority=priority,
                    degradation_level=level,
                    reason="Critical safety workload prioritized under emergency load shedding",
                )
            return AdmissionDecision(
                admitted=False,
                priority=priority,
                degradation_level=level,
                reason="System under critical load: only pre-payment Guard and Rescue are active",
                suggested_retry_after_seconds=120,
            )

        return AdmissionDecision(admitted=True, priority=priority, degradation_level=level, reason="Default")


# Global singleton
_backpressure_controller: Optional[BackpressureController] = None


def get_backpressure_controller() -> BackpressureController:
    global _backpressure_controller
    if _backpressure_controller is None:
        _backpressure_controller = BackpressureController()
    return _backpressure_controller
