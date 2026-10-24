/**
 * Webhook signature verification helper for TypeScript/JavaScript integrators.
 */

import * as crypto from "crypto";

export interface VerifyWebhookOptions {
  secret: string;
  signatureHeader: string;
  payload: string | Buffer;
  maxAgeSeconds?: number;
}

export function verifyWebhookSignature({
  secret,
  signatureHeader,
  payload,
  maxAgeSeconds = 300,
}: VerifyWebhookOptions): boolean {
  if (!secret || !signatureHeader) return false;

  try {
    const parts = signatureHeader.split(",").reduce((acc, part) => {
      const [k, v] = part.split("=");
      if (k && v) acc[k.trim()] = v.trim();
      return acc;
    }, {} as Record<string, string>);

    const timestamp = parseInt(parts["t"] || "0", 10);
    const v1Sig = parts["v1"];
    if (!timestamp || !v1Sig) return false;

    // Check age to protect against replay attacks
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestamp) > maxAgeSeconds) {
      return false;
    }

    const payloadBuffer = typeof payload === "string" ? Buffer.from(payload, "utf-8") : payload;
    const toSign = Buffer.concat([Buffer.from(`${timestamp}.`, "utf-8"), payloadBuffer]);

    const expected = crypto.createHmac("sha256", secret).update(toSign).digest("hex");
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(v1Sig));
  } catch {
    return false;
  }
}
