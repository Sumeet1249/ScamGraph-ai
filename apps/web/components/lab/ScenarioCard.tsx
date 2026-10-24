import { Play, Clock, Zap } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui";
import { humanize } from "@/lib/utils/format";

const badgeTone: Record<string, string> = {
  BENIGN: "border-safe/30 bg-safe/10 text-safe",
  CRITICAL: "border-danger/30 bg-danger/10 text-danger",
  HIGH: "border-risk-high/30 bg-risk-high/10 text-risk-high",
  MEDIUM: "border-caution/30 bg-caution/10 text-caution",
  AMBIGUOUS: "border-line bg-surface text-ink-dim",
  LOW: "border-success/30 bg-success/10 text-success",
};

/** A selectable scenario card for the ScamGraph Lab. */
export function ScenarioCard({
  title,
  badge,
  description,
  steps,
  onRun,
  disabled,
  difficulty,
  duration,
}: {
  title: string;
  badge: string;
  description: string;
  steps: number;
  onRun?: () => void;
  disabled?: boolean;
  difficulty?: string;
  duration?: number;
}) {
  return (
    <div className="panel flex flex-col p-5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-ink">{title}</h3>
          {difficulty && (
            <p className="text-[11px] text-ink-dim capitalize mt-1">{difficulty} • {duration} min</p>
          )}
        </div>
        <span className={cn("rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider2 whitespace-nowrap", badgeTone[badge] ?? badgeTone.MEDIUM)}>
          {humanize(badge)}
        </span>
      </div>
      <p className="mt-2 flex-1 text-xs leading-relaxed text-ink-muted">{description}</p>
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-3 text-[11px] text-ink-dim">
          <span className="flex items-center gap-1">
            <Zap className="h-3 w-3" />
            {steps} steps
          </span>
          {duration && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {duration}m
            </span>
          )}
        </div>
        <Button size="sm" variant="primary" onClick={onRun} disabled={disabled}>
          <Play className="h-3.5 w-3.5" />
          Start
        </Button>
      </div>
    </div>
  );
}
