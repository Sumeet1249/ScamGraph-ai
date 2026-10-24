"use client";

import {
  Card,
  Grid,
  MetricCard,
  Badge,
  SemanticBadge,
  PageSection,
  AssessmentCard,
} from "@/components/ui";
import { AlertTriangle, CheckCircle, AlertCircle, Info } from "lucide-react";

interface InvestigationResultsProps {
  data: {
    incident_id: string;
    analyzed_at: string;
    is_simulated?: boolean;
    assessment: {
      risk_level: string;
      evidence_confidence: string;
      risk_score: number;
      confidence_score: number;
      detected_pattern_name?: string;
      emerging_status?: string;
      is_insufficient_evidence?: boolean;
      intervention?: {
        action: string;
        friction_delay_seconds?: number;
        banner_message?: string;
      };
      explainability?: {
        what_happened: string;
        why_suspicious: string;
        what_to_do_next: string;
      };
    };
    signals?: Array<{
      signal_type: string;
      severity: string;
      confidence: number;
      description: string;
      dimension?: string;
    }>;
    pattern_match?: {
      pattern_name: string;
      match_score: number;
    };
    graph_correlation?: {
      related_incidents_count: number;
      shared_phone_count: number;
      shared_domain_count: number;
    };
    unified_assessment?: {
      fused_risk_score: number;
      risk_level: string;
      recommended_action: string;
      score_breakdown: Record<string, number>;
      active_weights: Record<string, number>;
      is_degraded: boolean;
      degraded_components: string[];
      rule_floor_applied: boolean;
      explanation: string;
    };
  };
}

const riskTone = (level: string) => {
  const map: Record<string, "success" | "caution" | "danger" | "neutral"> = {
    LOW: "success",
    MEDIUM: "caution",
    HIGH: "danger",
    INSUFFICIENT_EVIDENCE: "neutral",
  };
  return map[level] || "neutral";
};

