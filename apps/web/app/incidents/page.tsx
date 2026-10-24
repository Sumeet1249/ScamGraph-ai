"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  RotateCw,
  Search,
  Filter,
  Download,
  PlusCircle,
  Clock,
  Shield,
  ShieldAlert,
  ChevronRight,
  ExternalLink,
  Layers,
  Sparkles,
  FileText,
  User,
  Timer,
  CheckCircle2,
  Lock,
  X,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";
import { CANONICAL_INCIDENTS } from "@/lib/demo/incidents-db";

export interface IncidentRecord {
  id: string;
  ref: string;
  title: string;
  assessment: "HIGH_RISK" | "ACT_NOW" | "SUSPICIOUS" | "BE_CAREFUL" | "SAFE";
  confidence: number; // 0-100%
  artifacts_count: number;
  urgency: "CRIT_15M" | "CRIT_45M" | "HIGH_2H" | "HIGH_4H" | "MED";
  cluster_name: string;
  cluster_id?: string;
  modality: string;
  timestamp: string;
  state: "ACTIVE" | "TRIAGE_QUEUE" | "ESCALATED" | "RESOLVED";
  assignee: string;
  victim_loss?: number;
  target_vpa?: string;
  target_phone?: string;
}

const SEED_INCIDENTS: IncidentRecord[] = [
  {
    id: "SG-2026-84920",
    ref: "#SG-84920",
    title: "BESCOM Immediate Disconnection & Mandate",
    assessment: "HIGH_RISK",
    confidence: 98,
    artifacts_count: 4,
    urgency: "CRIT_45M",
    cluster_name: "#UTL-8490 State Electricity",
    cluster_id: "camp-power-urgent",
    modality: "WhatsApp + PhonePe UPI",
    timestamp: "2026-10-24T20:46:00Z",
    state: "ACTIVE",
    assignee: "Raghav M.",
    victim_loss: 11450,
    target_vpa: "util-power-84920@okaxis",
    target_phone: "+91 98765 43210",
  },
  {
    id: "SG-2026-84919",
    ref: "#SG-84919",
    title: "CBI Spoof & Digital Arrest Demand",
    assessment: "ACT_NOW",
    confidence: 94,
    artifacts_count: 3,
    urgency: "CRIT_15M",
    cluster_name: "#DAR-3041 CBI/Police Ring",
    cluster_id: "camp-digital-arrest",
    modality: "WhatsApp Video Call",
    timestamp: "2026-10-24T20:30:00Z",
    state: "ESCALATED",
    assignee: "Nodal Cell",
    victim_loss: 450000,
    target_vpa: "rbi.clearance@sbi",
    target_phone: "+91 22 4920 1829",
  },
  {
    id: "SG-2026-84918",
    ref: "#SG-84918",
    title: "Part-time YouTube Rating Reversal",
    assessment: "SUSPICIOUS",
    confidence: 88,
    artifacts_count: 2,
    urgency: "HIGH_2H",
    cluster_name: "#TSK-1092 Telegram Task",
    cluster_id: "camp-work-from-home",
    modality: "Telegram + UPI P2P",
    timestamp: "2026-10-24T20:14:00Z",
    state: "TRIAGE_QUEUE",
    assignee: "Unassigned",
    victim_loss: 28000,
    target_vpa: "merchant992@icici",
  },
  {
    id: "SG-2026-84917",
    ref: "#SG-84917",
    title: "PM Kisan 16th Installment APK",
    assessment: "HIGH_RISK",
    confidence: 92,
    artifacts_count: 5,
    urgency: "HIGH_4H",
    cluster_name: "#APK-5512 Malicious APK",
    cluster_id: "camp-apk-delivery",
    modality: "SMS + HTTP Dropper",
    timestamp: "2026-10-24T19:48:00Z",
    state: "ACTIVE",
    assignee: "Pooja K.",
    victim_loss: 8500,
    target_vpa: "kisan.yojna@pnb",
  },
  {
    id: "SG-2026-84916",
    ref: "#SG-84916",
    title: "SBI Credit Card Reward Lure",
    assessment: "BE_CAREFUL",
    confidence: 76,
    artifacts_count: 1,
    urgency: "MED",
    cluster_name: "Unlinked / Orphan (64%)",
    modality: "SMS Shortcode",
    timestamp: "2026-10-24T19:13:00Z",
    state: "TRIAGE_QUEUE",
    assignee: "Unassigned",
    victim_loss: 0,
    target_vpa: "reward-points@axis",
  },
  {
    id: "SG-2026-84915",
    ref: "#SG-84915",
    title: "WBSEDCL Overdue Bill Call",
    assessment: "HIGH_RISK",
    confidence: 96,
    artifacts_count: 3,
    urgency: "CRIT_45M",
    cluster_name: "#UTL-8490 State Electricity",
    cluster_id: "camp-power-urgent",
    modality: "Voice GSM + PhonePe",
    timestamp: "2026-10-24T18:53:00Z",
    state: "ACTIVE",
    assignee: "Raghav M.",
    victim_loss: 9800,
    target_vpa: "util-power-84920@okaxis",
  },
];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentRecord[]>(SEED_INCIDENTS);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterSegment, setFilterSegment] = useState<"ALL" | "SURGE" | "URGENT" | "ACTIVE" | "UNASSIGNED">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastSync, setLastSync] = useState<Date>(new Date());

  const fetchIncidents = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/incidents");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          // Read local investigations
          let localRecent: any[] = [];
          try {
            const raw = localStorage.getItem("recent_investigations");
            if (raw) localRecent = JSON.parse(raw);
          } catch (e) {}

          const dynamicItems: IncidentRecord[] = [
            ...localRecent.map((item: any, idx: number) => ({
              id: item.id || `SG-LOCAL-${idx}`,
              ref: `#${(item.id || "").slice(-8).toUpperCase() || "SG-LOC"}`,
              title: item.pattern || "Multi-Signal Investigation",
              assessment: (item.risk_score >= 85 ? "HIGH_RISK" : item.risk_score >= 70 ? "ACT_NOW" : item.risk_score >= 40 ? "SUSPICIOUS" : "SAFE") as any,
              confidence: item.confidence === "HIGH" ? 95 : item.confidence === "MEDIUM" ? 78 : 50,
              artifacts_count: (item.signals && item.signals.length) || 2,
              urgency: (item.risk_score >= 80 ? "CRIT_15M" : "HIGH_2H") as any,
              cluster_name: item.pattern || "Dynamic Intake",
              modality: "Web Intake / API",
              timestamp: item.last_activity || new Date().toISOString(),
              state: "ACTIVE" as any,
              assignee: "Automated Dispatch",
              victim_loss: item.risk_score * 250,
            })),
            ...SEED_INCIDENTS,
          ];

          // Deduplicate by ID
          const seen = new Set<string>();
          const deduped: IncidentRecord[] = [];
          for (const inc of dynamicItems) {
            if (!seen.has(inc.id)) {
              seen.add(inc.id);
              deduped.push(inc);
            }
          }
          setIncidents(deduped);
        }
      }
      setLastSync(new Date());
    } catch (err) {
      console.warn("Using offline canonical incidents:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 6000);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  const filteredIncidents = useMemo(() => {
    return incidents.filter((inc) => {
      if (filterSegment === "URGENT" && inc.urgency !== "CRIT_15M" && inc.urgency !== "CRIT_45M") return false;
      if (filterSegment === "ACTIVE" && inc.state !== "ACTIVE") return false;
      if (filterSegment === "UNASSIGNED" && inc.assignee !== "Unassigned") return false;
      if (filterSegment === "SURGE" && !inc.cluster_id) return false;

      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        inc.ref.toLowerCase().includes(q) ||
        inc.title.toLowerCase().includes(q) ||
        inc.cluster_name.toLowerCase().includes(q) ||
        inc.modality.toLowerCase().includes(q) ||
        (inc.target_vpa && inc.target_vpa.toLowerCase().includes(q))
      );
    });
  }, [incidents, filterSegment, searchQuery]);

  const selectedIncident = useMemo(() => {
    return selectedId ? incidents.find((inc) => inc.id === selectedId) || null : null;
  }, [incidents, selectedId]);

  return (
    <div className="w-full space-y-4 text-viz-text">
      {/* 1. Workspace Header Block */}
      <div className="bg-surface border border-border-divider rounded-lg p-5 shadow-xs shrink-0">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Incidents Telemetry</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold tracking-wider border border-border-divider">
                Stream A05
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-xs font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse" />
                {filteredIncidents.length} queue items
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1 max-w-3xl">
              Unified real-time feed of citizen fraud disclosures, automated honey-traps, banking rail telemetry, and triage-ready correlate events across jurisdictions.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={fetchIncidents}
              disabled={isLoading}
              className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors"
            >
              <RotateCw className={`w-3.5 h-3.5 text-viz-primary ${isLoading ? "animate-spin" : ""}`} />
              <span>Refresh Queue</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <Download className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Export Telemetry</span>
            </button>
            <Link
              href="/investigate"
              className="h-8 px-3.5 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Ingest Manual Report</span>
            </Link>
          </div>
        </div>

        {/* Quick Segment Filter Pills */}
        <div className="mt-3.5 flex items-center justify-between gap-4 overflow-x-auto pb-1">
          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={() => setFilterSegment("ALL")}
              className={`h-7 px-3 rounded-full text-xs font-medium transition-colors ${
                filterSegment === "ALL" ? "bg-viz-primary text-white" : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              All incidents ({incidents.length})
            </button>
            <button
              onClick={() => setFilterSegment("URGENT")}
              className={`h-7 px-3 rounded-full text-xs font-medium flex items-center gap-1.5 transition-colors ${
                filterSegment === "URGENT" ? "bg-viz-primary text-white" : "bg-tone-danger-bg text-tone-danger-text"
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse" />
              <span>High Urgency (&lt;1h window)</span>
            </button>
            <button
              onClick={() => setFilterSegment("SURGE")}
              className={`h-7 px-3 rounded-full text-xs font-medium transition-colors ${
                filterSegment === "SURGE" ? "bg-viz-primary text-white" : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              Surge &amp; Outbreak Cluster
            </button>
            <button
              onClick={() => setFilterSegment("ACTIVE")}
              className={`h-7 px-3 rounded-full text-xs font-medium transition-colors ${
                filterSegment === "ACTIVE" ? "bg-viz-primary text-white" : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              Under Active Review
            </button>
            <button
              onClick={() => setFilterSegment("UNASSIGNED")}
              className={`h-7 px-3 rounded-full text-xs font-medium transition-colors ${
                filterSegment === "UNASSIGNED" ? "bg-viz-primary text-white" : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              Unassigned Triage
            </button>
          </div>

          <div className="relative w-64 shrink-0 hidden md:block">
            <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-viz-neutral" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reference, VPA, cluster..."
              className="w-full h-7 pl-8 pr-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
            />
          </div>
        </div>
      </div>

      {/* 2. Main Incident Table: Full width */}
      <div className="w-full bg-surface rounded-xl border border-border-divider overflow-hidden shadow-xs" data-density="compact">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left border-collapse select-text">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="w-9 px-3 text-center">
                  <input type="checkbox" className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer" />
                </th>
                <th className="px-3 font-semibold">Incident Ref &amp; Signature</th>
                <th className="px-3 font-semibold">Assessment</th>
                <th className="px-3 font-semibold">Confidence</th>
                <th className="px-3 font-semibold">Urgency</th>
                <th className="px-3 font-semibold">Cluster &amp; Modality</th>
                <th className="px-3 font-semibold">Loss Quantum</th>
                <th className="px-3 font-semibold">Timestamp (IST)</th>
                <th className="px-3 font-semibold">State &amp; Assignee</th>
                <th className="px-3 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-xs text-viz-text">
              {filteredIncidents.map((inc) => {
                const isSelected = selectedId === inc.id;

                return (
                  <tr
                    key={inc.id}
                    onClick={() => setSelectedId(inc.id)}
                    className={`h-9 transition-colors cursor-pointer group ${
                      isSelected
                        ? "bg-[#0B6256]/[0.08] font-medium"
                        : "hover:bg-surface-subtle"
                    }`}
                  >
                    <td className="w-9 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => setSelectedId(isSelected ? null : inc.id)}
                        className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer"
                      />
                    </td>
                    <td className="px-3">
                      <div className="flex items-center gap-1.5 truncate max-w-[280px]">
                        <span className="font-mono font-semibold text-viz-primary">{inc.ref}</span>
                        <span className="text-viz-neutral">·</span>
                        <span className="font-semibold text-viz-text truncate">{inc.title}</span>
                      </div>
                    </td>
                    <td className="px-3 whitespace-nowrap">
                      {inc.assessment === "HIGH_RISK" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-[11px] font-bold">
                          <ShieldAlert className="w-3 h-3 text-error" />
                          High risk
                        </span>
                      ) : inc.assessment === "ACT_NOW" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text text-[11px] font-bold">
                          <Timer className="w-3 h-3 text-error" />
                          Act now
                        </span>
                      ) : inc.assessment === "SUSPICIOUS" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#F1ECE3] text-[#614714] text-[11px] font-semibold">
                          <AlertTriangle className="w-3 h-3 text-viz-warning" />
                          Suspicious
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface-subtle text-viz-neutral text-[11px]">
                          Be careful
                        </span>
                      )}
                    </td>
                    <td className="px-3 whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <span className="font-mono font-semibold text-viz-text">{inc.confidence}%</span>
                        <span className="text-viz-neutral text-[10px] bg-surface-subtle px-1 rounded">
                          ({inc.artifacts_count} Artf)
                        </span>
                      </div>
                    </td>
                    <td className="px-3 whitespace-nowrap">
                      {inc.urgency === "CRIT_15M" ? (
                        <span className="inline-flex items-center gap-1 text-tone-danger-strong-text font-bold bg-tone-danger-strong-bg px-1.5 py-0.5 rounded text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse" />
                          Crit &lt;15m
                        </span>
                      ) : inc.urgency === "CRIT_45M" ? (
                        <span className="inline-flex items-center gap-1 text-tone-danger-text font-bold bg-tone-danger-bg px-1.5 py-0.5 rounded text-[11px]">
                          Crit &lt;45m
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-viz-neutral font-medium bg-surface-subtle px-1.5 py-0.5 rounded text-[11px]">
                          Standard
                        </span>
                      )}
                    </td>
                    <td className="px-3 max-w-[200px]">
                      <div className="flex flex-col leading-tight truncate">
                        <span className="text-viz-primary font-medium truncate">{inc.cluster_name}</span>
                        <span className="text-viz-neutral text-[11px] truncate">{inc.modality}</span>
                      </div>
                    </td>
                    <td className="px-3 whitespace-nowrap font-mono text-[11px] font-semibold text-error">
                      {inc.victim_loss ? `₹${inc.victim_loss.toLocaleString("en-IN")}` : "—"}
                    </td>
                    <td className="px-3 whitespace-nowrap text-[11px] text-viz-neutral">
                      {formatDateTime(inc.timestamp)}
                    </td>
                    <td className="px-3 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 text-tone-info-text bg-tone-info-bg px-1.5 py-0.5 rounded text-[11px] font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-viz-info" />
                        {inc.assignee}
                      </span>
                    </td>
                    <td className="px-3 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => setSelectedId(inc.id)}
                        className="h-6 px-2.5 bg-viz-primary hover:bg-[#00483f] text-white rounded text-[11px] font-semibold inline-flex items-center transition-colors shadow-xs"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Centered Modal Popup with blurred backdrop */}
      {selectedIncident && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
          {/* Blurred Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-md transition-opacity"
            onClick={() => setSelectedId(null)}
            aria-hidden="true"
          />

          {/* Centered Modal Card */}
          <div
            role="dialog"
            aria-modal="true"
            className="relative w-full max-w-2xl bg-surface rounded-2xl shadow-2xl border border-border-divider overflow-hidden z-10 max-h-[90vh] flex flex-col animate-in zoom-in-95 duration-200"
          >
            {/* Modal Header */}
            <div className="px-6 py-4 bg-surface-subtle border-b border-border-divider flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-tone-danger-bg text-tone-danger-text flex items-center justify-center font-bold">
                  <ShieldAlert className="w-5 h-5 text-error" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-sm text-viz-primary">{selectedIncident.ref}</span>
                    <span className="text-[10px] uppercase bg-surface border border-border-divider px-1.5 py-0.5 rounded text-viz-neutral font-semibold">
                      Incident Triage
                    </span>
                  </div>
                  <h2 className="text-base font-bold text-viz-text leading-tight">{selectedIncident.title}</h2>
                </div>
              </div>
              <button
                onClick={() => setSelectedId(null)}
                className="h-8 w-8 rounded-lg hover:bg-surface-container-high flex items-center justify-center text-viz-neutral hover:text-viz-text transition-colors"
                aria-label="Close modal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              {/* Assessment & Metrics Strip */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-surface border border-border-divider">
                  <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Assessment</span>
                  <div className="mt-1">
                    {selectedIncident.assessment === "HIGH_RISK" ? (
                      <span className="inline-flex items-center gap-1 text-tone-danger-text font-bold">
                        <ShieldAlert className="w-3.5 h-3.5 text-error" />
                        High Risk
                      </span>
                    ) : selectedIncident.assessment === "ACT_NOW" ? (
                      <span className="inline-flex items-center gap-1 text-tone-danger-strong-text font-bold">
                        <Timer className="w-3.5 h-3.5 text-error" />
                        Act Now
                      </span>
                    ) : (
                      <span className="font-bold text-viz-text">{selectedIncident.assessment}</span>
                    )}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-surface border border-border-divider">
                  <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Confidence</span>
                  <div className="mt-1 font-mono font-bold text-sm text-viz-text">
                    {selectedIncident.confidence}% <span className="text-[10px] font-normal text-viz-neutral">({selectedIncident.artifacts_count} Artf)</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-surface border border-border-divider">
                  <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Loss Quantum</span>
                  <div className="mt-1 font-mono font-bold text-sm text-error">
                    {selectedIncident.victim_loss ? `₹${selectedIncident.victim_loss.toLocaleString("en-IN")}` : "—"}
                  </div>
                </div>
              </div>

              {/* Identified Fraud Vectors */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-viz-neutral block">
                  Identified Fraud Vectors &amp; Telemetry
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {selectedIncident.target_vpa && (
                    <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                      <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Beneficiary VPA</span>
                      <code className="text-xs font-mono font-bold text-viz-text select-all">{selectedIncident.target_vpa}</code>
                    </div>
                  )}
                  {selectedIncident.target_phone && (
                    <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                      <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Caller Telephony</span>
                      <code className="text-xs font-mono font-bold text-viz-text select-all">{selectedIncident.target_phone}</code>
                    </div>
                  )}
                  <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                    <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Syndicate Attribution</span>
                    <span className="text-xs font-semibold text-viz-primary">{selectedIncident.cluster_name}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                    <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Vector / Modality</span>
                    <span className="text-xs font-medium text-viz-text">{selectedIncident.modality}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div className="px-6 py-4 bg-surface-subtle border-t border-border-divider flex items-center justify-between gap-3">
              <button
                onClick={() => setSelectedId(null)}
                className="h-9 px-4 rounded-lg bg-surface border border-border-divider text-viz-text hover:bg-surface-container-high text-xs font-semibold transition-colors"
              >
                Dismiss
              </button>
              <div className="flex items-center gap-2">
                <Link
                  href={`/investigate?q=${encodeURIComponent(selectedIncident.target_vpa || selectedIncident.ref)}`}
                  className="h-9 px-3.5 rounded-lg bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors"
                >
                  <Search className="w-3.5 h-3.5 text-viz-neutral" />
                  <span>Cross-Correlate</span>
                </Link>
                <Link
                  href={`/incidents/${selectedIncident.id}`}
                  className="h-9 px-4 bg-viz-primary hover:bg-[#00483f] text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-xs"
                >
                  <span>Full Dossier</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
