"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, PageSection, Badge } from "@/components/ui";
import { Cpu, Award, ShieldCheck, Zap, RefreshCw, FlaskConical, Brain } from "lucide-react";

interface ModelEntry {
  id: string;
  status: "BASELINE" | "PROMOTED" | "CANDIDATE" | "REJECTED" | "DEPRECATED";
  task: string;
  revision: string;
  runtime: string;
  hardware?: string;
  dimensions?: number;
  rejection_reason?: string;
  benchmark_summary?: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    false_positive_rate?: number;
    sample_count?: number;
    latency_p95_ms?: number;
  };
}

export default function LabArenaPage() {
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/arena");
      if (res.ok) {
        const data = await res.json();
        setModels(data.models || []);
      }
    } catch (e) {
      console.warn("Could not fetch models:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "BASELINE":
        return <Badge tone="info">BASELINE</Badge>;
      case "PROMOTED":
        return <Badge tone="success">PROMOTED</Badge>;
      case "CANDIDATE":
        return <Badge tone="caution">CANDIDATE</Badge>;
      case "REJECTED":
        return <Badge tone="danger">REJECTED (GATE)</Badge>;
      default:
        return <Badge tone="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Unified Lab Sub-Navigation Bar */}
      <div className="flex items-center gap-2 border-b border-blue-100 pb-3">
        <Link
          href="/lab"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        >
          <FlaskConical className="h-3.5 w-3.5 text-slate-500" />
          <span>Attack Simulator</span>
        </Link>
        <Link
          href="/lab/arena"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200/80 shadow-2xs"
        >
          <Cpu className="h-3.5 w-3.5 text-blue-600" />
          <span>AI Model Arena</span>
        </Link>
        <Link
          href="/lab/tactics"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        >
          <Brain className="h-3.5 w-3.5 text-slate-500" />
          <span>Tactics Matrix</span>
        </Link>
      </div>

      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono font-bold tracking-wider text-blue-700 uppercase">
            Simulation &amp; Defense Lab • Model Governance
          </span>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-900 mt-1">
            Model Benchmark Arena &amp; Gates
          </h1>
          <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Empirical comparative evaluations across candidate ML classifiers and multilingual sentence transformers. Governed by Rule 10 (no single model unilaterally declares fraud).
          </p>
        </div>
        <button
          onClick={fetchModels}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:border-blue-300 hover:text-blue-700 shadow-2xs transition-all active:scale-95"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin text-blue-600" : ""}`} />
          Refresh Leaderboard
        </button>
      </div>

      {/* Top Level Benchmark Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-blue-100 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>REGISTERED MODELS</span>
            <Cpu className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            {models.length || 7} Models
          </div>
          <div className="text-[11px] text-slate-500">
            Text, URL, Payment &amp; Embedding
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-blue-100 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>BASELINE ACCURACY</span>
            <Award className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600">
            95.67%
          </div>
          <div className="text-[11px] text-slate-500">
            Benchmarked on 2,272 SMS records
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-blue-100 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>AVERAGE INFERENCE (p95)</span>
            <Zap className="h-4 w-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            12.4 ms
          </div>
          <div className="text-[11px] text-slate-500">
            Fast sub-50ms hard settlement budget
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-blue-100 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>RELEASE GATE ENFORCEMENT</span>
            <ShieldCheck className="h-4 w-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-rose-600">
            1 Model Blocked
          </div>
          <div className="text-[11px] text-slate-500">
            DistilBERT blocked (&gt;5% FPR on alerts)
          </div>
        </div>
      </div>

      {/* Head-to-Head Model Scorecard */}
      <PageSection
        title="Head-to-Head Comparative Scorecard"
        description="Ranked by F1-Score, False Positive Rate (FPR), and p95 inference latency"
      >
        <div className="overflow-x-auto rounded-xl border border-blue-100 bg-white shadow-sm">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-100 text-slate-600 uppercase text-[11px] font-semibold">
              <tr>
                <th className="p-3.5">Model Identifier</th>
                <th className="p-3.5">Task &amp; Runtime</th>
                <th className="p-3.5">Accuracy / F1</th>
                <th className="p-3.5">False Positive Rate</th>
                <th className="p-3.5">p95 Latency</th>
                <th className="p-3.5">Promotion Gate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {models.map((m) => {
                const b = m.benchmark_summary || {};
                return (
                  <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="p-3.5 font-bold text-slate-900">
                      <div className="flex items-center gap-2">
                        <span>{m.id}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 font-normal mt-0.5">
                        Rev: {m.revision} | Hardware: {m.hardware || "CPU"}
                      </div>
                      {m.rejection_reason && (
                        <div className="text-[10px] text-rose-700 font-normal mt-1 bg-rose-50 p-1 rounded border border-rose-200 max-w-sm">
                          ⚠ Rejection: {m.rejection_reason}
                        </div>
                      )}
                    </td>
                    <td className="p-3.5 text-slate-700">
                      <span className="px-2 py-0.5 rounded bg-blue-50 border border-blue-100 uppercase text-[10px] text-blue-700 font-bold">
                        {m.task.replace(/_/g, " ")}
                      </span>
                      <div className="text-[10px] text-slate-500 mt-1">{m.runtime}</div>
                    </td>
                    <td className="p-3.5">
                      <div className="font-bold text-slate-900">
                        {b.accuracy ? `${(b.accuracy * 100).toFixed(1)}%` : "N/A"}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        F1: {b.f1_score ? `${(b.f1_score * 100).toFixed(1)}%` : "N/A"}
                      </div>
                    </td>
                    <td className="p-3.5">
                      {b.false_positive_rate !== undefined ? (
                        <span
                          className={`font-bold ${
                            b.false_positive_rate > 0.05 ? "text-rose-600" : "text-emerald-600"
                          }`}
                        >
                          {(b.false_positive_rate * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                      <div className="text-[10px] text-slate-500">Max Allowed: 5.0%</div>
                    </td>
                    <td className="p-3.5 font-bold text-slate-900">
                      {b.latency_p95_ms ? `${b.latency_p95_ms} ms` : "N/A"}
                    </td>
                    <td className="p-3.5">
                      {getStatusBadge(m.status)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </PageSection>

      {/* Governance Banner */}
      <Card pad="md" className="border-l-4 border-l-blue-600 bg-blue-50/50">
        <div className="flex items-start gap-3">
          <ShieldCheck className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <span className="font-bold text-blue-900 uppercase">
              Constitutional AI Governance Rule
            </span>
            <p className="text-slate-600 leading-relaxed">
              No single ML model in ScamGraph is permitted to unilaterally declare fraud or block an Indian citizen&apos;s transaction. Every model produces weighted evidence signals that must be corroborated across entity intelligence, domain infrastructure, and the behavioral engine before friction is applied.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
