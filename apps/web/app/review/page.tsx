"use client";

import { useState } from "react";
import Link from "next/link";
import {
  FileCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCw,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  ShieldCheck,
  Lock,
  ChevronRight,
  Layers,
  Sparkles,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

interface ReviewItem {
  id: string;
  item_type: "INCIDENT_SCORE" | "MODEL_DEGRADATION" | "CAMPAIGN_MERGE" | "FALSE_POSITIVE_APPEAL";
  title: string;
  target_ref: string;
  model_score: number;
  model_recommendation: "BLOCK" | "CHALLENGE" | "ALLOW";
  disagreement_reason: string;
  submitted_by: string;
  submitted_at: string;
  evidence_snippets: string[];
  status: "PENDING" | "APPROVED" | "OVERRIDDEN";
}

const CANONICAL_REVIEWS: ReviewItem[] = [
  {
    id: "REV-2026-041",
    item_type: "INCIDENT_SCORE",
    title: "Borderline Electricity Bill Cutoff Mandate (#SG-84915)",
    target_ref: "#SG-84915",
    model_score: 68,
    model_recommendation: "CHALLENGE",
    disagreement_reason: "NLP Coercion score is 92%, but recipient account age > 4 years and zero past complaints.",
    submitted_by: "Autonomous Risk Sentinel",
    submitted_at: "2026-10-24T18:53:00Z",
    evidence_snippets: [
      "SMS Text: 'Dear consumer electricity bill overdue tonight power cut 21:30.'",
      "VPA: util-power-84920@okaxis (Co-occurs in Syndicate #UTL-8490)",
      "Amount: ₹9,800.00",
    ],
    status: "PENDING",
  },
  {
    id: "REV-2026-040",
    item_type: "FALSE_POSITIVE_APPEAL",
    title: "Merchant Disputed Lien on Verified Grocery Store",
    target_ref: "merchant-grocery@paytm",
    model_score: 52,
    model_recommendation: "ALLOW",
    disagreement_reason: "Received ₹1,500 from known compromised mule; merchant claims genuine POS sale of rations.",
    submitted_by: "Nodal Bank Desk (Axis Bank)",
    submitted_at: "2026-10-24T17:20:00Z",
    evidence_snippets: [
      "Invoice #INV-29401 attached: Rice & Cooking Oil ₹1,500.",
      "CCTV timestamp coincides with UTR 429810482910.",
    ],
    status: "PENDING",
  },
  {
    id: "REV-2026-039",
    item_type: "CAMPAIGN_MERGE",
    title: "Merge Proposed: #UTL-8490 and #UTL-8488 Syndicate Clusters",
    target_ref: "CLUSTER_MERGE_01",
    model_score: 94,
    model_recommendation: "BLOCK",
    disagreement_reason: "Graph correlation engine discovered 3 overlapping telephony LAC nodes and shared APK dropper server.",
    submitted_by: "Graph Neural Network Agent",
    submitted_at: "2026-10-24T16:00:00Z",
    evidence_snippets: [
      "Shared IP: 185.220.101.5 (Offshore Bulletproof Host)",
      "Common LAC tower sequence: 404-45 Karnataka corridor.",
    ],
    status: "PENDING",
  },
];

export default function ReviewQueuePage() {
  const [reviews, setReviews] = useState<ReviewItem[]>(CANONICAL_REVIEWS);
  const [selectedId, setSelectedId] = useState<string>("REV-2026-041");
  const [decisionNotes, setDecisionNotes] = useState<string>("");

  const selectedReview = reviews.find((r) => r.id === selectedId) || reviews[0];

  const handleDecision = (action: "APPROVE" | "OVERRIDE") => {
    setReviews((prev) =>
      prev.map((r) =>
        r.id === selectedId ? { ...r, status: action === "APPROVE" ? "APPROVED" : "OVERRIDDEN" } : r
      )
    );
    setDecisionNotes("");
  };

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* 1. Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A12 Human-in-the-Loop Review Queue</span>
          <span>•</span>
          <span>Dual-Axis Adjudication</span>
        </div>
      </div>

      {/* 2. Top Header Block */}
      <div className="bg-surface border-b border-border-divider px-4 lg:px-8 py-4 shrink-0 space-y-3">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
                <FileCheck className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Review Queue</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
                §7 A12
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-xs font-bold">
                {reviews.filter((r) => r.status === "PENDING").length} pending adjudications
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1 max-w-3xl">
              Human-in-the-loop review queue for borderline/degraded model scores, disputed bank liens, and high-impact automated freeze overrides.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Dual-Pane Adjudication Work Surface */}
      <div className="flex flex-1 w-full overflow-hidden min-h-[calc(100vh-12rem)]">
        {/* Left Side: Pending Reviews Queue */}
        <div className="w-full lg:w-1/2 overflow-y-auto border-r border-border-divider p-4 space-y-3 bg-surface">
          <div className="text-xs font-bold uppercase tracking-wider text-viz-neutral">
            Queue Items ({reviews.length})
          </div>

          <div className="space-y-2">
            {reviews.map((r) => {
              const isSelected = selectedId === r.id;
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedId(r.id)}
                  className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-[#0B6256]/[0.08] border-viz-primary shadow-xs"
                      : "bg-surface hover:bg-surface-subtle border-border-divider"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-viz-text">#{r.id}</span>
                      <span className="px-1.5 py-0.2 rounded bg-surface-subtle border border-border-divider text-[10px] uppercase font-semibold text-viz-neutral">
                        {r.item_type}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        r.status === "PENDING"
                          ? "bg-tone-warning-bg text-tone-warning-text"
                          : r.status === "APPROVED"
                          ? "bg-tone-info-bg text-tone-info-text"
                          : "bg-surface-subtle text-viz-neutral"
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-viz-text mt-1.5">{r.title}</h3>
                  <p className="text-[11px] text-viz-neutral mt-1 leading-relaxed line-clamp-2">
                    {r.disagreement_reason}
                  </p>

                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-border-divider/50 text-[11px] text-viz-neutral">
                    <span>Model: {r.model_recommendation} ({r.model_score}%)</span>
                    <span>{formatDateTime(r.submitted_at)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: Evidence Inspector & Adjudication Deck */}
        <div className="w-full lg:w-1/2 overflow-y-auto p-5 bg-surface-subtle space-y-4">
          {selectedReview ? (
            <div className="space-y-4">
              <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-viz-primary" />
                    <h2 className="text-sm font-bold text-viz-text">Evidence Inspector</h2>
                  </div>
                  <span className="font-mono text-xs font-bold text-viz-primary">{selectedReview.target_ref}</span>
                </div>

                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-viz-text">{selectedReview.title}</h3>
                  <div className="p-3 rounded bg-surface-subtle border border-border-divider text-xs text-viz-neutral space-y-1">
                    <span className="font-bold text-viz-text block">Disagreement / Appeal Rationale:</span>
                    <p className="leading-relaxed">{selectedReview.disagreement_reason}</p>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-viz-neutral block">
                    Forensic Artifacts
                  </span>
                  {selectedReview.evidence_snippets.map((snip, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-surface border border-border-divider font-mono text-[11px] text-viz-text">
                      {snip}
                    </div>
                  ))}
                </div>
              </div>

              {/* Adjudication Decision Card */}
              <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-viz-neutral">
                  Analyst Adjudication
                </h3>

                <textarea
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  placeholder="Enter §65B statutory rationale for confirming or overriding model assessment..."
                  className="w-full h-24 p-3 bg-surface-subtle border border-border-divider rounded-lg text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
                />

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <button
                    onClick={() => handleDecision("APPROVE")}
                    className="h-9 px-4 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Confirm Model Assessment</span>
                  </button>
                  <button
                    onClick={() => handleDecision("OVERRIDE")}
                    className="h-9 px-4 rounded bg-tone-danger-strong-bg hover:bg-[#f0c3bf] text-tone-danger-strong-text text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <XCircle className="w-3.5 h-3.5 text-error" />
                    <span>Override / Downgrade Risk</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-viz-neutral">Select an item from queue to adjudicate.</div>
          )}
        </div>
      </div>
    </div>
  );
}
