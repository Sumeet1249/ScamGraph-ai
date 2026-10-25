import { Play, Clock, Zap, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui";
import { humanize } from "@/lib/utils/format";

const badgeTone: Record<string, string> = {
  BENIGN: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  CRITICAL: "border-rose-500/30 bg-rose-500/10 text-rose-400",
  HIGH: "border-rose-500/30 bg-rose-500/10 text-rose-400",
  MEDIUM: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  AMBIGUOUS: "border-border bg-surface-2 text-text-muted",
  LOW: "border-blue-500/30 bg-blue-500/10 text-blue-400",
};

/** A selectable scenario card for the ScamGraph Lab workbench. */
export function ScenarioCard({
  title,
  badge,
  description,
  steps,
  onRun,
  disabled,
  difficulty,
  duration,
  isSelected,
}: {
  title: string;
  badge: string;
  description: string;
  steps: number;
  onRun?: () => void;
  disabled?: boolean;
  difficulty?: string;
  duration?: number;
  isSelected?: boolean;
}) {
  return (
    <div
      onClick={!disabled && !isSelected ? onRun : undefined}
      className={cn(
        "group relative flex flex-col rounded-xl border p-4 sm:p-5 transition-all text-left",
        isSelected
          ? "border-brand-primary bg-brand-primary/5 shadow-sm ring-1 ring-brand-primary"
          : "border-border bg-surface-1 hover:border-border-strong hover:bg-surface-2/60 cursor-pointer"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-text-primary tracking-tight leading-snug group-hover:text-brand-primary transition-colors">
            {title}
          </h3>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            {difficulty && (
              <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[10px] font-mono uppercase tracking-wider text-text-muted border border-border/50">
                {difficulty}
              </span>
            )}
            {duration && (
              <span className="flex items-center gap-1 text-[11px] font-mono text-text-muted">
                <Clock className="h-3 w-3 text-text-muted" />
                {duration} min
              </span>
            )}
          </div>
        </div>

        <span
          className={cn(
            "rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap flex-shrink-0",
            badgeTone[badge] ?? badgeTone.MEDIUM
          )}
        >
          {humanize(badge)}
        </span>
      </div>

      <p className="mt-3 text-xs leading-relaxed text-text-secondary line-clamp-3">
        {description}
      </p>

      <div className="mt-4 pt-3 border-t border-border/60 flex items-center justify-between gap-2">
        <div className="flex items-center gap-3 text-[11px] font-mono text-text-muted">
          <span className="flex items-center gap-1">
            <Zap className="h-3 w-3 text-amber-400" />
            {steps} steps
          </span>
        </div>

        <Button
          size="sm"
          variant={isSelected ? "secondary" : "primary"}
          onClick={(e) => {
            e.stopPropagation();
            onRun?.();
          }}
          disabled={disabled}
          className={cn(
            "h-8 px-3 text-xs font-medium transition-all",
            isSelected && "border-brand-primary/40 text-brand-primary bg-brand-primary/10 hover:bg-brand-primary/20"
          )}
        >
          {isSelected ? (
            <span className="flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary" />
              </span>
              In Progress
            </span>
          ) : (
            <span className="flex items-center gap-1.5">
              <Play className="h-3 w-3 fill-current" />
              Start
            </span>
          )}
        </Button>
      </div>
    </div>
  );
}
