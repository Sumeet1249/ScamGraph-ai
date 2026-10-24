import { ShieldAlert, ShieldX, ShieldCheck, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { AdaptiveIntervention, InterventionAction } from "@/lib/api/types";

const toneMap: Record<
  InterventionAction,
  { panel: string; text: string; Icon: typeof ShieldAlert }
> = {
  NONE: { panel: "border-line bg-surface", text: "text-ink-muted", Icon: ShieldCheck },
  PASSIVE: { panel: "border-line bg-surface", text: "text-ink-muted", Icon: ShieldCheck },
  CAUTION: { panel: "border-caution/30 bg-caution/10", text: "text-caution", Icon: AlertTriangle },
  STRONG_WARNING: { panel: "border-risk-high/30 bg-risk-high/10", text: "text-risk-high", Icon: ShieldAlert },
  PRE_PAYMENT_INTERVENTION: { panel: "border-danger/30 bg-danger/10", text: "text-danger", Icon: ShieldX },
};

/** Displays the adaptive intervention decision (combats alert fatigue). */
export function InterventionBanner({ intervention }: { intervention: AdaptiveIntervention }) {
  const t = toneMap[intervention.action] ?? toneMap.NONE;
  const { Icon } = t;

  return (
    <div className={cn("rounded-xl border p-5", t.panel)}>
      <div className="flex items-start gap-3">
        <span className={cn("flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-black/20", t.text)}>
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className={cn("text-sm font-semibold uppercase tracking-wider2", t.text)}>
              {(intervention.action as string).replace(/_/g, " ")}
            </span>
            {intervention.friction_delay_seconds > 0 && (
              <span className="font-mono text-xs text-ink-dim">
                {intervention.friction_delay_seconds}s friction
              </span>
            )}
          </div>
          {intervention.banner_title && (
            <p className="text-sm font-semibold text-ink">{intervention.banner_title}</p>
          )}
          {intervention.banner_message && (
            <p className="text-sm text-ink-muted">{intervention.banner_message}</p>
          )}
        </div>
      </div>
    </div>
  );
}
