"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Play,
  Pause,
  RotateCcw,
  ArrowRight,
  Radar,
  Share2,
  Cpu,
  ShieldCheck,
  Activity,
  Layers,
  Database,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

interface StageData {
  id: number;
  title: string;
  subtitle: string;
  href: string;
  actionText: string;
  icon: any;
  metric: string;
  metricLabel: string;
  badge: string;
  description: string;
  liveSnippet: {
    event: string;
    target: string;
    engine: string;
    status: string;
  };
  impact: string;
}

const DEFENSE_STAGES: StageData[] = [
  {
    id: 1,
    title: "Radar & Alerts",
    subtitle: "Inbound threat telemetry & velocity spikes",
    href: "/radar",
    actionText: "Open Outbreak Radar",
    icon: Radar,
    metric: "3,842 /hr",
    metricLabel: "National Signal Velocity",
    badge: "STAGE 1 · INGESTION & EARLY DETECTION",
    description: "Detects early scam velocity spikes and regional surges before victims approve payments.",
    liveSnippet: {
      event: "Velocity Spike: +340% SMS surge detected in Jaipur & Delhi NCR",
      target: "Electricity Bill Disconnection Pretext",
      engine: "Regional Outbreak Telemetry Engine",
      status: "Early Warning Active",
    },
    impact: "Provides 12 to 45 minutes of critical lead time before victim transactions hit banking rails.",
  },
  {
    id: 2,
    title: "Multi-Signal Graph",
    subtitle: "Entity correlation & infrastructure clustering",
    href: "/investigate",
    actionText: "Inspect Entity Graph",
    icon: Share2,
    metric: "14 Nodes",
    metricLabel: "Active Cluster Density",
    badge: "STAGE 2 · GRAPH CORRELATION",
    description: "Correlates phone numbers, fake URLs, and UPI IDs into a unified threat graph.",
    liveSnippet: {
      event: "Cluster Match: 1 Phone + 3 Phishing Domains linked to single Syndicate",
      target: "Entity Hash: SG-ENT-94021 (Mule Network)",
      engine: "Cytoscape Graph Intelligence Engine",
      status: "Co-occurrence 98.6%",
    },
    impact: "Unmasks the syndicate behind individual phishing links and identifies root infrastructure.",
  },
  {
    id: 3,
    title: "Mule Account AI",
    subtitle: "Turnover velocity & dwell-time anomaly models",
    href: "/mulehunter",
    actionText: "Launch MuleHunter AI",
    icon: Cpu,
    metric: "19 Rules",
    metricLabel: "Behavioral Heuristics",
    badge: "STAGE 3 · FINANCIAL LAUNDERING TRAP",
    description: "Catches laundering accounts using 19 behavioral turnover and dwell-time rules.",
    liveSnippet: {
      event: "Anomaly Tripped: Dwell-time < 3m, 98% rapid fan-out across 4 VPAs",
      target: "Account: rohit.enterprises91@ybl",
      engine: "RandomForest & IsolationForest Classifiers",
      status: "Mule Probability 98.4%",
    },
    impact: "Distinguishes legitimate merchant velocity from high-turnover syndicate cash mules in real time.",
  },
  {
    id: 4,
    title: "Freeze & Recovery",
    subtitle: "Interbank holds & Section 65B legal dossiers",
    href: "/alerts",
    actionText: "Coordinate Hold & Dossier",
    icon: ShieldCheck,
    metric: "₹1,84,000",
    metricLabel: "Arrested in Layer 1",
    badge: "STAGE 4 · INTERDICTION & BSA PACKAGING",
    description: "Executes interbank account holds and exports court-admissible Section 65B dossiers.",
    liveSnippet: {
      event: "CFCFRMS Broadcast: Immediate lien requested on beneficiary bank hop",
      target: "Dossier #SG-65B-2026-8492 compiled with SHA-256 signature",
      engine: "Interbank Gateway & Statutory Evidence Packager",
      status: "Funds Frozen",
    },
    impact: "Stops laundering before cash-out and delivers tamper-evident digital evidence for police FIRs.",
  },
];

