"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  RotateCw,
  Search,
  Filter,
  Download,
  CheckCheck,
  UserPlus,
  ShieldAlert,
  Flame,
  ArrowUpRight,
  TrendingUp,
  Clock,
  Layers,
  ChevronRight,
  ExternalLink,
  Lock,
  Timer,
  CheckCircle2,
  SlidersHorizontal,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

export interface AlertRecord {
  id: string;
  type: string;
  target_name: string;
  target_id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  trigger_metric: string;
  baseline: string;
  delta_label: string;
  first_seen: string;
  last_seen: string;
  status: "NEW" | "ACKNOWLEDGED" | "INVESTIGATING" | "RESOLVED";
  assignee: string;
  blast_radius_banks: string[];
  blast_radius_states: string[];
  quantum_at_risk: number;
}

const CANONICAL_ALERTS: AlertRecord[] = [
  {
    id: "ALT-9041",
    type: "Velocity Surge",
    target_name: "State Electricity Instant Cutoff (#UTL-8490)",
    target_id: "camp-power-urgent",
    severity: "CRITICAL",
    confidence: 98,
    trigger_metric: "6.2 cases/hr",
    baseline: "0.4 baseline",
    delta_label: "+1,450% (15.5x)",
    first_seen: "2026-10-24T20:30:00Z",
    last_seen: "2026-10-24T20:54:00Z",
    status: "INVESTIGATING",
    assignee: "Raghav M.",
    blast_radius_banks: ["Axis Bank Ltd", "HDFC Bank", "ICICI Bank", "SBI"],
    blast_radius_states: ["Karnataka", "West Bengal", "Maharashtra"],
    quantum_at_risk: 18450000,
  },
  {
    id: "ALT-9039",
    type: "Value Inversion",
    target_name: "#SG-84920 (Citizen Mandate Drain)",
    target_id: "SG-2026-84920",
    severity: "CRITICAL",
    confidence: 96,
    trigger_metric: "Param ₹11,450",
    baseline: "UI string ₹10",
    delta_label: "Tamper flag",
    first_seen: "2026-10-24T19:46:00Z",
    last_seen: "2026-10-24T20:46:00Z",
    status: "ACKNOWLEDGED",
    assignee: "Unassigned",
    blast_radius_banks: ["Axis Bank Ltd", "NPCI UPI Switch"],
    blast_radius_states: ["Karnataka"],
    quantum_at_risk: 11450,
  },
  {
    id: "ALT-9037",
    type: "Cross-BTS Hop",
    target_name: "Threat GSM Series (+91 98******10)",
    target_id: "camp-power-urgent",
    severity: "HIGH",
    confidence: 92,
    trigger_metric: "West Bengal SIM",
    baseline: "Karnataka towers",
    delta_label: "Roaming Anomaly",
    first_seen: "2026-10-24T18:50:00Z",
    last_seen: "2026-10-24T20:14:00Z",
    status: "INVESTIGATING",
    assignee: "Pooja K.",
    blast_radius_banks: ["Airtel Payments Bank"],
    blast_radius_states: ["West Bengal", "Karnataka"],
    quantum_at_risk: 4200000,
  },
  {
    id: "ALT-9034",
    type: "Bulletproof ASN",
    target_name: "bescom-bill-renew.in",
    target_id: "ENT-DOM-001",
    severity: "HIGH",
    confidence: 89,
    trigger_metric: "Offshore Host",
    baseline: "ASN 185.220.101.5",
    delta_label: "Bulletproof Proxy",
    first_seen: "2026-10-24T17:20:00Z",
    last_seen: "2026-10-24T19:48:00Z",
    status: "NEW",
    assignee: "Unassigned",
    blast_radius_banks: ["State Discom Gateway"],
    blast_radius_states: ["Pan-India"],
    quantum_at_risk: 2500000,
  },
  {
    id: "ALT-9028",
    type: "Mule Fan-out",
    target_name: "util-power-84920@okaxis",
    target_id: "ENT-UPI-AXIS-84920",
    severity: "CRITICAL",
    confidence: 97,
    trigger_metric: "6 outbound IMPS splits",
    baseline: "< 180s dispersal",
    delta_label: "Laundering Chain",
    first_seen: "2026-10-24T16:45:00Z",
    last_seen: "2026-10-24T19:00:00Z",
    status: "INVESTIGATING",
    assignee: "Raghav M.",
    blast_radius_banks: ["Axis Bank Ltd", "Yes Bank", "Paytm Payments Bank"],
    blast_radius_states: ["Karnataka", "Jharkhand"],
    quantum_at_risk: 148200,
  },
  {
    id: "ALT-9019",
    type: "Low Model Conf",
    target_name: "Audio recording (Voice impersonation)",
    target_id: "SG-2026-84915",
    severity: "MEDIUM",
    confidence: 68,
    trigger_metric: "Transcription Ambiguity",
    baseline: "STT 68%",
    delta_label: "Needs Human Review",
    first_seen: "2026-10-24T14:30:00Z",
    last_seen: "2026-10-24T17:45:00Z",
    status: "NEW",
    assignee: "Unassigned",
    blast_radius_banks: ["WBSEDCL Consumer Rail"],
    blast_radius_states: ["West Bengal"],
    quantum_at_risk: 9800,
  },
];

