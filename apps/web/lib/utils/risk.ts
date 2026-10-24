export type RiskLevel = "low" | "medium" | "high" | "critical" | "insufficient";

export interface RiskToken {
  bg: string;
  text: string;
  border: string;
  label: string;
}

export const riskTokens: Record<RiskLevel, RiskToken> = {
  low: {
    bg: "bg-tone-info-bg",
    text: "text-tone-info-text",
    border: "border-viz-info/30",
    label: "Low Risk",
  },
  medium: {
    bg: "bg-tone-warning-bg",
    text: "text-tone-warning-text",
    border: "border-viz-warning/30",
    label: "Medium Caution",
  },
  high: {
    bg: "bg-tone-warning-strong-bg",
    text: "text-tone-warning-strong-text",
    border: "border-tone-warning-strong-text/30",
    label: "High Suspicion",
  },
  critical: {
    bg: "bg-tone-danger-strong-bg",
    text: "text-tone-danger-strong-text",
    border: "border-tone-danger-text/30",
    label: "Critical Threat",
  },
  insufficient: {
    bg: "bg-surface-subtle",
    text: "text-viz-neutral",
    border: "border-border-divider",
    label: "Insufficient Evidence",
  },
};

export function riskBand(score: number): RiskLevel {
  if (score < 25) return "low";
  if (score < 50) return "medium";
  if (score < 75) return "high";
  return "critical";
}

export function severityToken(severity: string) {
  const s = severity?.toLowerCase();
  if (s === "critical") return riskTokens.critical;
  if (s === "high") return riskTokens.high;
  if (s === "medium") return riskTokens.medium;
  return riskTokens.low;
}
