"use client";

import { useRef } from "react";
import { useJourneyAnimation } from "@/lib/hooks/useJourneyAnimation";
import { humanizeStage } from "@/lib/utils/format";
import { JourneyNode } from "./JourneyNode";
import type { ScamJourney } from "@/lib/api/types";

/**
 * Vertical scam journey timeline. Nodes reveal sequentially via GSAP
 * (useJourneyAnimation). The current stage is marked "You are here".
 * If the backend provides a predicted next stage, we show it as a common
 * progression — never as a definitive attacker prediction.
 */
export function JourneyTimeline({ journey }: { journey: ScamJourney }) {
  const { ref } = useJourneyAnimation(journey.steps);
  const lastIndex = journey.steps.length - 1;

  return (
    <div ref={ref as React.RefObject<HTMLDivElement>} className="space-y-6">
      <div>
        <div className="eyebrow mb-2">Scam Journey</div>
        <div className="text-sm text-ink-muted">
          {journey.steps.length} events reconstructed · current stage{" "}
          <span className="font-medium text-ink">{humanizeStage(journey.current_stage)}</span>
        </div>
      </div>

      <ol className="relative">
        {/* vertical rail */}
        <span className="absolute left-[7px] top-2 bottom-2 w-px bg-line" aria-hidden />
        {journey.steps.map((step, i) => (
          <JourneyNode key={step.step_id} step={step} isCurrent={i === lastIndex} />
        ))}
      </ol>

      {journey.prediction && (
        <div className="panel p-4">
          <div className="eyebrow mb-1">Common next stage for matched workflow</div>
          <p className="text-sm text-ink">
            {humanizeStage(journey.prediction.predicted_next_stage)}
          </p>
          <p className="mt-1 text-xs text-ink-dim">{journey.prediction.rationale}</p>
          <p className="mt-2 text-xs text-ink-muted">
            <span className="font-medium">Recommended action:</span>{" "}
            {journey.prediction.recommended_preventive_action}
          </p>
        </div>
      )}
    </div>
  );
}
