import { cn } from "@/lib/utils/cn";
import { formatTime, formatOffset, humanizeStage } from "@/lib/utils/format";
import { severityToken } from "@/lib/utils/risk";
import type { JourneyStep } from "@/lib/api/types";

/** A single step in the scam journey timeline. */
export function JourneyNode({
  step,
  isCurrent,
}: {
  step: JourneyStep;
  isCurrent?: boolean;
}) {
  const signals = step.associated_signals ?? [];
  const maxSeverity = signals.length
    ? signals.reduce((m, s) => (s.severity > m ? s.severity : m), "INFO")
    : "INFO";

  return (
    <li data-journey-node className="relative pl-7">
      {/* Timeline rail dot */}
      <span
        className={cn(
          "absolute left-0 top-1.5 flex h-4 w-4 items-center justify-center rounded-full border-2 bg-base",
          isCurrent ? "border-accent" : "border-line",
        )}
      >
        {isCurrent && <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse-soft" />}
      </span>

      <div className="pb-7">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-xs text-ink-dim tabular-nums">{formatTime(step.timestamp)}</span>
          {step.time_delta_seconds != null && (
            <span className="font-mono text-[10px] text-ink-dim tabular-nums">{formatOffset(step.time_delta_seconds)}</span>
          )}
        </div>

        <div className="mt-1 flex items-center gap-2">
          <h4 className="text-sm font-semibold text-ink">{humanizeStage(step.stage)}</h4>
          {isCurrent && (
            <span className="rounded bg-accent/15 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider2 text-accent">
              You are here
            </span>
          )}
        </div>

        <p className="mt-1 text-xs text-ink-muted">{step.description}</p>

        {signals.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {signals.slice(0, 4).map((s) => (
              <span
                key={s.signal_id}
                className={cn(
                  "rounded border px-1.5 py-0.5 font-mono text-[10px]",
                  severityToken(s.severity),
                )}
                title={s.description}
              >
                {s.signal_type.replace(/_/g, " ").toLowerCase()}
              </span>
            ))}
            {signals.length > 4 && (
              <span className="text-[10px] text-ink-dim">+{signals.length - 4} more</span>
            )}
          </div>
        )}
      </div>
    </li>
  );
}
