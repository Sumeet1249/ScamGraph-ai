"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  AlertOctagon,
  ArrowLeft,
  Calendar,
  CheckCircle2,
  ChevronRight,
  Clock,
  Compass,
  CreditCard,
  ExternalLink,
  Flame,
  Globe,
  Layers,
  Phone,
  RefreshCw,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { Card, Badge } from "@/components/ui";
import dynamic from "next/dynamic";
import { formatDateTime } from "@/lib/utils/format";
import { demoGraph } from "@/lib/demo/fixtures";

const EvidenceGraph = dynamic(
  () => import("@/components/graph/EvidenceGraph").then((m) => m.EvidenceGraph),
  { ssr: false, loading: () => <div className="h-64 flex items-center justify-center text-xs text-text-muted">Loading network canvas...</div> }
);

interface CampaignDetail {
  campaign_id: string;
  schema_version: string;
  title: string;
  scam_family: string;
  family_confidence: number;
  lifecycle_state: string;
  velocity_state: string;
  review_state: string;
  first_seen: string;
  last_seen: string;
  incident_count: number;
  strongly_related_incident_count: number;
  unique_entity_count: number;
  unique_payment_identifier_count: number;
  unique_domain_count: number;
  unique_phone_count: number;
  languages: string[];
  channels: string[];
  regions: string[];
  journey_profile: string[];
  tactic_profile: string[];
  infrastructure_profile: string[];
  payment_profile: string[];
  confidence: number;
  current_velocity: number;
  baseline_velocity: number;
  growth_multiplier: number;
  acceleration: number;
  mutation_count: number;
  active_mutations: string[];
}

