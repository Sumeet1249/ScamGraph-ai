"use client";

import { useState, useEffect } from "react";
import { Card, Button, Badge } from "@/components/ui";
import {
  ChevronRight,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Phone,
  Globe,
  MessageSquare,
  ShieldCheck,
  ShieldAlert,
  CreditCard,
  KeyRound,
  AlertTriangle,
  ArrowRight,
  Lock,
  ExternalLink,
} from "lucide-react";

interface StepStimulus {
  channel?: string;
  timestamp?: string;
  sender?: string;
  text?: string;
  domain?: string;
  url?: string;
  page_title?: string;
  page_content?: {
    header?: string;
    notice?: string;
    form_fields?: Array<{ label: string; placeholder?: string; required?: boolean }>;
    [key: string]: any;
  };
  suspicious_indicators?: string[];
  caller_display?: string;
  caller?: string;
  transcript?: Array<{ speaker: string; text: string }>;
  call_transcript?: Array<string | { speaker: string; text: string }>;
  scenario?: string;
  upi_screen?: string;
  transaction?: {
    to?: string;
    amount?: string;
    purpose?: string;
    payee_name?: string;
    warning?: string;
  };
  transaction_details?: Record<string, any>;
  transaction_warning?: string;
  form_fields?: Array<{ label: string; value_entered?: string; placeholder?: string }>;
  checklist?: Array<{ action: string; details?: string; status?: string }>;
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
  counterfactual_outcomes?: Record<string, any> | null;
}

interface Props {
  sessionId: string;
  scenarioId: string;
  onComplete?: (debrief: any) => void;
}

