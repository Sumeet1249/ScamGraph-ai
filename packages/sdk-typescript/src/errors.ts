/**
 * ScamGraph TypeScript SDK Error Hierarchy
 */

export class ScamGraphAPIError extends Error {
  public readonly code: string;
  public readonly requestId?: string;
  public readonly statusCode?: number;
  public readonly details: Record<string, unknown>;

  constructor(
    message: string,
    options?: {
      code?: string;
      requestId?: string;
      statusCode?: number;
      details?: Record<string, unknown>;
    }
  ) {
    super(message);
    this.name = "ScamGraphAPIError";
    this.code = options?.code || "UNKNOWN_ERROR";
    this.requestId = options?.requestId;
    this.statusCode = options?.statusCode;
    this.details = options?.details || {};
  }
}

export class AuthenticationError extends ScamGraphAPIError {
  constructor(message = "Unauthorized: Invalid or missing API key", requestId?: string) {
    super(message, { code: "UNAUTHORIZED", statusCode: 401, requestId });
    this.name = "AuthenticationError";
  }
}

export class RateLimitError extends ScamGraphAPIError {
  constructor(message = "Rate limit exceeded (HTTP 429)", requestId?: string) {
    super(message, { code: "RATE_LIMITED", statusCode: 429, requestId });
    this.name = "RateLimitError";
  }
}

export class ValidationError extends ScamGraphAPIError {
  constructor(message = "Validation failed for request parameters", details?: Record<string, unknown>, requestId?: string) {
    super(message, { code: "VALIDATION_ERROR", statusCode: 400, details, requestId });
    this.name = "ValidationError";
  }
}

export class ConflictError extends ScamGraphAPIError {
  constructor(message = "Idempotency conflict: key re-used with differing payload", requestId?: string) {
    super(message, { code: "IDEMPOTENCY_CONFLICT", statusCode: 409, requestId });
    this.name = "ConflictError";
  }
}
