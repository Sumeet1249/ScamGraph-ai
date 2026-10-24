"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  CheckSquare,
  Check,
  X,
  HelpCircle,
  Clock,
  Filter,
  RefreshCw,
  GitMerge,
  GitFork,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/ui";

interface ReviewItem {
  review_id: string;
  review_type: string;
  priority_score: number;
  title: string;
  summary: string;
  evidence_context: Record<string, any>;
  candidate_entities: string[];
  candidate_campaign_ids: string[];
  status: string;
  decision?: string;
  reviewer_notes?: string;
  reviewer_id?: string;
  created_at: string;
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<ReviewItem | null>(null);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/console/reviews");
      if (res.ok) {
        const data = await res.json();
        setReviews(data);
        if (data.length > 0 && !selectedReview) {
          setSelectedReview(data[0]);
        }
      }
    } catch (e) {
      console.error("Failed to load review queue:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const handleDecision = async (decision: "CONFIRM" | "REJECT" | "UNCERTAIN" | "DEFER") => {
    if (!selectedReview) return;
    setSubmitting(true);
    try {
      const res = await fetch(`/api/v1/console/reviews/${selectedReview.review_id}/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          reviewer_notes: notes || `Adjudicated as ${decision} by fraud investigator.`,
          reviewer_id: "lead_fraud_analyst",
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        setReviews((prev) =>
          prev.map((r) => (r.review_id === updated.review_id ? updated : r))
        );
        setSelectedReview(updated);
        setNotes("");
      }
    } catch (e) {
      console.error("Failed to submit review decision:", e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Human-in-the-Loop Review Center"
          description="Operational adjudication for candidate campaign merges, supernode disambiguation, and novel variant reviews."
        />
        <Button variant="outline" size="sm" onClick={fetchReviews} disabled={loading}>
          <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
          Refresh Queue
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Queue List */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-ink-muted px-1">
            <span>Pending Decisions ({reviews.filter((r) => r.status === "PENDING").length})</span>
            <span>Sorted by Priority Score</span>
          </div>

          <div className="space-y-2">
            {reviews.map((item) => (
              <button
                key={item.review_id}
                onClick={() => {
                  setSelectedReview(item);
                  setNotes("");
                }}
                className={`w-full p-4 rounded-xl border text-left transition-all ${
                  selectedReview?.review_id === item.review_id
                    ? "border-accent bg-accent/5 shadow-sm"
                    : "border-line bg-surface hover:border-line-strong"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-surface-elevated text-ink-muted">
                    {item.review_type}
                  </span>
                  <div className="flex items-center gap-1 text-[11px] font-mono">
                    <span className="text-ink-dim">Priority:</span>
                    <span className="font-bold text-amber-400">
                      {Math.round(item.priority_score * 100)}%
                    </span>
                  </div>
                </div>

                <div className="text-xs font-semibold text-ink line-clamp-1">{item.title}</div>
                <p className="text-[11px] text-ink-muted line-clamp-2 mt-1">{item.summary}</p>

                <div className="flex items-center justify-between mt-2 pt-2 border-t border-line/60 text-[10px] text-ink-dim font-mono">
                  <span>Status: {item.status}</span>
                  {item.decision && (
                    <span className="font-bold text-accent">{item.decision}</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Selected Item Detail & Adjudication */}
        <div className="lg:col-span-7">
          {selectedReview ? (
            <div className="p-6 rounded-2xl border border-line bg-surface space-y-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-bold uppercase bg-surface-elevated text-accent mb-2">
                    {selectedReview.review_type}
                  </div>
                  <h3 className="text-lg font-bold text-ink">{selectedReview.title}</h3>
                  <p className="text-xs text-ink-muted leading-relaxed mt-1">
                    {selectedReview.summary}
                  </p>
                </div>
              </div>

              {/* Evidence Context Box */}
              <div className="space-y-3">
                <div className="text-xs font-bold text-ink-muted uppercase tracking-wider font-mono">
                  Adjudication Evidence Context
                </div>
                <div className="p-4 rounded-xl border border-line bg-surface-elevated/70 grid grid-cols-2 gap-3 text-xs font-mono">
                  {Object.entries(selectedReview.evidence_context).map(([k, v]) => (
                    <div key={k} className="p-2.5 rounded bg-surface border border-line">
                      <div className="text-ink-dim uppercase text-[10px]">{k.replace(/_/g, " ")}</div>
                      <div className="font-bold text-ink mt-0.5">{String(v)}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Candidate Entities */}
              {selectedReview.candidate_entities.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs font-bold text-ink-muted uppercase tracking-wider font-mono">
                    Candidate Entities Involved
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedReview.candidate_entities.map((ent) => (
                      <span
                        key={ent}
                        className="px-2.5 py-1 rounded-lg bg-surface border border-line text-xs font-mono text-ink"
                      >
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Decision Actions */}
              {selectedReview.status === "PENDING" ? (
                <div className="pt-4 border-t border-line space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-ink block mb-1">
                      Analyst Adjudication Notes
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Enter rationales, verification artifacts, or policy references..."
                      className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink outline-none focus:border-accent"
                      rows={3}
                    />
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <Button
                      variant="primary"
                      onClick={() => handleDecision("CONFIRM")}
                      disabled={submitting}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white"
                    >
                      <Check className="h-4 w-4 mr-1.5" />
                      Confirm Recommendation
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleDecision("REJECT")}
                      disabled={submitting}
                      className="border-red-500/40 text-red-400 hover:bg-red-500/10"
                    >
                      <X className="h-4 w-4 mr-1.5" />
                      Reject (False Match)
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleDecision("UNCERTAIN")}
                      disabled={submitting}
                    >
                      <HelpCircle className="h-4 w-4 mr-1.5" />
                      Needs Evidence
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 space-y-2">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                    <ShieldCheck className="h-4 w-4" />
                    Adjudicated: {selectedReview.decision}
                  </div>
                  <p className="text-xs text-ink-muted font-mono">
                    Notes: {selectedReview.reviewer_notes || "No notes entered"}
                  </p>
                  <div className="text-[10px] text-ink-dim font-mono">
                    Reviewer: {selectedReview.reviewer_id}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center border border-line rounded-2xl bg-surface text-ink-dim text-sm">
              Select a review item to inspect evidence context and record decision.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
