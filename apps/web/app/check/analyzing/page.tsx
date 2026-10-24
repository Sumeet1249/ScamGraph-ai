"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Shield,
  CheckCircle2,
  Loader2,
  Lock,
  ArrowRight,
  Database,
  Search,
  Cpu,
  Network,
} from "lucide-react";

interface StepItem {
  id: number;
  title: string;
  desc: string;
  icon: any;
  status: "pending" | "running" | "completed";
  duration: number;
}

function AnalysisProcessingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentStep, setCurrentStep] = useState(0);
  const [isDone, setIsDone] = useState(false);
  const [caseId, setCaseId] = useState<string>("SG-2026-89412");

  const queryContent = searchParams.get("content") || "Suspicious electricity bill update SMS";
  const entityType = searchParams.get("type") || "Message with a link";

  // Trigger real-time forensic API call on mount
  useEffect(() => {
    let active = true;

    async function triggerInvestigation() {
      try {
        let attachedFiles: any[] = [];
        if (typeof window !== "undefined") {
          try {
            const raw = sessionStorage.getItem("sg_active_evidence_files");
            if (raw) attachedFiles = JSON.parse(raw);
          } catch (e) {
            console.error("Failed to read cached files:", e);
          }
        }

        const res = await fetch("/api/v1/investigate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content: queryContent,
            type: entityType,
            attached_files: attachedFiles,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          if (active && data.incident_id) {
            setCaseId(data.incident_id);
          }
        }
      } catch (err) {
        console.error("Forensic analysis dispatch error:", err);
      }
    }

    triggerInvestigation();

    return () => {
      active = false;
    };
  }, [queryContent, entityType]);

  const steps: StepItem[] = [
    {
      id: 1,
      title: "Semantic Coercion & Urgency Parsing",
      desc: "Extracting fear triggers, fake administrative authority markers, and deadline tokens.",
      icon: Search,
      status: currentStep > 0 ? "completed" : currentStep === 0 ? "running" : "pending",
      duration: 700,
    },
    {
      id: 2,
      title: "Infrastructure & Domain Forensics",
      desc: "Checking domain registration age, DNS clusters, and redirect hops.",
      icon: Cpu,
      status: currentStep > 1 ? "completed" : currentStep === 1 ? "running" : "pending",
      duration: 800,
    },
    {
      id: 3,
      title: "Mule Account & NPCI Rail Correlation",
      desc: "Traversing Graph Neural Network (GNN) 6-hop mule rings across known syndicates.",
      icon: Network,
      status: currentStep > 2 ? "completed" : currentStep === 2 ? "running" : "pending",
      duration: 800,
    },
    {
      id: 4,
      title: "Campaign Vector Fusion & Risk Decision",
      desc: "Cosine similarity against 1.4M Indian fraud events & Section 65B hash generation.",
      icon: Database,
      status: currentStep > 3 ? "completed" : currentStep === 3 ? "running" : "pending",
      duration: 700,
    },
  ];

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (currentStep < 4) {
      timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, steps[currentStep]?.duration || 750);
    } else {
      setIsDone(true);
      // Auto redirect to C03 Result after completion with real case ID
      timer = setTimeout(() => {
        router.push(`/check/result/${caseId}`);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [currentStep, router, caseId]);

  return (
    <div className="w-full bg-ground py-12 md:py-16">
      <div className="max-w-[760px] mx-auto px-4 md:px-8">
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-6">
          {/* Header */}
          <div className="flex flex-col gap-1 border-b border-border-divider pb-4">
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-viz-primary animate-ping" />
              [C02] Multi-Signal Forensic Pipeline
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-on-surface">
              Analyzing Threat Telemetry &amp; Progression Markers
            </h1>
            <p className="text-xs text-on-surface-variant line-clamp-1">
              Target query: &ldquo;{queryContent}&rdquo;
            </p>
          </div>

          {/* Stepper Progress Visualizer */}
          <div className="flex flex-col gap-4">
            {steps.map((s, idx) => {
              const Icon = s.icon;
              return (
                <div
                  key={s.id}
                  className={`flex items-start gap-4 p-4 rounded-lg border transition-all ${
                    s.status === "completed"
                      ? "bg-surface border-border-divider shadow-xs"
                      : s.status === "running"
                      ? "bg-selected-tint border-viz-primary shadow-sm"
                      : "bg-surface-subtle border-transparent opacity-60"
                  }`}
                >
                  <div className="mt-0.5 shrink-0">
                    {s.status === "completed" ? (
                      <CheckCircle2 className="h-5 w-5 text-viz-primary" />
                    ) : s.status === "running" ? (
                      <Loader2 className="h-5 w-5 text-viz-primary animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-border-control flex items-center justify-center text-[10px] text-viz-neutral font-bold">
                        {s.id}
                      </div>
                    )}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h2 className="text-xs font-bold text-on-surface">{s.title}</h2>
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-viz-neutral">
                        {s.status === "completed"
                          ? "Verified"
                          : s.status === "running"
                          ? "Executing..."
                          : "Queued"}
                      </span>
                    </div>
                    <p className="text-[11px] text-on-surface-variant mt-0.5 leading-relaxed">
                      {s.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer Action & Status Bar */}
          <div className="pt-4 border-t border-border-divider flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-viz-neutral text-[11px]">
              <Lock className="h-3.5 w-3.5 text-viz-primary" />
              <span>Zero plain credentials logged. ISO 27001 encrypted pipeline.</span>
            </div>

            {isDone ? (
              <button
                type="button"
                onClick={() => router.push(`/check/result/${caseId}`)}
                className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <span>View Result Dossier</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            ) : (
              <span className="text-[11px] font-semibold text-viz-primary animate-pulse">
                Evaluating against 1,420,850 Indian fraud events...
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisProcessingPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full min-h-[60vh] flex items-center justify-center bg-ground">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 text-viz-primary animate-spin" />
            <p className="text-xs font-semibold text-on-surface-variant">Initializing multi-modal inspection pipeline...</p>
          </div>
        </div>
      }
    >
      <AnalysisProcessingContent />
    </Suspense>
  );
}
