"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Search,
  Copy,
  Eye,
  EyeOff,
  Building,
  Landmark,
  Share2,
  Lock,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Gavel,
  Layers,
  FileText,
  TrendingUp,
  ArrowUpRight,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

interface EntityData {
  id: string;
  type: string;
  identifier: string;
  psp: string;
  ifsc: string;
  branch: string;
  holder_mask: string;
  holder_real?: string;
  risk_state: string;
  risk_score: number;
  confidence: number;
  status_rule: string;
  first_observed: string;
  last_observed: string;
  corroborated_cases: number;
  syndicate_id: string;
  syndicate_name: string;
  avg_ticket: number;
  total_ingress: number;
  egress_velocity: string;
  lien_placed: number;
  cfr_ref: string;
  direct_edges: {
    type: string;
    identifier: string;
    label: string;
    status: string;
  }[];
}

const CANONICAL_ENTITY: EntityData = {
  id: "ENT-UPI-AXIS-84920",
  type: "UPI Virtual Payment Address (VPA)",
  identifier: "util-power-84920@okaxis",
  psp: "Axis Bank Ltd",
  ifsc: "UTIB0000849",
  branch: "Koramangala 4th Block, Bengaluru, KA",
  holder_mask: "**H** D*****",
  holder_real: "ROHIT DASGUPTA",
  risk_state: "High Risk Mule Destination",
  risk_score: 98,
  confidence: 98.4,
  status_rule: "Correlated Mule Destination in Ongoing Syndicate Investigation (Zero-PII Rule §4.11)",
  first_observed: "2026-10-21T09:15:00Z",
  last_observed: "2026-10-24T20:46:00Z",
  corroborated_cases: 14,
  syndicate_id: "#UTL-8490",
  syndicate_name: "State Electricity Instant Cutoff Syndicate",
  avg_ticket: 10850,
  total_ingress: 148200,
  egress_velocity: "18 mins to P2P USDT Counterparty",
  lien_placed: 24350,
  cfr_ref: "CFC-2026-94810",
  direct_edges: [
    { type: "Telephony Anchor", identifier: "+91 98******10", label: "14 Co-occurrences", status: "Primary SIM Pool" },
    { type: "Domain Infrastructure", identifier: "bescom-bill-renew.in", label: "14 Referrals", status: "DNS Sinkholed" },
    { type: "Exit Counterparty", identifier: "crypto-p2p-gateway@binance", label: "3 IMPS Sweeps", status: "High Velocity" },
  ],
};