export function SimulationSession({ sessionId, scenarioId, onComplete }: Props) {
  const [activeSessionId, setActiveSessionId] = useState<string>(sessionId);
  const [currentStep, setCurrentStep] = useState<SimulationStep | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationDecisionResult | null>(null);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  // Initialize simulation session
  useEffect(() => {
    let isMounted = true;
    const loadFirstStep = async () => {
      setIsLoading(true);
      setErrorNotice(null);
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

        if (!res.ok) {
          throw new Error(`Failed to start simulation (${res.status})`);
        }

        const data = await res.json();
        if (isMounted) {
          if (data.session_id) {
            setActiveSessionId(data.session_id);
          }
          setCurrentStep(data.first_step);
        }
      } catch (err: any) {
        if (isMounted) {
          console.error("Failed to start simulation:", err);
          setErrorNotice(err.message || "Failed to load simulation scenario.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadFirstStep();
    return () => {
      isMounted = false;
    };
  }, [scenarioId]);

  const handleDecision = async (decision: string) => {
    if (!currentStep) return;

    setSelectedDecision(decision);
    setIsLoading(true);
    setErrorNotice(null);

    const currentSid = activeSessionId || sessionId;

    try {
      const res = await fetch("/api/v1/simulator/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: currentSid,
          step_id: currentStep.step_id,
          decision: decision,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(errJson.detail || errJson.error || "Decision processing failed");
      }

      const data: SimulationDecisionResult = await res.json();
      setResult(data);

      // Determine if scenario has reached completion
      const isComplete = data.session_completed || !data.next_step;
      if (isComplete) {
        setSessionEnded(true);
        setTimeout(() => {
          fetchDebrief(data.session_id || currentSid);
        }, 1500);
      }
    } catch (err: any) {
      console.error("Failed to process decision:", err);
      setErrorNotice(err.message || "Failed to submit decision. Please retry.");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDebrief = async (sid: string) => {
    try {
      const res = await fetch(`/api/v1/simulator/debrief/${sid}`);
      if (res.ok) {
        const debrief = await res.json();
        onComplete?.(debrief);
      } else {
        // Fallback debrief if backend endpoint is unavailable
        onComplete?.({
          scenario_title: currentStep?.title || "Simulation Scenario",
          performance_score: result?.is_safer_decision ? 85 : 40,
          final_risk_score: result?.risk_score ?? 60,
          final_risk_level: result?.risk_level ?? "MEDIUM",
          decision_count: 3,
          duration_seconds: 45,
          learning_points: [
            "Always inspect external links and domain certificates before interacting.",
            "Verify claims directly with official customer care numbers from past bills.",
            "Never approve payments or disclose OTPs under social pressure.",
          ],
        });
      }
    } catch (err) {
      console.error("Failed to fetch debrief:", err);
    }
  };

  const handleContinue = () => {
    if (result?.next_step) {
      setCurrentStep(result.next_step);
      setResult(null);
      setSelectedDecision(null);
    } else {
      // Reached end of path without next step
      fetchDebrief(activeSessionId || sessionId);
    }
  };

  if (isLoading && !currentStep) {
    return (
      <div className="flex items-center justify-center py-24 rounded-2xl border border-border bg-surface-1">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="h-9 w-9 animate-spin rounded-full border-2 border-border-strong border-t-brand-primary" />
          </div>
          <p className="text-sm font-medium text-text-secondary">Initializing simulation sandbox...</p>
        </div>
      </div>
    );
  }

  // Show error notice if initialization or decision failed
  if (errorNotice && !result && !currentStep) {
    return (
      <Card pad="lg" className="border border-danger/40 bg-danger/5 text-center py-12">
        <AlertTriangle className="h-8 w-8 text-danger mx-auto mb-3" />
        <h3 className="text-base font-semibold text-text-primary mb-1">Scenario Encountered an Issue</h3>
        <p className="text-xs text-text-secondary max-w-md mx-auto mb-5">{errorNotice}</p>
        <Button variant="secondary" size="sm" onClick={() => window.location.reload()}>
          <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
          Reload Workbench
        </Button>
      </Card>
    );
  }

  // Decision outcome & feedback state
  if (result) {
    const isTerminated = sessionEnded || !result.next_step;
    return (
      <div className="space-y-6 animate-fadeIn">
        {/* Outcome Banner */}
        <div
          className={`rounded-2xl p-6 border transition-all ${
            result.is_safer_decision
              ? "border-emerald-500/40 bg-emerald-500/10 text-text-primary"
              : "border-rose-500/40 bg-rose-500/10 text-text-primary"
          }`}
        >
          <div className="flex items-start gap-4">
            <div
              className={`p-2.5 rounded-xl ${
                result.is_safer_decision ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"
              }`}
            >
              {result.is_safer_decision ? (
                <ShieldCheck className="h-6 w-6" />
              ) : (
                <ShieldAlert className="h-6 w-6" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1.5">
                <span
                  className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                    result.is_safer_decision ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                  }`}
                >
                  {result.is_safer_decision ? "Safe Decision" : "Vulnerability Exploited"}
                </span>
              </div>
              <h3 className="font-semibold text-lg text-text-primary mb-2">{result.outcome_text}</h3>
              <p className="text-xs text-text-secondary leading-relaxed bg-surface-1/60 p-3 rounded-lg border border-border">
                💡 <span className="font-medium text-text-primary">Debrief Feedback:</span> {result.feedback}
              </p>
            </div>
          </div>
        </div>

        {/* Risk & Impact Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <Card pad="md" className="border border-border bg-surface-1">
            <span className="eyebrow text-text-muted">Calculated Risk Score</span>
            <div className="flex items-baseline gap-2 mt-2">
              <p
                className={`text-2xl font-bold font-mono ${
                  result.risk_level === "CRITICAL" || result.risk_level === "HIGH"
                    ? "text-rose-400"
                    : result.risk_level === "MEDIUM"
                    ? "text-amber-400"
                    : "text-emerald-400"
                }`}
              >
                {result.risk_score}/100
              </p>
              <span className="text-xs font-mono uppercase text-text-muted">[{result.risk_level}]</span>
            </div>
          </Card>

          <Card pad="md" className="border border-border bg-surface-1">
            <span className="eyebrow text-text-muted">Trajectory Impact</span>
            <div className="flex items-center gap-2.5 mt-2">
              <TrendingUp
                className={`h-5 w-5 ${result.is_safer_decision ? "text-emerald-400 rotate-180" : "text-rose-400"}`}
              />
              <span className="text-sm font-semibold text-text-primary">
                {result.is_safer_decision ? "Attack Surface Mitigated" : "Attacker Leverage Escalated"}
              </span>
            </div>
          </Card>
        </div>

        {/* What-If Counterfactual Matrix */}
        {result.counterfactual_outcomes && Object.keys(result.counterfactual_outcomes).length > 0 && (
          <Card pad="md" className="border border-border-strong bg-surface-1">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-border">
              <span className="eyebrow text-text-muted">Counterfactual Analysis (Alternative Decisions)</span>
              <span className="text-[11px] text-text-muted">Compare Path Outcomes</span>
            </div>
            <div className="space-y-2">
              {Object.entries(result.counterfactual_outcomes).map(([alt_decision, alt_result]: [string, any]) => (
                <div
                  key={alt_decision}
                  className="flex items-center justify-between rounded-lg bg-surface-2/70 p-3 text-xs border border-border/50"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-text-primary font-medium capitalize">
                      {alt_decision.replace(/_/g, " ")}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-text-muted truncate max-w-xs">{alt_result?.outcome}</span>
                    <span
                      className={`font-mono font-bold px-1.5 py-0.5 rounded ${
                        (alt_result?.risk_score ?? 50) >= 60
                          ? "bg-rose-500/20 text-rose-300"
                          : "bg-emerald-500/20 text-emerald-300"
                      }`}
                    >
                      {alt_result?.risk_score ?? "N/A"}/100
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Navigation / Completion Action */}
        {isTerminated ? (
          <div className="rounded-xl border border-border bg-surface-2 p-5 text-center space-y-3">
            <CheckCircle className="h-6 w-6 text-emerald-400 mx-auto" />
            <h4 className="text-sm font-semibold text-text-primary">Scenario Path Complete</h4>
            <p className="text-xs text-text-secondary max-w-md mx-auto">
              Your decision path has concluded. Generating post-simulation analytical debrief and behavioral score.
            </p>
            <Button
              variant="primary"
              className="mt-2 w-full sm:w-auto"
              onClick={() => fetchDebrief(activeSessionId || sessionId)}
            >
              View Full Debrief Report
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        ) : (
          <Button
            variant="primary"
            className="w-full py-3"
            onClick={handleContinue}
            disabled={isLoading || !result.next_step}
          >
            Continue to Next Step
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        )}
      </div>
    );
  }

  // Active step prompt state
  if (currentStep) {
    return (
      <div className="space-y-6 animate-fadeIn">
        {/* Progress Tracker */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden border border-border/40">
              <div
                className="h-full bg-brand-primary transition-all duration-500 rounded-full"
                style={{ width: `${Math.max(10, currentStep.progress?.percentage || 25)}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] font-mono text-text-muted whitespace-nowrap">
            Step {currentStep.progress?.current_step || 1} of {currentStep.progress?.total_steps || 4}
          </p>
        </div>

        {/* Stimulus Presentation Box */}
        <div className="rounded-2xl border border-border bg-surface-1 overflow-hidden shadow-sm">
          <div className="p-4 bg-surface-2 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-brand-primary/10 text-brand-primary border border-brand-primary/20">
                Stimulus: {currentStep.stimulus_type.replace(/_/g, " ")}
              </span>
            </div>
            <span className="text-[11px] font-mono text-text-muted">Interactive Scenario Workbench</span>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-text-primary mb-1">{currentStep.title}</h2>
              <p className="text-xs text-text-secondary leading-relaxed">{currentStep.description}</p>
            </div>

            {/* Render realistic stimulus artifact */}
            <RenderStimulus stimulus={currentStep.stimulus_content} type={currentStep.stimulus_type} />
          </div>
        </div>

        {/* Inline Error Notice if a decision failed */}
        {errorNotice && (
          <div className="rounded-xl border border-danger/40 bg-danger/10 p-3.5 flex items-center justify-between text-xs text-danger">
            <span className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {errorNotice}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setSelectedDecision(null)}
              className="text-xs py-1 px-2.5 h-auto"
            >
              Dismiss
            </Button>
          </div>
        )}

        {/* Victim Decision Choices */}
        <Card pad="lg" className="border border-border bg-surface-1">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-border">
            <span className="eyebrow text-text-muted">Victim Decision Point</span>
            <span className="text-[11px] text-text-muted font-mono">Select your next action</span>
          </div>
          <p className="text-sm font-semibold text-text-primary mb-4">{currentStep.decision_prompt}</p>

          <div className="space-y-2.5">
            {currentStep.decision_options?.map((option) => {
              const isSelected = selectedDecision === option.decision;
              return (
                <button
                  key={option.decision}
                  onClick={() => handleDecision(option.decision)}
                  disabled={isLoading}
                  className={`w-full rounded-xl p-4 text-left transition-all border text-xs sm:text-sm ${
                    isSelected
                      ? "bg-brand-primary/15 border-brand-primary text-text-primary shadow-sm ring-1 ring-brand-primary"
                      : "bg-surface-2/60 text-text-primary hover:bg-surface-2 hover:border-border-strong border-border"
                  } ${isLoading ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <span className="font-semibold text-text-primary">{option.label}</span>
                    {option.hint && (
                      <span className="font-mono text-[11px] text-text-muted whitespace-nowrap px-1.5 py-0.5 rounded bg-surface-3">
                        {option.hint}
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </Card>
      </div>
    );
  }

  return (
    <Card pad="lg" className="text-center py-12">
      <p className="text-sm text-text-secondary">Ready to start simulation.</p>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Rich Multi-Modal Stimulus Renderers
// ─────────────────────────────────────────────────────────────────────────────

interface RenderStimulusProps {
  stimulus: StepStimulus;
  type: string;
}

function RenderStimulus({ stimulus, type }: RenderStimulusProps) {
  switch (type) {
    case "message":
      return (
        <div className="rounded-xl bg-surface-2 border border-border p-4 space-y-3 font-sans">
          <div className="flex items-center justify-between pb-2 border-b border-border/60">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-brand-primary" />
              <span className="text-xs font-semibold text-text-primary">
                {stimulus.channel || "SMS / Push Notice"}
              </span>
            </div>
            {stimulus.timestamp && (
              <span className="text-[11px] font-mono text-text-muted">{stimulus.timestamp}</span>
            )}
          </div>
          {stimulus.sender && (
            <p className="text-[11px] text-text-muted font-mono">From: {stimulus.sender}</p>
          )}
          <div className="rounded-lg bg-surface-1 p-3.5 border-l-4 border-l-amber-500 shadow-inner">
            <p className="text-xs sm:text-sm text-text-primary leading-relaxed whitespace-pre-line">
              &quot;{stimulus.text}&quot;
            </p>
          </div>
        </div>
      );

    case "website":
      return (
        <div className="rounded-xl bg-surface-2 border border-border overflow-hidden shadow-inner">
          {/* Simulated Browser URL Bar */}
          <div className="p-3 bg-surface-3 border-b border-border flex items-center gap-2">
            <div className="flex items-center gap-1.5 mr-2">
              <div className="h-2.5 w-2.5 rounded-full bg-rose-500/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-amber-500/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/80" />
            </div>
            <div className="flex-1 flex items-center gap-2 rounded-lg bg-surface-1 px-3 py-1.5 border border-border text-xs font-mono text-text-secondary">
              <Lock className="h-3.5 w-3.5 text-amber-400 flex-shrink-0" />
              <span className="text-amber-300">http://</span>
              <span className="text-text-primary font-semibold">{stimulus.domain || "example-pay.test"}</span>
              <span className="text-text-muted">/bill</span>
            </div>
          </div>

          <div className="p-5 space-y-4">
            <h3 className="text-base font-bold text-text-primary">{stimulus.page_title}</h3>
            {stimulus.page_content?.header && (
              <p className="text-xs text-text-secondary">{stimulus.page_content.header}</p>
            )}

            {stimulus.page_content?.notice && (
              <div className="rounded-lg bg-amber-500/10 p-3 border-l-4 border-l-amber-500 text-xs text-amber-300 font-medium">
                ⚠️ {stimulus.page_content.notice}
              </div>
            )}

            {/* Web Form Fields */}
            {stimulus.page_content?.form_fields && (
              <div className="space-y-3 pt-2">
                {stimulus.page_content.form_fields.map((f: any, i: number) => (
                  <div key={i} className="space-y-1">
                    <label className="text-[11px] font-medium text-text-secondary">{f.label}</label>
                    <input
                      type="text"
                      disabled
                      placeholder={f.placeholder || "Enter details..."}
                      className="w-full rounded-lg bg-surface-1 border border-border px-3 py-2 text-xs text-text-primary cursor-not-allowed opacity-80"
                    />
                  </div>
                ))}
              </div>
            )}

            {/* Suspicious Indicators Alert */}
            {stimulus.suspicious_indicators && stimulus.suspicious_indicators.length > 0 && (
              <div className="rounded-xl bg-rose-500/10 p-3.5 border border-rose-500/30 space-y-2 mt-4">
                <span className="eyebrow text-rose-400">Heuristic Signals Detected</span>
                <ul className="space-y-1 text-xs text-rose-300">
                  {stimulus.suspicious_indicators.map((ind: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-rose-400 font-bold">•</span>
                      <span>{ind}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      );

    case "phone_call":
    case "agent_conversation":
      const transcript = stimulus.transcript || stimulus.call_transcript || [];
      return (
        <div className="rounded-xl bg-surface-2 border border-border p-4 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400 animate-pulse">
                <Phone className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-text-primary font-mono">
                  {stimulus.caller_display || stimulus.caller || "DIRECT DIAL: +91 99999 99999"}
                </p>
                <p className="text-[10px] text-text-muted">Live Active Voice Channel</p>
              </div>
            </div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
              High Pressure Call
            </span>
          </div>

          {/* Transcript Dialogue */}
          <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
            {transcript.map((item: any, idx: number) => {
              const speaker = typeof item === "string" ? "AGENT" : item.speaker;
              const text = typeof item === "string" ? item : item.text;
              const isOfficer = speaker === "OFFICIAL" || speaker?.includes("City Power Official");
              const isAgent = speaker === "AGENT" || speaker?.includes("AGENT");

              return (
                <div
                  key={idx}
                  className={`rounded-lg p-3 text-xs leading-relaxed ${
                    isOfficer
                      ? "bg-emerald-500/10 border border-emerald-500/20 text-text-primary"
                      : isAgent
                      ? "bg-rose-500/10 border border-rose-500/20 text-text-primary"
                      : "bg-surface-1 border border-border text-text-primary"
                  }`}
                >
                  <p
                    className={`font-mono text-[10px] font-bold uppercase mb-1 ${
                      isOfficer ? "text-emerald-400" : isAgent ? "text-rose-400" : "text-brand-primary"
                    }`}
                  >
                    {speaker}:
                  </p>
                  <p className="text-text-secondary">{text}</p>
                </div>
              );
            })}
          </div>
        </div>
      );

    case "verification_form":
      return (
        <div className="rounded-xl bg-surface-2 border border-border p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <KeyRound className="h-4 w-4 text-amber-400" />
            <h4 className="text-xs font-bold text-text-primary">{stimulus.page_title || "Verification Form"}</h4>
          </div>

          <div className="space-y-3">
            {stimulus.form_fields?.map((field: any, idx: number) => (
              <div key={idx} className="space-y-1">
                <label className="text-[11px] font-medium text-text-muted">{field.label}</label>
                <div className="rounded-lg bg-surface-1 border border-border px-3 py-2 text-xs font-mono text-text-primary">
                  {field.value_entered || field.placeholder || "••••••••"}
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-lg bg-rose-500/10 p-3 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5 text-rose-400" />
            <span>
              Sensitive credentials and 6-digit one-time passcode requested on an untrusted domain.
            </span>
          </div>
        </div>
      );

    case "payment_request":
      const details = stimulus.transaction || stimulus.transaction_details || {};
      return (
        <div className="rounded-xl bg-surface-2 border border-border p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-rose-400" />
              <span className="text-xs font-bold text-text-primary">
                {stimulus.upi_screen || stimulus.payment_app || "Simulated UPI Payment"}
              </span>
            </div>
            <span className="text-[10px] font-mono text-rose-400 bg-rose-500/20 px-2 py-0.5 rounded border border-rose-500/30">
              Debit Approval
            </span>
          </div>

          <div className="rounded-xl bg-surface-1 p-4 border border-border space-y-2.5">
            {Object.entries(details).map(([key, val]) => (
              <div key={key} className="flex items-center justify-between text-xs py-1 border-b border-border/40 last:border-0">
                <span className="text-text-muted capitalize">{key.replace(/_/g, " ")}:</span>
                <span className="font-mono font-semibold text-text-primary">{String(val)}</span>
              </div>
            ))}
          </div>

          {(stimulus.transaction_warning || details.warning) && (
            <div className="rounded-lg bg-rose-500/15 p-3 border border-rose-500/30 text-xs text-rose-300 font-medium">
              {stimulus.transaction_warning || details.warning}
            </div>
          )}
        </div>
      );

    default:
      return (
        <div className="rounded-xl bg-surface-2 p-4 border border-border text-xs font-mono text-text-muted overflow-x-auto">
          {JSON.stringify(stimulus, null, 2)}
        </div>
      );
  }
}
