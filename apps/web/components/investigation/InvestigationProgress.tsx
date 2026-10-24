"use client";

import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useInvestigationProgress } from "@/lib/hooks/useInvestigationProgress";
import type { ProgressStep } from "@/lib/hooks/useInvestigationProgress";

const statusIcon: Record<ProgressStep["status"], React.ReactNode> = {
  complete: <CheckCircle2 className="h-4 w-4 text-safe" />,
  active: <Loader2 className="h-4 w-4 animate-spin text-accent" />,
  pending: <Circle className="h-4 w-4 text-ink-dim" />,
  error: <XCircle className="h-4 w-4 text-danger" />,
};

/**
 * GSAP-driven investigation progress screen. Steps reveal sequentially; only
 * a step the engine has confirmed is marked complete (never fabricated).
 * Phase 1: renders the step architecture. Phase 2 wires statuses to the API.
 */
export function InvestigationProgress() {
  const { steps, containerRef } = useInvestigationProgress();

  return (
    <div className="panel-elevated p-6">
      <div className="eyebrow mb-4">Investigating Incident</div>
      <div ref={containerRef} className="space-y-1">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3 py-1.5">
            <span className="shrink-0">{statusIcon[step.status]}</span>
            <span
              className={cn(
                "text-sm transition-colors",
                step.status === "complete" && "text-ink",
                step.status === "active" && "text-ink font-medium",
                step.status === "pending" && "text-ink-dim",
                step.status === "error" && "text-danger",
              )}
            >
              {step.label}
            </span>
            {step.status === "active" && (
              <span className="ml-auto font-mono text-[10px] text-ink-dim">in progress</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
