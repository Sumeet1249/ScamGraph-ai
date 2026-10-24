"""ScamGraph Python SDK Error Hierarchy."""

from typing import Any, Dict, Optional


class ScamGraphAPIError(Exception):
    """Base exception for all ScamGraph API interactions."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.request_id = request_id
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(ScamGraphAPIError):
    """Raised when an API key is missing, invalid, or revoked."""
    pass


class RateLimitError(ScamGraphAPIError):
    """Raised when request volume exceeds negotiated quota (HTTP 429)."""
    pass


class ValidationError(ScamGraphAPIError):
    """Raised when input parameters fail validation checks."""
    pass


class ConflictError(ScamGraphAPIError):
    """Raised when an idempotency key was previously submitted with differing payloads."""
    pass


class ServiceUnavailableError(ScamGraphAPIError):
    """Raised when backend intelligence subsystems are temporarily degraded (HTTP 503)."""
    pass
