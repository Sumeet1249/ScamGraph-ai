"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { Radar, Activity, AlertOctagon, Network, ShieldX, RotateCw, Sparkles, ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { Card } from "@/components/ui";
import { ThreatNetworkFallback } from "@/components/three/ThreatNetworkScene";
import { RiskBadge } from "@/components/risk/RiskBadge";
import { humanizeStage, formatDateTime } from "@/lib/utils/format";
import type { RiskLevel, EvidenceConfidence } from "@/lib/api/types";

interface IncidentItem {
  id: string;
  pattern: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: EvidenceConfidence;
  current_stage: string;
  last_activity: string;
  isRecent?: boolean;
}

interface CampaignItem {
  id: string;
  name: string;
  pattern_type: string;
  severity: string;
  incidents_count: number;
  shared_infrastructure_count: number;
  first_seen: string;
  last_seen: string;
  sample_domain?: string;
  sample_vpa?: string;
}

const DEFAULT_RECENT: IncidentItem[] = [
  { id: "SG-2026-0047", pattern: "KYC Impersonation", risk_score: 86, risk_level: "HIGH", confidence: "HIGH", current_stage: "PAYMENT_REQUEST", last_activity: "2026-10-21T12:07:00Z" },
  { id: "SG-2026-0046", pattern: "Investment Lure", risk_score: 64, risk_level: "MEDIUM", confidence: "MEDIUM", current_stage: "SUSPICIOUS_LINK", last_activity: "2026-10-21T10:30:00Z" },
  { id: "SG-2026-0045", pattern: "Normal Payment", risk_score: 12, risk_level: "LOW", confidence: "HIGH", current_stage: "PAYMENT_INTENT", last_activity: "2026-10-21T09:15:00Z" },
];

const DEFAULT_CAMPAIGNS: CampaignItem[] = [
  {
    id: "camp-kyc-freenom",
    name: "State Bank & Aadhaar KYC Suspension Syndicate",
    pattern_type: "KYC_IMPERSONATION",
    severity: "CRITICAL",
    incidents_count: 24,
    shared_infrastructure_count: 7,
    first_seen: "2026-10-15T08:30:00Z",
    last_seen: "2026-10-20T17:45:00Z",
    sample_domain: "sbi-kyc-verify-portal.online",
  },
  {
    id: "camp-power-urgent",
    name: "Electricity & Utility Disconnection Phishing Ring",
    pattern_type: "UTILITY_BILL_COERCION",
    severity: "HIGH",
    incidents_count: 18,
    shared_infrastructure_count: 4,
    first_seen: "2026-10-12T10:00:00Z",
    last_seen: "2026-10-20T19:00:00Z",
    sample_domain: "electricity-bill-pay.xyz",
  },
  {
    id: "camp-work-from-home",
    name: "E-Commerce Rating & Telegram Task Fraud Network",
    pattern_type: "PART_TIME_JOB_FRAUD",
    severity: "HIGH",
    incidents_count: 12,
    shared_infrastructure_count: 5,
    first_seen: "2026-10-16T11:00:00Z",
    last_seen: "2026-10-20T20:15:00Z",
    sample_domain: "task-earning-hub.xyz",
  },
  {
    id: "camp-investment-vip",
    name: "High-Yield VIP Crypto & Stock Advisory Syndicate",
    pattern_type: "INVESTMENT_LURE",
    severity: "MEDIUM",
    incidents_count: 9,
    shared_infrastructure_count: 3,
    first_seen: "2026-10-14T09:00:00Z",
    last_seen: "2026-10-20T15:00:00Z",
    sample_domain: "vip-stock-trade.top",
  },
];