export default function CampaignDetailPage({ params }: { params: { id: string } }) {
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "journey" | "entities" | "mutations" | "graph">("overview");

  useEffect(() => {
    async function loadCampaign() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/v1/campaigns/${params.id}`);
        if (!res.ok) {
          throw new Error(`Campaign '${params.id}' not found on backend.`);
        }
        const data = await res.json();
        setCampaign(data);
      } catch (err: any) {
        console.error("Failed to load campaign:", err);
        setError(err.message || "Failed to load campaign.");
      } finally {
        setLoading(false);
      }
    }
    loadCampaign();
  }, [params.id]);

  const getTone = (state: string): "danger" | "caution" | "brand" | "neutral" => {
    if (state === "OUTBREAK" || state === "CRITICAL") return "danger";
    if (state === "SURGING" || state === "HIGH") return "caution";
    if (state === "RESURGING" || state === "EMERGING") return "brand";
    return "neutral";
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-surface-subtle animate-pulse rounded" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} pad="md" className="h-28 animate-pulse bg-surface-subtle" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="space-y-6">
        <Link href="/radar" className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Outbreak Radar
        </Link>
        <Card pad="md" className="border-red-500/30 bg-red-950/20 text-red-200">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 text-red-400" />
            <div>
              <p className="text-sm font-semibold text-red-400">Campaign Not Found</p>
              <p className="text-xs text-red-300/80">{error || "Unable to retrieve campaign."}</p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link href="/radar" className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary transition-colors">
          <ArrowLeft className="h-3.5 w-3.5" /> Outbreak Radar
        </Link>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-text-muted">{campaign.campaign_id}</span>
          <DemoDataBadge />
        </div>
      </div>

      {/* Campaign Header */}
      <PageHeader
        eyebrow={`Campaign Intelligence · ${campaign.scam_family.replace(/_/g, " ")}`}
        title={campaign.title}
        description={`Multi-incident verified threat cluster. Tracking ${campaign.incident_count} reports across ${campaign.channels.join(", ") || "multiple channels"}.`}
        actions={
          <div className="flex items-center gap-2">
            <Badge tone={getTone(campaign.lifecycle_state)}>Status: {campaign.lifecycle_state}</Badge>
            <Badge tone={getTone(campaign.velocity_state)}>Velocity: {campaign.velocity_state}</Badge>
            <Badge tone="neutral">Review: {campaign.review_state}</Badge>
          </div>
        }
      />

      {/* Core KPI Metrics */}
      <div className="grid gap-3 grid-cols-2 sm:grid-cols-4 lg:grid-cols-6">
        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Incident Nodes</span>
          <p className="mt-1 font-mono text-2xl font-bold text-text-primary">{campaign.incident_count}</p>
          <span className="text-[10px] text-text-muted">{campaign.strongly_related_incident_count} strongly linked</span>
        </Card>

        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Current Velocity</span>
          <p className="mt-1 font-mono text-2xl font-bold text-amber-400">{campaign.current_velocity.toFixed(1)}/d</p>
          <span className="text-[10px] text-text-muted">Baseline: {campaign.baseline_velocity.toFixed(1)}/d</span>
        </Card>

        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Growth Rate</span>
          <p className="mt-1 font-mono text-2xl font-bold text-orange-400">+{((campaign.growth_multiplier - 1) * 100).toFixed(0)}%</p>
          <span className="text-[10px] text-text-muted">{campaign.growth_multiplier.toFixed(2)}x baseline</span>
        </Card>

        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Confidence</span>
          <p className="mt-1 font-mono text-2xl font-bold text-emerald-400">{(campaign.confidence * 100).toFixed(0)}%</p>
          <span className="text-[10px] text-text-muted">Evidence backed</span>
        </Card>

        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Unique Entities</span>
          <p className="mt-1 font-mono text-2xl font-bold text-text-primary">{campaign.unique_entity_count}</p>
          <span className="text-[10px] text-text-muted">{campaign.unique_payment_identifier_count} VPAs / accounts</span>
        </Card>

        <Card pad="md" className="bg-surface-subtle/40">
          <span className="text-[11px] font-semibold text-text-muted uppercase">Mutations</span>
          <p className="mt-1 font-mono text-2xl font-bold text-cyan-400">{campaign.mutation_count}</p>
          <span className="text-[10px] text-text-muted">Tracked rotations</span>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-4 text-xs font-medium">
        {[
          { key: "overview", label: "Overview & Velocity" },
          { key: "journey", label: "Journey & Tactics" },
          { key: "entities", label: "Infrastructure & Payments" },
          { key: "mutations", label: "Mutation Lineage" },
          { key: "graph", label: "Network Graph" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`pb-2.5 transition-colors border-b-2 font-semibold ${
              activeTab === tab.key
                ? "border-brand-primary text-brand-primary"
                : "border-transparent text-text-muted hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview & Velocity */}
      {activeTab === "overview" && (
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Activity className="h-4 w-4 text-brand-primary" /> Velocity & Outbreak Dynamics
            </span>

            <div className="rounded-xl border border-border bg-surface-subtle p-4 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-text-muted">Outbreak Tier:</span>
                <Badge tone={getTone(campaign.velocity_state)}>{campaign.velocity_state}</Badge>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-text-muted">Acceleration Factor:</span>
                <span className="font-mono text-text-primary">+{campaign.acceleration} reports/24h²</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-text-muted">Historical Window:</span>
                <span className="font-mono text-text-primary">14 Days Rolling Baseline</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-text-muted">First Detected:</span>
                <span className="font-mono text-text-primary">{formatDateTime(campaign.first_seen)}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-text-muted">Last Incident Observed:</span>
                <span className="font-mono text-text-primary">{formatDateTime(campaign.last_seen)}</span>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-surface-subtle p-4 space-y-2">
              <span className="text-xs font-bold text-text-primary">Why This Campaign is Trending</span>
              <p className="text-xs text-text-secondary leading-relaxed">
                {campaign.lifecycle_state === "OUTBREAK"
                  ? `Report volume surged +${((campaign.growth_multiplier - 1) * 100).toFixed(0)}% over the 14-day baseline with ${campaign.strongly_related_incident_count} strongly correlated incident nodes.`
                  : `Active network cluster with steady ${campaign.current_velocity.toFixed(1)} reports/day across ${campaign.regions.join(", ") || "targeted regions"}.`}
              </p>
            </div>
          </Card>

          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Globe className="h-4 w-4 text-cyan-400" /> Geography & Demographics
            </span>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-text-muted">Target Regions:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {campaign.regions.length > 0 ? (
                    campaign.regions.map((reg) => (
                      <span key={reg} className="rounded-md bg-surface-subtle px-2 py-0.5 border border-border font-medium">
                        {reg}
                      </span>
                    ))
                  ) : (
                    <span className="text-text-muted italic">Coarse multi-region footprint</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-text-muted">Languages / Scripts:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {campaign.languages.map((l) => (
                    <span key={l} className="rounded-md bg-surface-subtle px-2 py-0.5 border border-border font-medium">
                      {l}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-text-muted">Delivery Channels:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {campaign.channels.map((ch) => (
                    <span key={ch} className="rounded-md bg-surface-subtle px-2 py-0.5 border border-border font-medium">
                      {ch}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab 2: Journey & Tactics */}
      {activeTab === "journey" && (
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Compass className="h-4 w-4 text-brand-primary" /> Dominant Scam Journey Progression
            </span>
            <div className="space-y-2">
              {campaign.journey_profile.map((stage, idx) => (
                <div key={idx} className="flex items-center gap-3 rounded-lg border border-border bg-surface-subtle p-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-primary/20 text-brand-primary text-xs font-bold">
                    {idx + 1}
                  </span>
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-text-primary">{stage.replace(/_/g, " ")}</p>
                    <span className="text-[11px] text-text-muted">Observed across {campaign.incident_count} reports</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-400" /> Psychological Tactics & Levers
            </span>
            <div className="flex flex-wrap gap-2">
              {campaign.tactic_profile.map((tac) => (
                <span key={tac} className="rounded-lg border border-border bg-surface-subtle px-3 py-1.5 text-xs font-medium text-amber-300">
                  {tac.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Tab 3: Infrastructure & Payments */}
      {activeTab === "entities" && (
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-emerald-400" /> Payment Identifiers & VPAs
            </span>
            <div className="divide-y divide-border rounded-lg border border-border bg-surface-subtle">
              {campaign.payment_profile.map((vpa, i) => (
                <div key={i} className="flex items-center justify-between p-3 text-xs">
                  <span className="font-mono font-medium text-emerald-300">{vpa}</span>
                  <Badge tone="danger">COLLECTION_VPA</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card pad="md" className="border-border bg-surface-card space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Phone className="h-4 w-4 text-blue-400" /> Phone Numbers & Domains
            </span>
            <div className="divide-y divide-border rounded-lg border border-border bg-surface-subtle">
              {campaign.infrastructure_profile.map((infra, i) => (
                <div key={i} className="flex items-center justify-between p-3 text-xs">
                  <span className="font-mono font-medium text-text-primary">{infra}</span>
                  <Badge tone="brand">{infra.includes(".") ? "DOMAIN" : "PHONE"}</Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Tab 4: Mutations */}
      {activeTab === "mutations" && (
        <Card pad="md" className="border-border bg-surface-card space-y-4">
          <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
            <RotateCcw className="h-4 w-4 text-purple-400" /> Mutation & Drift Lineage
          </span>
          {campaign.active_mutations.length > 0 ? (
            <div className="space-y-2">
              {campaign.active_mutations.map((mut, idx) => (
                <div key={idx} className="flex items-center justify-between rounded-lg border border-border bg-surface-subtle p-3 text-xs">
                  <span className="font-mono font-medium text-purple-300">{mut}</span>
                  <span className="text-[11px] text-text-muted">Recorded during campaign update</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-text-muted">No active mutations recorded for this campaign.</p>
          )}
        </Card>
      )}

      {/* Tab 5: Network Graph */}
      {activeTab === "graph" && (
        <Card pad="md" className="border-border bg-surface-card space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-text-primary">
            Bounded Cytoscape Multi-Node Network
          </span>
          <EvidenceGraph graph={demoGraph} />
        </Card>
      )}
    </div>
  );
}