export function InvestigationResults({ data }: InvestigationResultsProps) {
  const confScore = getConfidenceScore(assessment);

  // Use detected signal confidence directly for the risk score
  const detectedSignalsConf = signals.length > 0
    ? Math.max(
        ...signals.map((s) => {
          const c = typeof s.confidence === "number" ? s.confidence : 0;
          return c <= 1 ? Math.round(c * 100) : Math.round(c);
        })
      )
    : 0;

  const patternConf = typeof pattern_match?.match_score === "number"
    ? Math.round(pattern_match.match_score * 100)
    : 0;

  const rawScore = typeof assessment?.risk_score === "number" && !isNaN(assessment.risk_score)
    ? assessment.risk_score
    : 0;

  const riskScore = detectedSignalsConf > 0
    ? Math.max(detectedSignalsConf, patternConf, rawScore)
    : (rawScore > 0 ? rawScore : patternConf);

  const effectiveRiskLevel =
    assessment.risk_level === "INSUFFICIENT_EVIDENCE" && riskScore < 40
      ? "INSUFFICIENT_EVIDENCE"
      : riskScore >= 70
      ? "HIGH"
      : riskScore >= 40
      ? "MEDIUM"
      : (assessment.risk_level || "LOW");

  return (
    <div className="space-y-8">
      {/* Demo Mode Banner */}
      {data.is_simulated && (
        <Card pad="md" className="border-l-4 border-l-caution bg-caution/5">
          <div className="flex items-center gap-3">
            <span className="h-2 w-2 rounded-full bg-caution animate-pulse-soft flex-shrink-0" />
            <p className="text-body-sm font-semibold text-caution">
              This analysis was performed in DEMO MODE. Results are for illustration purposes only and may not reflect real threat assessments.
            </p>
          </div>
        </Card>
      )}

      {/* Risk Summary Cards */}
      <Grid columns="3" gap="md">
        <MetricCard
          label="Risk Level"
          value={
            <span className="text-xl sm:text-2xl font-bold leading-tight block break-words">
              {formatRiskLevel(effectiveRiskLevel)}
            </span>
          }
          tone={riskTone(effectiveRiskLevel)}
          detail={
            effectiveRiskLevel === "INSUFFICIENT_EVIDENCE"
              ? "Limited evidence available"
              : undefined
          }
        />
        <MetricCard
          label="Risk Score"
          value={<span className="font-mono tabular-nums">{riskScore}<span className="text-sm font-normal text-text-muted">/100</span></span>}
          tone={
            effectiveRiskLevel === "INSUFFICIENT_EVIDENCE"
              ? "neutral"
              : riskScore >= 70
              ? "danger"
              : riskScore >= 40
              ? "caution"
              : "success"
          }
          detail={
            effectiveRiskLevel === "INSUFFICIENT_EVIDENCE"
              ? "Insufficient evidence to calibrate index"
              : riskScore >= 70
              ? "High multi-signal corroboration index"
              : riskScore >= 40
              ? "Moderate threat indicators observed"
              : "Baseline activity — corroboration index"
          }
        />
        <MetricCard
          label="Evidence Confidence"
          value={<span className="font-mono">{assessment.evidence_confidence || "LOW"}</span>}
          tone={
            confScore >= 0.8 ? "success" : confScore >= 0.5 ? "caution" : "neutral"
          }
          detail={
            assessment.evidence_confidence
              ? `${assessment.evidence_confidence.toUpperCase()} independent source corroboration`
              : "Preliminary assessment"
          }
        />
      </Grid>

      {/* Pattern & Emerging Status */}
      <PageSection title="Pattern Detection">
        <Grid columns="2" gap="md">
          {assessment.detected_pattern_name && (
            <AssessmentCard
              title="Detected Pattern"
              badge={
                pattern_match ? (
                  <Badge tone="info">{Math.round(pattern_match.match_score * 100)}% match</Badge>
                ) : undefined
              }
            >
              <p className="font-mono text-body-sm">{assessment.detected_pattern_name}</p>
            </AssessmentCard>
          )}

          {assessment.emerging_status && (
            <AssessmentCard
              title="Emerging Status"
              badge={<SemanticBadge kind={assessment.emerging_status as any} />}
            >
              <p className="text-body-sm text-text-secondary">
                {assessment.emerging_status === "KNOWN_PATTERN"
                  ? "Matches a known scam workflow"
                  : assessment.emerging_status === "MUTATED_VARIANT"
                  ? "Variant of a known pattern detected"
                  : assessment.emerging_status === "POSSIBLE_EMERGING_CAMPAIGN"
                  ? "May be part of an emerging threat"
                  : "No significant pattern match"}
              </p>
            </AssessmentCard>
          )}
        </Grid>
      </PageSection>

      {/* Explainability */}
      {assessment.explainability && (
        <PageSection title="Analysis Explanation">
          <div className="space-y-4">
            <Card pad="md" className="border-l-4 border-l-danger">
              <p className="text-label text-danger uppercase mb-2">What Happened</p>
              <p className="text-body text-text-primary">{assessment.explainability.what_happened}</p>
            </Card>

            <Card pad="md" className="border-l-4 border-l-warning">
              <p className="text-label text-warning uppercase mb-2">Why Suspicious</p>
              <p className="text-body text-text-primary">{assessment.explainability.why_suspicious}</p>
            </Card>

            <Card pad="md" className="border-l-4 border-l-info">
              <p className="text-label text-info uppercase mb-2">Recommended Action</p>
              <p className="text-body text-text-primary">{assessment.explainability.what_to_do_next}</p>
            </Card>
          </div>
        </PageSection>
      )}

      {/* Intervention Recommendation */}
      {assessment.intervention && (
        <PageSection title="Recommended Intervention">
          <Card pad="lg" className="bg-surface-2">
            <div className="flex items-start gap-4">
              {assessment.intervention.action === "PRE_PAYMENT_INTERVENTION" ? (
                <AlertTriangle className="h-6 w-6 text-danger flex-shrink-0 mt-1" />
              ) : assessment.intervention.action === "STRONG_WARNING" ? (
                <AlertCircle className="h-6 w-6 text-warning flex-shrink-0 mt-1" />
              ) : assessment.intervention.action === "CAUTION" ? (
                <AlertCircle className="h-6 w-6 text-caution flex-shrink-0 mt-1" />
              ) : (
                <CheckCircle className="h-6 w-6 text-success flex-shrink-0 mt-1" />
              )}
              <div className="flex-1">
                <h4 className="font-semibold text-text-primary text-h3">
                  {assessment.intervention.action.replace(/_/g, " ")}
                </h4>
                {assessment.intervention.banner_message && (
                  <p className="text-body mt-2 text-text-secondary">{assessment.intervention.banner_message}</p>
                )}
                {assessment.intervention.friction_delay_seconds && assessment.intervention.friction_delay_seconds > 0 && (
                  <p className="text-body-sm text-text-muted mt-2">
                    Suggested friction delay: {assessment.intervention.friction_delay_seconds}s
                  </p>
                )}
              </div>
            </div>
          </Card>
        </PageSection>
      )}

      {/* Detected Signals */}
      {signals.length > 0 && (
        <PageSection
          title="Detected Signals"
          description={`${signals.length} suspicious indicator${signals.length !== 1 ? "s" : ""} found`}
        >
          <div className="space-y-3">
            {signals.slice(0, 10).map((signal, idx) => (
              <Card key={idx} pad="md" className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-label text-text-muted uppercase">
                      {signal.dimension || signal.signal_type}
                    </span>
                    <Badge
                      tone={
                        signal.severity === "CRITICAL" || signal.severity === "HIGH"
                          ? "danger"
                          : signal.severity === "MEDIUM"
                          ? "caution"
                          : "neutral"
                      }
                    >
                      {signal.severity}
                    </Badge>
                  </div>
                  <p className="text-body text-text-primary font-semibold">{signal.signal_type}</p>
                  <p className="text-body-sm text-text-secondary mt-1">{signal.description}</p>
                </div>
                <div className="flex-shrink-0 text-right">
                  <p className="text-body-sm font-semibold text-text-primary">
                    {Math.round(signal.confidence * 100)}%
                  </p>
                  <p className="text-caption text-text-muted">Confidence</p>
                </div>
              </Card>
            ))}
            {signals.length > 10 && (
              <p className="text-body-sm text-text-muted text-center py-2">
                +{signals.length - 10} more signals detected
              </p>
            )}
          </div>
        </PageSection>
      )}

      {/* Graph Correlation */}
      {graph_correlation && (
        <PageSection title="Infrastructure Correlation">
          <Grid columns="3" gap="md">
            <MetricCard
              label="Related Incidents"
              value={graph_correlation.related_incidents_count}
              tone="neutral"
              detail="Same patterns observed"
            />
            <MetricCard
              label="Shared Phones"
              value={graph_correlation.shared_phone_count}
              tone={graph_correlation.shared_phone_count > 0 ? "caution" : "success"}
              detail="Overlapping identifiers"
            />
            <MetricCard
              label="Shared Domains"
              value={graph_correlation.shared_domain_count}
              tone={graph_correlation.shared_domain_count > 0 ? "caution" : "success"}
              detail="Infrastructure overlap"
            />
          </Grid>
        </PageSection>
      )}

      {/* Unified Multi-Signal Assessment (Module D) */}
      {data.unified_assessment && (
        <PageSection
          title="ScamGraph Unified Risk Engine (DPIP + Mule + Graph + NLP)"
          description="Cross-subsystem fused risk assessment with degraded-mode weight redistribution"
        >
          <Card pad="lg" className="bg-surface-2 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-border">
              <div>
                <span className="text-caption text-text-muted uppercase font-mono">Fused Assessment</span>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-2xl font-bold font-mono text-text-primary">
                    {Math.round(data.unified_assessment.fused_risk_score * 100)}/100
                  </span>
                  <Badge
                    tone={
                      data.unified_assessment.risk_level === "CRITICAL" || data.unified_assessment.risk_level === "HIGH"
                        ? "danger"
                        : data.unified_assessment.risk_level === "MEDIUM"
                        ? "caution"
                        : "success"
                    }
                  >
                    {data.unified_assessment.risk_level}
                  </Badge>
                  <span className="text-xs font-mono font-bold uppercase px-2 py-0.5 rounded bg-surface-3 text-cyan-400 border border-border">
                    {data.unified_assessment.recommended_action}
                  </span>
                </div>
              </div>

              {data.unified_assessment.is_degraded && (
                <div className="text-xs font-mono px-2.5 py-1 rounded bg-amber-950/60 text-amber-300 border border-amber-800">
                  ⚠ Degraded Mode: {data.unified_assessment.degraded_components.join(", ")} missing (weights dynamically redistributed)
                </div>
              )}
            </div>

            {/* Score Breakdown across 4 engines */}
            <div>
              <span className="text-caption text-text-muted uppercase font-mono block mb-2">
                Subsystem Signal Breakdown & Normalized Weights:
              </span>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                {Object.entries(data.unified_assessment.score_breakdown).map(([engine, score]) => (
                  <div key={engine} className="p-2.5 bg-surface-1 rounded border border-border">
                    <div className="text-text-muted capitalize">{engine} Engine</div>
                    <div className="text-sm font-bold text-text-primary mt-1">
                      {Math.round(score * 100)}%
                    </div>
                    <div className="text-[10px] text-text-muted mt-0.5">
                      Weight: {Math.round((data.unified_assessment?.active_weights[engine] || 0) * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <p className="text-xs font-mono text-text-secondary bg-surface-1 p-3 rounded border border-border">
              {data.unified_assessment.explanation}
            </p>
          </Card>
        </PageSection>
      )}

      {/* Incident ID */}
      <div className="rounded-lg bg-surface-2 p-4">
        <p className="text-label text-text-muted uppercase">Incident ID</p>
        <p className="text-mono-data text-text-primary font-semibold mt-1">{data.incident_id}</p>
        <p className="text-caption text-text-muted mt-2">
          Analyzed at {new Date(data.analyzed_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