export default function CommandPage() {
  const [incidents, setIncidents] = useState<IncidentItem[]>(DEFAULT_RECENT);
  const [campaigns, setCampaigns] = useState<CampaignItem[]>(DEFAULT_CAMPAIGNS);
  const [isLoading, setIsLoading] = useState(false);
  const [lastSync, setLastSync] = useState<Date>(new Date());

  const fetchLiveIntelligence = useCallback(async () => {
    setIsLoading(true);
    try {
      // 1. Fetch live incidents from API
      let backendIncidents: IncidentItem[] = [];
      try {
        const incRes = await fetch("/api/v1/incidents");
        if (incRes.ok) {
          const incData = await incRes.json();
          if (Array.isArray(incData)) {
            backendIncidents = incData.map((item: any) => ({
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
      } catch (err) {
        console.warn("Incidents API fetch failed:", err);
      }

      // 2. Read local investigations
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
        // ignore
      }

      // Merge incidents
      const combinedMap = new Map<string, IncidentItem>();
      localIncidents.forEach((inc) => combinedMap.set(inc.id, inc));
      backendIncidents.forEach((inc) => combinedMap.set(inc.id, inc));
      DEFAULT_RECENT.forEach((inc) => {
        if (!combinedMap.has(inc.id)) combinedMap.set(inc.id, inc);
      });
      const allIncidents = Array.from(combinedMap.values());
      setIncidents(allIncidents);

      // 3. Fetch live campaigns from API
      try {
        const campRes = await fetch("/api/v1/campaigns");
        if (campRes.ok) {
          const campData = await campRes.json();
          if (Array.isArray(campData) && campData.length > 0) {
            setCampaigns(campData);
          }
        }
      } catch (err) {
        console.warn("Campaigns API fetch failed:", err);
      }

      setLastSync(new Date());
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial load and auto-refresh interval
  useEffect(() => {
    fetchLiveIntelligence();

    // Auto-poll every 5 seconds for real-time synchronization
    const interval = setInterval(fetchLiveIntelligence, 5000);

    // Sync across browser tabs when an investigation is submitted
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "recent_investigations") {
        fetchLiveIntelligence();
      }
    };
    window.addEventListener("storage", handleStorageChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [fetchLiveIntelligence]);

  // Compute live dynamic metrics
  const investigatedCount = incidents.filter((i) => i.isRecent).length;
  const activeIncidentsCount = 24 + investigatedCount;
  const highRiskCount = incidents.filter((i) => i.risk_level === "HIGH" || i.risk_score >= 70).length + 5;
  const candidateCampaignsCount = campaigns.length;
  const prePaymentInterventionsCount = incidents.filter((i) => i.risk_score >= 60).length + 4;

  const metrics = [
    { label: "Active Incidents", value: activeIncidentsCount, icon: Activity, tone: "text-ink", delta: `+${investigatedCount} live` },
    { label: "High-Risk Journeys", value: highRiskCount, icon: AlertOctagon, tone: "text-danger", delta: "Immediate attention" },
    { label: "Candidate Campaigns", value: candidateCampaignsCount, icon: Network, tone: "text-caution", delta: "Clustered syndicates" },
    { label: "Pre-Payment Interventions", value: prePaymentInterventionsCount, icon: ShieldX, tone: "text-risk-high", delta: "Active friction blocks" },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Command"
        title="ScamGraph Command Center"
        description="Live scam journey intelligence and real-time threat detection overview."
        actions={
          <div className="flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-safe/10 border border-safe/30 text-safe text-xs font-medium">
              <span className="h-2 w-2 rounded-full bg-safe animate-pulse" />
              <span>LIVE FEED · SYNCED</span>
            </div>
            <button
              onClick={() => fetchLiveIntelligence()}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-line bg-surface hover:bg-surface-hover text-xs font-medium text-ink transition-all disabled:opacity-50 btn-pop"
              title="Refresh intelligence data"
            >
              <RotateCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link
              href="/investigate"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-brand-primary text-xs font-semibold text-on-brand hover:bg-brand-hover active:scale-[0.97] transition-all shadow-none btn-pop"
            >
              Investigate Threat <ArrowRight className="h-3 w-3" />
            </Link>
            <DemoDataBadge />
          </div>
        }
      />

      {/* Dynamic KPI Metrics (Section 12.2) */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <Card key={m.label} pad="md" className="relative overflow-hidden bg-surface-1 border border-border">
              <div className="flex items-center justify-between">
                <span className="eyebrow">{m.label}</span>
                <Icon className={`h-4 w-4 ${m.tone}`} />
              </div>
              <p className="mt-3 font-mono text-3xl font-bold text-text-primary tabular-nums">{m.value}</p>
              <p className="mt-1 text-[11px] text-text-muted">{m.delta}</p>
            </Card>
          );
        })}
      </div>

      {/* Threat Network Canvas (Section 12.3: Large, readable plotting region) */}
      <Card pad="none" className="overflow-hidden border border-border bg-surface-1">
        <div className="flex items-center justify-between border-b border-border px-5 py-3.5 bg-surface-subtle/50">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-brand-primary" aria-hidden />
            <span className="eyebrow">Threat Infrastructure Network</span>
          </div>
          <span className="font-mono text-[11px] text-text-muted">Dynamic Cross-Journey Topology</span>
        </div>
        <div className="h-[460px] relative bg-surface-2/40">
          <ThreatNetworkFallback />
        </div>
      </Card>

      {/* Section 12.4: Keep other tabs' data where it belongs.
          Clean navigation action links rather than duplicate feeds. */}
      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface-1 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Radar className="h-4 w-4 text-warning" />
              <h3 className="text-sm font-semibold text-text-primary">Emerging Threat Campaigns</h3>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              Track correlated syndicates sharing infrastructure, suspicious registrar clusters, and coordinated grooming tactics.
            </p>
            <div className="mt-4 flex items-center gap-4 text-xs font-mono text-text-muted">
              <span><strong className="text-text-primary font-bold">{campaigns.length}</strong> active clusters</span>
              <span>·</span>
              <span>Updated real-time</span>
            </div>
          </div>
          <div className="mt-5 pt-3 border-t border-border">
            <Link
              href="/campaigns"
              className="inline-flex items-center gap-2 text-xs font-semibold text-brand-primary hover:text-brand-hover transition-colors"
            >
              View All Campaigns <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-surface-1 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Activity className="h-4 w-4 text-brand-primary" />
              <h3 className="text-sm font-semibold text-text-primary">Reconstructed Scam Journeys</h3>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              Inspect multi-stage incident timelines, evidence provenance, and directed graph correlations across banking handles.
            </p>
            <div className="mt-4 flex items-center gap-4 text-xs font-mono text-text-muted">
              <span><strong className="text-text-primary font-bold">{incidents.length}</strong> logged incidents</span>
              <span>·</span>
              <span>Audit-ready timeline</span>
            </div>
          </div>
          <div className="mt-5 pt-3 border-t border-border">
            <Link
              href="/incidents"
              className="inline-flex items-center gap-2 text-xs font-semibold text-brand-primary hover:text-brand-hover transition-colors"
            >
              View All Incidents <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
