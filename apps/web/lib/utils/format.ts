export function formatDateTime(val?: string | number | Date | null): string {
  if (!val) return "—";
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return d.toLocaleString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(val);
  }
}

export function formatTime(val?: string | number | Date | null): string {
  if (!val) return "—";
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return d.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return String(val);
  }
}

export function formatOffset(seconds?: number): string {
  if (typeof seconds !== "number" || isNaN(seconds)) return "+00s";
  const abs = Math.abs(seconds);
  const mins = Math.floor(abs / 60);
  const secs = abs % 60;
  const sign = seconds >= 0 ? "+" : "-";
  if (mins === 0) return `${sign}${secs}s`;
  return `${sign}${mins}m ${secs.toString().padStart(2, "0")}s`;
}

export function humanize(str?: string | null): string {
  if (!str) return "—";
  return str
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

export function humanizeStage(stage?: string | null): string {
  if (!stage) return "Initial Contact";
  const map: Record<string, string> = {
    INITIAL_CONTACT: "Initial Contact",
    IMPERSONATION: "Entity Impersonation",
    URGENCY_INDUCEMENT: "Psychological Coercion",
    MALICIOUS_LINK: "Malicious Lure / Link",
    CREDENTIAL_HARVEST: "Credential / OTP Harvesting",
    REMOTE_ACCESS: "Remote Access Exploit",
    PAYMENT_INTENT: "Payment Intent Initiation",
    SETTLEMENT: "Fund Transfer / Mule Settlement",
  };
  return map[stage] || humanize(stage);
}

export function pct(num?: number | null): string {
  if (typeof num !== "number" || isNaN(num)) return "0%";
  const normalized = num <= 1 ? num * 100 : num;
  return `${Math.round(normalized)}%`;
}

export function similarityBucket(score?: number | null): string {
  if (typeof score !== "number" || isNaN(score)) return "Low";
  const s = score <= 1 ? score * 100 : score;
  if (s >= 85) return "Very High";
  if (s >= 70) return "High";
  if (s >= 50) return "Moderate";
  return "Low";
}

export function shortId(id?: string | null, startLen = 8, endLen?: number): string {
  if (!id) return "—";
  if (endLen !== undefined) {
    if (id.length <= startLen + endLen) return id;
    return `${id.slice(0, startLen)}…${id.slice(-endLen)}`;
  }
  if (id.length <= startLen) return id;
  return id.slice(0, startLen);
}
