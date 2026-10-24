"use client";

import { useState, useEffect } from "react";
import { Card, Button, Badge } from "@/components/ui";
import { ChevronRight, RotateCcw, CheckCircle, AlertCircle, TrendingUp } from "lucide-react";

interface StepStimulus {
  channel?: string;
  timestamp?: string;
  sender?: string;
  text?: string;
  domain?: string;
  url?: string;
  page_title?: string;
  [key: string]: any;
}

interface SimulationStep {
  session_id: string;
  scenario_id: string;
  step_id: string;
  title: string;
  description: string;
  stimulus_type: "message" | "website" | "phone_call" | "payment_request" | "verification_form" | "agent_conversation";
  stimulus_content: StepStimulus;
  decision_prompt: string;
  decision_options: Array<{
    decision: string;
    label: string;
    hint?: string;
  }>;
  progress: {
    current_step: number;
    total_steps: number;
    percentage: number;
  };
}

interface SimulationDecisionResult {
  session_id: string;
  step_id: string;
  decision: string;
  outcome_text: string;
  is_safer_decision: boolean;
  risk_score: number;
  risk_level: string;
  feedback: string;
  next_step?: SimulationStep | null;
  session_completed: boolean;
  signals_generated: Array<any>;
  counterfactual_outcomes: Record<string, any>;
}

interface Props {
  sessionId: string;
  scenarioId: string;
  onComplete?: (debrief: any) => void;
}

