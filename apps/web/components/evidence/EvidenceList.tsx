"use client";

import { useMemo, useState } from "react";
import { cn } from "@/lib/utils/cn";
import { EvidenceCard } from "./EvidenceCard";
import { EmptyState } from "@/components/shared/States";
import type { EvidenceSignal } from "@/lib/api/types";

const FILTERS = [
  { id: "all", label: "All" },
  { id: "message", label: "Message" },
  { id: "tinyfish", label: "TinyFish" },
  { id: "url", label: "URL" },
  { id: "infrastructure", label: "Infrastructure" },
  { id: "graph", label: "Graph" },
  { id: "ai", label: "AI" },
  { id: "payment", label: "Payment" },
] as const;

type FilterId = (typeof FILTERS)[number]["id"];

function normalizeSignal(s: any, idx: number, isCounterDefault = false): EvidenceSignal {
  if (!s) {
    return {
      signal_id: `sig-unknown-${idx}`,
      dimension: "UNKNOWN",
      signal_type: "OBSERVED_SIGNAL",
      severity: "LOW",
      confidence: 0.8,
      weight: 1.0,
      description: "Observed evidence artifact",
      observed_at: new Date().toISOString(),
      is_counter_evidence: isCounterDefault,
      provenance: {
        source_service: "services.verification",
        detector_name: "SignalDetector",
      },
    };
  }

  if (typeof s === "string") {
    return {
      signal_id: `counter-${idx}`,
      dimension: "COUNTER_EVIDENCE",
      signal_type: "LEGITIMACY_INDICATOR",
      severity: "LOW",
      confidence: 0.85,
      weight: 1.0,
      description: s,
      observed_at: new Date().toISOString(),
      is_counter_evidence: true,
      provenance: {
        source_service: "services.verification",
        detector_name: "CounterEvidenceVerifier",
      },
    };
  }

  return {
    signal_id: s.signal_id || `sig-${idx}`,
    dimension: s.dimension || (s.is_counter_evidence ? "COUNTER_EVIDENCE" : "SEMANTIC"),
    signal_type: s.signal_type || (s.is_counter_evidence ? "LEGITIMACY_INDICATOR" : "DETECTED_SIGNAL"),
    severity: (s.severity || "LOW").toUpperCase() as any,
    confidence: typeof s.confidence === "number" ? s.confidence : 0.85,
    weight: typeof s.weight === "number" ? s.weight : 1.0,
    description: s.description || s.summary || s.text || s.title || (typeof s === "object" ? JSON.stringify(s) : "Observed signal"),
    observed_at: s.observed_at || s.timestamp || new Date().toISOString(),
    is_counter_evidence: Boolean(s.is_counter_evidence ?? isCounterDefault),
    provenance: {
      source_service: s.provenance?.source_service || "services.investigation",
      detector_name: s.provenance?.detector_name || "PatternDetector",
      target_artifact: s.provenance?.target_artifact,
      raw_evidence: s.provenance?.raw_evidence,
    },
  };
}

function matchesFilter(signal: EvidenceSignal, filter: FilterId): boolean {
  if (filter === "all") return true;
  const source = `${signal.provenance?.source_service || ""} ${signal.signal_type || ""}`.toLowerCase();
  const dim = (signal.dimension || "").toLowerCase();
  switch (filter) {
    case "message":
      return source.includes("message") || source.includes("semantic");
    case "tinyfish":
      return source.includes("tinyfish");
    case "url":
      return dim === "url" || source.includes("url");
    case "infrastructure":
      return dim === "infrastructure";
    case "graph":
      return dim === "historical" || dim === "campaign" || dim === "graph";
    case "ai":
      return source.includes("semantic") || source.includes("pattern") || source.includes("ai");
    case "payment":
      return dim === "payment" || source.includes("payment") || source.includes("vpa");
    default:
      return true;
  }
}

/** Filterable evidence browser. Clicking a card opens the EvidenceDrawer. */
export function EvidenceList({
  signals = [],
  counterEvidence = [],
  onSelect,
}: {
  signals?: any[];
  counterEvidence?: any[];
  onSelect?: (signal: EvidenceSignal) => void;
}) {
  const [filter, setFilter] = useState<FilterId>("all");

  const normalizedSignals = useMemo(() => {
    const sigs = Array.isArray(signals) ? signals.map((s, i) => normalizeSignal(s, i, false)) : [];
    const counter = Array.isArray(counterEvidence) ? counterEvidence.map((c, i) => normalizeSignal(c, i, true)) : [];
    return [...sigs, ...counter];
  }, [signals, counterEvidence]);

  const filtered = useMemo(() => {
    return normalizedSignals.filter((s) => matchesFilter(s, filter));
  }, [normalizedSignals, filter]);

  return (
    <div className="space-y-4">
      <div
        role="tablist"
        aria-label="Filter evidence by source"
        className="flex flex-wrap gap-1"
      >
        {FILTERS.map((f) => (
          <button
            key={f.id}
            role="tab"
            aria-selected={filter === f.id}
            onClick={() => setFilter(f.id)}
            className={cn(
              "rounded-full px-3 py-1.5 text-xs font-medium transition-all btn-pop",
              filter === f.id
                ? "bg-brand-primary/15 text-brand-primary border border-brand-primary/35 font-semibold"
                : "text-text-secondary hover:text-text-primary hover:bg-surface-2 border border-transparent",
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No evidence for this filter"
          message="Try a different source filter, or run an investigation to produce signals."
        />
      ) : (
        <div className="grid gap-2.5 sm:grid-cols-2">
          {filtered.map((s) => (
            <EvidenceCard key={s.signal_id} signal={s} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}
