export type RiskLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL"
  | "INSUFFICIENT_EVIDENCE"
  | "VERIFIED"
  | string;

export type RiskBand = "low" | "medium" | "high" | "critical";

export function riskBand(score: number): RiskBand {
  if (score >= 75) return "critical";
  if (score >= 50) return "high";
  if (score >= 25) return "medium";
  return "low";
}

export const riskTokens = {
  insufficient: {
    text: "text-text-muted",
    bar: "bg-surface-border",
    bg: "bg-surface-subtle",
    border: "border-border",
    badge: "border-border bg-surface-subtle text-text-muted",
  },
  low: {
    text: "text-safe",
    bar: "bg-safe",
    bg: "bg-safe/10",
    border: "border-safe/30",
    badge: "border-safe/30 bg-safe/10 text-safe",
  },
  medium: {
    text: "text-warning",
    bar: "bg-warning",
    bg: "bg-warning/10",
    border: "border-warning/30",
    badge: "border-warning/30 bg-warning/10 text-warning",
  },
  high: {
    text: "text-danger",
    bar: "bg-danger",
    bg: "bg-danger/10",
    border: "border-danger/30",
    badge: "border-danger/30 bg-danger/10 text-danger",
  },
  critical: {
    text: "text-danger font-bold",
    bar: "bg-danger",
    bg: "bg-danger/20",
    border: "border-danger/40",
    badge: "border-danger/40 bg-danger/20 text-danger",
  },
};

export function severityBgToken(severity?: string | null): string {
  if (!severity) return "bg-surface-subtle text-text-muted border-border";
  const s = severity.toUpperCase();
  switch (s) {
    case "CRITICAL":
      return "border-danger/40 bg-danger/15 text-danger font-medium";
    case "HIGH":
      return "border-danger/30 bg-danger/10 text-danger";
    case "MEDIUM":
      return "border-warning/30 bg-warning/10 text-warning";
    case "LOW":
      return "border-safe/30 bg-safe/10 text-safe";
    default:
      return "border-border bg-surface-subtle text-text-muted";
  }
}

export function severityToken(severity?: string | null): string {
  if (!severity) return "text-text-muted";
  const s = severity.toUpperCase();
  switch (s) {
    case "CRITICAL":
      return "text-danger font-bold";
    case "HIGH":
      return "text-danger";
    case "MEDIUM":
      return "text-warning";
    case "LOW":
      return "text-safe";
    default:
      return "text-text-muted";
  }
}
