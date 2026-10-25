"use client";

import { useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { ScenarioCard } from "@/components/lab/ScenarioCard";
import { SimulationSession } from "@/components/lab/SimulationSession";
import { Card, Button } from "@/components/ui";
import { RotateCcw } from "lucide-react";

interface Scenario {
  scenario_id: string;
  title: string;
  category: string;
  difficulty: string;
  estimated_duration_minutes: number;
  description: string;
  expected_risk_level: string;
}

export default function LabPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [debrief, setDebrief] = useState<any | null>(null);

  // Fetch scenarios on mount
  useEffect(() => {
    fetch("/api/v1/simulator/scenarios")
      .then((res) => res.json())
      .then((data) => {
        setScenarios(data.scenarios || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch scenarios:", err);
        setLoading(false);
      });
  }, []);

  const handleRunScenario = (scenarioId: string) => {
    const newSessionId = `SIM-${scenarioId}-${Date.now()}`;
    setSessionId(newSessionId);
    setRunning(scenarioId);
    setDebrief(null);
  };

  const handleScenarioComplete = (debriefData: any) => {
    setDebrief(debriefData);
  };

  const handleRestart = () => {
    setRunning(null);
    setSessionId(null);
    setDebrief(null);
  };

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Simulation & Defense"
        title="ScamGraph Lab"
        description="Interactive training scenarios. Make decisions at each step, see how scams unfold, and learn safer alternatives. Every choice matters."
        actions={
          <div className="flex items-center gap-3">
            {running && (
              <Button variant="secondary" size="sm" onClick={handleRestart}>
                <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
                Reset Workbench
              </Button>
            )}
            <DemoDataBadge />
          </div>
        }
      />

      {/* Section 11.2: 4/8 Split Layout */}
      <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
        {/* Left Workbench: Scenario Selection & Controls */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="eyebrow">Available Scenarios</span>
            <span className="font-mono text-[11px] text-text-muted">{scenarios.length} loaded</span>
          </div>

          {loading ? (
            <div className="rounded-xl border border-border bg-surface-1 p-8 text-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-border-strong border-t-brand-primary mx-auto mb-3" />
              <p className="text-xs text-text-muted">Loading scenarios...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {scenarios.map((scenario) => {
                const isSelected = running === scenario.scenario_id;
                return (
                  <div
                    key={scenario.scenario_id}
                    className={`transition-all rounded-xl ${
                      isSelected ? "ring-2 ring-brand-primary rounded-xl" : ""
                    }`}
                  >
                    <ScenarioCard
                      title={scenario.title}
                      badge={scenario.expected_risk_level}
                      description={scenario.description}
                      steps={Math.ceil(scenario.estimated_duration_minutes / 2)}
                      difficulty={scenario.difficulty}
                      duration={scenario.estimated_duration_minutes}
                      onRun={() => handleRunScenario(scenario.scenario_id)}
                      disabled={isSelected && !debrief}
                    />
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Region: Active Simulation or Useful Empty State */}
        <div className="min-w-0">
          {running && sessionId ? (
            <div>
              {!debrief && (
                <SimulationSession
                  sessionId={sessionId}
                  scenarioId={running}
                  onComplete={handleScenarioComplete}
                />
              )}

              {debrief && (
                <SimulationDebrief
                  debrief={debrief}
                  onRestart={handleRestart}
                  onSelectScenario={handleRunScenario}
                />
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border-strong bg-surface-1/40 p-12 text-center flex flex-col items-center justify-center min-h-[420px]">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-2 border border-border text-text-muted mb-4">
                <RotateCcw className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-text-primary">No Active Scenario</h3>
              <p className="mt-1.5 max-w-md text-xs text-text-secondary leading-relaxed">
                Select a training scenario from the workbench on the left to begin an interactive simulation session.
                You will be presented with real-time victim choices to see how risk evolves.
              </p>
              <div className="mt-6 flex items-center gap-3 text-xs font-mono text-text-muted">
                <span>· Branching decision trees</span>
                <span>· Dual-axis risk tracking</span>
                <span>· Post-run debrief</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

interface DebriefProps {
  debrief: any;
  onRestart: () => void;
  onSelectScenario: (scenarioId: string) => void;
}

function SimulationDebrief({ debrief, onRestart, onSelectScenario }: DebriefProps) {
  const riskScore = debrief.final_risk_score ?? 50;
  const isDanger = riskScore >= 60;
  const isCaution = riskScore >= 30 && riskScore < 60;
  const riskColor = isDanger ? "text-rose-400" : isCaution ? "text-amber-400" : "text-emerald-400";

  const durationText =
    debrief.duration_seconds < 60
      ? `${debrief.duration_seconds || 1}s`
      : `${Math.round(debrief.duration_seconds / 60)}m`;

  return (
    <div className="space-y-6 animate-fadeIn">
      <Card pad="lg" className="bg-gradient-to-r from-surface-2 via-surface-1 to-surface-2 border border-brand-primary/40 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <span className="eyebrow text-brand-primary">Scenario Debrief & Scoring</span>
            <h2 className="text-xl font-bold mt-1 text-text-primary">{debrief.scenario_title || "Simulation Debrief"}</h2>
            <p className="text-xs text-text-secondary mt-1">Post-incident behavioral and security posture review</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold font-mono text-brand-primary">{debrief.performance_score ?? 85}%</p>
            <p className="text-[11px] font-mono uppercase text-text-muted">Defense Score</p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-4">
        <Card pad="md" className="border border-border bg-surface-1">
          <span className="eyebrow text-text-muted">Final Risk</span>
          <p className={`text-2xl font-bold font-mono mt-1 ${riskColor}`}>{riskScore}/100</p>
          <p className="text-[11px] font-mono uppercase text-text-muted mt-0.5">{debrief.final_risk_level || "EVALUATED"}</p>
        </Card>
        <Card pad="md" className="border border-border bg-surface-1">
          <span className="eyebrow text-text-muted">Decisions Taken</span>
          <p className="text-2xl font-bold font-mono text-text-primary mt-1">{debrief.decision_count || 1}</p>
          <p className="text-[11px] font-mono text-text-muted mt-0.5">Interaction checkpoints</p>
        </Card>
        <Card pad="md" className="border border-border bg-surface-1">
          <span className="eyebrow text-text-muted">Duration</span>
          <p className="text-2xl font-bold font-mono text-text-primary mt-1">{durationText}</p>
          <p className="text-[11px] font-mono text-text-muted mt-0.5">Time in scenario</p>
        </Card>
      </div>

      <Card pad="lg" className="border border-border bg-surface-1">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-border">
          <span className="eyebrow text-text-muted">Key Learning Points & Defensive Habits</span>
          <span className="text-[11px] font-mono text-text-muted">Actionable Takeaways</span>
        </div>
        <div className="space-y-2.5">
          {debrief.learning_points?.map((point: string, idx: number) => (
            <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-surface-2/60 border border-border/50 text-xs">
              <span className="text-brand-primary font-bold mt-0.5">•</span>
              <p className="text-text-secondary leading-relaxed">{point}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button variant="secondary" className="flex-1" onClick={onRestart}>
          <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
          Choose Another Scenario
        </Button>
        {debrief.recommended_next_scenario && (
          <Button
            variant="primary"
            className="flex-1"
            onClick={() => onSelectScenario(debrief.recommended_next_scenario)}
          >
            Recommended Next Challenge
          </Button>
        )}
      </div>
    </div>
  );
}
