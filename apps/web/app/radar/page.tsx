"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  AlertOctagon,
  AlertTriangle,
  ArrowUpRight,
  Clock,
  Eye,
  Filter,
  Flame,
  Globe,
  Layers,
  Radio,
  RefreshCw,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { Card, Badge } from "@/components/ui";

interface RadarBlip {
  blip_id: string;
  campaign_id: string;
  title: string;
  scam_family: string;
  ring: "CRITICAL" | "SURGING" | "EMERGING" | "WATCH";
  radius_norm: number;
  angle_rad: number;
  size: number;
  pulse_speed: number;
  severity: "INFO" | "WATCH" | "ELEVATED" | "HIGH" | "CRITICAL";
  confidence: number;
  incident_count: number;
  growth_percent: number;
  is_resurgent: boolean;
  is_mutating: boolean;
  top_reason: string;
}

interface OutbreakSignal {
  signal_id: string;
  campaign_id: string;
  signal_type: string;
  severity: string;
  confidence: number;
  current_velocity: number;
  baseline_velocity: number;
  acceleration: number;
  incident_count_window: number;
  unique_entity_count_window: number;
  regions: string[];
  channels: string[];
  languages: string[];
  strongest_evidence: string[];
  reason_codes: string[];
  first_detected: string;
  last_updated: string;
}

interface RadarSummary {
  active_campaigns: number;
  emerging_count: number;
  surging_count: number;
  outbreak_count: number;
  critical_count: number;
  new_incidents_24h: number;
  high_risk_signals: number;
  last_updated: string;
  demo_mode: boolean;
}

const RING_RADII = {
  CRITICAL: 110,
  SURGING: 195,
  EMERGING: 275,
};

