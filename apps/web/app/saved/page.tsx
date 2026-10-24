"use client";

import { useState } from "react";
import Link from "next/link";
import { Bookmark, Lock, Search, ExternalLink, Trash2, ArrowRight } from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

interface SavedQuery {
  id: string;
  name: string;
  query_dsl: string;
  target_type: string;
  last_run: string;
  result_count: number;
}

const CANONICAL_SAVED: SavedQuery[] = [
  {
    id: "SQ-001",
    name: "Urgent Electricity Cutoff Syndicates (<4h velocity surge)",
    query_dsl: "modality:UPI AND tag:electricity AND velocity:>200%",
    target_type: "Campaigns",
    last_run: "2026-10-24T20:00:00Z",
    result_count: 2,
  },
  {
    id: "SQ-002",
    name: "High-Loss Digital Arrest RTGS Transfers (> ₹5,00,000)",
    query_dsl: "modality:RTGS AND loss:>500000 AND state:ACTIVE",
    target_type: "Incidents",
    last_run: "2026-10-24T19:30:00Z",
    result_count: 6,
  },
  {
    id: "SQ-003",
    name: "Karnataka Discom Mule Accounts (OKAXIS Handles)",
    query_dsl: "vpa:*@okaxis AND campaign:#UTL-8490",
    target_type: "Entities",
    last_run: "2026-10-24T18:15:00Z",
    result_count: 14,
  },
];

export default function SavedInvestigationsPage() {
  const [queries, setQueries] = useState<SavedQuery[]>(CANONICAL_SAVED);

  const removeQuery = (id: string) => {
    setQueries((prev) => prev.filter((q) => q.id !== id));
  };

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A17 Saved Investigations &amp; Monitors</span>
        </div>
      </div>

      <div className="p-4 lg:p-8 space-y-5 max-w-[1280px] mx-auto w-full">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
              <Bookmark className="w-3.5 h-3.5" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-viz-text">Saved Investigations</h1>
            <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
              §7 A17
            </span>
          </div>
          <p className="text-xs text-viz-neutral mt-1">
            Bookmarked graph exploration filters, active surveillance triggers, and cross-team investigation queries.
          </p>
        </div>

        <div className="space-y-3">
          {queries.map((q) => (
            <div
              key={q.id}
              className="p-4 rounded-xl bg-surface border border-border-divider flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.2 rounded bg-surface-subtle border border-border-divider font-mono text-[10px] font-bold text-viz-neutral">
                    {q.target_type}
                  </span>
                  <h3 className="text-sm font-bold text-viz-text">{q.name}</h3>
                </div>
                <code className="text-xs font-mono text-viz-primary block bg-surface-subtle px-2 py-1 rounded max-w-xl">
                  {q.query_dsl}
                </code>
                <span className="text-[11px] text-viz-neutral block pt-1">
                  Last evaluated: {formatDateTime(q.last_run)} · Found {q.result_count} matching records
                </span>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <Link
                  href="/search"
                  className="h-8 px-3 rounded bg-viz-primary text-white text-xs font-semibold flex items-center gap-1.5 hover:bg-[#00483f] transition-colors"
                >
                  <span>Execute Query</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <button
                  onClick={() => removeQuery(q.id)}
                  className="p-2 rounded hover:bg-surface-subtle text-viz-neutral hover:text-error transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
