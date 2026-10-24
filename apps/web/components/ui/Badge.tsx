import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

type Tone = "neutral" | "brand" | "brand2" | "info" | "caution" | "danger" | "success" | "outline";

const toneMap: Record<Tone, string> = {
  neutral: "bg-surface-2 text-text-secondary border-border-strong",
  brand: "bg-brand-primary/12 text-brand-primary border-brand-primary/30",
  brand2: "bg-brand-secondary/12 text-brand-secondary border-brand-secondary/30",
  info: "bg-info/12 text-info border-info/30",
  caution: "bg-warning/12 text-warning border-warning/30",
  danger: "bg-danger/12 text-danger border-danger/30",
  success: "bg-success/12 text-success border-success/30",
  outline: "bg-transparent text-text-muted border-border",
};

const dataToneMap: Record<Tone, string> = {
  neutral: "neutral",
  brand: "neutral",
  brand2: "info",
  info: "info",
  caution: "warning",
  danger: "critical",
  success: "success",
  outline: "neutral",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

/** Generic compact pill. For semantic risk/variant/status, use <SemanticBadge/>. */
export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      data-tone={dataToneMap[tone] || "neutral"}
      className={cn("sg-badge", className)}
      {...props}
    />
  );
}

/** Semantic kinds the spec requires, with consistent tones and labels. */
export type SemanticKind =
  | "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN" | "INSUFFICIENT_EVIDENCE"
  | "COMPLETE" | "PARTIAL" | "UNAVAILABLE" | "FAILED" | "RUNNING"
  | "KNOWN_PATTERN" | "MUTATED_VARIANT" | "POSSIBLE_EMERGING_CAMPAIGN" | "NO_SIGNIFICANT_MATCH"
  | "DEMO";

const kindMap: Record<SemanticKind, { tone: Tone; label: string; dot?: string }> = {
  LOW: { tone: "success", label: "Low", dot: "bg-risk-low" },
  MEDIUM: { tone: "caution", label: "Medium", dot: "bg-risk-medium" },
  HIGH: { tone: "danger", label: "High", dot: "bg-risk-high" },
  UNKNOWN: { tone: "neutral", label: "Unknown", dot: "bg-text-muted" },
  INSUFFICIENT_EVIDENCE: { tone: "neutral", label: "Insufficient Evidence", dot: "bg-risk-insufficient" },
  COMPLETE: { tone: "success", label: "Complete", dot: "bg-success" },
  PARTIAL: { tone: "caution", label: "Partial", dot: "bg-warning" },
  UNAVAILABLE: { tone: "neutral", label: "Unavailable", dot: "bg-text-muted" },
  FAILED: { tone: "danger", label: "Failed", dot: "bg-danger" },
  RUNNING: { tone: "caution", label: "Running", dot: "bg-warning animate-pulse" },
  KNOWN_PATTERN: { tone: "info", label: "Known Pattern" },
  MUTATED_VARIANT: { tone: "caution", label: "Mutated Variant", dot: "bg-warning" },
  POSSIBLE_EMERGING_CAMPAIGN: { tone: "brand2", label: "Possible Emerging Campaign" },
  NO_SIGNIFICANT_MATCH: { tone: "neutral", label: "No Significant Match" },
  DEMO: { tone: "caution", label: "Demo Data", dot: "bg-warning" },
};

export function SemanticBadge({
  kind,
  className,
}: {
  kind: SemanticKind;
  className?: string;
}) {
  const { tone, label, dot } = kindMap[kind];
  return (
    <span
      data-tone={dataToneMap[tone] || "neutral"}
      className={cn("sg-badge", className)}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dot)} aria-hidden />}
      {label}
    </span>
  );
}

/** Status dot + label for partial-result provider states. */
export function StatusDot({
  kind,
  className,
}: {
  kind: Extract<SemanticKind, "COMPLETE" | "PARTIAL" | "UNAVAILABLE" | "FAILED" | "RUNNING">;
  className?: string;
}) {
  const map = {
    COMPLETE: { c: "success", l: "Complete" },
    PARTIAL: { c: "warning", l: "Partial" },
    UNAVAILABLE: { c: "neutral", l: "Unavailable" },
    FAILED: { c: "danger", l: "Failed" },
    RUNNING: { c: "warning", l: "Running" },
  } as const;
  const { c, l } = map[kind];
  return (
    <span className={cn("inline-flex items-center gap-2 text-body-sm text-text-secondary", className)}>
      <span className="sg-dot" data-tone={c} aria-hidden />
      {l}
    </span>
  );
}