export function SimulationSession({ sessionId, scenarioId, onComplete }: Props) {
  const [currentStep, setCurrentStep] = useState<SimulationStep | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationDecisionResult | null>(null);
  const [sessionEnded, setSessionEnded] = useState(false);

  // Fetch initial step
  useEffect(() => {
    const loadFirstStep = async () => {
      try {
        const res = await fetch("/api/v1/simulator/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scenario_id: scenarioId,
            user_id: "user_training_session",
            language: "en",
          }),
        });
        const data = await res.json();
        setCurrentStep(data.first_step);
      } catch (err) {
        console.error("Failed to start simulation:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadFirstStep();
  }, [scenarioId]);

  const handleDecision = async (decision: string) => {
    if (!currentStep) return;

    setSelectedDecision(decision);
    setIsLoading(true);

    try {
      const res = await fetch("/api/v1/simulator/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          step_id: currentStep.step_id,
          decision: decision,
        }),
      });
      const data: SimulationDecisionResult = await res.json();
      setResult(data);

      // If scenario is complete, fetch debrief
      if (data.session_completed) {
        setSessionEnded(true);
        // Fetch debrief in a moment
        setTimeout(() => {
          fetchDebrief(data.session_id);
        }, 2000);
      }
    } catch (err) {
      console.error("Failed to process decision:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDebrief = async (sessionId: string) => {
    try {
      const res = await fetch(`/api/v1/simulator/debrief/${sessionId}`);
      const debrief = await res.json();
      onComplete?.(debrief);
    } catch (err) {
      console.error("Failed to fetch debrief:", err);
    }
  };

  const handleContinue = () => {
    if (result?.next_step) {
      setCurrentStep(result.next_step);
      setResult(null);
      setSelectedDecision(null);
    }
  };

  if (isLoading && !currentStep) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-border-strong border-t-brand-primary" />
          </div>
          <p className="text-body text-text-secondary">Loading scenario...</p>
        </div>
      </div>
    );
  }

  // Show decision outcome and feedback
  if (result) {
    return (
      <div className="space-y-6">
        {/* Outcome Banner */}
        <Card pad="lg" className={`border-l-4 ${result.is_safer_decision ? "border-l-success bg-success/5" : "border-l-danger bg-danger/5"}`}>
          <div className="flex items-start gap-4">
            {result.is_safer_decision ? (
              <CheckCircle className="h-6 w-6 text-success flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="h-6 w-6 text-danger flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <h3 className="font-semibold text-h3 mb-2">
                {result.is_safer_decision ? "Safer Decision" : "Risky Decision"}
              </h3>
              <p className="text-body text-text-secondary mb-3">{result.outcome_text}</p>
              <p className="text-body-sm text-text-secondary italic">{result.feedback}</p>
            </div>
          </div>
        </Card>

        {/* Risk Context */}
        <div className="grid grid-cols-2 gap-4">
          <Card pad="md">
            <p className="text-label text-text-muted uppercase mb-2">Risk Score</p>
            <p className={`text-h2 font-bold ${result.risk_level === "CRITICAL" || result.risk_level === "HIGH" ? "text-danger" : result.risk_level === "MEDIUM" ? "text-warning" : "text-success"}`}>
              {result.risk_score}/100
            </p>
            <p className="text-caption text-text-muted mt-1">{result.risk_level}</p>
          </Card>
          <Card pad="md" className="bg-surface-2">
            <p className="text-label text-text-muted uppercase mb-2">Decision Impact</p>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-warning" />
              <p className="text-body-sm">{result.is_safer_decision ? "Risk Reduced" : "Risk Increased"}</p>
            </div>
          </Card>
        </div>

        {/* What-If Counterfactuals */}
        {Object.keys(result.counterfactual_outcomes).length > 0 && (
          <Card pad="lg" className="border border-border-strong">
            <p className="text-label text-text-muted uppercase mb-4">What If?</p>
            <div className="space-y-2">
              {Object.entries(result.counterfactual_outcomes).map(([alt_decision, alt_result]: [string, any]) => (
                <div key={alt_decision} className="flex items-center justify-between rounded-lg bg-surface-2 p-3">
                  <span className="text-body-sm font-semibold text-text-secondary">{alt_decision.replace(/_/g, " ")}</span>
                  <span className="text-body-sm font-bold">{alt_result.risk_score}/100</span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Continue or Complete */}
        {sessionEnded ? (
          <Card pad="lg" className="bg-surface-2">
            <p className="text-body font-semibold text-text-primary">Scenario Complete</p>
            <p className="text-body-sm text-text-secondary mt-2">Review your debrief to see learning points and recovery guidance.</p>
          </Card>
        ) : (
          <Button variant="primary" className="w-full" onClick={handleContinue} disabled={isLoading || !result.next_step}>
            Continue to Next Step
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>
    );
  }

  // Show current step with decision prompt
  if (currentStep) {
    return (
      <div className="space-y-6">
        {/* Progress */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-2 bg-surface-2 rounded-full overflow-hidden">
              <div
                className="h-full bg-brand-primary transition-all duration-500"
                style={{ width: `${currentStep.progress.percentage}%` }}
              />
            </div>
          </div>
          <p className="text-caption text-text-muted ml-3">
            Step {currentStep.progress.current_step} of {currentStep.progress.total_steps}
          </p>
        </div>

        {/* Stimulus Card */}
        <Card pad="lg" className="border-l-4 border-l-brand-primary">
          <p className="text-label text-text-muted uppercase mb-2">{currentStep.stimulus_type}</p>
          <h2 className="text-h2 font-bold mb-4">{currentStep.title}</h2>
          <p className="text-body text-text-secondary mb-6">{currentStep.description}</p>

          {/* Render stimulus based on type */}
          <RenderStimulus stimulus={currentStep.stimulus_content} type={currentStep.stimulus_type} />
        </Card>

        {/* Decision Prompt */}
        <Card pad="lg">
          <p className="text-label text-text-muted uppercase mb-4">Your Decision</p>
          <p className="text-body font-semibold mb-4">{currentStep.decision_prompt}</p>

          <div className="space-y-3">
            {currentStep.decision_options.map((option) => (
              <button
                key={option.decision}
                onClick={() => handleDecision(option.decision)}
                disabled={isLoading || selectedDecision === option.decision}
                className={`w-full rounded-lg p-4 text-left transition-all border ${
                  selectedDecision === option.decision
                    ? "bg-brand-primary text-on-brand border-transparent font-medium"
                    : "bg-surface text-text-primary hover:bg-surface-hover border-border-input"
                } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
              >
                <p className="font-semibold">{option.label}</p>
                {option.hint && (
                  <p className="text-body-sm opacity-75 mt-1">{option.hint}</p>
                )}
              </button>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  return (
    <Card pad="lg" className="text-center">
      <p className="text-body text-text-secondary">Failed to load simulation scenario</p>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

interface RenderStimulusProps {
  stimulus: StepStimulus;
  type: string;
}

function RenderStimulus({ stimulus, type }: RenderStimulusProps) {
  switch (type) {
    case "message":
      return (
        <div className="rounded-lg bg-surface-1 p-4 border border-border">
          <div className="flex items-center justify-between mb-3">
            <p className="text-caption font-semibold text-text-muted uppercase">
              {stimulus.channel || "Message"}
            </p>
            {stimulus.timestamp && (
              <p className="text-caption text-text-muted">{stimulus.timestamp}</p>
            )}
          </div>
          {stimulus.sender && (
            <p className="text-body-sm text-text-muted mb-3">From: {stimulus.sender}</p>
          )}
          <p className="text-body p-4 bg-background rounded border-l-4 border-l-caution">
            &quot;{stimulus.text}&quot;
          </p>
        </div>
      );

    case "website":
      return (
        <div className="rounded-lg bg-surface-1 p-6 border border-border">
          <div className="mb-4 pb-4 border-b border-border">
            <p className="text-caption text-text-muted mb-1">Domain</p>
            <p className="text-mono text-body-sm text-text-primary font-semibold">
              {stimulus.domain}
            </p>
          </div>
          <h3 className="text-h3 font-bold mb-4">{stimulus.page_title}</h3>
          <p className="text-body text-text-secondary mb-6">{stimulus.page_content?.header}</p>
          {stimulus.page_content?.notice && (
            <div className="rounded-lg bg-caution/10 p-4 mb-6 border-l-4 border-l-caution">
              <p className="text-body-sm text-caution font-semibold">
                {stimulus.page_content.notice}
              </p>
            </div>
          )}
          {stimulus.suspicious_indicators && (
            <div className="rounded-lg bg-danger/10 p-4 border border-danger/30">
              <p className="text-label text-danger uppercase mb-3 font-semibold">Suspicious indicators:</p>
              <ul className="space-y-2">
                {stimulus.suspicious_indicators.map((indicator: string, idx: number) => (
                  <li key={idx} className="text-body-sm text-danger flex items-start gap-2">
                    <span className="font-bold mt-1">•</span>
                    <span>{indicator}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );

    case "payment_request":
      return (
        <div className="rounded-lg bg-surface-1 p-6 border border-border">
          <p className="text-label text-text-muted uppercase mb-4">Payment Details</p>
          <div className="space-y-4">
            {Object.entries(stimulus.transaction_details || {}).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between pb-3 border-b border-border">
                <p className="text-body-sm text-text-muted capitalize">{key.replace(/_/g, " ")}</p>
                <p className="text-body font-semibold text-text-primary">{String(value)}</p>
              </div>
            ))}
          </div>
          {stimulus.transaction_warning && (
            <div className="rounded-lg bg-danger/10 p-4 mt-4 border-l-4 border-l-danger">
              <p className="text-body-sm text-danger font-semibold">{stimulus.transaction_warning}</p>
            </div>
          )}
        </div>
      );

    default:
      return (
        <div className="rounded-lg bg-surface-1 p-4 border border-border">
          <p className="text-body text-text-secondary">{JSON.stringify(stimulus, null, 2)}</p>
        </div>
      );
  }
}
