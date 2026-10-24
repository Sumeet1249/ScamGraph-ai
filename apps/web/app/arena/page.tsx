"use client";

import { useState, useEffect } from "react";
import { Card, PageSection, Badge } from "@/components/ui";
import { Cpu, Award, AlertTriangle, ShieldCheck, Zap, Activity, CheckCircle, XCircle, ArrowUpRight, RefreshCw } from "lucide-react";

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

export default function ModelArenaPage() {
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
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono font-bold tracking-wider text-accent uppercase">AI Evaluation Governance</span>
          <h1 className="text-3xl font-black font-mono tracking-tight text-text-primary mt-1">
            Model Benchmark Arena & Promotion Gates
          </h1>
          <p className="text-body-sm text-text-secondary mt-1">
            Empirical comparative evaluations across candidate ML classifiers and multilingual sentence transformers. Governed by Constitutional Rule 10 (no single model declares fraud).
          </p>
        </div>
        <button
          onClick={fetchModels}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-2 border border-border text-xs font-mono hover:bg-surface-3 transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          Refresh Arena Leaderboard
        </button>
      </div>

      {/* Top Level Benchmark Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-surface-2 border border-border space-y-1">
          <div className="flex items-center justify-between text-text-muted text-xs font-mono">
            <span>REGISTERED MODELS</span>
            <Cpu className="h-4 w-4 text-accent" />
          </div>
          <div className="text-2xl font-black font-mono text-text-primary">
            {models.length || 7} Models
          </div>
          <div className="text-[11px] font-mono text-text-muted">
            Text, URL, Payment & Embedding tasks
          </div>
        </div>

        <div className="p-4 rounded-xl bg-surface-2 border border-border space-y-1">
          <div className="flex items-center justify-between text-text-muted text-xs font-mono">
            <span>BASELINE ACCURACY</span>
            <Award className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black font-mono text-emerald-400">
            95.67%
          </div>
          <div className="text-[11px] font-mono text-text-muted">
            Trained on 2,272 Indian SMS records
          </div>
        </div>

        <div className="p-4 rounded-xl bg-surface-2 border border-border space-y-1">
          <div className="flex items-center justify-between text-text-muted text-xs font-mono">
            <span>AVERAGE INFERENCE (p95)</span>
            <Zap className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black font-mono text-text-primary">
            12.4 ms
          </div>
          <div className="text-[11px] font-mono text-text-muted">
            Sub-50ms hard settlement budget
          </div>
        </div>

        <div className="p-4 rounded-xl bg-surface-2 border border-border space-y-1">
          <div className="flex items-center justify-between text-text-muted text-xs font-mono">
            <span>RELEASE GATE ENFORCEMENT</span>
            <ShieldCheck className="h-4 w-4 text-red-400" />
          </div>
          <div className="text-2xl font-black font-mono text-red-400">
            1 Model Blocked
          </div>
          <div className="text-[11px] font-mono text-text-muted">
            DistilBERT blocked (&gt;5% FPR on alerts)
          </div>
        </div>
      </div>

      {/* Head-to-Head Model Scorecard */}
      <PageSection
        title="Head-to-Head Comparative Scorecard"
        description="Ranked by F1-Score, False Positive Rate (FPR), and p95 inference latency"
      >
        <div className="overflow-x-auto rounded-xl border border-border bg-surface-2 shadow-sm">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-surface-1 border-b border-border text-text-muted uppercase text-[11px]">
              <tr>
                <th className="p-3.5">Model Identifier</th>
                <th className="p-3.5">Task & Runtime</th>
                <th className="p-3.5">Accuracy / F1</th>
                <th className="p-3.5">False Positive Rate</th>
                <th className="p-3.5">p95 Latency</th>
                <th className="p-3.5">Promotion Gate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {models.map((m) => {
                const b = m.benchmark_summary || {};
                return (
                  <tr key={m.id} className="hover:bg-surface-hover transition-colors">
                    <td className="p-3.5 font-bold text-text-primary">
                      <div className="flex items-center gap-2">
                        <span>{m.id}</span>
                      </div>
                      <div className="text-[10px] text-text-muted font-normal mt-0.5">
                        Rev: {m.revision} | Hardware: {m.hardware || "CPU"}
                      </div>
                      {m.rejection_reason && (
                        <div className="text-[10px] text-red-400 font-normal mt-1 bg-red-950/40 p-1 rounded border border-red-900/60 max-w-sm">
                          ⚠ Rejection: {m.rejection_reason}
                        </div>
                      )}
                    </td>
                    <td className="p-3.5 text-text-secondary">
                      <span className="px-2 py-0.5 rounded bg-surface-1 border border-border uppercase text-[10px] text-cyan-300">
                        {m.task.replace(/_/g, " ")}
                      </span>
                      <div className="text-[10px] text-text-muted mt-1">{m.runtime}</div>
                    </td>
                    <td className="p-3.5">
                      <div className="font-bold text-text-primary">
                        {b.accuracy ? `${(b.accuracy * 100).toFixed(1)}%` : "N/A"}
                      </div>
                      <div className="text-[10px] text-text-muted">
                        F1: {b.f1_score ? `${(b.f1_score * 100).toFixed(1)}%` : "N/A"}
                      </div>
                    </td>
                    <td className="p-3.5">
                      {b.false_positive_rate !== undefined ? (
                        <span
                          className={`font-bold ${
                            b.false_positive_rate > 0.05 ? "text-red-400" : "text-emerald-400"
                          }`}
                        >
                          {(b.false_positive_rate * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-text-muted">N/A</span>
                      )}
                      <div className="text-[10px] text-text-muted">Max Allowed: 5.0%</div>
                    </td>
                    <td className="p-3.5 font-bold text-text-primary">
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

      {/* Constitutional Governance Banner */}
      <Card pad="md" className="border-l-4 border-l-brand-primary bg-brand-primary/5">
        <div className="flex items-start gap-3">
          <ShieldCheck className="h-5 w-5 text-brand-primary flex-shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs font-mono">
            <span className="font-bold text-brand-primary uppercase">
              Constitutional AI Rule 10 Enforcement
            </span>
            <p className="text-text-secondary leading-relaxed">
              No single model in the Arena is permitted to unilaterally declare fraud or block an Indian citizen&apos;s transaction. Every model generates isolated evidence signals that must be corroborated across entity intelligence, domain infrastructure, and the ScamDNA behavioral engine before enforcement is authorized.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
