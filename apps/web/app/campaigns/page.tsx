"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import {
  FolderKanban,
  AlertTriangle,
  Flame,
  ArrowUpRight,
  TrendingUp,
  Search,
  SlidersHorizontal,
  Bookmark,
  Download,
  Star,
  ExternalLink,
  ShieldAlert,
  Clock,
  Layers,
  CheckCircle2,
  X,
  RotateCw,
  MoreVertical,
  Activity,
  FileText,
  Lock,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

export interface CampaignRecord {
  id: string;
  cluster_id: string;
  name: string;
  pattern_type: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  lifecycle: "Surging" | "Active" | "Resurgent" | "Emerging" | "Dormant";
  velocity_label: string;
  velocity_trend: number; // percentage
  confidence: number; // percentage
  incidents_count: number;
  financial_loss_total: number;
  financial_loss_lien: number;
  target_vector: string;
  modality: string;
  languages: string[];
  last_seen: string;
  first_seen: string;
  review_state: "Needs review" | "Confirmed cluster" | "Unreviewed" | "Archived";
  sample_domain?: string;
  sample_vpa?: string;
  lac_pool?: string;
  description: string;
  is_outbreak_candidate?: boolean;
}

const CANONICAL_CAMPAIGNS: CampaignRecord[] = [
  {
    id: "camp-power-urgent",
    cluster_id: "#UTL-8490",
    name: "State Electricity Instant Cutoff Syndicate",
    pattern_type: "UTILITY_BILL_COERCION",
    severity: "CRITICAL",
    lifecycle: "Surging",
    velocity_label: "+340% / 4h",
    velocity_trend: 340,
    confidence: 94,
    incidents_count: 142,
    financial_loss_total: 18450000,
    financial_loss_lien: 4280000,
    target_vector: "PhonePe/GPay UPI",
    modality: "util-power-*",
    languages: ["hi", "Hinglish", "en"],
    last_seen: "2026-10-24T20:58:00Z",
    first_seen: "2026-10-18T09:15:00Z",
    review_state: "Needs review",
    sample_domain: "electricity-bill-pay.xyz",
    sample_vpa: "util-power-84920@okaxis",
    lac_pool: "+91 98******10 Pool (LAC 404-45)",
    description: "Active pan-regional coercive payment extortion campaign targeting metropolitan power utility subscribers via automated GSM spoofing, falsified disconnection work-orders, and rapid UPI push collect requests.",
    is_outbreak_candidate: true,
  },
  {
    id: "camp-kyc-freenom",
    cluster_id: "#KYC-4091",
    name: "State Bank & Aadhaar KYC Suspension Syndicate",
    pattern_type: "KYC_IMPERSONATION",
    severity: "CRITICAL",
    lifecycle: "Surging",
    velocity_label: "+280% / 6h",
    velocity_trend: 280,
    confidence: 96,
    incidents_count: 98,
    financial_loss_total: 24500000,
    financial_loss_lien: 8900000,
    target_vector: "Spoofed Banking Portal",
    modality: "NetBanking / OTP Harvesting",
    languages: ["hi", "en", "mr"],
    last_seen: "2026-10-24T20:15:00Z",
    first_seen: "2026-10-15T08:30:00Z",
    review_state: "Needs review",
    sample_domain: "sbi-kyc-verify-portal.online",
    sample_vpa: "secure.verify@paytm",
    lac_pool: "+91 91******44 Pool (LAC 404-12)",
    description: "Coordinated cluster targeting banking customers using spoofed SMS, KYC warnings, and credential harvesting landing pages mimicking nationalized banks.",
    is_outbreak_candidate: true,
  },
  {
    id: "camp-work-from-home",
    cluster_id: "#TSK-1092",
    name: "Telegram Pre-paid Task & Rating Scam Wave",
    pattern_type: "PART_TIME_JOB_FRAUD",
    severity: "HIGH",
    lifecycle: "Active",
    velocity_label: "+45% steady",
    velocity_trend: 45,
    confidence: 91,
    incidents_count: 89,
    financial_loss_total: 11200000,
    financial_loss_lien: 3100000,
    target_vector: "Telegram Web Bot",
    modality: "Merchant VPAs",
    languages: ["en", "hi"],
    last_seen: "2026-10-24T20:30:00Z",
    first_seen: "2026-10-16T11:00:00Z",
    review_state: "Confirmed cluster",
    sample_domain: "task-earning-hub.xyz",
    sample_vpa: "merchant992@icici",
    lac_pool: "Telegram Bot Gateway",
    description: "Deceptive part-time job lures promising daily returns for rating videos, transitioning to mandatory prepaid deposit tasks on fake crypto exchanges.",
    is_outbreak_candidate: false,
  },
  {
    id: "camp-digital-arrest",
    cluster_id: "#DAR-3041",
    name: "CBI / Mumbai Police Digital Arrest Telephony",
    pattern_type: "DIGITAL_ARREST",
    severity: "CRITICAL",
    lifecycle: "Resurgent",
    velocity_label: "+190% surging",
    velocity_trend: 190,
    confidence: 88,
    incidents_count: 34,
    financial_loss_total: 39500000,
    financial_loss_lien: 12000000,
    target_vector: "Skype Video Call",
    modality: "RTGS Demands & Fake Police Setup",
    languages: ["hi", "en"],
    last_seen: "2026-10-24T19:45:00Z",
    first_seen: "2026-10-19T14:20:00Z",
    review_state: "Needs review",
    sample_domain: "cbi-investigation-notice.gov.in.top",
    sample_vpa: "rbi.clearance@sbi",
    lac_pool: "VoIP Trunking +91 22******90",
    description: "Intimidation extortion ring operating fake police station backgrounds over video calls, coercing victims into liquidating mutual funds and RTGS wire transfers.",
    is_outbreak_candidate: true,
  },
  {
    id: "camp-apk-delivery",
    cluster_id: "#APK-5512",
    name: "PM Kisan Yojna Malicious APK Delivery",
    pattern_type: "MALICIOUS_APK",
    severity: "HIGH",
    lifecycle: "Emerging",
    velocity_label: "+80% accelerating",
    velocity_trend: 80,
    confidence: 88,
    incidents_count: 29,
    financial_loss_total: 6800000,
    financial_loss_lien: 1500000,
    target_vector: "Direct APK Link",
    modality: "SMS Spoof / RAT Infiltration",
    languages: ["hi", "bn"],
    last_seen: "2026-10-24T18:10:00Z",
    first_seen: "2026-10-21T06:00:00Z",
    review_state: "Unreviewed",
    sample_domain: "pmkisan-subsidy-apply.apk.top",
    sample_vpa: "kisan.yojna@pnb",
    lac_pool: "SMS Gateway HLR 404-67",
    description: "Trojanized APK masquerading as welfare subsidy app, extracting SMS inbox tokens and granting automated accessibility service permissions.",
    is_outbreak_candidate: true,
  },
  {
    id: "camp-microloan-harass",
    cluster_id: "#LOA-9018",
    name: "Instant 5-Minute Microloan Contact Ring",
    pattern_type: "MICROLOAN_EXTORTION",
    severity: "MEDIUM",
    lifecycle: "Dormant",
    velocity_label: "-35% cooling",
    velocity_trend: -35,
    confidence: 95,
    incidents_count: 210,
    financial_loss_total: 14200000,
    financial_loss_lien: 5200000,
    target_vector: "App Permissions Harvest",
    modality: "WhatsApp Coercion",
    languages: ["Hinglish", "en"],
    last_seen: "2026-10-23T11:20:00Z",
    first_seen: "2026-10-01T10:00:00Z",
    review_state: "Archived",
    sample_domain: "quick-rupee-loan.in",
    sample_vpa: "recovery.finserv@hdfc",
    lac_pool: "WhatsApp Cloud API",
    description: "Predatory unlicensed lending app harvesting victim contact lists and issuing automated morphing blackmail messages to victim associates.",
    is_outbreak_candidate: false,
  },
];

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignRecord[]>(CANONICAL_CAMPAIGNS);
  const [selectedId, setSelectedId] = useState<string>("camp-power-urgent");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPreset, setFilterPreset] = useState<"ALL" | "OUTBREAK" | "SURGING" | "REVIEW">("ALL");
  const [starredMap, setStarredMap] = useState<Record<string, boolean>>({ "camp-power-urgent": true });
  const [selectedRows, setSelectedRows] = useState<Record<string, boolean>>({ "camp-power-urgent": true });
  const [isLoading, setIsLoading] = useState(false);
  const [lastSync, setLastSync] = useState<Date>(new Date());

  const fetchCampaigns = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/campaigns");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          // Merge dynamic API records with rich canonical fields
          const updated = CANONICAL_CAMPAIGNS.map((canon) => {
            const match = data.find((d: any) => d.id === canon.id || d.name?.includes(canon.name.split(" ")[0]));
            if (match) {
              return {
                ...canon,
                incidents_count: match.incidents_count || canon.incidents_count,
                last_seen: match.last_seen || canon.last_seen,
              };
            }
            return canon;
          });
          setCampaigns(updated);
        }
      }
      setLastSync(new Date());
    } catch (err) {
      console.warn("Using offline canonical campaign intelligence:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCampaigns();
    const interval = setInterval(fetchCampaigns, 8000);
    return () => clearInterval(interval);
  }, [fetchCampaigns]);

  const filteredCampaigns = useMemo(() => {
    return campaigns.filter((c) => {
      // Preset filtering
      if (filterPreset === "OUTBREAK" && !c.is_outbreak_candidate) return false;
      if (filterPreset === "SURGING" && c.lifecycle !== "Surging") return false;
      if (filterPreset === "REVIEW" && c.review_state !== "Needs review") return false;

      // Query filtering
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        c.name.toLowerCase().includes(q) ||
        c.cluster_id.toLowerCase().includes(q) ||
        c.pattern_type.toLowerCase().includes(q) ||
        c.target_vector.toLowerCase().includes(q) ||
        (c.sample_vpa && c.sample_vpa.toLowerCase().includes(q)) ||
        (c.sample_domain && c.sample_domain.toLowerCase().includes(q))
      );
    });
  }, [campaigns, filterPreset, searchQuery]);

  const selectedCampaign = useMemo(() => {
    return campaigns.find((c) => c.id === selectedId) || campaigns[0];
  }, [campaigns, selectedId]);

  const toggleStar = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setStarredMap((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedRows((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString("en-IN")}`;
  };

  return (
    <div className="w-full space-y-4 text-viz-text">
      {/* 1. Top Command Deck & Filters */}
      <div className="bg-surface border border-border-divider rounded-lg p-5 shadow-xs shrink-0">
        {/* Title Block */}
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Campaigns</h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded bg-surface-subtle border border-border-divider text-xs font-semibold text-viz-neutral">
                {campaigns.length} active clusters
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-xs font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse" />
                4 outbreak candidates
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1 max-w-2xl">
              Aggregated cross-incident syndicate waves classified by backend correlation and ScamDNA heuristics.
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={fetchCampaigns}
              disabled={isLoading}
              className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors"
              title="Refresh live cluster intelligence"
            >
              <RotateCw className={`w-3.5 h-3.5 text-viz-primary ${isLoading ? "animate-spin" : ""}`} />
              <span>Refresh</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <Bookmark className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Saved views</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <Download className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Export table</span>
            </button>
          </div>
        </div>

        {/* Quick Preset Filter Pills & Search */}
        <div className="px-4 lg:px-8 pb-3 flex items-center justify-between gap-4 overflow-x-auto">
          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={() => setFilterPreset("ALL")}
              className={`h-7 px-3 rounded-full text-xs font-medium transition-colors ${
                filterPreset === "ALL"
                  ? "bg-viz-primary text-white"
                  : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              All campaigns ({campaigns.length})
            </button>
            <button
              onClick={() => setFilterPreset("OUTBREAK")}
              className={`h-7 px-3 rounded-full text-xs font-medium flex items-center gap-1.5 transition-colors ${
                filterPreset === "OUTBREAK"
                  ? "bg-viz-primary text-white"
                  : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-viz-warning" />
              <span>Outbreak candidates (4)</span>
            </button>
            <button
              onClick={() => setFilterPreset("SURGING")}
              className={`h-7 px-3 rounded-full text-xs font-medium flex items-center gap-1.5 transition-colors ${
                filterPreset === "SURGING"
                  ? "bg-viz-primary text-white"
                  : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              <TrendingUp className="w-3 h-3 text-error" />
              <span>Surging velocity (2)</span>
            </button>
            <button
              onClick={() => setFilterPreset("REVIEW")}
              className={`h-7 px-3 rounded-full text-xs font-medium flex items-center gap-1.5 transition-colors ${
                filterPreset === "REVIEW"
                  ? "bg-viz-primary text-white"
                  : "bg-surface-subtle hover:bg-surface-container-high text-viz-text"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-viz-info" />
              <span>Pending analyst review (3)</span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative w-64 shrink-0 hidden md:block">
            <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-viz-neutral" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter cluster, VPA, domain..."
              className="w-full h-7 pl-8 pr-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
            />
          </div>
        </div>

        {/* Dimension Controls Bar */}
        <div className="px-4 lg:px-8 py-2 bg-surface-subtle border-t border-border-divider flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <div className="h-6 px-2 bg-surface border border-border-divider rounded flex items-center gap-1 text-viz-text font-medium">
              <span className="text-viz-neutral">Modality:</span>
              <span>UPI &amp; Bill Payment</span>
            </div>
            <div className="h-6 px-2 bg-surface border border-border-divider rounded flex items-center gap-1 text-viz-text font-medium">
              <span className="text-viz-neutral">Languages:</span>
              <span>hi, bn, Hinglish, en</span>
            </div>
            <div className="h-6 px-2 bg-surface border border-border-divider rounded flex items-center gap-1 text-viz-text font-medium">
              <span className="text-viz-neutral">Window:</span>
              <span>Last 24h</span>
            </div>
            {(searchQuery || filterPreset !== "ALL") && (
              <button
                onClick={() => {
                  setSearchQuery("");
                  setFilterPreset("ALL");
                }}
                className="text-viz-primary hover:underline ml-1 font-medium"
              >
                Reset filters
              </button>
            )}
          </div>
          <div className="flex items-center gap-2 text-viz-neutral text-[11px]">
            <span>
              Showing <strong className="text-viz-text font-semibold">{filteredCampaigns.length}</strong> of {campaigns.length} campaigns
            </span>
            <span>·</span>
            <span>
              Updated <strong className="text-viz-text font-semibold">{Math.round((Date.now() - lastSync.getTime()) / 1000)}s ago</strong>
            </span>
          </div>
        </div>
      </div>

      {/* 3. Main Split Console (§3.2, §4.4) */}
      <div className="flex flex-1 w-full overflow-hidden min-h-[calc(100vh-14rem)]">
        {/* Left Data Work Surface: 36px Compact Rows */}
        <div className="flex-1 overflow-x-auto bg-surface" data-density="compact">
          <table className="w-full text-left border-collapse select-text min-w-[900px]">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="w-9 px-3 text-center">
                  <input
                    type="checkbox"
                    className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer"
                    onChange={(e) => {
                      const all: Record<string, boolean> = {};
                      if (e.target.checked) filteredCampaigns.forEach((c) => (all[c.id] = true));
                      setSelectedRows(all);
                    }}
                  />
                </th>
                <th className="w-8 px-0 text-center" />
                <th className="px-3 font-semibold">Campaign ID &amp; Name</th>
                <th className="px-3 font-semibold">Lifecycle</th>
                <th className="px-3 font-semibold">Velocity</th>
                <th className="px-3 font-semibold">ScamDNA Conf.</th>
                <th className="px-3 font-semibold">Incidents</th>
                <th className="px-3 font-semibold">Financial Loss</th>
                <th className="px-3 font-semibold">Target Vector</th>
                <th className="px-3 font-semibold">Languages</th>
                <th className="px-3 font-semibold">Last Seen (IST)</th>
                <th className="px-3 font-semibold">Review State</th>
                <th className="px-3 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-xs text-viz-text font-normal">
              {filteredCampaigns.map((c) => {
                const isSelected = selectedId === c.id;
                const isStarred = !!starredMap[c.id];
                const isChecked = !!selectedRows[c.id];

                return (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedId(c.id)}
                    className={`h-9 transition-colors cursor-pointer group ${
                      isSelected
                        ? "bg-[#0B6256]/[0.08] border-l-[3px] border-l-viz-primary font-medium"
                        : "hover:bg-surface-container-low border-l-[3px] border-l-transparent"
                    }`}
                  >
                    <td className="w-9 px-3 text-center">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) => toggleSelect(c.id, e as any)}
                        className="w-3.5 h-3.5 accent-viz-primary rounded cursor-pointer"
                      />
                    </td>
                    <td className="w-8 px-0 text-center">
                      <button
                        onClick={(e) => toggleStar(c.id, e)}
                        className="text-viz-neutral hover:text-viz-warning transition-colors"
                      >
                        <Star
                          className={`w-3.5 h-3.5 ${
                            isStarred ? "text-viz-warning fill-viz-warning" : "text-border-control"
                          }`}
                        />
                      </button>
                    </td>
                    <td className="px-3">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[11px] px-1 rounded bg-[#E8DFCF] text-[#4A3306] font-mono font-bold">
                          {c.cluster_id}
                        </span>
                        <span className="font-semibold text-viz-text truncate max-w-xs">{c.name}</span>
                      </div>
                    </td>
                    <td className="px-3">
                      {c.lifecycle === "Surging" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-tone-danger-bg text-tone-danger-text text-[11px] font-bold">
                          <span className="w-2 h-2 rounded-full border-2 border-error ring-1 ring-error animate-pulse inline-block" />
                          Surging
                        </span>
                      ) : c.lifecycle === "Resurgent" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-[#F1ECE3] text-[#614714] text-[11px] font-semibold">
                          <RotateCw className="w-2.5 h-2.5 text-viz-warning" />
                          Resurgent
                        </span>
                      ) : c.lifecycle === "Emerging" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-tone-info-bg text-tone-info-text text-[11px] font-semibold">
                          <span className="w-1.5 h-1.5 rounded-full bg-viz-info" />
                          Emerging
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-surface-subtle text-viz-neutral text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-viz-primary" />
                          Active
                        </span>
                      )}
                    </td>
                    <td className="px-3">
                      <div
                        className={`flex items-center gap-1 text-[11px] font-mono font-semibold ${
                          c.velocity_trend > 100
                            ? "text-error"
                            : c.velocity_trend > 0
                            ? "text-viz-warning"
                            : "text-viz-neutral"
                        }`}
                      >
                        <ArrowUpRight className="w-3 h-3" />
                        <span>{c.velocity_label}</span>
                      </div>
                    </td>
                    <td className="px-3">
                      <span className="text-[11px] text-viz-text font-medium">High ({c.confidence}%)</span>
                    </td>
                    <td className="px-3">
                      <span className="font-semibold text-viz-text tabular-nums">{c.incidents_count} cases</span>
                    </td>
                    <td className="px-3">
                      <span className="font-mono text-[11px] text-error font-semibold tabular-nums">
                        {formatINR(c.financial_loss_total)}
                      </span>
                    </td>
                    <td className="px-3 text-viz-neutral text-[11px] truncate max-w-xs">{c.target_vector}</td>
                    <td className="px-3 text-[11px]">
                      <div className="flex items-center gap-1">
                        {c.languages.slice(0, 2).map((lang) => (
                          <span
                            key={lang}
                            className="px-1 bg-surface-subtle rounded border border-border-divider font-mono text-[10px]"
                          >
                            {lang}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-3 text-[11px] whitespace-nowrap">
                      <span>{formatDateTime(c.last_seen)}</span>
                    </td>
                    <td className="px-3">
                      {c.review_state === "Needs review" ? (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text text-[11px] font-bold">
                          <AlertTriangle className="w-3 h-3" />
                          Needs review
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[11px]">
                          Confirmed
                        </span>
                      )}
                    </td>
                    <td className="px-3 text-right whitespace-nowrap">
                      <div className="inline-flex items-center gap-1">
                        <Link
                          href={`/campaigns/${c.id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="h-6 px-2 bg-viz-primary hover:bg-[#00483f] text-white rounded text-[11px] font-semibold flex items-center transition-colors"
                        >
                          Open
                        </Link>
                        <button
                          onClick={(e) => e.stopPropagation()}
                          className="w-6 h-6 flex items-center justify-center text-viz-neutral hover:text-viz-text rounded hover:bg-surface-subtle"
                        >
                          <MoreVertical className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Right-Hand Campaign Detail Quick Drawer (380px wide docked §4.4 & §7.A) */}
        <aside className="w-80 xl:w-[380px] shrink-0 bg-surface-subtle border-l border-border-divider flex flex-col justify-between overflow-y-auto">
          {selectedCampaign ? (
            <div className="flex flex-col">
              {/* Drawer Header */}
              <div className="px-4 py-3 bg-surface border-b border-border-divider flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded bg-[#0B6256]/10 flex items-center justify-center text-viz-primary font-bold">
                    <FolderKanban className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-viz-neutral font-bold tracking-wider block">
                      Selected Syndicate Cluster
                    </span>
                    <h2 className="text-sm font-bold text-viz-text leading-tight">{selectedCampaign.cluster_id}</h2>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <Link
                    href={`/campaigns/${selectedCampaign.id}`}
                    className="h-7 px-2.5 bg-viz-primary hover:bg-[#00483f] text-white rounded text-xs font-semibold flex items-center gap-1 transition-colors"
                  >
                    <span>Full Workspace</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Outbreak Status Alert Banner */}
              {selectedCampaign.is_outbreak_candidate && (
                <div className="m-3 p-3 rounded bg-tone-danger-strong-bg border border-error/50 flex items-start gap-2.5">
                  <ShieldAlert className="w-5 h-5 text-error shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[11px] font-bold text-tone-danger-strong-text uppercase tracking-wide">
                      Outbreak Candidate Active
                    </div>
                    <p className="text-xs text-tone-danger-text mt-0.5 leading-snug">
                      Surge threshold exceeded: <strong>{selectedCampaign.velocity_label}</strong> with {selectedCampaign.incidents_count} confirmed victims.
                    </p>
                  </div>
                </div>
              )}

              {/* Title & Description */}
              <div className="px-4 py-2">
                <h3 className="text-sm font-bold text-viz-text">{selectedCampaign.name}</h3>
                <p className="text-xs text-viz-neutral mt-1 leading-relaxed">{selectedCampaign.description}</p>
              </div>

              {/* Financial Quantum Box */}
              <div className="px-4 py-2">
                <div className="p-3 rounded bg-surface border border-border-divider grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-[10px] uppercase font-bold text-viz-neutral">Drained Quantum</div>
                    <div className="text-base font-bold font-mono text-error mt-0.5">
                      {formatINR(selectedCampaign.financial_loss_total)}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase font-bold text-viz-neutral">Active Bank Lien</div>
                    <div className="text-base font-bold font-mono text-viz-primary mt-0.5">
                      {formatINR(selectedCampaign.financial_loss_lien)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Top Shared IOCs */}
              <div className="px-4 py-2 space-y-2">
                <div className="text-[11px] font-bold uppercase tracking-wider text-viz-neutral">
                  Top Shared Infrastructure
                </div>
                <div className="space-y-1.5 text-xs">
                  {selectedCampaign.sample_vpa && (
                    <div className="p-2 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Primary Collect VPA</span>
                      <code className="text-xs font-mono font-bold text-viz-text">{selectedCampaign.sample_vpa}</code>
                    </div>
                  )}
                  {selectedCampaign.sample_domain && (
                    <div className="p-2 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Spoofed Phishing Domain</span>
                      <code className="text-xs font-mono font-bold text-viz-text">{selectedCampaign.sample_domain}</code>
                    </div>
                  )}
                  {selectedCampaign.lac_pool && (
                    <div className="p-2 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] text-viz-neutral uppercase block font-semibold">Telephony SIM Rotation Pool</span>
                      <code className="text-xs font-mono font-bold text-viz-text">{selectedCampaign.lac_pool}</code>
                    </div>
                  )}
                </div>
              </div>

              {/* Fast Action Controls */}
              <div className="p-4 mt-2 border-t border-border-divider bg-surface space-y-2">
                <div className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider">
                  Enforcement Actions
                </div>
                <button className="w-full h-8 px-3 rounded bg-error hover:bg-[#851313] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Section 102 CrPC Lien Freeze</span>
                </button>
                <button className="w-full h-8 px-3 rounded bg-surface-subtle hover:bg-surface-container-high border border-border-control text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors">
                  <FileText className="w-3.5 h-3.5 text-viz-neutral" />
                  <span>Generate §65B BSA Evidence Packet</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-viz-neutral">Select a campaign cluster to inspect details.</div>
          )}
        </aside>
      </div>
    </div>
  );
}
