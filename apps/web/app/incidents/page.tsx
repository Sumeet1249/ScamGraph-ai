"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { RiskBadge } from "@/components/risk/RiskBadge";
import { humanizeStage, formatDateTime } from "@/lib/utils/format";
import type { RiskLevel, EvidenceConfidence } from "@/lib/api/types";
import { RotateCw, Sparkles } from "lucide-react";
import { CANONICAL_INCIDENTS } from "@/lib/demo/incidents-db";

export interface IncidentItem {
  id: string;
  pattern: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: EvidenceConfidence;
  current_stage: string;
  last_activity: string;
  isRecent?: boolean;
}

const DEFAULT_INCIDENTS: IncidentItem[] = Object.values(CANONICAL_INCIDENTS).map((c) => ({
  id: c.id,
  pattern: c.pattern,
  risk_score: c.risk_score,
  risk_level: c.risk_level,
  confidence: c.confidence,
  current_stage: c.current_stage,
  last_activity: c.last_activity,
  isRecent: c.isRecent,
}));

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentItem[]>(DEFAULT_INCIDENTS);
  const [isLoading, setIsLoading] = useState(false);

  const fetchIncidents = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch from backend API
      const res = await fetch("/api/v1/incidents");
      let backendIncidents: IncidentItem[] = [];
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          backendIncidents = data
            .filter((item: any) => !CANONICAL_INCIDENTS[item.id]) // Exclude stubs colliding with canonical records
            .map((item: any) => ({
              id: item.id,
              pattern: item.pattern || item.title || "Multi-Signal Investigation",
              risk_score: typeof item.risk_score === "number" ? item.risk_score : 0,
              risk_level: (item.risk_level as RiskLevel) || "LOW",
              confidence: (item.confidence as EvidenceConfidence) || "LOW",
              current_stage: item.current_stage || "INITIAL_CONTACT",
              last_activity: item.last_activity || item.created_at || new Date().toISOString(),
              isRecent: true,
            }));
        }
      }

      // 2. Read local storage cache for instant client-side persistence
      let localIncidents: IncidentItem[] = [];
      try {
        const raw = localStorage.getItem("recent_investigations");
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            localIncidents = parsed.map((item: any) => ({
              ...item,
              isRecent: true,
            }));
          }
        }
      } catch (e) {
        // Ignore localStorage error
      }

      // 3. Merge: Dynamic new investigations first, followed by canonical records
      const combinedMap = new Map<string, IncidentItem>();

      // Add local first (user's most recent interactions)
      localIncidents.forEach((inc) => {
        if (!CANONICAL_INCIDENTS[inc.id]) {
          combinedMap.set(inc.id, inc);
        }
      });

      // Add backend items
      backendIncidents.forEach((inc) => {
        if (!combinedMap.has(inc.id) && !CANONICAL_INCIDENTS[inc.id]) {
          combinedMap.set(inc.id, inc);
        }
      });

      // Always populate authoritative canonical records
      DEFAULT_INCIDENTS.forEach((inc) => {
        combinedMap.set(inc.id, inc);
      });

      setIncidents(Array.from(combinedMap.values()));
    } catch (err) {
      console.warn("Failed to load incidents:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Command"
        title="Incidents"
        description="Reconstructed scam journeys. Newly investigated threats appear dynamically here."
        actions={
          <div className="flex items-center gap-3">
            <button
              onClick={fetchIncidents}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-border bg-surface-1 hover:bg-surface-2 text-xs font-medium text-text-primary transition-all disabled:opacity-50 btn-pop"
              title="Refresh incidents list"
            >
              <RotateCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <DemoDataBadge />
          </div>
        }
      />

      {/* Dense Row / List Layout (Section 8.2) */}
      <div className="overflow-hidden rounded-xl border border-border bg-surface-1 divide-y divide-border">
        {incidents.map((inc) => {
          const isHigh = inc.risk_score >= 70 || inc.risk_level === "HIGH" || inc.risk_level === "CRITICAL";
          const isMed = !isHigh && (inc.risk_score >= 40 || inc.risk_level === "MEDIUM");
          const isInsufficient = inc.risk_level === "INSUFFICIENT_EVIDENCE";

          return (
            <Link
              key={inc.id}
              href={`/incidents/${inc.id}`}
              className="group block px-5 py-4 transition-colors hover:bg-surface-2/60 focus-visible:bg-surface-2/80 focus-visible:outline-none"
            >
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1.5fr_1fr_1.2fr] sm:items-center">
                {/* Left: ID, Type/Label, Time */}
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-semibold text-text-primary group-hover:text-brand-primary transition-colors">
                      {inc.id}
                    </span>
                    {inc.isRecent && (
                      <span className="inline-flex items-center gap-1 rounded bg-brand-primary/10 border border-brand-primary/25 px-1.5 py-0.2 text-[10px] font-semibold text-brand-primary">
                        <Sparkles className="h-2.5 w-2.5" />
                        Investigated
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-text-secondary truncate font-medium">
                    {inc.pattern}
                  </p>
                  <p className="mt-0.5 text-xs text-text-muted font-mono">
                    {humanizeStage(inc.current_stage)} · {formatDateTime(inc.last_activity)}
                  </p>
                </div>

                {/* Middle: Risk Index Score + Progress bar */}
                <div className="flex flex-col justify-center">
                  <div className="flex items-baseline justify-between text-xs">
                    <span className="text-[11px] text-text-muted uppercase tracking-wider2 font-semibold">
                      Risk Index
                    </span>
                    <span className="font-mono text-sm font-bold text-text-primary tabular-nums">
                      {inc.risk_score}
                      <span className="text-[10px] font-normal text-text-muted">/100</span>
                    </span>
                  </div>
                  <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-surface-3">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isInsufficient
                          ? "bg-text-muted"
                          : isHigh
                          ? "bg-danger"
                          : isMed
                          ? "bg-warning"
                          : "bg-success"
                      }`}
                      style={{ width: `${Math.max(4, Math.min(100, inc.risk_score))}%` }}
                    />
                  </div>
                </div>

                {/* Right: Risk Level, Confidence, Status Badge */}
                <div className="flex flex-wrap items-center justify-end gap-2 text-xs">
                  <span
                    className={`inline-flex items-center rounded-md border px-2 py-0.5 font-semibold uppercase text-[11px] tracking-wider2 ${
                      isInsufficient
                        ? "border-border bg-surface-2 text-text-muted"
                        : isHigh
                        ? "border-danger/30 bg-danger/10 text-danger"
                        : isMed
                        ? "border-warning/30 bg-warning/10 text-warning"
                        : "border-success/30 bg-success/10 text-success"
                    }`}
                  >
                    {isInsufficient ? "Insufficient Evidence" : `${inc.risk_level} Risk`}
                  </span>

                  <span
                    className="rounded-md border border-border bg-surface-2 px-2 py-0.5 font-mono text-[11px] text-text-secondary"
                    title={`Corroboration Confidence: ${inc.confidence}`}
                  >
                    Conf: <span className="font-bold text-text-primary">{inc.confidence}</span>
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
