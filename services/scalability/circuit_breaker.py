"""
ScamGraph AI — Provider Circuit Breaker Engine V3
Phase 7D / Prompt 24

Prevents cascading failures and retry storms when external intelligence providers
(TinyFish, Whisper, OCR, LLMs) degrade or become unreachable.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger("scamgraph.scalability.circuit_breaker")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # Normal operation: requests pass through
    OPEN = "OPEN"           # Tripped: requests fail fast without calling provider
    HALF_OPEN = "HALF_OPEN" # Probing: trial requests test provider recovery


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while circuit is in OPEN state."""
    pass


class CircuitBreaker:
    """
    Stateful circuit breaker guarding external network and provider dependencies.
    Tracks failure counts, open windows, and allows graceful fallback degradation.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        half_open_max_trials: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.half_open_max_trials = half_open_max_trials

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_state_change: float = time.time()
        self.last_failure_time: float = 0.0

    def can_execute(self) -> bool:
        """Check if request is allowed through or should fail fast."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout_seconds:
                logger.info("CircuitBreaker[%s]: Recovery timeout elapsed; entering HALF_OPEN", self.name)
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.success_count = 0
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        """Record successful upstream execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_trials:
                logger.info("CircuitBreaker[%s]: Probing succeeded; resetting to CLOSED", self.name)
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """Record failure and trip circuit to OPEN if threshold reached."""
        now = time.time()
        self.last_failure_time = now
        self.failure_count += 1

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("CircuitBreaker[%s]: Probe failed; tripping back to OPEN (%s)", self.name, str(error))
            self.state = CircuitState.OPEN
            self.last_state_change = now
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error("CircuitBreaker[%s]: Failure threshold reached (%d); tripping to OPEN", self.name, self.failure_count)
                self.state = CircuitState.OPEN
                self.last_state_change = now


class CircuitBreakerRegistry:
    """Central registry of circuit breakers for all external providers."""

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create(self, name: str, failure_threshold: int = 5, recovery_timeout_seconds: float = 30.0) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout_seconds=recovery_timeout_seconds,
            )
        return self._breakers[name]


# Global singleton
_circuit_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_registry() -> CircuitBreakerRegistry:
    global _circuit_registry
    if _circuit_registry is None:
        _circuit_registry = CircuitBreakerRegistry()
    return _circuit_registry
