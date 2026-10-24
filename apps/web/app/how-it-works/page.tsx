"use client";

import Link from "next/link";
import {
  Shield,
  Search,
  Scale,
  Network,
  Cpu,
  Database,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Layers,
  FileCheck2,
} from "lucide-react";

export default function HowItWorksPage() {
  const dimensions = [
    {
      num: "01",
      name: "Semantic Urgency & Impersonation NLP",
      desc: "Detects coercive Hindi/Hinglish/English keywords, fake CBI/police threats, electricity cutoff deadlines, and emotional blackmail markers.",
      icon: Search,
    },
    {
      num: "02",
      name: "Web Infrastructure & TinyFish RDAP",
      desc: "Measures domain registration age, DNS clusters, free TLD usage (.tk, .ml), and stealth redirect chains leading to remote APK downloads.",
      icon: Cpu,
    },
    {
      num: "03",
      name: "Payment Intent & VPA Discrepancy",
      desc: "Detects mismatches between purported corporate/government entities and the actual beneficiary UPI handle (e.g., electricity bill paid to private individual).",
      icon: Scale,
    },
    {
      num: "04",
      name: "Temporal Grooming Velocity",
      desc: "Tracks the elapsed time across contact stages. Attackers applying rapid acceleration to force payment within 30 minutes are flagged.",
      icon: Layers,
    },
    {
      num: "05",
      name: "Reused Infrastructure & Sender Telemetry",
      desc: "Correlates recycled mobile numbers, shared virtual servers, and SIM box clusters across multi-victim datasets.",
      icon: Network,
    },
    {
      num: "06",
      name: "Historical Incident Graph Traversal",
      desc: "Queries Neo4j property graphs to link incoming identifiers with past 1930 NCRP complaints and police notices.",
      icon: Database,
    },
    {
      num: "07",
      name: "High-Dimensional Campaign Similarity",
      desc: "Computes multilingual sentence embeddings (MiniLM-L12-v2) to match tactic variants against 38 active Indian scam syndicate clusters.",
      icon: FileCheck2,
    },
  ];

  return (
    <div className="w-full bg-ground py-10 md:py-16">
      <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">How ScamGraph Works [M02]</li>
          </ol>
        </nav>

        {/* Section Header */}
        <div className="max-w-[760px] mb-12">
          <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
            <span className="w-2 h-2 rounded-full bg-viz-primary" />
            [M02] Forensic Verification Architecture
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight mb-3">
            7-Dimensional Scam Journey Recognition
          </h1>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            Existing fraud systems check payments only at the point of settlement. ScamGraph AI reconstructs the psychological and infrastructural journey that precedes financial intent.
          </p>
        </div>

        {/* 7 Dimensions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {dimensions.map((dim) => {
            const Icon = dim.icon;
            return (
              <div
                key={dim.num}
                className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col justify-between gap-4"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-xl font-bold text-viz-primary">
                      {dim.num}
                    </span>
                    <div className="p-2 bg-surface-subtle rounded-lg text-viz-primary">
                      <Icon className="h-4 w-4" />
                    </div>
                  </div>
                  <h2 className="text-sm font-bold text-on-surface mb-1.5">
                    {dim.name}
                  </h2>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    {dim.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Dual-Axis Matrix Card */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col md:flex-row items-center justify-between gap-8 mb-12">
          <div className="max-w-[560px]">
            <span className="text-xs font-bold uppercase tracking-wider text-viz-primary">
              Core Design Rule
            </span>
            <h2 className="text-xl md:text-2xl font-bold text-on-surface mt-1 mb-2">
              Dual-Axis Risk Assessment &amp; No Single Model
            </h2>
            <p className="text-xs text-on-surface-variant leading-relaxed mb-4">
              No single machine learning model or LLM is permitted to unilaterally declare fraud. The system independently computes <strong>Risk Level</strong> (Severity of threat) and <strong>Evidence Confidence</strong> (Corroboration certainty). If data points are sparse, we default to <strong>INSUFFICIENT_EVIDENCE</strong> rather than causing false alarms.
            </p>
            <div className="flex items-center gap-2">
              <Link
                href="/check"
                className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-6 py-2 text-xs font-bold transition-all shadow-sm"
              >
                <span>Try Universal Check</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Matrix Badge Display */}
          <div className="w-full md:w-auto p-5 bg-surface-subtle rounded-xl border border-border-divider flex flex-col gap-2.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface">
              Evaluation Grid States:
            </span>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded bg-tone-info-bg px-2 py-1 font-semibold text-tone-info-text border border-tone-info-bg">
                State 1 · No strong warning signs
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded bg-surface-subtle px-2 py-1 font-semibold text-viz-neutral border border-border-control">
                State 2 · Insufficient evidence
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded bg-tone-warning-bg px-2 py-1 font-semibold text-tone-warning-text border border-tone-warning-strong-bg">
                State 4 · Be careful
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded bg-tone-danger-strong-bg px-2 py-1 font-bold text-tone-danger-strong-text border border-tone-danger-text">
                State 6 · High risk / Act now
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