export default function RadarPage() {
  const [blips, setBlips] = useState<RadarBlip[]>([]);
  const [signals, setSignals] = useState<OutbreakSignal[]>([]);
  const [summary, setSummary] = useState<RadarSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBlip, setSelectedBlip] = useState<RadarBlip | null>(null);
  const [timeFilter, setTimeFilter] = useState<"1H" | "24H" | "7D" | "30D">("24H");
  const [familyFilter, setFamilyFilter] = useState<string>("ALL");
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);
  const [demoMode, setDemoMode] = useState<boolean>(true);

  const fetchRadarData = async () => {
    setLoading(true);
    setError(null);
    try {
      const demoParam = demoMode ? "?demo_mode=true" : "";
      const [sumRes, blipsRes, sigsRes] = await Promise.all([
        fetch(`/api/v1/radar/summary${demoParam}`),
        fetch(`/api/v1/radar/blips${demoParam}`),
        fetch(`/api/v1/radar/signals${demoParam}`),
      ]);

      if (!sumRes.ok || !blipsRes.ok || !sigsRes.ok) {
        throw new Error("Network intelligence engine temporarily unavailable.");
      }

      const sumData = await sumRes.json();
      const blipsData = await blipsRes.json();
      const sigsData = await sigsRes.json();

      setSummary(sumData);
      setBlips(blipsData);
      setSignals(sigsData);
      if (blipsData.length > 0 && !selectedBlip) {
        setSelectedBlip(blipsData[0]);
      }
    } catch (err: any) {
      console.error("Radar data fetch error:", err);
      setError(err.message || "Failed to load Outbreak Radar intelligence.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRadarData();
  }, [demoMode]);

  // Filter blips
  const filteredBlips = useMemo(() => {
    return blips.filter((b) => {
      if (familyFilter !== "ALL" && b.scam_family !== familyFilter) {
        return false;
      }
      return true;
    });
  }, [blips, familyFilter]);

  // Color helper
  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return "#ef4444"; // red-500
      case "HIGH":
      case "SURGING":
        return "#f97316"; // orange-500
      case "ELEVATED":
        return "#eab308"; // yellow-500
      case "WATCH":
      case "EMERGING":
        return "#06b6d4"; // cyan-500
      default:
        return "#64748b"; // slate-500
    }
  };

  const getTone = (sev: string): "danger" | "caution" | "brand" | "neutral" => {
    if (sev === "CRITICAL") return "danger";
    if (sev === "HIGH" || sev === "SURGING") return "caution";
    if (sev === "ELEVATED" || sev === "WATCH") return "brand";
    return "neutral";
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        eyebrow="Network Surveillance"
        title="Scam Outbreak Radar"
        description="Live detection of emerging scam campaigns, velocity acceleration, mutation drift, and resurgence across the ScamGraph network."
        actions={
          <div className="flex items-center gap-3">
            <button
              onClick={() => setReducedMotion(!reducedMotion)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium border transition-colors ${reducedMotion
                  ? "bg-surface-raised border-brand-primary text-brand-primary"
                  : "bg-surface-subtle border-border text-text-secondary hover:text-text-primary"
                }`}
            >
              {reducedMotion ? "Motion: Reduced" : "Motion: Dynamic"}
            </button>
            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium border transition-colors ${demoMode
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                  : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                }`}
            >
              {demoMode ? "DEMO DATA" : "LIVE NETWORK"}
            </button>
            <button
              onClick={fetchRadarData}
              disabled={loading}
              className="flex items-center gap-1.5 rounded-lg border border-border bg-surface-subtle px-3 py-1.5 text-xs text-text-secondary hover:bg-surface-raised hover:text-text-primary transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        }
      />

      {/* Surveillance Summary Bar */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <Card pad="md" className="border-line bg-surface-subtle/40">
          <div className="flex items-center justify-between text-xs text-text-secondary">
            <span>Active Campaigns</span>
            <Radio className="h-4 w-4 text-brand-primary" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold text-text-primary">
            {summary ? summary.active_campaigns : "--"}
          </p>
          <span className="text-[11px] text-text-muted">Multi-signal verified</span>
        </Card>

        <Card pad="md" className="border-line bg-surface-subtle/40">
          <div className="flex items-center justify-between text-xs text-text-secondary">
            <span>Critical Outbreaks</span>
            <AlertOctagon className="h-4 w-4 text-red-500" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold text-red-500">
            {summary ? summary.outbreak_count : "--"}
          </p>
          <span className="text-[11px] text-red-400/80">&gt;3.5x baseline velocity</span>
        </Card>

        <Card pad="md" className="border-line bg-surface-subtle/40">
          <div className="flex items-center justify-between text-xs text-text-secondary">
            <span>Surging Threats</span>
            <Flame className="h-4 w-4 text-orange-400" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold text-orange-400">
            {summary ? summary.surging_count : "--"}
          </p>
          <span className="text-[11px] text-orange-400/80">Accelerating volume</span>
        </Card>

        <Card pad="md" className="border-line bg-surface-subtle/40">
          <div className="flex items-center justify-between text-xs text-text-secondary">
            <span>Emerging Variants</span>
            <Sparkles className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold text-cyan-400">
            {summary ? summary.emerging_count : "--"}
          </p>
          <span className="text-[11px] text-cyan-400/80">Early pattern detection</span>
        </Card>

        <Card pad="md" className="border-line bg-surface-subtle/40">
          <div className="flex items-center justify-between text-xs text-text-secondary">
            <span>New Reports (24h)</span>
            <Clock className="h-4 w-4 text-text-muted" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold text-text-primary">
            {summary ? summary.new_incidents_24h : "--"}
          </p>
          <span className="text-[11px] text-text-muted">Deduplicated timeline</span>
        </Card>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface-subtle/60 p-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-text-muted flex items-center gap-1.5">
            <Filter className="h-3.5 w-3.5" /> Window:
          </span>
          {(["1H", "24H", "7D", "30D"] as const).map((w) => (
            <button
              key={w}
              onClick={() => setTimeFilter(w)}
              className={`rounded-lg px-2.5 py-1 text-xs font-mono font-medium transition-colors ${timeFilter === w
                  ? "bg-brand-primary text-black font-bold"
                  : "bg-surface-raised text-text-secondary hover:text-text-primary"
                }`}
            >
              {w}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-text-muted">Family:</span>
          <select
            value={familyFilter}
            onChange={(e) => setFamilyFilter(e.target.value)}
            className="rounded-lg border border-border bg-surface-raised px-2.5 py-1 text-xs text-text-primary focus:outline-none focus:border-brand-primary"
          >
            <option value="ALL">All Scam Families</option>
            <option value="DIGITAL_ARREST">Digital Arrest</option>
            <option value="TASK_SCAM">Task / Job Scam</option>
            <option value="FAKE_SUPPORT">Fake Support / Power</option>
            <option value="CUSTOMS_PARCEL">Customs Parcel / Narcotics</option>
          </select>
        </div>
      </div>

      {/* Error or Degraded State */}
      {error && (
        <Card pad="md" className="border-red-500/30 bg-red-950/20 text-red-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldAlert className="h-5 w-5 text-red-400" />
              <div>
                <p className="text-sm font-semibold text-red-400">Network Intelligence Degraded</p>
                <p className="text-xs text-red-300/80">{error}</p>
              </div>
            </div>
            <button
              onClick={fetchRadarData}
              className="rounded-lg border border-red-500/40 px-3 py-1.5 text-xs text-red-300 hover:bg-red-500/20"
            >
              Retry Connection
            </button>
          </div>
        </Card>
      )}

      {/* Main Radar Screen Layout */}
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        {/* Left: Concentric Radar Canvas */}
        <Card pad="none" className="relative overflow-hidden bg-surface-card border-border min-h-[580px] flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-border px-5 py-3.5 bg-surface-subtle/50">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-text-primary">
                Analytical Radar Canvas
              </span>
              <span className="font-mono text-[11px] text-text-muted">· Concentric Severity Projection</span>
            </div>
            <div className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
              <span>Inner: Critical</span>
              <span>·</span>
              <span>Mid: Surging</span>
              <span>·</span>
              <span>Outer: Emerging</span>
            </div>
          </div>

          {/* SVG Radar Display */}
          <div className="relative flex flex-1 items-center justify-center p-4">
            <svg
              viewBox="0 0 700 700"
              className="w-full max-w-[620px] aspect-square overflow-visible select-none"
              role="img"
              aria-label="Scam Outbreak Radar concentric rings visualization"
            >
              <defs>
                <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#0f172a" stopOpacity="0.8" />
                  <stop offset="60%" stopColor="#090d16" stopOpacity="0.95" />
                  <stop offset="100%" stopColor="#030712" stopOpacity="1" />
                </radialGradient>
                <linearGradient id="sweepGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Background circle */}
              <circle cx="350" cy="350" r="340" fill="url(#radarGlow)" stroke="#1e293b" strokeWidth="1.5" />

              {/* Grid Crosshairs */}
              <line x1="10" y1="350" x2="690" y2="350" stroke="#1e293b" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="350" y1="10" x2="350" y2="690" stroke="#1e293b" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="110" y1="110" x2="590" y2="590" stroke="#0f172a" strokeWidth="1" />
              <line x1="590" y1="110" x2="110" y2="590" stroke="#0f172a" strokeWidth="1" />

              {/* Concentric Rings */}
              {/* Outer Ring: Emerging / Watch */}
              <circle
                cx="350"
                cy="350"
                r={RING_RADII.EMERGING}
                fill="none"
                stroke="#0284c7"
                strokeWidth="1.2"
                strokeDasharray="6 4"
                opacity="0.4"
              />
              <text x="355" y="85" fill="#38bdf8" fontSize="10" fontFamily="monospace" opacity="0.6">
                EMERGING / WATCH RING (r=275px)
              </text>

              {/* Middle Ring: Surging */}
              <circle
                cx="350"
                cy="350"
                r={RING_RADII.SURGING}
                fill="none"
                stroke="#f97316"
                strokeWidth="1.5"
                strokeDasharray="5 3"
                opacity="0.5"
              />
              <text x="355" y="165" fill="#fb923c" fontSize="10" fontFamily="monospace" opacity="0.7">
                SURGING RING (r=195px)
              </text>

              {/* Inner Ring: Critical / Outbreak */}
              <circle
                cx="350"
                cy="350"
                r={RING_RADII.CRITICAL}
                fill="#ef4444"
                fillOpacity="0.04"
                stroke="#ef4444"
                strokeWidth="2"
                opacity="0.7"
              />
              <text x="355" y="250" fill="#f87171" fontSize="10" fontFamily="monospace" fontWeight="bold">
                CRITICAL OUTBREAK ZONE (r=110px)
              </text>

              {/* Center Hub */}
              <circle cx="350" cy="350" r="16" fill="#0f172a" stroke="#38bdf8" strokeWidth="2" />
              <circle cx="350" cy="350" r="4" fill="#38bdf8" />
              <text x="350" y="378" fill="#94a3b8" fontSize="9" textAnchor="middle" fontFamily="monospace">
                SCAMGRAPH CORE
              </text>

              {/* Radar Sweep Animation (Disabled if reducedMotion) */}
              {!reducedMotion && (
                <g className="origin-center animate-[spin_4s_linear_infinite]" style={{ transformOrigin: "350px 350px" }}>
                  <path
                    d="M 350 350 L 350 10 A 340 340 0 0 1 590 110 Z"
                    fill="url(#sweepGradient)"
                    opacity="0.3"
                  />
                  <line x1="350" y1="350" x2="350" y2="10" stroke="#38bdf8" strokeWidth="1.5" opacity="0.8" />
                </g>
              )}

              {/* Campaign Blips */}
              {filteredBlips.map((blip) => {
                const targetRadius =
                  blip.ring === "CRITICAL"
                    ? 70 + (blip.radius_norm * 40)
                    : blip.ring === "SURGING"
                      ? 140 + (blip.radius_norm * 50)
                      : 220 + (blip.radius_norm * 55);

                const cx = 350 + targetRadius * Math.cos(blip.angle_rad);
                const cy = 350 + targetRadius * Math.sin(blip.angle_rad);
                const color = getSeverityColor(blip.ring);
                const isSelected = selectedBlip?.campaign_id === blip.campaign_id;

                return (
                  <g
                    key={blip.blip_id}
                    className="cursor-pointer transition-transform hover:scale-125 focus:outline-none"
                    onClick={() => setSelectedBlip(blip)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        setSelectedBlip(blip);
                      }
                    }}
                    tabIndex={0}
                    role="button"
                    aria-label={`Campaign ${blip.title}, status ${blip.ring}, ${blip.incident_count} reports`}
                  >
                    {/* Pulsing ring for high velocity / outbreaks */}
                    {!reducedMotion && blip.pulse_speed > 1.2 && (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={blip.size + 8}
                        fill="none"
                        stroke={color}
                        strokeWidth="1.5"
                        opacity="0.6"
                        className="animate-ping"
                        style={{ animationDuration: `${Math.max(1, 3.5 - blip.pulse_speed)}s` }}
                      />
                    )}

                    {/* Confidence halo */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={blip.size + 4}
                      fill={color}
                      fillOpacity={isSelected ? "0.25" : "0.10"}
                      stroke={isSelected ? "#ffffff" : color}
                      strokeWidth={isSelected ? "2" : "0.8"}
                    />

                    {/* Core blip node */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r={Math.max(4, blip.size / 2)}
                      fill={color}
                      stroke="#ffffff"
                      strokeWidth="1.2"
                    />

                    {/* Label */}
                    <text
                      x={cx}
                      y={cy + (blip.size / 2) + 12}
                      fill="#e2e8f0"
                      fontSize="9"
                      fontWeight={isSelected ? "bold" : "normal"}
                      fontFamily="monospace"
                      textAnchor="middle"
                      className="pointer-events-none drop-shadow-md"
                    >
                      {blip.scam_family.replace(/_/g, " ")} ({blip.incident_count})
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Canvas Footer Legend */}
          <div className="flex flex-wrap items-center justify-between border-t border-border px-5 py-3 text-xs text-text-muted bg-surface-subtle/30">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
                Critical Zone
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-orange-500" />
                Surging Zone
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-cyan-500" />
                Emerging Zone
              </span>
            </div>
            <span className="font-mono text-[11px] text-text-muted">
              Blip Size = Incident Volume · Pulse = Velocity Multiplier
            </span>
          </div>
        </Card>

        {/* Right Sidebar: Selected Campaign Inspector & Top Outbreaks */}
        <div className="space-y-6">
          {/* Selected Campaign Inspector */}
          {selectedBlip ? (
            <Card pad="md" className="border-border bg-surface-card">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2">
                  <Badge tone={getTone(selectedBlip.ring)}>{selectedBlip.ring}</Badge>
                  <span className="font-mono text-xs text-text-muted">{selectedBlip.campaign_id}</span>
                </div>
                <Link
                  href={`/campaigns/${selectedBlip.campaign_id}`}
                  className="flex items-center gap-1 text-xs text-brand-primary hover:underline font-medium"
                >
                  Deep Inspection <ArrowUpRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                <h3 className="text-base font-bold text-text-primary leading-tight">
                  {selectedBlip.title}
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {selectedBlip.top_reason}
                </p>

                <div className="grid grid-cols-2 gap-2 pt-2">
                  <div className="rounded-lg bg-surface-subtle p-2.5">
                    <span className="text-[10px] uppercase font-bold text-text-muted">Growth Rate</span>
                    <p className="font-mono text-lg font-bold text-amber-400">
                      +{selectedBlip.growth_percent}%
                    </p>
                  </div>
                  <div className="rounded-lg bg-surface-subtle p-2.5">
                    <span className="text-[10px] uppercase font-bold text-text-muted">Incident Nodes</span>
                    <p className="font-mono text-lg font-bold text-text-primary">
                      {selectedBlip.incident_count}
                    </p>
                  </div>
                </div>

                <div className="space-y-1.5 pt-2 text-xs">
                  <div className="flex justify-between text-text-muted">
                    <span>Scam Family:</span>
                    <span className="font-medium text-text-primary">{selectedBlip.scam_family}</span>
                  </div>
                  <div className="flex justify-between text-text-muted">
                    <span>Evidence Confidence:</span>
                    <span className="font-mono text-emerald-400">
                      {(selectedBlip.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-text-muted">
                    <span>Mutations Tracked:</span>
                    <span className="font-mono text-text-primary">
                      {selectedBlip.is_mutating ? "Active Drift Detected" : "Stable Pattern"}
                    </span>
                  </div>
                  {selectedBlip.is_resurgent && (
                    <div className="flex items-center gap-1.5 rounded-lg bg-purple-500/10 p-2 text-purple-300">
                      <RotateCcw className="h-3.5 w-3.5" />
                      <span>Resurgent campaign after dormancy</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ) : (
            <Card pad="md" className="border-border bg-surface-card text-center text-text-muted py-8">
              <Eye className="mx-auto h-8 w-8 opacity-40 mb-2" />
              <p className="text-xs">Click any radar blip to inspect campaign dynamics</p>
            </Card>
          )}

          {/* Top Outbreaks Sidebar */}
          <Card pad="md" className="border-border bg-surface-card">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-1.5">
                <Flame className="h-4 w-4 text-orange-400" /> Top Outbreaks
              </span>
              <span className="text-[11px] font-mono text-text-muted">Live Rank</span>
            </div>

            <div className="mt-3 space-y-2.5">
              {filteredBlips
                .filter((b) => b.ring === "CRITICAL" || b.ring === "SURGING")
                .map((b, idx) => (
                  <div
                    key={b.blip_id}
                    onClick={() => setSelectedBlip(b)}
                    className="flex cursor-pointer items-center justify-between rounded-lg border border-border bg-surface-subtle/50 p-2.5 hover:bg-surface-raised transition-colors"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-text-muted">#{idx + 1}</span>
                        <p className="text-xs font-semibold text-text-primary line-clamp-1">{b.title}</p>
                      </div>
                      <span className="text-[10px] text-text-muted">
                        {b.incident_count} reports · +{b.growth_percent}%
                      </span>
                    </div>
                    <Badge tone={getTone(b.ring)}>{b.ring}</Badge>
                  </div>
                ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Feed: Emerging Signals Timeline */}
      <Card pad="none" className="border-border bg-surface-card">
        <div className="flex items-center justify-between border-b border-border px-5 py-3.5 bg-surface-subtle/50">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-brand-primary" />
            <span className="text-xs font-bold uppercase tracking-wider text-text-primary">
              Outbreak Signal Chronology
            </span>
          </div>
          <span className="font-mono text-[11px] text-text-muted">
            {signals.length} real-time escalations recorded
          </span>
        </div>

        <div className="divide-y divide-border">
          {signals.slice(0, 6).map((sig) => (
            <div key={sig.signal_id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-3 hover:bg-surface-subtle/30 transition-colors">
              <div className="space-y-1">
                <div className="flex items-center gap-2.5">
                  <Badge tone={getTone(sig.severity)}>{sig.signal_type}</Badge>
                  <span className="font-mono text-xs font-bold text-text-primary">
                    Campaign: {sig.campaign_id}
                  </span>
                  <span className="text-[11px] text-text-muted">
                    {(sig.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="text-xs text-text-secondary">
                  {sig.strongest_evidence.join(" · ") || sig.reason_codes.join(", ")}
                </p>
                {sig.regions.length > 0 && (
                  <div className="flex items-center gap-1.5 text-[11px] text-text-muted pt-0.5">
                    <Globe className="h-3 w-3" />
                    <span>Regions: {sig.regions.join(", ")}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <span className="font-mono text-xs text-text-muted">
                  Velocity: {sig.current_velocity.toFixed(1)}/day
                </span>
                <Link
                  href={`/campaigns/${sig.campaign_id}`}
                  className="rounded-lg border border-border bg-surface-subtle px-2.5 py-1 text-xs text-brand-primary hover:bg-surface-raised"
                >
                  View Campaign
                </Link>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
