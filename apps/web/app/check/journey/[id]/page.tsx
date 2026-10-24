"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldAlert,
  ArrowRight,
  LifeBuoy,
  FileCheck2,
  Clock,
  AlertTriangle,
  Scale,
  CheckCircle2,
  ChevronLeft,
} from "lucide-react";

export default function ScamJourneyPage() {
  const params = useParams();
  const caseId = (params?.id as string) || "SG-2026-89412";
  const [stages, setStages] = useState<any[]>([]);

  useEffect(() => {
    let active = true;
    async function loadData() {
      try {
        const res = await fetch(`/api/v1/investigate?id=${encodeURIComponent(caseId)}`);
        if (res.ok) {
          const json = await res.json();
          if (active && json.journey?.stages) {
            setStages(json.journey.stages);
            return;
          }
        }
      } catch (err) {
        console.error("Failed to load journey stages:", err);
      }
      if (active) {
        setStages(fallbackStages);
      }
    }
    loadData();
    return () => {
      active = false;
    };
  }, [caseId]);

  const fallbackStages = [
    {
      num: 1,
      name: "Initial Contact",
      symbol: "●",
      symbolType: "observed",
      time: "T + 00:00",
      channel: "SMS from +91-9876543210",
      desc: "Victim receives unsolicited SMS alerting to urgent electricity power bill disconnection scheduled for tonight.",
      signals: ["Sender unverified in TRAI DLT registry", "High frequency dispatch pattern"],
    },
    {
      num: 2,
      name: "Impersonation & Fear Induction",
      symbol: "●",
      symbolType: "observed",
      time: "T + 00:15",
      channel: "Fake Discom Officer Identity",
      desc: "Adversary poses as state power authority officer, applying psychological fear of immediate utility blackout at 9:30 PM.",
      signals: ["Coercion language index: 0.94", "High threat urgency keyword match"],
    },
    {
      num: 3,
      name: "Coercive Pressure Tactic",
      symbol: "◉",
      symbolType: "reported",
      time: "T + 00:35",
      channel: "Direct Phone Call & SMS link",
      desc: "Adversary directs victim to open a shortened bit.ly URL to resolve ledger balance or face immediate disconnection penalty.",
      isCurrentStage: true,
      signals: ["Shortened redirect URL (bit.ly/elec-bill-update)", "User reported call pressure"],
    },
    {
      num: 4,
      name: "Malicious APK / Fake VPA Request",
      symbol: "○",
      symbolType: "inferred",
      time: "T + 01:10 (Inferred)",
      channel: "Android APK Trojan / VPA Intent",
      desc: "Target page attempts to push remote access APK to intercept two-factor SMS OTPs or prompts for ₹10 test verification fee.",
      signals: ["Correlated with 14 active NCRP complaints", "Known Trojan signature: RAT.Banker.v1"],
    },
    {
      num: 5,
      name: "Multi-Hop Mule Exfiltration",
      symbol: "◌",
      symbolType: "projected",
      time: "T + 01:45 (Projected)",
      channel: "NPCI UPI / IMPS Mule Swarm",
      desc: "Funds debited from victim account are split across 3 layer-1 mule accounts within 4 minutes, escalating to crypto OTC rails.",
      signals: ["Cluster Mule Velocity: ₹12.4 Lakhs/hr", "Layer-2 exit node in secondary state"],
    },
  ];

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="max-w-[1200px] mx-auto px-4 md:px-8">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li>
              <Link href={`/check/result/${caseId}`} className="hover:text-viz-primary transition-colors">
                Case #{caseId}
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Topological Scam Journey [C04]</li>
          </ol>
        </nav>

        {/* Section Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-viz-primary" />
              [C04] Progression Modeling &amp; Velocity Radar
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-on-surface tracking-tight">
              Sequential Coercion Architecture &amp; Scam Path
            </h1>
            <p className="text-xs md:text-sm text-on-surface-variant mt-1 leading-relaxed">
              ScamGraph reconstructs psychological grooming and technical exploitation stages before money enters interbank switches.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href={`/check/result/${caseId}`}
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full border border-border-control bg-surface px-4 py-1.5 text-xs font-semibold text-on-surface hover:bg-surface-subtle transition-colors shadow-sm"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Back to Summary</span>
            </Link>
            <Link
              href="/rescue"
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-tone-danger-text text-surface px-4 py-1.5 text-xs font-bold hover:bg-tone-danger-strong-text transition-colors shadow-sm"
            >
              <LifeBuoy className="h-4 w-4" />
              <span>Enter Rescue</span>
            </Link>
          </div>
        </div>

        {/* 5-Stage Topological Journey Board */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-8">
          {/* Top Status & Velocity Strip */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-b border-border-divider pb-6">
            <div className="p-3.5 bg-surface-subtle rounded-lg border border-border-divider">
              <span className="text-[10px] font-bold uppercase text-viz-neutral tracking-wider">
                Current Position
              </span>
              <div className="text-base font-bold text-viz-primary mt-0.5">
                Stage 3: Pressure Tactic
              </div>
              <span className="text-[11px] text-on-surface-variant">
                Pre-transaction threshold
              </span>
            </div>
            <div className="p-3.5 bg-surface-subtle rounded-lg border border-border-divider">
              <span className="text-[10px] font-bold uppercase text-viz-neutral tracking-wider">
                Coercion Velocity
              </span>
              <div className="text-base font-bold text-on-surface mt-0.5">
                35 Minutes to Payment Prompt
              </div>
              <span className="text-[11px] text-tone-danger-text font-semibold">
                High Grooming Speed
              </span>
            </div>
            <div className="p-3.5 bg-surface-subtle rounded-lg border border-border-divider">
              <span className="text-[10px] font-bold uppercase text-viz-neutral tracking-wider">
                Financial Boundary
              </span>
              <div className="text-base font-bold text-tone-danger-text mt-0.5">
                Not Yet Crossed
              </div>
              <span className="text-[11px] text-on-surface-variant">
                100% loss prevention opportunity
              </span>
            </div>
          </div>

          {/* Sequential Stages Stream */}
          <div className="flex flex-col gap-6 relative">
            {stages.map((stg, idx) => (
              <div key={stg.num} className="relative flex flex-col gap-3">
                {/* Boundary Divider Between Stage 3 and Stage 4 */}
                {stg.num === 4 && (
                  <div className="my-2 py-3 px-4 rounded-lg bg-tone-danger-bg border-2 border-tone-danger-strong-bg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
                    <div className="flex items-center gap-2 text-tone-danger-text">
                      <AlertTriangle className="h-5 w-5 shrink-0" />
                      <div>
                        <span className="text-xs font-bold uppercase tracking-wider block">
                          Critical Payment Boundary
                        </span>
                        <span className="text-[11px] text-tone-danger-strong-text">
                          Crossing this point initiates non-reversible UPI / IMPS banking transactions.
                        </span>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold bg-tone-danger-text text-surface px-2.5 py-1 rounded-full uppercase tracking-wider whitespace-nowrap">
                      Statutory Freeze Gate
                    </span>
                  </div>
                )}

                <div
                  className={`p-5 rounded-xl border transition-all ${
                    stg.isCurrentStage
                      ? "bg-selected-tint border-2 border-viz-primary shadow-sm"
                      : stg.symbolType === "projected"
                      ? "bg-surface-subtle border-dashed border-border-control opacity-75"
                      : "bg-surface border-border-divider"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                          stg.symbolType === "observed"
                            ? "bg-viz-primary text-on-primary"
                            : stg.symbolType === "reported"
                            ? "border-2 border-viz-primary bg-surface text-viz-primary"
                            : stg.symbolType === "inferred"
                            ? "border-2 border-dashed border-border-control text-viz-neutral"
                            : "border-2 border-dotted border-border-control text-viz-neutral"
                        }`}
                      >
                        {stg.symbol}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-on-surface">
                            Stage {stg.num}: {stg.name}
                          </span>
                          {stg.isCurrentStage && (
                            <span className="text-[10px] font-bold bg-viz-primary text-on-primary px-2 py-0.5 rounded-full uppercase tracking-wider">
                              You may be here
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-viz-neutral font-medium">
                          {stg.channel}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-mono text-viz-neutral">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{stg.time}</span>
                    </div>
                  </div>

                  <p className="text-xs text-on-surface-variant leading-relaxed mb-3">
                    {stg.desc}
                  </p>

                  <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                    <span className="text-viz-neutral font-semibold">Evidence markers:</span>
                    {stg.signals.map((sig, sIdx) => (
                      <span
                        key={sIdx}
                        className="rounded bg-surface-subtle px-2 py-0.5 border border-border-divider text-on-surface text-[10px] font-medium"
                      >
                        {sig}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Action Footer */}
          <div className="pt-4 border-t border-border-divider flex flex-wrap items-center justify-between gap-4">
            <div className="text-xs text-on-surface-variant max-w-[500px]">
              <strong>Forensic Protection Rule:</strong> Halting contact at Stage 3 permanently stops attacker monetization without any fund loss or identity exposure.
            </div>

            <div className="flex items-center gap-3">
              <Link
                href={`/rescue/package/${caseId}`}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-6 py-2 text-xs font-bold transition-all shadow-sm"
              >
                <FileCheck2 className="h-4 w-4" />
                <span>Export Case Dossier</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
