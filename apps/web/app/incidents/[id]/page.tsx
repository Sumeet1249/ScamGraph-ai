"use client";

import { useState, useEffect } from "react";
import { ShieldAlert, Layers3 } from "lucide-react";
import { Card, Tabs, TabsList, TabsTrigger, TabsPanel, Badge } from "@/components/ui";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { RiskGauge } from "@/components/risk/RiskGauge";
import { ConfidenceIndicator } from "@/components/risk/ConfidenceIndicator";
import { ReasonCodes } from "@/components/risk/ReasonCodes";
import { InterventionBanner } from "@/components/risk/InterventionBanner";
import { CurrentStage } from "@/components/journey/CurrentStage";
import { PaymentProximity } from "@/components/journey/PaymentProximity";
import { JourneyTimeline } from "@/components/journey/JourneyTimeline";
import { EvidenceList } from "@/components/evidence/EvidenceList";
import { EvidenceDrawer } from "@/components/evidence/EvidenceDrawer";
import { EvidenceGraph } from "@/components/graph/EvidenceGraph";
import { humanize } from "@/lib/utils/format";
import { getUnifiedIncident, CANONICAL_INCIDENTS } from "@/lib/demo/incidents-db";
import type { EvidenceSignal } from "@/lib/api/types";

export default function IncidentPage({ params }: { params: { id: string } }) {
  const [selectedSignal, setSelectedSignal] = useState<EvidenceSignal | null>(null);
  const [incidentData, setIncidentData] = useState(() => getUnifiedIncident(params.id));

  useEffect(() => {
    // Check if there is dynamic data stored in localStorage for this ID
    try {
      const raw = localStorage.getItem("recent_investigations");
      if (raw) {
        const list = JSON.parse(raw);
        if (Array.isArray(list)) {
          const match = list.find((x: any) => x.id === params.id);
          if (match) {
            setIncidentData(getUnifiedIncident(params.id, match));
            return;
          }
        }
      }
    } catch (e) {
      // Ignore storage error
    }

    // Also check canonical map
    if (CANONICAL_INCIDENTS[params.id]) {
      setIncidentData(CANONICAL_INCIDENTS[params.id]);
    }
  }, [params.id]);

  const { journey, assessment, graph, pattern } = incidentData;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={`Incident ${params.id}`}
        title={pattern || assessment.pattern_name || "Investigated Threat Incident"}
        description={`Reconstructed multi-signal journey for ${pattern || "investigated threat"}.`}
        actions={<DemoDataBadge />}
      />

      {/* Status row */}
      <div className="flex flex-wrap items-center gap-2.5">
        <Badge tone={assessment.emerging_status === "MUTATED_VARIANT" ? "caution" : "neutral"}>
          {humanize(assessment.emerging_status)}
        </Badge>
        <Badge tone="brand">{assessment.detected_pattern_name}</Badge>
        <Badge tone={assessment.intervention.action === "PRE_PAYMENT_INTERVENTION" ? "danger" : "neutral"}>
          <ShieldAlert className="h-3 w-3" />
          {humanize(assessment.intervention.action)}
        </Badge>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="journey">Journey</TabsTrigger>
          <TabsTrigger value="evidence">Evidence</TabsTrigger>
          <TabsTrigger value="graph">Graph</TabsTrigger>
        </TabsList>

        {/* ── Overview ─────────────────────────────────────────────── */}
        <TabsPanel value="overview" className="space-y-6">
          <div className="grid gap-4 lg:grid-cols-[1fr_1fr_1fr]">
            <RiskGauge score={assessment.risk_score} level={assessment.risk_level} />
            <ConfidenceIndicator confidence={assessment.evidence_confidence} />
            <div className="space-y-4">
              <CurrentStage stage={journey.current_stage} paymentProximate />
              <PaymentProximity proximate />
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <div className="eyebrow mb-3 flex items-center gap-2">
                <Layers3 className="h-3.5 w-3.5" />
                Why ScamGraph intervened
              </div>
              <ReasonCodes
                reasons={
                  assessment.reason_codes && assessment.reason_codes.length > 0
                    ? assessment.reason_codes
                    : [
                        `[SUPPORT] Analyzed payload pattern: ${pattern}`,
                        `[SUPPORT] Corroboration index calculated at ${assessment.risk_score}/100`,
                        `[SUPPORT] Current observed stage: ${journey.current_stage}`,
                      ]
                }
                onSelect={() => setSelectedSignal(assessment.signals?.[0] ?? null)}
              />
            </Card>
            <Card>
              <div className="eyebrow mb-3">Counter Evidence</div>
              {assessment.counter_evidence.length > 0 ? (
                <ul className="space-y-2">
                  {assessment.counter_evidence.map((c) => (
                    <li key={c.signal_id} className="rounded-lg border border-safe/20 bg-safe/[0.04] px-3 py-2 text-sm text-ink-muted">
                      {c.description}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-ink-dim">No counter evidence observed.</p>
              )}
              <p className="mt-3 text-xs text-ink-dim">
                Counter evidence does not establish legitimacy on its own.
              </p>
            </Card>
          </div>

          <InterventionBanner intervention={assessment.intervention} />
        </TabsPanel>

        {/* ── Journey ───────────────────────────────────────────────── */}
        <TabsPanel value="journey">
          <div className="max-w-2xl">
            <JourneyTimeline journey={journey} />
          </div>
        </TabsPanel>

        {/* ── Evidence ──────────────────────────────────────────────── */}
        <TabsPanel value="evidence">
          <EvidenceList
            signals={assessment.signals}
            counterEvidence={assessment.counter_evidence}
            onSelect={setSelectedSignal}
          />
        </TabsPanel>

        {/* ── Graph ─────────────────────────────────────────────────── */}
        <TabsPanel value="graph">
          <EvidenceGraph graph={graph} />
        </TabsPanel>
      </Tabs>

      <EvidenceDrawer signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