export function DefenseLifecycleMotion() {
  const [activeStageId, setActiveStageId] = useState<number>(1);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [progressPercent, setProgressPercent] = useState<number>(0);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isPlaying) {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    setProgressPercent(0);
    const duration = 4000; // 4 seconds per stage
    const tick = 50;

    progressIntervalRef.current = setInterval(() => {
      setProgressPercent((prev) => {
        if (prev >= 100) return 100;
        return prev + (tick / duration) * 100;
      });
    }, tick);

    timerRef.current = setTimeout(() => {
      setActiveStageId((curr) => (curr >= 4 ? 1 : curr + 1));
    }, duration);

    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, activeStageId]);

  const handleSelectStage = (id: number) => {
    setActiveStageId(id);
    setProgressPercent(0);
  };

  const handleTogglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const handleRestart = () => {
    setActiveStageId(1);
    setProgressPercent(0);
    setIsPlaying(true);
  };

  const currentStage = DEFENSE_STAGES.find((s) => s.id === activeStageId) || DEFENSE_STAGES[0];

  return (
    <div className="mt-6 pt-5 border-t border-slate-100">
      {/* ── Sub-header with Playback Controls ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-600 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600" />
          </span>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
            Investigation &amp; Defense Lifecycle (4 Connected Stages)
          </span>
        </div>

        {/* Player Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto bg-slate-50 p-1 rounded-xl border border-slate-200">
          <button
            type="button"
            onClick={handleTogglePlay}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-700 hover:text-blue-700 hover:bg-white transition-all shadow-none hover:shadow-xs"
            title={isPlaying ? "Pause auto-tour" : "Resume auto-tour"}
          >
            {isPlaying ? (
              <>
                <Pause className="h-3 w-3 text-blue-600" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="h-3 w-3 text-blue-600 fill-current" />
                <span>Auto-Tour</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleRestart}
            className="p-1 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-white transition-all"
            title="Restart cycle"
          >
            <RotateCcw className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* ── Connecting Progression Line (Hidden on small screens) ── */}
      <div className="relative mb-3 hidden lg:block">
        <div className="h-[2px] w-full bg-slate-100 relative">
          <div
            className="h-full bg-blue-600 transition-all duration-700 ease-out"
            style={{ width: `${((activeStageId - 1) / 3) * 100}%` }}
          />
        </div>
      </div>

      {/* ── 4 Connected Stage Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {DEFENSE_STAGES.map((stage) => {
          const isActive = activeStageId === stage.id;
          const Icon = stage.icon;

          return (
            <div
              key={stage.id}
              onClick={() => handleSelectStage(stage.id)}
              className={`p-3.5 rounded-xl border transition-all text-left cursor-pointer relative overflow-hidden group ${
                isActive
                  ? "border-blue-500 bg-blue-50/80 shadow-sm ring-1 ring-blue-500/30 scale-[1.01]"
                  : "border-blue-100 bg-blue-50/30 hover:bg-blue-50/60 hover:border-blue-200"
              }`}
            >
              {/* Active Progress Bar at top of active card */}
              {isActive && isPlaying && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-blue-100 overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-75"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              )}

              <div className="flex items-center justify-between text-xs font-bold text-blue-900 mb-1.5">
                <span className="flex items-center gap-1.5">
                  <span
                    className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold transition-colors ${
                      isActive ? "bg-blue-600 text-white shadow-xs" : "bg-blue-600 text-white"
                    }`}
                  >
                    {stage.id}
                  </span>
                  <span className="tracking-tight">{stage.title}</span>
                </span>
                <ArrowRight
                  className={`h-3.5 w-3.5 transition-transform ${
                    isActive ? "text-blue-600 translate-x-0.5" : "text-blue-400 group-hover:translate-x-0.5"
                  }`}
                />
              </div>

              <p className="text-[11px] text-slate-600 leading-snug">
                {stage.description}
              </p>

              {/* Stage Specific Mini-Metric */}
              <div className="mt-2.5 pt-2 border-t border-blue-100/60 flex items-center justify-between text-[10px] font-mono">
                <span className="text-slate-500">{stage.metricLabel}</span>
                <span className={`font-bold ${isActive ? "text-blue-700" : "text-slate-700"}`}>
                  {stage.metric}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Dynamic Live Operational Telemetry Showcase ── */}
      <div className="mt-4 rounded-xl border border-blue-100 bg-gradient-to-r from-blue-50/50 via-slate-50/60 to-blue-50/50 p-4 transition-all animate-fadeIn">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-600 text-white">
                {currentStage.badge}
              </span>
              <span className="text-[11px] font-semibold text-slate-700">
                {currentStage.subtitle}
              </span>
            </div>

            <div className="rounded-lg bg-white border border-slate-200/80 p-3 shadow-2xs space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-900 font-mono flex items-center gap-1.5 truncate">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  {currentStage.liveSnippet.event}
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap ml-2">
                  {currentStage.liveSnippet.status}
                </span>
              </div>

              <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100 gap-2">
                <span>
                  <strong className="text-slate-700">Target / Artifact:</strong> {currentStage.liveSnippet.target}
                </span>
                <span className="font-mono text-[10px] text-blue-700">
                  {currentStage.liveSnippet.engine}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-600">
              <strong className="text-slate-800">Operational Value: </strong>
              {currentStage.impact}
            </p>
          </div>

          {/* Quick CTA to jump to the actual screen */}
          <div className="shrink-0 flex sm:flex-col justify-end">
            <Link
              href={currentStage.href}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-xs font-bold text-white shadow-sm transition-all hover:translate-x-0.5"
            >
              <span>{currentStage.actionText}</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