export default function AlertCenterPage() {
  const [alerts, setAlerts] = useState<AlertRecord[]>(CANONICAL_ALERTS);
  const [selectedId, setSelectedId] = useState<string>("ALT-9041");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredAlerts = useMemo(() => {
    return alerts.filter((a) => {
      if (severityFilter !== "ALL" && a.severity !== severityFilter) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        a.id.toLowerCase().includes(q) ||
        a.type.toLowerCase().includes(q) ||
        a.target_name.toLowerCase().includes(q) ||
        a.trigger_metric.toLowerCase().includes(q)
      );
    });
  }, [alerts, severityFilter, searchQuery]);

  const selectedAlert = useMemo(() => {
    return alerts.find((a) => a.id === selectedId) || alerts[0];
  }, [alerts, selectedId]);

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* 1. Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A10 Alert Center</span>
          <span>•</span>
          <span>SSE Telemetry: Connected</span>
        </div>
      </div>

      {/* 2. Top Header & Summary Metric Strips */}
      <div className="bg-surface border-b border-border-divider px-4 lg:px-8 py-4 shrink-0 space-y-4">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-error text-white flex items-center justify-center font-bold">
                <ShieldAlert className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Alert Center</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
                §7 A10
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-xs font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse" />
                {alerts.length} active alerts
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1 max-w-3xl">
              Deduplicated real-time intelligence alerts across campaigns, sudden velocity spikes, autonomous model divergence, and high-urgency financial extractions.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button className="h-8 px-3 rounded bg-viz-primary text-white text-xs font-semibold flex items-center gap-1.5 hover:bg-[#00483f] transition-colors shadow-xs">
              <CheckCheck className="w-3.5 h-3.5" />
              <span>Mark Acknowledged</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <UserPlus className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Assign Analyst</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <Download className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* 5-Column Situational Metric Strips */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-1">
          <div className="p-3 bg-surface-subtle rounded border border-border-divider flex flex-col justify-between">
            <span className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider">Total Active</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-2xl font-bold font-mono text-viz-text">42</span>
              <span className="text-[11px] text-viz-neutral">Deduped 314</span>
            </div>
          </div>
          <div className="p-3 bg-tone-danger-bg/50 rounded border border-error/20 flex flex-col justify-between">
            <span className="text-[10px] uppercase font-bold text-tone-danger-text tracking-wider">Outbreak Candidates</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-2xl font-bold font-mono text-error">04</span>
              <span className="text-[11px] font-bold text-error">State 7 Octagon</span>
            </div>
          </div>
          <div className="p-3 bg-surface-subtle rounded border border-border-divider flex flex-col justify-between">
            <span className="text-[10px] uppercase font-bold text-viz-warning tracking-wider">Drainage Spikes</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-2xl font-bold font-mono text-viz-text">12</span>
              <span className="text-[11px] text-viz-warning font-semibold">Velocity &gt; 3.0x</span>
            </div>
          </div>
          <div className="p-3 bg-surface-subtle rounded border border-border-divider flex flex-col justify-between">
            <span className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider">Model Disagreement</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-2xl font-bold font-mono text-viz-text">07</span>
              <span className="text-[11px] text-viz-neutral">&lt;70% Conf</span>
            </div>
          </div>
          <div className="p-3 bg-[#0B6256]/[0.08] rounded border border-viz-primary/20 flex flex-col justify-between">
            <span className="text-[10px] uppercase font-bold text-viz-primary tracking-wider">Under Active Review</span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-2xl font-bold font-mono text-viz-primary">19</span>
              <span className="text-[11px] text-viz-primary font-medium">5 Analysts Active</span>
            </div>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-border-divider text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-viz-neutral" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter trigger metric, campaign..."
                className="w-full h-7 pl-8 pr-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
              />
            </div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="h-7 px-2 bg-surface border border-border-divider rounded text-xs text-viz-text font-medium focus:outline-none"
            >
              <option value="ALL">Severity: All</option>
              <option value="CRITICAL">Critical (Octagon)</option>
              <option value="HIGH">High (Shield)</option>
              <option value="MEDIUM">Medium (Triangle)</option>
            </select>
          </div>
          <div className="flex items-center gap-2 text-viz-neutral text-[11px]">
            <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
            <span>SSE Feed Active (14ms lag)</span>
          </div>
        </div>
      </div>

      {/* 3. Main Alert Table + Docked 380px Detail Drawer */}
      <div className="flex flex-1 w-full overflow-hidden min-h-[calc(100vh-14rem)]">
        {/* Table View */}
        <div className="flex-1 overflow-x-auto bg-surface" data-density="compact">
          <table className="w-full text-left border-collapse select-text min-w-[900px]">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="w-9 px-3 text-center">
                  <input type="checkbox" className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer" />
                </th>
                <th className="px-3 font-semibold">Alert ID &amp; Type</th>
                <th className="px-3 font-semibold">Correlated Campaign / Target</th>
                <th className="px-3 font-semibold">Severity</th>
                <th className="px-3 font-semibold">Conf.</th>
                <th className="px-3 font-semibold">Trigger Metric &amp; Baseline</th>
                <th className="px-3 font-semibold">Last Seen</th>
                <th className="px-3 font-semibold">Lifecycle</th>
                <th className="px-3 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-xs text-viz-text">
              {filteredAlerts.map((a) => {
                const isSelected = selectedId === a.id;

                return (
                  <tr
                    key={a.id}
                    onClick={() => setSelectedId(a.id)}
                    className={`h-9 transition-colors cursor-pointer group ${
                      isSelected
                        ? "bg-[#0B6256]/[0.08] border-l-[3px] border-l-viz-primary font-medium"
                        : "hover:bg-surface-container-low border-l-[3px] border-l-transparent"
                    }`}
                  >
                    <td className="w-9 px-3 text-center">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => setSelectedId(a.id)}
                        className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer"
                      />
                    </td>
                    <td className="px-3 font-medium">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono font-bold text-viz-text">#{a.id}</span>
                        <span className="px-1.5 py-0.2 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text font-mono text-[10px] uppercase font-bold">
                          {a.type}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 text-viz-primary font-semibold truncate max-w-[200px]">
                      {a.target_name}
                    </td>
                    <td className="px-3">
                      {a.severity === "CRITICAL" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text text-[11px] font-bold">
                          <Timer className="w-3 h-3 text-error" />
                          Critical · Octagon
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-[11px] font-semibold">
                          <ShieldAlert className="w-3 h-3 text-error" />
                          High · Shield
                        </span>
                      )}
                    </td>
                    <td className="px-3 font-mono font-bold">{a.confidence}%</td>
                    <td className="px-3">
                      <div className="flex items-center gap-1.5 text-[11px]">
                        <span className="font-semibold text-error">{a.trigger_metric}</span>
                        <span className="text-viz-neutral">vs {a.baseline}</span>
                        <span className="px-1 rounded bg-tone-danger-bg text-tone-danger-text font-bold text-[10px]">
                          {a.delta_label}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 text-[11px] text-viz-neutral whitespace-nowrap">
                      {formatDateTime(a.last_seen)}
                    </td>
                    <td className="px-3 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface-subtle text-viz-neutral text-[11px] font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-viz-primary" />
                        {a.status} ({a.assignee})
                      </span>
                    </td>
                    <td className="px-3 text-right whitespace-nowrap">
                      <button className="text-viz-primary hover:underline text-[12px] font-semibold inline-flex items-center gap-0.5">
                        Open alert
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Right-Hand Docked Detail Drawer (380px) */}
        <aside className="w-80 xl:w-[380px] shrink-0 bg-surface-subtle border-l border-border-divider flex flex-col justify-between overflow-y-auto">
          {selectedAlert ? (
            <div className="flex flex-col">
              <div className="px-4 py-3 bg-surface border-b border-border-divider flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text flex items-center justify-center font-bold">
                    <ShieldAlert className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-viz-neutral font-bold tracking-wider block">
                      Focused Alert Node
                    </span>
                    <h2 className="text-sm font-bold text-viz-text leading-tight">#{selectedAlert.id}</h2>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text font-bold text-xs">
                  {selectedAlert.severity}
                </span>
              </div>

              {/* Blast Radius Box */}
              <div className="p-4 bg-surface border-b border-border-divider space-y-2">
                <h3 className="text-sm font-bold text-viz-text">{selectedAlert.target_name}</h3>
                <div className="p-3 rounded bg-surface-subtle border border-border-divider space-y-2 text-xs">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral block">Blast Radius Analysis</span>
                  <div className="flex justify-between items-center">
                    <span className="text-viz-neutral">Quantum at Risk:</span>
                    <span className="font-mono font-bold text-error">
                      ₹{selectedAlert.quantum_at_risk.toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div>
                    <span className="text-viz-neutral block mb-1">Affected Institutions:</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedAlert.blast_radius_banks.map((b) => (
                        <span key={b} className="px-1.5 py-0.5 rounded bg-surface border border-border-divider text-[10px] font-medium text-viz-text">
                          {b}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Deck */}
              <div className="p-4 mt-auto border-t border-border-divider bg-surface space-y-2">
                <div className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider">
                  Automated Escalation Workflow
                </div>
                <button className="w-full h-8 px-3 rounded bg-error hover:bg-[#851313] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Dispatch Section 91 CrPC Restraint Notice</span>
                </button>
                <Link
                  href={`/campaigns/${selectedAlert.target_id}`}
                  className="w-full h-8 px-3 rounded bg-surface-subtle hover:bg-surface-container-high border border-border-control text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span>Open Correlated Campaign Workspace</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-viz-neutral">Select an alert to inspect blast radius.</div>
          )}
        </aside>
      </div>
    </div>
  );
}
