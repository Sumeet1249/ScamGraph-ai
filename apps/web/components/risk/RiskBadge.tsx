import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { riskBand, riskTokens, type RiskLevel } from "@/lib/utils/risk";

interface RiskBadgeProps {
  /** Integer risk index 0–100 (normalized by the API client). */
  score: number;
  level: string;
  confidence: string;
  showScore?: boolean;
  size?: "sm" | "md" | "lg";
}

/**
 * Compact risk badge with a mini progress meter.
 * Risk is an INDEX (0–100), never rendered as a probability.
 * Risk Level and Evidence Confidence are kept visually separate (Architecture Rule 11).
 */
export function RiskBadge({
  score,
  level,
  confidence,
  showScore = true,
  size = "md",
}: RiskBadgeProps) {
  const isInsufficient = level === "INSUFFICIENT_EVIDENCE";
  const band = riskBand(score);
  const tokens = isInsufficient ? riskTokens.insufficient : riskTokens[band];

  let Icon = ShieldCheck;
  if (isInsufficient) Icon = HelpCircle;
  else if (band === "critical" || band === "high") Icon = ShieldAlert;
  else if (band === "medium") Icon = AlertTriangle;

  const isLg = size === "lg";
  const confTone =
    confidence === "HIGH" ? "border-safe/30 bg-safe/10 text-safe"
    : confidence === "MEDIUM" ? "border-signal/30 bg-signal/10 text-signal"
    : "border-line bg-surface text-ink-dim";

  return (
    <div className="flex flex-wrap items-center gap-2">
      {showScore && (
        <div
          className={cn(
            "flex flex-col justify-center rounded-lg border border-line bg-elevated px-3 py-1.5",
            isLg ? "min-w-[130px]" : "min-w-[100px]",
          )}
        >
          <div className="flex items-baseline justify-between gap-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-wider2 text-ink-dim">
              Risk Index
            </span>
            <span className="font-mono">
              <span className={cn("font-bold", tokens.text, isLg ? "text-xl" : "text-base")}>
                {score}
              </span>
              <span className="text-[10px] text-ink-dim">/100</span>
            </span>
          </div>
          <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-surface-2">
            <div
              className={cn("h-full rounded-full transition-[width] duration-700 ease-out", tokens.bar)}
              style={{ width: `${Math.max(3, Math.min(100, score))}%` }}
            />
          </div>
        </div>
      )}

      <div
        className={cn(
          "flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-bold uppercase tracking-wider2",
          tokens.bg,
          tokens.border,
          tokens.text,
        )}
      >
        <Icon className="h-4 w-4 shrink-0" />
        <span>{(level as string).replace(/_/g, " ")}</span>
      </div>

      <div
        className={cn(
          "rounded-md border px-2 py-1 font-mono text-[11px] font-semibold uppercase tracking-wider2",
          confTone,
        )}
        title="Evidence Confidence is calibrated separately from Risk Level"
      >
        Conf: <span className="font-bold">{confidence}</span>
      </div>
    </div>
  );
}
