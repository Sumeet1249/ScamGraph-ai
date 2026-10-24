"""Exceptions for TinyFish WebInvestigator integration (Step 17)."""


class TinyFishError(Exception):
    """Base exception for all TinyFish errors."""
    pass


class TinyFishConfigError(TinyFishError):
    """Raised when required configuration or API key is absent."""
    pass


class TinyFishTimeoutError(TinyFishError):
    """Raised when TinyFish API call exceeds bounded timeout."""
    pass


class TinyFishRateLimitError(TinyFishError):
    """Raised when TinyFish API returns HTTP 429 rate limit exceeded."""
    pass


class TinyFishMalformedResponseError(TinyFishError):
    """Raised when TinyFish response cannot be parsed as valid JSON or expected structure."""
    pass