export default function EntityDetailPage({ params }: { params: { id: string } }) {
  const [entity, setEntity] = useState<EntityData>(CANONICAL_ENTITY);
  const [isRevealed, setIsRevealed] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(entity.identifier);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full space-y-4 text-viz-text">
      <div className="space-y-4 w-full">
        {/* Breadcrumb Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border-divider font-mono font-semibold uppercase text-viz-neutral">
              Entity Dossier
            </span>
            <span className="text-viz-neutral">/</span>
            <Link href="/entities" className="text-viz-neutral hover:text-viz-primary font-medium">
              Entities
            </Link>
            <span className="text-viz-neutral">/</span>
            <span className="font-mono font-bold text-viz-text">{params.id || entity.id}</span>
            <span className="ml-2 px-2 py-0.5 rounded-full bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold inline-flex items-center gap-1">
              <ShieldAlert className="w-3.5 h-3.5 text-error" />
              State 6: High Risk Mule Node
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-2.5 py-1 rounded bg-surface border border-border-divider text-viz-neutral flex items-center gap-1.5 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
              <span>Real-Time Intelligence: Active</span>
            </span>
          </div>
        </div>

        {/* Primary Entity Header Card */}
        <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
            <div className="flex items-start gap-3.5 min-w-0">
              <div className="w-12 h-12 rounded-xl bg-[#0B6256]/10 text-viz-primary flex items-center justify-center shrink-0">
                <Landmark className="w-6 h-6" />
              </div>
              <div className="flex flex-col min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs uppercase tracking-wider font-semibold text-viz-neutral">
                    {entity.type}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-[11px] text-viz-neutral">
                    PSP: {entity.psp}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-[#E7EDF4] text-[#1A446C] text-[11px] font-medium">
                    §4.11 Zero-PII Enforced
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 mt-1">
                  <h1 className="text-2xl font-bold font-mono tracking-tight text-viz-text">
                    {isRevealed ? entity.identifier : entity.identifier}
                  </h1>
                  <button
                    onClick={handleCopy}
                    className="p-1 rounded hover:bg-surface-subtle text-viz-neutral hover:text-viz-text transition-colors"
                    title="Copy identifier"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  {copied && <span className="text-xs text-viz-primary font-medium">Copied!</span>}

                  <button
                    onClick={() => setIsRevealed(!isRevealed)}
                    className="px-2 h-7 rounded bg-surface-subtle hover:bg-surface-container-high text-xs font-medium text-viz-text flex items-center gap-1 border border-border-divider transition-colors"
                  >
                    {isRevealed ? <EyeOff className="w-3.5 h-3.5 text-viz-neutral" /> : <Eye className="w-3.5 h-3.5 text-viz-neutral" />}
                    <span>{isRevealed ? "Hide PII" : "Audit Reveal"}</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-viz-neutral">
                  <span className="flex items-center gap-1 text-viz-text font-medium">
                    <Building className="w-3.5 h-3.5 text-viz-primary" />
                    {entity.branch}
                  </span>
                  <span>•</span>
                  <span>IFSC: {entity.ifsc}</span>
                  <span>•</span>
                  <span>
                    Holder: <strong className="text-viz-text font-mono">{isRevealed ? entity.holder_real : entity.holder_mask}</strong>
                  </span>
                </div>

                <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded bg-surface-subtle border border-border-divider text-xs">
                  <span className="w-2 h-2 rounded-full bg-viz-warning shrink-0" />
                  <span className="font-semibold text-[#4A3306]">Observed Classification:</span>
                  <span className="text-viz-neutral">{entity.status_rule}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex flex-wrap lg:flex-col xl:flex-row items-stretch lg:items-end gap-2 shrink-0">
              <Link
                href="/investigate"
                className="px-3 h-8 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs"
              >
                <Search className="w-3.5 h-3.5" />
                <span>Investigate (A07)</span>
              </Link>
              <Link
                href="/graph"
                className="px-3 h-8 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
              >
                <Share2 className="w-3.5 h-3.5 text-viz-neutral" />
                <span>Graph Topology (A08)</span>
              </Link>
              <button className="px-3 h-8 rounded bg-tone-danger-bg hover:bg-tone-danger-strong-bg text-tone-danger-text text-xs font-bold flex items-center justify-center gap-1.5 transition-colors">
                <Gavel className="w-3.5 h-3.5 text-error" />
                <span>Section 102 CrPC Lien Notice</span>
              </button>
            </div>
          </div>

          {/* Observation Metric Chips */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 pt-3 border-t border-border-divider text-xs">
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">First Observed</span>
              <span className="font-semibold text-viz-text mt-0.5 block">{formatDateTime(entity.first_observed)}</span>
              <span className="text-[10px] text-viz-neutral">Via BESCOM Smish Pool</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Last Activity</span>
              <span className="font-semibold text-error mt-0.5 block">{formatDateTime(entity.last_observed)}</span>
              <span className="text-[10px] text-error font-medium">Active Egress Window</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Corroborated Incidents</span>
              <span className="font-semibold text-viz-text mt-0.5 block">{entity.corroborated_cases} Cases Validated</span>
              <span className="text-[10px] text-viz-primary">100% telemetry match</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Syndicate Cluster</span>
              <Link href={`/campaigns/camp-power-urgent`} className="font-semibold text-viz-primary mt-0.5 block hover:underline">
                {entity.syndicate_id}
              </Link>
              <span className="text-[10px] text-viz-neutral truncate block">{entity.syndicate_name}</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Active Lien Status</span>
              <span className="font-semibold font-mono text-viz-primary mt-0.5 block">
                ₹{entity.lien_placed.toLocaleString("en-IN")}
              </span>
              <span className="text-[10px] text-viz-neutral">Served to Axis Bank</span>
            </div>
          </div>
        </div>

        {/* 7 Canonical Entity Tabs */}
        <div className="bg-surface rounded-lg p-1 border border-border-divider flex items-center gap-1 overflow-x-auto text-xs">
          {[
            { key: "overview", label: "1. Overview" },
            { key: "timeline", label: "2. Forensic Timeline (18)" },
            { key: "relationships", label: "3. Direct Relationships (12)" },
            { key: "campaigns", label: "4. Correlated Campaigns (2)" },
            { key: "evidence", label: "5. Evidence & Banking Receipts (14)" },
            { key: "resolution", label: "6. Resolution & Merge History" },
            { key: "disputes", label: "7. Disputes & Legal Notices" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 rounded-md font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.key
                  ? "bg-viz-primary text-white font-semibold shadow-xs"
                  : "text-viz-neutral hover:text-viz-text hover:bg-surface-subtle"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dual Analytical Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column (7 cols): Behavioral Pattern & Financial Rail */}
          <div className="lg:col-span-7 space-y-4">
            {/* Pattern Card */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-sm font-bold text-viz-text">Behavioral Pattern &amp; Role Vector</h2>
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono font-medium">
                  Model: TTP-FLOW-v4
                </span>
              </div>

              <div className="p-3 rounded bg-surface-subtle border border-border-divider flex items-start gap-3">
                <div className="w-8 h-8 rounded bg-tone-danger-bg text-tone-danger-text flex items-center justify-center shrink-0 font-bold">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-viz-text">Hypothesis: Primary Cash-Out / Mule Aggregator</span>
                    <span className="font-bold text-error font-mono">Confidence: {entity.confidence}%</span>
                  </div>
                  <p className="text-xs text-viz-neutral mt-1 leading-relaxed">
                    Node exhibits classic high-velocity funneling topology. Rapid ₹10 decoy micro-authorizations trigger secondary consumer mandates, siphoning rounded ticket values into secondary layer accounts within minutes.
                  </p>
                </div>
              </div>

              {/* Metrics Strip */}
              <div className="grid grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral block">Average Ingress Ticket</span>
                  <div className="text-base font-bold font-mono text-viz-text mt-0.5">₹{entity.avg_ticket.toLocaleString("en-IN")}</div>
                  <span className="text-[10px] text-viz-neutral">Range: ₹9,800 – ₹14,200</span>
                </div>
                <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral block">Total Corroborated Ingress</span>
                  <div className="text-base font-bold font-mono text-viz-primary mt-0.5">₹{entity.total_ingress.toLocaleString("en-IN")}</div>
                  <span className="text-[10px] text-viz-neutral">14 settled consumer debits</span>
                </div>
                <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral block">Egress Velocity</span>
                  <div className="text-base font-bold font-mono text-error mt-0.5">18 mins</div>
                  <span className="text-[10px] text-error font-medium">To P2P USDT Counterparty</span>
                </div>
              </div>
            </div>

            {/* Financial Rail & Account Artifacts */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <Landmark className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-sm font-bold text-viz-text">Financial Rail &amp; Account Artifacts</h2>
                </div>
                <span className="px-2 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold text-xs">
                  Notice Form 1930 Active
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded bg-surface-subtle border border-border-divider space-y-2">
                  <span className="text-[11px] font-bold uppercase text-viz-neutral block">Bank Node Specifications</span>
                  <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                    <span className="text-viz-neutral">Acquiring PSP:</span>
                    <span className="font-semibold text-viz-text">{entity.psp}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                    <span className="text-viz-neutral">Target VPA:</span>
                    <code className="font-mono text-viz-text font-semibold">{entity.identifier}</code>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="text-viz-neutral">IFSC &amp; Branch:</span>
                    <span className="font-medium text-viz-text">{entity.ifsc}</span>
                  </div>
                </div>

                <div className="p-3 rounded bg-surface-subtle border border-border-divider space-y-2">
                  <span className="text-[11px] font-bold uppercase text-viz-neutral block">Regulatory Restraint &amp; Status</span>
                  <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                    <span className="text-viz-neutral">Freezing Order:</span>
                    <span className="font-bold text-error">Served (14m ago)</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                    <span className="text-viz-neutral">Lien Placed:</span>
                    <span className="font-mono font-bold text-viz-primary">₹{entity.lien_placed.toLocaleString("en-IN")}</span>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="text-viz-neutral">CFCFRMS Ref:</span>
                    <code className="font-mono text-viz-primary font-bold">{entity.cfr_ref}</code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (5 cols): 1-Hop Relationship Network & Direct Links */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <Share2 className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-sm font-bold text-viz-text">1-Hop Relationship Network</h2>
                </div>
                <span className="text-xs px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-medium">
                  {entity.direct_edges.length} Bound Edges
                </span>
              </div>

              <div className="space-y-2 text-xs">
                {entity.direct_edges.map((edge, idx) => (
                  <div key={idx} className="p-3 rounded bg-surface-subtle border border-border-divider flex items-center justify-between">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-viz-neutral block">{edge.type}</span>
                      <code className="text-xs font-mono font-bold text-viz-text mt-0.5 block">{edge.identifier}</code>
                      <span className="text-[11px] text-viz-neutral">{edge.label}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-[11px] font-bold">
                      {edge.status}
                    </span>
                  </div>
                ))}
              </div>

              <Link
                href="/graph"
                className="w-full h-8 px-3 rounded bg-surface-subtle hover:bg-surface-container-high border border-border-control text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>Launch Interactive Graph Canvas</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
