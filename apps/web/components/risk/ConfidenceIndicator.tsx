import { cn } from "@/lib/utils/cn";
import type { EvidenceConfidence } from "@/lib/api/types";

const toneMap: Record<EvidenceConfidence, { ring: string; text: string; dot: string }> = {
  HIGH: { ring: "border-safe/30 bg-safe/10", text: "text-safe", dot: "bg-safe" },
  MEDIUM: { ring: "border-signal/30 bg-signal/10", text: "text-signal", dot: "bg-signal" },
  LOW: { ring: "border-line bg-surface", text: "text-ink-dim", dot: "bg-ink-dim" },
};

const labelMap: Record<EvidenceConfidence, string> = {
  HIGH: "Multi-source corroboration across independent dimensions.",
  MEDIUM: "Corroborated across some dimensions; partial coverage.",
  LOW: "Limited corroboration. Treat conclusions as preliminary.",
};

/** Evidence confidence, shown separately from risk (Architecture Rule 11 & Section 9.2). */
export function ConfidenceIndicator({
  confidence,
}: {
  confidence: EvidenceConfidence;
}) {
  const isHigh = confidence === "HIGH";
  const isMed = confidence === "MEDIUM";

  const dotColor = isHigh ? "bg-success" : isMed ? "bg-warning" : "bg-text-muted";
  const textColor = isHigh ? "text-success" : isMed ? "text-warning" : "text-text-muted";
  const badgeStyle = isHigh
    ? "border-success/30 bg-success/10 text-success"
    : isMed
    ? "border-warning/30 bg-warning/10 text-warning"
    : "border-border bg-surface-2 text-text-muted";

  return (
    <div className="panel p-5 bg-surface-1 border border-border flex flex-col justify-between">
      <div>
        <div className="eyebrow mb-3">Evidence Confidence</div>
        <div className="flex items-center gap-2.5">
          <span className={cn("h-2.5 w-2.5 rounded-full", dotColor)} aria-hidden />
          <span className={cn("text-2xl font-bold font-mono tracking-tight", textColor)}>
            {confidence}
          </span>
          <span
            className={cn(
              "ml-auto inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider2",
              badgeStyle
            )}
          >
            {isHigh ? "Corroborated" : isMed ? "Partial" : "Preliminary"}
          </span>
        </div>
      </div>
      <div className="mt-4 pt-3 border-t border-border/80">
        <p className="text-xs text-text-secondary leading-relaxed">
          {labelMap[confidence] ?? labelMap.LOW}
        </p>
        <p className="mt-2 text-[11px] text-text-muted font-mono">
          Independent cross-signal dimensions verified
        </p>
      </div>
    </div>
  );
}
