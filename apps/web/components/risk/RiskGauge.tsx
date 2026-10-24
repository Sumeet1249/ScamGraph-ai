"use client";

import { cn } from "@/lib/utils/cn";
import { riskBand, riskTokens } from "@/lib/utils/risk";
import { useRiskAnimation } from "@/lib/hooks/useRiskAnimation";
import type { RiskLevel } from "@/lib/utils/risk";

/**
 * Large risk gauge for the incident Overview tab.
 * Animates the numeric index as evidence arrives (explains "why intervene now").
 * Risk is an INDEX (0–100), never a probability — no "%" suffix.
 */
export function RiskGauge({
  score,
  level,
}: {
  score: number;
  level: RiskLevel | string;
}) {
  const display = useRiskAnimation(score);
  const isInsufficient = level === "INSUFFICIENT_EVIDENCE";
  const band = riskBand(score);
  const tokens = isInsufficient ? riskTokens.insufficient : riskTokens[band];

  return (
    <div className="panel p-5">
      <div className="eyebrow mb-3">Threat Assessment</div>
      <div className="flex items-end gap-4">
        <div className={cn("font-mono text-5xl font-bold leading-none tabular-nums", tokens.text)}>
          {display}
        </div>
        <div className="pb-1">
          <div className={cn("text-sm font-semibold uppercase tracking-wider2", tokens.text)}>
            {(level as string).replace(/_/g, " ")}
          </div>
          <div className="text-[11px] text-ink-dim">Risk index · 0–100</div>
        </div>
      </div>
      <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-surface-2">
        <div
          className={cn("h-full rounded-full transition-[width] duration-700 ease-out", tokens.bar)}
          style={{ width: `${Math.max(3, Math.min(100, score))}%` }}
          role="progressbar"
          aria-valuenow={score}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Risk index"
        />
      </div>
      <p className="mt-3 text-xs text-ink-dim">
        Risk is a corroboration index, not a fraud probability.
      </p>
    </div>
  );
}
