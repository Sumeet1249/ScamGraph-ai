import { ShieldCheck, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { shortId, formatTime } from "@/lib/utils/format";
import { severityBgToken } from "@/lib/utils/risk";
import { SourceBadge } from "./SourceBadge";
import type { EvidenceSignal } from "@/lib/api/types";

/**
 * One evidence item. Clickable to open the EvidenceDrawer for full provenance.
 * Counter-evidence is visually distinguished (legitimacy indicators, shown
 * without implying they establish legitimacy).
 */
export function EvidenceCard({
  signal,
  onSelect,
  className,
}: {
  signal: EvidenceSignal;
  onSelect?: (signal: EvidenceSignal) => void;
  className?: string;
}) {
  const isCounter = Boolean(signal?.is_counter_evidence);
  const signalTypeLabel = (signal?.signal_type || "OBSERVED SIGNAL").replace(/_/g, " ").toLowerCase();
  const sourceName = (signal?.provenance?.source_service || "analyzer").split(".").pop() ?? "analyzer";
  const evId = signal?.signal_id ? shortId(signal.signal_id, 4, 2).replace("…", "") : "01";

  return (
    <button
      type="button"
      onClick={() => onSelect?.(signal)}
      className={cn(
        "w-full rounded-lg border p-3.5 text-left transition-colors hover:border-border-strong",
        isCounter
          ? "border-safe/25 bg-safe/[0.06] text-text-primary"
          : severityBgToken(signal?.severity || "LOW"),
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={isCounter ? "text-safe" : "text-text-primary"}>
              {isCounter ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
            </span>
            <span className="truncate text-sm font-semibold text-text-primary capitalize">
              {signalTypeLabel}
            </span>
          </div>
          <p className="mt-1.5 line-clamp-2 text-xs text-text-muted">{signal?.description || "No description provided"}</p>
        </div>
        <SourceBadge source={sourceName} />
      </div>

      <div className="mt-3 flex items-center justify-between font-mono text-[10px] text-text-muted">
        <span>{formatTime(signal?.observed_at || new Date())}</span>
        <span>EV-{evId}</span>
      </div>
    </button>
  );
}
