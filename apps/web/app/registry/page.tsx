"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Search,
  PlusCircle,
  FileText,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Lock,
  ExternalLink,
  History,
  Filter,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  Check,
  Ban,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button, Card, Badge, Input } from "@/components/ui";

interface ScreeningMatch {
  identifier_type: string;
  match_type: string;
  matched_fingerprint: string;
  entity_id?: string;
  report_id: string;
  report_status: string;
  category: string;
  reporting_source: string;
  reported_at: string;
  is_disputed: boolean;
  is_revoked: boolean;
  risk_score: number;
  reason_code: string;
  confidence: number;
  warnings?: string[];
  data_freshness?: string;
}

interface ScreeningResult {
  screening_id: string;
  screened_at: string;
  total_queried: number;
  total_hits: number;
  has_confirmed_hit: boolean;
  has_disputed_hit: boolean;
  has_revoked_hit: boolean;
  highest_risk_score: number;
  matches: ScreeningMatch[];
  warnings?: string[];
}

interface RegistryStats {
  total_entities: number;
  total_reports: number;
  confirmed_count: number;
  under_review_count: number;
  disputed_count: number;
  revoked_count: number;
  screening_count: number;
  audit_event_count: number;
  active_key_version: string;
  supported_identifier_types: string[];
  system_status: string;
}

interface AuditEventItem {
  audit_id: string;
  timestamp: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor_org: string;
  actor_user: string;
  previous_state?: string;
  new_state?: string;
  reason?: string;
  integrity_hash: string;
}

