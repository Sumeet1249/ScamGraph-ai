import { cn } from "@/lib/utils/cn";
import { humanize } from "@/lib/utils/format";

const sourceTone: Record<string, string> = {
  MESSAGE_ANALYZER: "border-accent/30 bg-accent/10 text-accent",
  URL_ANALYZER: "border-signal/30 bg-signal/10 text-signal",
  TINYFISH: "border-safe/30 bg-safe/10 text-safe",
  PAYMENT_MODEL: "border-caution/30 bg-caution/10 text-caution",
  USER_INPUT: "border-line bg-surface text-ink-dim",
};

/** Compact source provenance badge for an evidence item. */
export function SourceBadge({ source }: { source: string }) {
  const tone = sourceTone[source] ?? "border-line bg-surface text-ink-muted";
  return (
    <span
      className={cn(
        "rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider2",
        tone,
      )}
    >
      {humanize(source)}
    </span>
  );
}
