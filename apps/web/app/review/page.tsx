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
  X,
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
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [decisionNotes, setDecisionNotes] = useState<string>("");

  const selectedReview = reviews.find((r) => r.id === selectedId) || null;

  const handleDecision = (action: "APPROVE" | "OVERRIDE") => {
    if (!selectedId) return;
    setReviews((prev) =>
      prev.map((r) =>
        r.id === selectedId ? { ...r, status: action === "APPROVE" ? "APPROVED" : "OVERRIDDEN" } : r
      )
    );
    setDecisionNotes("");
    setSelectedId(null);
  };

  return (
    <div className="w-full space-y-4 text-viz-text">
      {/* 1. Top Header Block */}
      <div className="bg-surface border border-border-divider rounded-lg p-5 shadow-xs shrink-0 space-y-3">
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

      {/* 2. Full Width Review Items Grid / List */}
      <div className="w-full bg-surface border border-border-divider rounded-lg p-5 min-h-[calc(100vh-14rem)] space-y-3">
        <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-viz-neutral pb-2 border-b border-border-divider">
          <span>Adjudication Queue ({reviews.length} items)</span>
          <span className="text-[11px] font-normal normal-case text-viz-neutral">Click any item to inspect evidence and adjudicate</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {reviews.map((r) => {
            const isSelected = selectedId === r.id;
            return (
              <div
                key={r.id}
                onClick={() => setSelectedId(r.id)}
                className={`p-4 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? "bg-[#0B6256]/[0.08] border-viz-primary shadow-xs ring-1 ring-viz-primary"
                    : "bg-surface-subtle hover:bg-surface border-border-divider hover:border-viz-primary/40 shadow-xs"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-viz-text">#{r.id}</span>
                      <span className="px-1.5 py-0.5 rounded bg-surface border border-border-divider text-[10px] uppercase font-semibold text-viz-neutral">
                        {r.item_type}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        r.status === "PENDING"
                          ? "bg-tone-warning-bg text-tone-warning-text"
                          : r.status === "APPROVED"
                          ? "bg-tone-info-bg text-tone-info-text"
                          : "bg-surface text-viz-neutral border border-border-divider"
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-viz-text mt-2">{r.title}</h3>
                  <p className="text-[11px] text-viz-neutral mt-1 leading-relaxed line-clamp-2">
                    {r.disagreement_reason}
                  </p>
                </div>

                <div className="mt-3 pt-3 border-t border-border-divider/50 flex items-center justify-between text-[11px]">
                  <span className="text-viz-neutral">
                    Model: <strong className="text-viz-text">{r.model_recommendation}</strong> ({r.model_score}%)
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedId(r.id);
                    }}
                    className="px-2.5 py-1 bg-viz-primary hover:bg-[#00483f] text-white text-[11px] font-semibold rounded transition-colors inline-flex items-center gap-1"
                  >
                    <span>Adjudicate</span>
                    <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Centered Modal Popup with Backdrop Blur */}
      {selectedReview && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-md transition-opacity duration-200"
          onClick={() => setSelectedId(null)}
        >
          <div
            className="bg-surface border border-border-divider rounded-xl shadow-2xl max-w-xl w-full max-h-[90vh] overflow-y-auto flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="px-5 py-3.5 bg-surface-subtle border-b border-border-divider flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded bg-viz-primary/10 text-viz-primary flex items-center justify-center font-bold">
                  <FileCheck className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-[10px] uppercase text-viz-neutral font-bold tracking-wider block">
                    Evidence Inspector &amp; Adjudication
                  </span>
                  <h2 className="text-base font-mono font-bold text-viz-text leading-tight">{selectedReview.id} ({selectedReview.target_ref})</h2>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  selectedReview.status === "PENDING"
                    ? "bg-tone-warning-bg text-tone-warning-text"
                    : selectedReview.status === "APPROVED"
                    ? "bg-tone-info-bg text-tone-info-text"
                    : "bg-surface text-viz-neutral border border-border-divider"
                }`}>
                  {selectedReview.status}
                </span>
                <button
                  onClick={() => setSelectedId(null)}
                  className="p-1 rounded hover:bg-surface-subtle text-viz-neutral hover:text-viz-text transition-colors"
                  aria-label="Close modal"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-5 space-y-4 text-xs">
              <div>
                <h3 className="text-sm font-bold text-viz-text leading-tight">{selectedReview.title}</h3>
                <div className="flex items-center gap-2 text-[11px] text-viz-neutral mt-1">
                  <span>Submitted by: <strong className="text-viz-text">{selectedReview.submitted_by}</strong></span>
                  <span>•</span>
                  <span>Timestamp: <strong className="text-viz-text">{formatDateTime(selectedReview.submitted_at)}</strong></span>
                </div>
              </div>

              {/* Disagreement Rationale Box */}
              <div className="p-3.5 rounded bg-surface-subtle border border-border-divider space-y-1.5 text-xs">
                <span className="font-bold text-viz-text block uppercase tracking-wider text-[10px] text-viz-neutral">
                  Disagreement / Appeal Rationale:
                </span>
                <p className="leading-relaxed text-viz-text">{selectedReview.disagreement_reason}</p>
                <div className="pt-1 flex items-center gap-2 text-[11px] text-viz-neutral">
                  <span>Model Recommendation: <strong className="text-viz-primary">{selectedReview.model_recommendation}</strong></span>
                  <span>•</span>
                  <span>Model Score: <strong className="text-viz-text">{selectedReview.model_score}%</strong></span>
                </div>
              </div>

              {/* Forensic Artifacts */}
              <div className="space-y-1.5 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-viz-neutral block">
                  Forensic Artifacts
                </span>
                {selectedReview.evidence_snippets.map((snip, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-surface-subtle border border-border-divider font-mono text-[11px] text-viz-text">
                    {snip}
                  </div>
                ))}
              </div>

              {/* Adjudication Notes Box */}
              <div className="space-y-1.5 text-xs">
                <label className="text-[10px] font-bold uppercase tracking-wider text-viz-neutral block">
                  Analyst Adjudication Notes (§65B statutory rationale)
                </label>
                <textarea
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  placeholder="Enter statutory rationale for confirming or overriding model assessment..."
                  className="w-full h-20 p-2.5 bg-surface-subtle border border-border-divider rounded-lg text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
                />
              </div>
            </div>

            {/* Modal Footer / Action Buttons */}
            <div className="p-4 border-t border-border-divider bg-surface-subtle space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleDecision("APPROVE")}
                  className="h-8 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Confirm Model Assessment</span>
                </button>
                <button
                  onClick={() => handleDecision("OVERRIDE")}
                  className="h-8 px-3 rounded bg-tone-danger-strong-bg hover:bg-[#f0c3bf] text-tone-danger-strong-text text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <XCircle className="w-3.5 h-3.5 text-error" />
                  <span>Override / Downgrade Risk</span>
                </button>
              </div>
              <button
                onClick={() => setSelectedId(null)}
                className="w-full h-7 rounded bg-surface border border-border-control hover:bg-surface-container-high text-xs font-medium text-viz-neutral hover:text-viz-text transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