export default function SmartRegistryPage() {
  const [activeTab, setActiveTab] = useState<"screen" | "ingest" | "review" | "audit">("screen");

  // Live Statistics
  const [stats, setStats] = useState<RegistryStats | null>(null);

  // Screening state
  const [idType, setIdType] = useState<string>("UPI_VPA");
  const [idValue, setIdValue] = useState<string>("");
  const [screeningLoading, setScreeningLoading] = useState<boolean>(false);
  const [screeningResult, setScreeningResult] = useState<ScreeningResult | null>(null);
  const [screeningError, setScreeningError] = useState<string | null>(null);

  // Ingestion state
  const [reportingOrg, setReportingOrg] = useState<string>("BANK_HDFC_01");
  const [category, setCategory] = useState<string>("MULE_ACCOUNT");
  const [reason, setReason] = useState<string>("");
  const [ingestIdentType, setIngestIdentType] = useState<string>("UPI_VPA");
  const [ingestIdentValue, setIngestIdentValue] = useState<string>("");
  const [evidenceRef, setEvidenceRef] = useState<string>("I4C-COMPLAINT-1930-2026-X99");
  const [confidence, setConfidence] = useState<number>(0.92);
  const [ingestLoading, setIngestLoading] = useState<boolean>(false);
  const [ingestSuccess, setIngestSuccess] = useState<string | null>(null);

  // Review & Dispute state
  const [reports, setReports] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [selectedReport, setSelectedReport] = useState<any | null>(null);
  const [reviewNotes, setReviewNotes] = useState<string>("");
  const [reviewLoading, setReviewLoading] = useState<boolean>(false);
  const [disputeReason, setDisputeReason] = useState<string>("");
  const [disputeLoading, setDisputeLoading] = useState<boolean>(false);
  const [revocationReason, setRevocationReason] = useState<string>("");
  const [revocationLoading, setRevocationLoading] = useState<boolean>(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Audit state
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [auditLoading, setAuditLoading] = useState<boolean>(false);

  useEffect(() => {
    loadStats();
    loadReviewQueue();
  }, [statusFilter]);

  useEffect(() => {
    if (activeTab === "audit") {
      loadAuditEvents();
    }
  }, [activeTab]);

  const loadStats = async () => {
    try {
      const res = await fetch("/api/v1/registry/statistics");
      if (res.ok) {
        const data: RegistryStats = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error("Failed to load registry statistics", e);
    }
  };

  const loadReviewQueue = async () => {
    try {
      const url = statusFilter === "ALL"
        ? "/api/v1/registry/reports"
        : `/api/v1/registry/reports?status=${statusFilter}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (e) {
      console.error("Failed to load registry review queue", e);
    }
  };

  const loadAuditEvents = async () => {
    setAuditLoading(true);
    try {
      const res = await fetch("/api/v1/registry/audit-events?limit=50");
      if (res.ok) {
        const data = await res.json();
        setAuditEvents(data);
      }
    } catch (e) {
      console.error("Failed to load audit events", e);
    } finally {
      setAuditLoading(false);
    }
  };

  const handleScreening = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!idValue.trim()) return;

    setScreeningLoading(true);
    setScreeningError(null);
    setScreeningResult(null);

    try {
      const res = await fetch("/api/v1/registry/screen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          caller_org: "SCAMGRAPH_CONSOLE_OPS",
          identifiers: [
            {
              identifier_type: idType,
              raw_value: idValue.trim(),
            },
          ],
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err);
      }

      const data: ScreeningResult = await res.json();
      setScreeningResult(data);
      loadStats();
    } catch (err: any) {
      setScreeningError(err.message || "Screening failed.");
    } finally {
      setScreeningLoading(false);
    }
  };

  const handleIngestReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestIdentValue.trim() || !reason.trim()) return;

    setIngestLoading(true);
    setIngestSuccess(null);

    try {
      const res = await fetch("/api/v1/registry/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reporting_org: reportingOrg,
          category,
          reason,
          identifiers: [
            {
              identifier_type: ingestIdentType,
              raw_value: ingestIdentValue.trim(),
            },
          ],
          evidence_references: [evidenceRef],
          confidence: Number(confidence),
        }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      setIngestSuccess(`Report ${data.report_id} ingested successfully into Smart Registry.`);
      setReason("");
      setIngestIdentValue("");
      loadReviewQueue();
      loadStats();
    } catch (err: any) {
      alert("Failed to submit report: " + err.message);
    } finally {
      setIngestLoading(false);
    }
  };

  const handleReviewDecision = async (reportId: string, newStatus: string) => {
    if (!reviewNotes.trim()) {
      alert("Please enter review commentary / justification.");
      return;
    }
    setReviewLoading(true);
    try {
      const res = await fetch(`/api/v1/registry/reports/${reportId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          new_status: newStatus,
          reviewer: "Compliance_Lead_Officer_401",
          notes: reviewNotes,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setActionSuccess(`Report ${reportId} status updated to ${newStatus}.`);
      setReviewNotes("");
      setSelectedReport(null);
      loadReviewQueue();
      loadStats();
    } catch (e: any) {
      alert("Review decision failed: " + e.message);
    } finally {
      setReviewLoading(false);
    }
  };

  const handleDisputeSubmit = async (reportId: string) => {
    if (!disputeReason.trim()) return;
    setDisputeLoading(true);
    try {
      const res = await fetch("/api/v1/registry/disputes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report_id: reportId,
          disputing_org: "BANK_ICICI_01",
          reason: disputeReason,
          evidence_documents: ["doc_mandi_verification_oct2026.pdf"],
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setActionSuccess(`Dispute filed for ${reportId}. Status transitioned to DISPUTED.`);
      setDisputeReason("");
      setSelectedReport(null);
      loadReviewQueue();
      loadStats();
    } catch (e: any) {
      alert("Dispute failed: " + e.message);
    } finally {
      setDisputeLoading(false);
    }
  };

  const handleRevocationSubmit = async (reportId: string, reportingOrgOwner: string) => {
    if (!revocationReason.trim()) return;
    setRevocationLoading(true);
    try {
      const res = await fetch("/api/v1/registry/revocations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report_id: reportId,
          authorizing_org: reportingOrgOwner,
          revocation_reason: revocationReason,
          authorized_by: "Compliance_Lead_Officer_401",
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setActionSuccess(`Report ${reportId} revoked. Active screening hits suppressed.`);
      setRevocationReason("");
      setSelectedReport(null);
      loadReviewQueue();
      loadStats();
    } catch (e: any) {
      alert("Revocation failed: " + e.message);
    } finally {
      setRevocationLoading(false);
    }
  };

  // Synthetic demo preset loaders
  const loadSyntheticPreset = (type: string, val: string) => {
    setIdType(type);
    setIdValue(val);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header */}
      <PageHeader
        eyebrow="RBIH DPIP-Inspired Platform"
        title={
          <div className="flex items-center gap-3">
            <span>Smart Suspect Registry</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono font-medium bg-indigo-950/80 text-indigo-300 border border-indigo-800/60">
              Keyed HMAC-SHA-256
            </span>
          </div>
        }
        description="Federated financial fraud intelligence repository inspired by RBI Innovation Hub DPIP. Real-time privacy-preserving identifier screening, multi-source ingestion, formal dispute arbitration, and SHA-256 audit logs."
        actions={
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={() => { loadStats(); loadReviewQueue(); }}>
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
            </Button>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Registry Active
            </span>
          </div>
        }
      />

      {/* High-Level Stat Counters */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-surface-1 border-border">
          <div className="text-xs font-medium text-text-muted uppercase tracking-wider">Confirmed Suspects</div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-1">
            {stats ? stats.confirmed_count : "..."}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Active screening hits
          </div>
        </Card>
        <Card className="p-4 bg-surface-1 border-border">
          <div className="text-xs font-medium text-text-muted uppercase tracking-wider">Privacy Engine</div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
            {stats ? `HMAC-${stats.active_key_version}` : "HMAC-v1"}
          </div>
          <div className="text-[11px] text-text-muted mt-1 flex items-center gap-1">
            <Lock className="w-3 h-3 text-cyan-400" /> Key rotation active
          </div>
        </Card>
        <Card className="p-4 bg-surface-1 border-border">
          <div className="text-xs font-medium text-text-muted uppercase tracking-wider">Disputed Entries</div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
            {stats ? stats.disputed_count : "..."}
          </div>
          <div className="text-[11px] text-amber-400 mt-1 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" /> Risk discounted 50%
          </div>
        </Card>
        <Card className="p-4 bg-surface-1 border-border">
          <div className="text-xs font-medium text-text-muted uppercase tracking-wider">Audit Records</div>
          <div className="text-2xl font-bold font-mono text-indigo-300 mt-1">
            {stats ? stats.audit_event_count : "..."}
          </div>
          <div className="text-[11px] text-indigo-400 mt-1 flex items-center gap-1">
            <History className="w-3 h-3" /> SHA-256 sealed
          </div>
        </Card>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-1">
        <button
          onClick={() => setActiveTab("screen")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
            activeTab === "screen"
              ? "border-brand-primary text-text-primary -mb-px"
              : "border-transparent text-text-muted hover:text-text-primary"
          }`}
        >
          <Search className="w-4 h-4" />
          Real-Time Screening
        </button>
        <button
          onClick={() => setActiveTab("ingest")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
            activeTab === "ingest"
              ? "border-brand-primary text-text-primary -mb-px"
              : "border-transparent text-text-muted hover:text-text-primary"
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          Ingest Suspect Report
        </button>
        <button
          onClick={() => setActiveTab("review")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
            activeTab === "review"
              ? "border-brand-primary text-text-primary -mb-px"
              : "border-transparent text-text-muted hover:text-text-primary"
          }`}
        >
          <FileText className="w-4 h-4" />
          Review Queue & Disputes
        </button>
        <button
          onClick={() => setActiveTab("audit")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold transition border-b-2 ${
            activeTab === "audit"
              ? "border-brand-primary text-text-primary -mb-px"
              : "border-transparent text-text-muted hover:text-text-primary"
          }`}
        >
          <History className="w-4 h-4" />
          Audit Ledger
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 rounded-lg text-emerald-300 text-xs flex items-center justify-between">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* ── TAB 1: Real-Time Screening ───────────────────────────────── */}
      {activeTab === "screen" && (
        <div className="space-y-6">
          <Card className="p-6 bg-surface-1 border-border space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <h2 className="text-base font-semibold text-text-primary">Screen Identifiers Against Smart Registry</h2>
                <p className="text-xs text-text-muted mt-0.5">
                  Pre-transaction screening checks keyed HMAC fingerprints without exposing cleartext PII across network boundaries.
                </p>
              </div>

              {/* Synthetic test presets */}
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[11px] font-mono text-text-muted mr-1">Synthetic Presets:</span>
                <button
                  type="button"
                  onClick={() => loadSyntheticPreset("UPI_VPA", "electricity.desk@oksbi")}
                  className="px-2 py-1 text-[11px] font-mono bg-surface-2 hover:bg-surface-3 rounded border border-border text-cyan-400 transition"
                >
                  ⚡ Utility Phishing
                </button>
                <button
                  type="button"
                  onClick={() => loadSyntheticPreset("PHONE", "+919876543210")}
                  className="px-2 py-1 text-[11px] font-mono bg-surface-2 hover:bg-surface-3 rounded border border-border text-amber-400 transition"
                >
                  📱 Telegram Mule Phone
                </button>
                <button
                  type="button"
                  onClick={() => loadSyntheticPreset("BANK_ACCOUNT", "SBIN0001234:009876543210")}
                  className="px-2 py-1 text-[11px] font-mono bg-surface-2 hover:bg-surface-3 rounded border border-border text-orange-400 transition"
                >
                  🌾 Disputed Merchant
                </button>
                <button
                  type="button"
                  onClick={() => loadSyntheticPreset("UPI_VPA", "clean.salary@icici")}
                  className="px-2 py-1 text-[11px] font-mono bg-surface-2 hover:bg-surface-3 rounded border border-border text-emerald-400 transition"
                >
                  ✅ Clean Payee
                </button>
              </div>
            </div>

            <form onSubmit={handleScreening} className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2">
              <div className="sm:col-span-1">
                <label className="block text-xs font-medium text-text-muted mb-1">Identifier Type</label>
                <select
                  value={idType}
                  onChange={(e) => setIdType(e.target.value)}
                  className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-brand-primary"
                >
                  <option value="UPI_VPA">UPI VPA (Handle)</option>
                  <option value="PHONE">Phone Number</option>
                  <option value="BANK_ACCOUNT">Bank Account (IFSC:ACC)</option>
                  <option value="URL_DOMAIN">URL / Domain</option>
                  <option value="TRANSACTION_REF">Transaction Ref (UTR/RRN)</option>
                  <option value="DEVICE_ID">Device ID / IMEI</option>
                  <option value="EMAIL">Email Address</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-text-muted mb-1">Identifier Value</label>
                <Input
                  value={idValue}
                  onChange={(e) => setIdValue(e.target.value)}
                  placeholder="e.g. electricity.desk@oksbi, +919876543210, SBIN0001234:009876543210"
                />
              </div>

              <div className="sm:col-span-1 flex items-end">
                <Button type="submit" variant="primary" disabled={screeningLoading} className="w-full">
                  {screeningLoading ? "Screening..." : "Screen Now"}
                </Button>
              </div>
            </form>
          </Card>

          {/* Screening Output */}
          {screeningError && (
            <div className="p-4 bg-red-950/50 border border-red-800 rounded-lg text-red-300 text-sm">
              {screeningError}
            </div>
          )}

          {screeningResult && (
            <Card className="p-6 bg-surface-1 border-border space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-text-primary">Screening Result</h3>
                    <span className="text-[11px] font-mono text-text-muted">ID: {screeningResult.screening_id}</span>
                  </div>
                  <p className="text-xs text-text-muted mt-0.5">
                    Screened at {new Date(screeningResult.screened_at).toLocaleTimeString()} UTC
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {screeningResult.total_hits > 0 ? (
                    screeningResult.has_revoked_hit && !screeningResult.has_confirmed_hit ? (
                      <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-gray-900 text-gray-300 border border-gray-700">
                        REVOKED MATCH (SUPPRESSED)
                      </span>
                    ) : screeningResult.has_disputed_hit ? (
                      <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-amber-950 text-amber-300 border border-amber-800">
                        DISPUTED MATCH (REVIEW)
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-red-950 text-red-300 border border-red-800 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        CONFIRMED REGISTRY HIT
                      </span>
                    )
                  ) : (
                    <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      NO REGISTRY HIT (CLEAN)
                    </span>
                  )}
                </div>
              </div>

              {screeningResult.matches.length > 0 ? (
                <div className="space-y-4">
                  {screeningResult.matches.map((m, idx) => (
                    <div key={idx} className="p-4 rounded-lg bg-surface-2 border border-border space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-cyan-400">{m.identifier_type}</span>
                          <span className="text-xs text-text-muted">Report Ref:</span>
                          <span className="font-mono text-xs text-text-primary">{m.report_id}</span>
                          <span className="text-xs text-text-muted">({m.category})</span>
                        </div>
                        <div className="flex items-center gap-2 font-mono text-xs">
                          <span className="text-text-muted">Risk Score:</span>
                          <span className={`font-bold ${m.risk_score >= 0.7 ? "text-red-400" : m.risk_score > 0 ? "text-amber-400" : "text-gray-400"}`}>
                            {m.risk_score.toFixed(2)}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono bg-surface-1 p-2.5 rounded border border-border/60">
                        <div>
                          <span className="text-text-muted block text-[10px] uppercase">Status</span>
                          <span className="text-text-primary font-semibold">{m.report_status}</span>
                        </div>
                        <div>
                          <span className="text-text-muted block text-[10px] uppercase">Reporting Source</span>
                          <span className="text-text-primary">{m.reporting_source}</span>
                        </div>
                        <div>
                          <span className="text-text-muted block text-[10px] uppercase">Match Reason</span>
                          <span className="text-amber-300">{m.reason_code}</span>
                        </div>
                      </div>

                      {m.warnings && m.warnings.length > 0 && (
                        <div className="p-2 bg-amber-950/40 border border-amber-800/60 rounded text-[11px] text-amber-300">
                          {m.warnings.join(" ")}
                        </div>
                      )}

                      <div className="text-[11px] font-mono text-text-muted break-all bg-black/40 p-2 rounded">
                        <span className="text-indigo-400">HMAC Fingerprint: </span>
                        {m.matched_fingerprint}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center space-y-2">
                  <p className="text-sm text-text-muted">
                    No active fraud records or suspect accounts match this identifier fingerprint in the Smart Registry.
                  </p>
                  <p className="text-xs text-text-dim">
                    Query: <span className="font-mono text-text-primary">{idValue}</span>
                  </p>
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* ── TAB 2: Ingest Suspect Report ─────────────────────────────── */}
      {activeTab === "ingest" && (
        <Card className="p-6 bg-surface-1 border-border space-y-5">
          <div>
            <h2 className="text-base font-semibold text-text-primary">Ingest Suspect Identifier or Mule Account</h2>
            <p className="text-xs text-text-muted mt-0.5">
              Submit verified financial fraud intelligence to the centralized registry with provenance records and automatic entity linkage.
            </p>
          </div>

          {ingestSuccess && (
            <div className="p-3 bg-emerald-950/70 border border-emerald-800 rounded-lg text-emerald-300 text-xs">
              {ingestSuccess}
            </div>
          )}

          <form onSubmit={handleIngestReport} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">Reporting Institution</label>
                <Input
                  value={reportingOrg}
                  onChange={(e) => setReportingOrg(e.target.value)}
                  placeholder="e.g. BANK_HDFC_01, PSP_PHONEPE_02"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">Fraud Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-brand-primary"
                >
                  <option value="MULE_ACCOUNT">Mule Account (Layering / Cash-Out)</option>
                  <option value="KYC_SCAM">KYC Expiry / Aadhaar Suspension Impersonation</option>
                  <option value="UTILITY_PHISHING">Electricity / Gas Disconnection Scam</option>
                  <option value="INVESTMENT_FRAUD">High-Yield / Task Scam / Telegram Scheme</option>
                  <option value="DIGITAL_ARREST">CBI / Police Digital Arrest Coercion</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">Identifier Type</label>
                <select
                  value={ingestIdentType}
                  onChange={(e) => setIngestIdentType(e.target.value)}
                  className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-brand-primary"
                >
                  <option value="UPI_VPA">UPI VPA</option>
                  <option value="PHONE">Phone Number</option>
                  <option value="BANK_ACCOUNT">Bank Account (IFSC:ACC)</option>
                  <option value="URL_DOMAIN">URL / Phishing Landing Page</option>
                  <option value="TRANSACTION_REF">Transaction Reference</option>
                  <option value="DEVICE_ID">Device Identifier</option>
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-text-muted mb-1">Identifier Value</label>
                <Input
                  value={ingestIdentValue}
                  onChange={(e) => setIngestIdentValue(e.target.value)}
                  placeholder="e.g. quick.pay99@oksbi"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted mb-1">Factual Justification & Modus Operandi</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                className="w-full bg-surface-2 border border-border rounded-lg p-3 text-sm text-text-primary focus:outline-none focus:border-brand-primary"
                placeholder="Provide factual rationale (e.g. rapid fund pass-through within 120 seconds of incoming victim credit; multi-source fan-in aggregation)."
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">External Evidence Reference</label>
                <Input
                  value={evidenceRef}
                  onChange={(e) => setEvidenceRef(e.target.value)}
                  placeholder="I4C complaint, FIR ID, or internal incident token"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-muted mb-1">
                  Confidence Score: <span className="font-mono text-cyan-400">{confidence}</span>
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="1.0"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  className="w-full accent-brand-primary"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Button type="submit" variant="primary" disabled={ingestLoading}>
                {ingestLoading ? "Submitting..." : "Submit to Smart Registry"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* ── TAB 3: Review Queue & Disputes ──────────────────────────── */}
      {activeTab === "review" && (
        <div className="space-y-6">
          <Card className="p-6 bg-surface-1 border-border space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-text-primary">Registry Review Queue & Governance</h2>
                <p className="text-xs text-text-muted mt-0.5">
                  Audit, dispute, and revoke reported identifiers. Status transitions are immutable and cryptographically sealed.
                </p>
              </div>

              {/* Status Filters */}
              <div className="flex items-center gap-1.5 flex-wrap">
                {["ALL", "CONFIRMED", "DISPUTED", "REVOKED", "REPORTED"].map((st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-2.5 py-1 text-xs font-mono rounded border transition ${
                      statusFilter === st
                        ? "bg-brand-primary/20 border-brand-primary text-text-primary"
                        : "bg-surface-2 border-border text-text-muted hover:text-text-primary"
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            {/* Reports List */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="border-b border-border text-text-muted text-[11px] uppercase">
                    <th className="py-2.5 px-3">Report ID</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Source Org</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {reports.length > 0 ? (
                    reports.map((rep) => (
                      <tr key={rep.report_id} className="hover:bg-surface-2/60 transition">
                        <td className="py-2.5 px-3 font-bold text-cyan-400">{rep.report_id}</td>
                        <td className="py-2.5 px-3 text-text-primary">{rep.category}</td>
                        <td className="py-2.5 px-3 text-text-muted">{rep.reporting_org}</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              rep.status === "CONFIRMED"
                                ? "bg-red-950 text-red-400 border border-red-800"
                                : rep.status === "DISPUTED"
                                ? "bg-amber-950 text-amber-400 border border-amber-800"
                                : rep.status === "REVOKED"
                                ? "bg-gray-800 text-gray-400 border border-gray-700"
                                : "bg-blue-950 text-blue-400 border border-blue-800"
                            }`}
                          >
                            {rep.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-text-primary">{(rep.confidence * 100).toFixed(0)}%</td>
                        <td className="py-2.5 px-3 text-right space-x-2">
                          <button
                            onClick={() => setSelectedReport(rep)}
                            className="px-2.5 py-1 rounded bg-surface-3 hover:bg-surface-2 text-text-primary transition"
                          >
                            Manage
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-text-muted">
                        No reports matching filter criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Action Modal for Selected Report */}
          {selectedReport && (
            <Card className="p-6 bg-surface-2 border-brand-primary/40 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-text-primary">Manage Report: {selectedReport.report_id}</h3>
                  <span className="text-xs text-text-muted">({selectedReport.category})</span>
                </div>
                <button onClick={() => setSelectedReport(null)} className="text-text-muted hover:text-white">✕</button>
              </div>

              <div className="text-xs text-text-secondary space-y-1">
                <div><strong>Reason:</strong> {selectedReport.reason}</div>
                <div><strong>Reporting Source:</strong> {selectedReport.reporting_org}</div>
                <div><strong>Current Status:</strong> {selectedReport.status}</div>
                {selectedReport.entity_id && (
                  <div><strong>Linked Entity ID:</strong> <span className="font-mono text-cyan-400">{selectedReport.entity_id}</span></div>
                )}
              </div>

              {/* Review Disposition Section */}
              <div className="p-4 bg-surface-1 rounded-lg border border-border space-y-3">
                <div className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-brand-primary" /> Compliance Review Disposition
                </div>
                <p className="text-[11px] text-text-muted">
                  Adjudicate report validity to transition between REPORTED, CONFIRMED, or REJECTED.
                </p>
                <textarea
                  rows={2}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Enter compliance adjudication commentary..."
                  className="w-full bg-surface-2 border border-border rounded p-2 text-xs text-text-primary"
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="primary"
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision(selectedReport.report_id, "CONFIRMED")}
                  >
                    Confirm Report
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision(selectedReport.report_id, "UNDER_REVIEW")}
                  >
                    Mark Under Review
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    disabled={reviewLoading}
                    onClick={() => handleReviewDecision(selectedReport.report_id, "REJECTED")}
                  >
                    Reject Report
                  </Button>
                </div>
              </div>

              {/* Dispute and Revocation controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                {/* File Dispute */}
                <div className="p-4 bg-surface-1 rounded-lg border border-border space-y-3">
                  <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">
                    <AlertTriangle className="w-4 h-4" /> File Formal Dispute
                  </div>
                  <p className="text-[11px] text-text-muted">
                    Contest this record with documentary justification. Report transitions to DISPUTED.
                  </p>
                  <textarea
                    rows={2}
                    value={disputeReason}
                    onChange={(e) => setDisputeReason(e.target.value)}
                    placeholder="Enter formal justification for dispute..."
                    className="w-full bg-surface-2 border border-border rounded p-2 text-xs text-text-primary"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={disputeLoading || !disputeReason.trim()}
                    onClick={() => handleDisputeSubmit(selectedReport.report_id)}
                  >
                    {disputeLoading ? "Submitting..." : "Submit Dispute"}
                  </Button>
                </div>

                {/* Authorized Revocation */}
                <div className="p-4 bg-surface-1 rounded-lg border border-border space-y-3">
                  <div className="flex items-center gap-2 text-red-400 font-semibold text-xs">
                    <RotateCcw className="w-4 h-4" /> Authorized Revocation
                  </div>
                  <p className="text-[11px] text-text-muted">
                    Withdraw this report upon customer remediation. Active screening hits will be suppressed.
                  </p>
                  <textarea
                    rows={2}
                    value={revocationReason}
                    onChange={(e) => setRevocationReason(e.target.value)}
                    placeholder="Enter factual grounds for revocation..."
                    className="w-full bg-surface-2 border border-border rounded p-2 text-xs text-text-primary"
                  />
                  <Button
                    size="sm"
                    variant="danger"
                    disabled={revocationLoading || !revocationReason.trim()}
                    onClick={() => handleRevocationSubmit(selectedReport.report_id, selectedReport.reporting_org)}
                  >
                    {revocationLoading ? "Revoking..." : "Authorize Revocation"}
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* ── TAB 4: Audit Ledger ──────────────────────────────────────── */}
      {activeTab === "audit" && (
        <Card className="p-6 bg-surface-1 border-border space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-text-primary">Immutable Cryptographic Audit Ledger</h2>
              <p className="text-xs text-text-muted mt-0.5">
                Every state transition, screening query, dispute, and revocation is sealed with an HMAC / SHA-256 integrity token.
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={loadAuditEvents} disabled={auditLoading}>
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh Log
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-border text-text-muted text-[11px] uppercase">
                  <th className="py-2.5 px-3">Audit ID</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity ID</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Transition</th>
                  <th className="py-2.5 px-3">SHA-256 Seal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {auditEvents.length > 0 ? (
                  auditEvents.map((ev) => (
                    <tr key={ev.audit_id} className="hover:bg-surface-2/60 transition">
                      <td className="py-2.5 px-3 text-cyan-400 font-bold">{ev.audit_id}</td>
                      <td className="py-2.5 px-3 text-text-muted">
                        {new Date(ev.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-2.5 px-3 text-text-primary font-semibold">{ev.action}</td>
                      <td className="py-2.5 px-3 text-indigo-300">{ev.entity_id}</td>
                      <td className="py-2.5 px-3 text-text-muted">{ev.actor_org}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-text-muted">{ev.previous_state || "—"}</span>
                        {" → "}
                        <span className="text-text-primary font-bold">{ev.new_state}</span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-[10px] text-text-dim truncate max-w-[140px]">
                        {ev.integrity_hash}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-text-muted">
                      {auditLoading ? "Loading audit events..." : "No audit events found."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
