/**
 * Official ScamGraph TypeScript SDK Client
 */

import {
  AuthenticationError,
  ConflictError,
  RateLimitError,
  ScamGraphAPIError,
  ValidationError,
} from "./errors";
import { verifyWebhookSignature, VerifyWebhookOptions } from "./webhooks";

export interface ScamGraphClientConfig {
  apiKey: string;
  baseUrl?: string;
  timeoutMs?: number;
}

export interface CheckRequest {
  messageText?: string;
  url?: string;
  phone?: string;
  vpa?: string;
  externalReference?: string;
  idempotencyKey?: string;
  environment?: "LIVE" | "SANDBOX";
}

export interface CheckResponse {
  check_id: string;
  request_id: string;
  risk_level: string;
  risk_score: number;
  confidence: string;
  urgency: string;
  recommended_action: string;
  reason_codes: string[];
  journey_summary?: Record<string, unknown>;
  network_signal: string;
  processing_ms: number;
}

export interface GuardRequest {
  vpa: string;
  amount?: number;
  messageText?: string;
  qrPayload?: string;
  externalReference?: string;
  fastPath?: boolean;
  idempotencyKey?: string;
  environment?: "LIVE" | "SANDBOX";
}

export interface GuardResponse {
  guard_id: string;
  request_id: string;
  action: "ALLOW_NORMAL_FLOW" | "SHOW_CAUTION" | "VERIFY_INDEPENDENTLY" | "PAUSE_BEFORE_PAYMENT" | "STRONG_WARNING" | "ESCALATE_REVIEW";
  friction_level: number;
  risk_score: number;
  confidence: string;
  intervention_title: string;
  intervention_message: string;
  safe_guidance: string[];
  latency_tier: string;
  processing_ms: number;
}

export class ScamGraphClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeoutMs: number;

  constructor(config: ScamGraphClientConfig) {
    if (!config.apiKey) {
      throw new AuthenticationError("API key must be provided to initialize ScamGraphClient.");
    }
    this.apiKey = config.apiKey.trim();
    this.baseUrl = (config.baseUrl || "http://localhost:8001/api/v1/").replace(/\/+$/, "") + "/";
    this.timeoutMs = config.timeoutMs || 10000;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}, idempotencyKey?: string): Promise<T> {
    const url = new URL(endpoint.replace(/^\/+/, ""), this.baseUrl).toString();
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
      "User-Agent": "@scamgraph/sdk-typescript/2.0.0",
      ...(options.headers as Record<string, string>),
    };

    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorJson = await response.json().catch(() => ({}));
        const reqId = response.headers.get("X-Request-Id") || undefined;

        if (response.status === 401) throw new AuthenticationError(errorJson.detail || "Unauthorized", reqId);
        if (response.status === 429) throw new RateLimitError(errorJson.detail || "Rate limit exceeded", reqId);
        if (response.status === 409) throw new ConflictError(errorJson.detail || "Idempotency conflict", reqId);
        if (response.status === 400) throw new ValidationError(errorJson.detail || "Validation error", errorJson, reqId);

        throw new ScamGraphAPIError(errorJson.detail || `Request failed with HTTP ${response.status}`, {
          statusCode: response.status,
          requestId: reqId,
        });
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timeout);
    }
  }

  public async check(req: CheckRequest): Promise<CheckResponse> {
    return this.request<CheckResponse>(
      "check",
      {
        method: "POST",
        body: JSON.stringify({
          message_text: req.messageText,
          url: req.url,
          phone: req.phone,
          vpa: req.vpa,
          external_reference: req.externalReference,
          environment: req.environment || "LIVE",
        }),
      },
      req.idempotencyKey
    );
  }

  public async guard(req: GuardRequest): Promise<GuardResponse> {
    return this.request<GuardResponse>(
      "guard/check",
      {
        method: "POST",
        body: JSON.stringify({
          vpa: req.vpa,
          amount: req.amount,
          message_text: req.messageText,
          qr_payload: req.qrPayload,
          external_reference: req.externalReference,
          fast_path: req.fastPath !== false,
          environment: req.environment || "LIVE",
        }),
      },
      req.idempotencyKey
    );
  }

  public static verifyWebhook(options: VerifyWebhookOptions): boolean {
    return verifyWebhookSignature(options);
  }
}
