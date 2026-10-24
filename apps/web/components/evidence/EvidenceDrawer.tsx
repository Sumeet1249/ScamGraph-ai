"use client";

import { useEffect } from "react";
import { X, ShieldCheck, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { shortId, formatTime, humanize, pct } from "@/lib/utils/format";
import { severityBgToken, severityToken } from "@/lib/utils/risk";
import { SourceBadge } from "./SourceBadge";
import type { EvidenceSignal } from "@/lib/api/types";

/**
 * Slide-over drawer showing the full provenance of a selected evidence signal.
 * Opens when a reason code or evidence card is clicked. Esc/backdrop closes.
 */
export function EvidenceDrawer({
  signal,
  onClose,
}: {
  signal: EvidenceSignal | null;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!signal) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [signal, onClose]);

  if (!signal) return null;
  const isCounter = Boolean(signal.is_counter_evidence);
  const signalTypeLabel = (signal.signal_type || "SIGNAL").replace(/_/g, " ").toLowerCase();
  const sourceService = signal.provenance?.source_service || "services.unknown";
  const sourceName = sourceService.split(".").pop() ?? sourceService;
  const evId = signal.signal_id ? shortId(signal.signal_id, 4, 3) : "001";

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-background/70 backdrop-blur-sm" onClick={onClose} aria-hidden />
      <aside
        role="dialog"
        aria-label="Evidence details"
        aria-modal="true"
        className="absolute inset-y-0 right-0 flex w-full max-w-md flex-col border-l border-border bg-surface-raised animate-fade-in shadow-2xl"
      >
        {/* Header */}
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <span className={isCounter ? "text-safe" : "text-text-primary"}>
              {isCounter ? <ShieldCheck className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
            </span>
            <span className="text-sm font-semibold text-text-primary">Evidence</span>
            <span className="font-mono text-xs text-text-muted">EV-{evId}</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border-input text-text-muted hover:text-text-primary hover:bg-surface-hover"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 space-y-5 overflow-y-auto scrollbar-thin p-5">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={cn("rounded border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider2", isCounter ? "border-safe/30 bg-safe/10 text-safe" : severityBgToken(signal.severity || "LOW"))}>
                {isCounter ? "Counter evidence" : (signal.severity || "LOW")}
              </span>
              <span className="rounded border border-border-input bg-surface px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider2 text-text-muted">
                {humanize(signal.dimension || "UNKNOWN")}
              </span>
            </div>
            <h3 className="mt-3 text-lg font-semibold text-text-primary capitalize">
              {signalTypeLabel}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-text-secondary">{signal.description || "No description provided."}</p>
          </div>

          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-[11px] uppercase tracking-wider2 text-text-muted">Source</dt>
              <dd className="mt-0.5"><SourceBadge source={sourceName} /></dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wider2 text-text-muted">Confidence</dt>
              <dd className={cn("mt-0.5 font-mono", severityToken(signal.severity || "LOW"))}>{pct(signal.confidence ?? 0.8)}%</dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wider2 text-text-muted">Weight</dt>
              <dd className="mt-0.5 font-mono text-text-secondary">{signal.weight ?? 1.0}×</dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wider2 text-text-muted">Observed</dt>
              <dd className="mt-0.5 font-mono text-xs text-text-secondary">{formatTime(signal.observed_at || new Date())}</dd>
            </div>
          </dl>

          <div>
            <div className="eyebrow mb-2">Provenance</div>
            <div className="rounded-xl border border-border bg-surface p-4 space-y-2 text-sm">
              <div className="flex justify-between gap-3">
                <span className="text-text-muted">Service</span>
                <span className="font-mono text-xs text-text-secondary">{sourceService}</span>
              </div>
              <div className="flex justify-between gap-3">
                <span className="text-text-muted">Detector</span>
                <span className="font-mono text-xs text-text-secondary">{signal.provenance?.detector_name || "Unknown"}</span>
              </div>
              {signal.provenance?.target_artifact && (
                <div className="flex justify-between gap-3">
                  <span className="text-text-muted">Target</span>
                  <span className="font-mono text-xs text-text-secondary text-right">{signal.provenance.target_artifact}</span>
                </div>
              )}
            </div>
          </div>

          {signal.provenance?.raw_evidence && Object.keys(signal.provenance.raw_evidence).length > 0 && (
            <div>
              <div className="eyebrow mb-2">Raw Evidence</div>
              <pre className="rounded-xl border border-border bg-surface-inset overflow-x-auto p-3 text-[11px] leading-relaxed text-text-secondary">
                {JSON.stringify(signal.provenance.raw_evidence, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
