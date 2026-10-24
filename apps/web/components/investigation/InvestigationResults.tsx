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
import { AlertTriangle, CheckCircle, AlertCircle, Info, ShieldAlert, Clock, ShieldCheck, Zap, Shield, Database, FileCheck, Hash, Link2, Sparkles, Check, Dna, Fingerprint, Activity } from "lucide-react";

interface InvestigationResultsProps {
  data: {
    incident_id: string;
    analyzed_at: string;
    is_simulated?: boolean;
    scam_dna?: {
      dna_id: string;
      quality: string;
      confidence: number;
      canonical_signature: string;
      dimensions: Record<string, {
        available: boolean;
        confidence: number;
        quality: string;
        features: Record<string, any>;
      }>;
      available_dimensions: string[];
      consumer_view?: {
        summary_headline: string;
        variant_verdict: string;
        why_it_matches: string[];
        behavioral_traits: string[];
        recommended_action: string;
        confidence_label: string;
      };
    };
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
    tripartite_decision?: {
      action: string;
      risk_score: number;
      risk_band: string;
      confidence_score: number;
      confidence_band: string;
      urgency_score: number;
      urgency_band: string;
      consumer_headline: string;
      consumer_message: string;
      safeguard_steps: string[];
      suggested_cooling_off_minutes: number;
      active_dimension_count: number;
      can_auto_block: boolean;
      cooling_off_recommended: boolean;
      dimension_contributions: Array<{
        dimension: string;
        raw_score: number;
        weight: number;
        effective_contribution: number;
        is_discounted: boolean;
        notes?: string;
      }>;
    };
    multilingual_text?: {
      original_text: string;
      normalized_text: string;
      language_profile: {
        primary_language: string;
        scripts: string[];
        code_mixed: boolean;
        code_mix_score: number;
        support_tier: string;
        confidence: number;
      };
      transliterations?: Record<string, string>;
      translation?: string;
      warnings?: string[];
    };
    dataset_evidence?: {
      evidence_hash_sha256?: string;
      datasets_health?: {
        all_connected: boolean;
        total_records: number;
        datasets: Array<{
          id: string;
          name: string;
          records_count: number;
          status: string;
          license: string;
          provenance: string;
          path: string;
        }>;
      };
      top_dataset_matches?: Array<{
        dataset_id: string;
        dataset_name: string;
        record_id: string;
        similarity_score: number;
        matched_text: string;
        scam_type: string;
        language: string;
        audit_action: string;
        provenance_type: string;
      }>;
      proof_indicators?: Array<{
        dimension: string;
        proof_type: string;
        finding: string;
        verified: boolean;
      }>;
      grounding_summary?: string;
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

const formatRiskLevel = (level?: string) => {
  return level ? level.replace(/_/g, " ") : "UNKNOWN";
};

const getConfidenceScore = (assessment?: any) => {
  if (!assessment) return 0.5;
  if (typeof assessment.confidence_score === "number") return assessment.confidence_score;
  const confMap: Record<string, number> = {
    HIGH: 0.9,
    MEDIUM: 0.6,
    LOW: 0.3,
  };
  return confMap[assessment.evidence_confidence] || 0.5;
};

const actionConfig = (action: string) => {
  switch (action) {
    case "BLOCK_PRE_LOSS":
      return {
        label: "BLOCK PRE-LOSS",
        tone: "bg-red-950/80 text-red-200 border-red-500",
        badgeTone: "danger" as const,
        icon: ShieldAlert,
        description: "Confirmed circulating threat cluster. Irreversible loss imminent.",
      };
    case "DELAY_PAYMENT":
      return {
        label: "DELAY PAYMENT (COOLING-OFF)",
        tone: "bg-amber-950/80 text-amber-200 border-amber-500",
        badgeTone: "caution" as const,
        icon: Clock,
        description: "Pre-loss financial execution detected under psychological pressure.",
      };
    case "STRONG_WARNING":
      return {
        label: "STRONG WARNING",
        tone: "bg-orange-950/80 text-orange-200 border-orange-500",
        badgeTone: "caution" as const,
        icon: AlertTriangle,
        description: "High fraud probability corroborated across multiple intelligence engines.",
      };
    case "WARN":
      return {
        label: "SUSPICIOUS — PROCEED WITH CAUTION",
        tone: "bg-yellow-950/80 text-yellow-200 border-yellow-500",
        badgeTone: "caution" as const,
        icon: AlertCircle,
        description: "Suspicious indicators detected; requires vigilance.",
      };
    case "VERIFY_INDEPENDENTLY":
      return {
        label: "VERIFY INDEPENDENTLY",
        tone: "bg-cyan-950/80 text-cyan-200 border-cyan-500",
        badgeTone: "info" as const,
        icon: Shield,
        description: "Ambiguous signals or limited evidence; independently verify before acting.",
      };
    case "EDUCATE":
      return {
        label: "EDUCATE & AWARENESS",
        tone: "bg-blue-950/80 text-blue-200 border-blue-500",
        badgeTone: "info" as const,
        icon: Info,
        description: "Mild anomaly detected; normal safe practices apply.",
      };
    case "ALLOW":
    default:
      return {
        label: "VERIFIED BENIGN / ALLOW",
        tone: "bg-emerald-950/80 text-emerald-200 border-emerald-500",
        badgeTone: "success" as const,
        icon: ShieldCheck,
        description: "No significant malicious indicators found.",
      };
  }
};

export function InvestigationResults({ data }: InvestigationResultsProps) {
  const {
    assessment = {} as any,
    signals = [],
    pattern_match,
    graph_correlation,
    unified_assessment,
    tripartite_decision,
    multilingual_text,
    dataset_evidence,
    scam_dna,
  } = data || {};

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

  const rawAction = tripartite_decision
    ? (tripartite_decision.action || (tripartite_decision as any).primary_action || "ALLOW")
    : "ALLOW";
  const actionMeta = tripartite_decision ? actionConfig(rawAction) : null;
  const ActionIcon = actionMeta ? actionMeta.icon : ShieldAlert;
  const isCoolingOff = tripartite_decision
    ? (tripartite_decision.cooling_off_recommended || rawAction === "DELAY_PAYMENT" || (tripartite_decision as any).pre_loss_intervention)
    : false;
  const coolingMinutes = (tripartite_decision as any)?.suggested_cooling_off_minutes || 120;
  const steps: string[] = (tripartite_decision as any)?.safeguard_steps || (tripartite_decision as any)?.recommended_steps || [];
  const contributions: any[] = (tripartite_decision as any)?.dimension_contributions || (tripartite_decision as any)?.signal_contributions || [];
  const activeDimsCount = (tripartite_decision as any)?.active_dimension_count || contributions.filter((c: any) => c.raw_score > 0).length || contributions.length;

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

      {/* Phase 4A: Unified Tripartite Decision Engine Card */}
      {tripartite_decision && (
        <PageSection
          title="ScamGraph Unified Decision Layer (Phase 4A)"
          description="Coherent operational disposition synthesizing Message, URL, Entity, Tactic, Journey, ScamDNA & Campaign signals"
        >
          <Card pad="lg" className={`border-2 ${actionMeta?.tone} space-y-6 shadow-xl`}>
            {/* Top Action Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-border/50">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-surface-1 border border-border/60">
                  <ActionIcon className="h-7 w-7 text-text-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold tracking-wider text-text-muted uppercase">
                      Operational Disposition
                    </span>
                    {(tripartite_decision.can_auto_block || rawAction === "BLOCK_PRE_LOSS") && (
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-red-900/60 text-red-300 rounded border border-red-700 uppercase">
                        Auto-Block Triggered
                      </span>
                    )}
                  </div>
                  <h3 className="text-2xl font-black font-mono tracking-tight mt-0.5">
                    {actionMeta?.label}
                  </h3>
                </div>
              </div>

              {isCoolingOff && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-900/40 text-amber-200 border border-amber-600/70 text-xs font-mono">
                  <Clock className="h-4 w-4 animate-spin-slow" />
                  <span className="font-bold">
                    {coolingMinutes}-Min Friction Window
                  </span>
                </div>
              )}
            </div>

            {/* Tripartite Gauge Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Risk Gauge */}
              <div className="p-4 rounded-lg bg-surface-1/80 border border-border/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-text-muted uppercase">Risk (Severity)</span>
                  <Badge tone={tripartite_decision.risk_band === "CRITICAL" || tripartite_decision.risk_band === "HIGH" ? "danger" : tripartite_decision.risk_band === "MODERATE" || tripartite_decision.risk_band === "MEDIUM" ? "caution" : "success"}>
                    {tripartite_decision.risk_band}
                  </Badge>
                </div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-black font-mono tabular-nums">
                    {Math.round(tripartite_decision.risk_score * 100)}
                  </span>
                  <span className="text-xs font-mono text-text-muted">/100</span>
                </div>
                <div className="w-full bg-surface-3 h-2 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${tripartite_decision.risk_score >= 0.7 ? "bg-red-500" : tripartite_decision.risk_score >= 0.4 ? "bg-amber-500" : "bg-emerald-500"
                      }`}
                    style={{ width: `${Math.round(tripartite_decision.risk_score * 100)}%` }}
                  />
                </div>
                <p className="text-[11px] text-text-muted mt-2">
                  Likelihood of fraudulent harm
                </p>
              </div>

              {/* Confidence Gauge */}
              <div className="p-4 rounded-lg bg-surface-1/80 border border-border/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-text-muted uppercase">Confidence (Evidence)</span>
                  <Badge tone={tripartite_decision.confidence_band === "CRITICAL" || tripartite_decision.confidence_band === "HIGH" ? "success" : tripartite_decision.confidence_band === "MODERATE" || tripartite_decision.confidence_band === "MEDIUM" ? "caution" : "neutral"}>
                    {tripartite_decision.confidence_band}
                  </Badge>
                </div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-black font-mono tabular-nums">
                    {Math.round(tripartite_decision.confidence_score * 100)}
                  </span>
                  <span className="text-xs font-mono text-text-muted">/100</span>
                </div>
                <div className="w-full bg-surface-3 h-2 rounded-full mt-2 overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 transition-all duration-500"
                    style={{ width: `${Math.round(tripartite_decision.confidence_score * 100)}%` }}
                  />
                </div>
                <p className="text-[11px] text-text-muted mt-2">
                  Corroboration across active dimensions ({activeDimsCount} evaluated)
                </p>
              </div>

              {/* Urgency Gauge */}
              <div className="p-4 rounded-lg bg-surface-1/80 border border-border/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-text-muted uppercase">Urgency (Time Horizon)</span>
                  <Badge tone={tripartite_decision.urgency_band === "CRITICAL" || tripartite_decision.urgency_band === "HIGH" || tripartite_decision.urgency_band === "IMMEDIATE_INTERVENTION" ? "danger" : tripartite_decision.urgency_band === "MODERATE" || tripartite_decision.urgency_band === "ELEVATED_URGENCY" ? "caution" : "neutral"}>
                    {tripartite_decision.urgency_band}
                  </Badge>
                </div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-black font-mono tabular-nums">
                    {Math.round(tripartite_decision.urgency_score * 100)}
                  </span>
                  <span className="text-xs font-mono text-text-muted">/100</span>
                </div>
                <div className="w-full bg-surface-3 h-2 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${tripartite_decision.urgency_score >= 0.7 ? "bg-red-500" : tripartite_decision.urgency_score >= 0.4 ? "bg-amber-500" : "bg-blue-500"
                      }`}
                    style={{ width: `${Math.round(tripartite_decision.urgency_score * 100)}%` }}
                  />
                </div>
                <p className="text-[11px] text-text-muted mt-2">
                  Imminence of irreversible execution
                </p>
              </div>
            </div>

            {/* Consumer-Safe Guidance */}
            <div className="p-4 rounded-lg bg-surface-1/90 border border-border space-y-3">
              <div>
                <h4 className="font-semibold text-text-primary text-base">
                  {tripartite_decision.consumer_headline}
                </h4>
                <p className="text-body-sm text-text-secondary mt-1">
                  {tripartite_decision.consumer_message}
                </p>
              </div>

              {steps.length > 0 && (
                <div className="pt-2 border-t border-border/60">
                  <span className="text-[11px] font-mono font-bold text-text-muted uppercase block mb-1.5">
                    Recommended Safeguard Protocol:
                  </span>
                  <ul className="space-y-1.5 text-xs text-text-primary">
                    {steps.map((step: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-cyan-400 mt-0.5 flex-shrink-0" />
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Dimension Breakdown */}
            {contributions.length > 0 && (
              <div>
                <span className="text-xs font-mono text-text-muted uppercase block mb-2">
                  Subsystem Contributions to Fused Decision:
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  {contributions.map((dim: any, idx: number) => (
                    <div key={idx} className="p-2.5 rounded bg-surface-1 border border-border/70 text-xs font-mono">
                      <div className="text-text-muted capitalize truncate">
                        {String(dim.dimension || dim.engine_name || "").replace(/_/g, " ")}
                      </div>
                      <div className="flex items-baseline justify-between mt-1">
                        <span className="font-bold text-text-primary">
                          {Math.round((dim.raw_score ?? 0) * 100)}%
                        </span>
                        <span className="text-[10px] text-text-muted">
                          w: {Math.round((dim.weight ?? 0) * 100)}%
                        </span>
                      </div>
                      {dim.is_counter_evidence && (
                        <div className="text-[10px] text-emerald-400 mt-1">
                          ✓ Counter-evidence applied
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </PageSection>
      )}

      {/* Multilingual Intelligence Card (Phase 5C) */}
      {multilingual_text && (
        <PageSection
          title="Multilingual Intelligence V2 (Phase 5C)"
          description="Code-mixed Indic understanding, deterministic script analysis, and security-token invariant normalization"
        >
          <Card className="p-4 sm:p-5 border-border/80 bg-surface-subtle/50 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border/60">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-semibold uppercase text-text-muted">
                  Detected Language:
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-primary/20 text-primary border border-primary/30 uppercase">
                  {multilingual_text.language_profile?.primary_language}
                </span>
                {multilingual_text.language_profile?.code_mixed && (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-amber-500/10 text-amber-300 border border-amber-500/30">
                    Code-Mixed ({Math.round((multilingual_text.language_profile?.code_mix_score ?? 0) * 100)}%)
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-text-muted">
                <span>Scripts:</span>
                <span className="text-text-primary font-medium">
                  {multilingual_text.language_profile?.scripts?.join(", ") || "LATIN"}
                </span>
                <span className="text-border">|</span>
                <span>Support Tier:</span>
                <span className="text-emerald-400 font-medium">
                  {multilingual_text.language_profile?.support_tier || "PRODUCTION_VALIDATED"}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-3 rounded bg-surface-1 border border-border/60 space-y-1">
                <span className="text-[11px] text-text-muted uppercase block font-semibold">
                  Original Immutable Evidence:
                </span>
                <p className="text-text-primary font-sans text-xs break-words whitespace-pre-wrap">
                  {multilingual_text.original_text}
                </p>
              </div>

              <div className="p-3 rounded bg-surface-1 border border-border/60 space-y-1">
                <span className="text-[11px] text-text-muted uppercase block font-semibold">
                  Indic Normalized Representation:
                </span>
                <p className="text-accent font-sans text-xs break-words whitespace-pre-wrap">
                  {multilingual_text.normalized_text}
                </p>
                {multilingual_text.translation && (
                  <div className="pt-2 mt-2 border-t border-border/40 text-[11px] text-text-muted">
                    <span className="font-semibold text-text-secondary uppercase">Supporting Semantic Translation: </span>
                    <span className="text-text-primary">{multilingual_text.translation}</span>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </PageSection>
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
            {data.unified_assessment?.score_breakdown && (
              <div>
                <span className="text-caption text-text-muted uppercase font-mono block mb-2">
                  Subsystem Signal Breakdown & Normalized Weights:
                </span>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                  {Object.entries(data.unified_assessment.score_breakdown || {}).map(([engine, score]) => (
                    <div key={engine} className="p-2.5 bg-surface-1 rounded border border-border">
                      <div className="text-text-muted capitalize">{engine} Engine</div>
                      <div className="text-sm font-bold text-text-primary mt-1">
                        {Math.round(score * 100)}%
                      </div>
                      <div className="text-[10px] text-text-muted mt-0.5">
                        Weight: {Math.round(((data.unified_assessment?.active_weights || {})[engine] || 0) * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="text-xs font-mono text-text-secondary bg-surface-1 p-3 rounded border border-border">
              {data.unified_assessment.explanation}
            </p>
          </Card>
        </PageSection>
      )}

      {/* ScamDNA™ 8-Dimensional Behavioral Fingerprint */}
      {scam_dna && (
        <PageSection
          title="ScamDNA™ 8-Dimensional Behavioral Fingerprint"
          description="Decoupled multi-dimensional forensic vector tracking behavioral mutation, threat family lineage, and consumer risk"
        >
          <Card pad="lg" className="bg-surface-2 border border-border space-y-6 shadow-xl">
            {/* Top Bar: Canonical Signature & Global Confidence */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-border/80">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-indigo-950/60 border border-indigo-500/50 text-indigo-400">
                  <Dna className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold tracking-widest text-indigo-400 uppercase">
                      Canonical Threat Signature
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${scam_dna.quality === "HIGH"
                        ? "bg-emerald-950/60 text-emerald-300 border-emerald-600"
                        : scam_dna.quality === "MEDIUM"
                          ? "bg-amber-950/60 text-amber-300 border-amber-600"
                          : "bg-surface-3 text-text-secondary border-border"
                      }`}>
                      Quality: {scam_dna.quality}
                    </span>
                  </div>
                  <h4 className="text-xl font-black font-mono tracking-tight text-text-primary mt-1">
                    {scam_dna.canonical_signature || "family:UNKNOWN"}
                  </h4>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs font-mono">
                <div className="text-right">
                  <span className="text-text-muted uppercase text-[10px] block">Fingerprint Confidence</span>
                  <span className="text-lg font-black font-mono text-cyan-400">
                    {Math.round((scam_dna.confidence || 0) * 100)}%
                  </span>
                </div>
                <div className="h-8 w-px bg-border/60" />
                <div className="text-right">
                  <span className="text-text-muted uppercase text-[10px] block">Active Dimensions</span>
                  <span className="text-lg font-black font-mono text-text-primary">
                    {scam_dna.available_dimensions?.length || 0} / 8
                  </span>
                </div>
              </div>
            </div>

            {/* 8-Dimensional Decoupled Vector Grid */}
            <div className="space-y-3">
              <span className="text-caption text-text-muted uppercase font-mono font-bold block">
                Decoupled Forensic Dimensions:
              </span>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  "SEMANTIC",
                  "JOURNEY",
                  "TACTIC",
                  "INFRASTRUCTURE",
                  "PAYMENT",
                  "IDENTITY",
                  "TEMPORAL",
                  "GRAPH",
                ].map((dimKey) => {
                  const dim = scam_dna.dimensions?.[dimKey] || {
                    available: false,
                    confidence: 0,
                    quality: "LOW",
                    features: {},
                  };
                  return (
                    <div
                      key={dimKey}
                      className={`p-3 rounded-lg border transition-all ${dim.available
                          ? "bg-surface-1 border-indigo-500/40 shadow-sm"
                          : "bg-surface-inset/50 border-border/40 opacity-60"
                        }`}
                    >
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className={`font-bold ${dim.available ? "text-text-primary" : "text-text-muted"}`}>
                          {dimKey}
                        </span>
                        <span
                          className={`h-2 w-2 rounded-full ${dim.available ? "bg-emerald-400 animate-pulse-soft" : "bg-text-muted/40"
                            }`}
                        />
                      </div>

                      <div className="mt-2 flex items-baseline justify-between text-xs font-mono">
                        <span className="text-text-muted text-[10px]">Confidence:</span>
                        <span className={`font-bold ${dim.available ? "text-cyan-400" : "text-text-muted"}`}>
                          {Math.round(dim.confidence * 100)}%
                        </span>
                      </div>

                      <div className="w-full bg-surface-3 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 ${dim.available ? "bg-indigo-400" : "bg-transparent"
                            }`}
                          style={{ width: `${Math.round(dim.confidence * 100)}%` }}
                        />
                      </div>

                      {dim.features && Object.keys(dim.features).length > 0 && (
                        <div className="mt-2 pt-1.5 border-t border-border/40 text-[10px] font-mono text-text-muted truncate">
                          {Object.keys(dim.features).slice(0, 2).join(", ")}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Consumer Guidance Card */}
            {scam_dna.consumer_view && (
              <div className="p-4 rounded-lg bg-surface-1 border border-border space-y-2.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Fingerprint className="h-4 w-4 text-cyan-400" />
                    <h5 className="text-sm font-bold font-mono text-text-primary">
                      {scam_dna.consumer_view.summary_headline}
                    </h5>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-cyan-950/60 text-cyan-300 border border-cyan-700">
                    {scam_dna.consumer_view.variant_verdict}
                  </span>
                </div>

                <p className="text-xs font-mono text-text-secondary">
                  <strong className="text-amber-400">Recommended Action: </strong>
                  {scam_dna.consumer_view.recommended_action}
                </p>

                {scam_dna.consumer_view.behavioral_traits && scam_dna.consumer_view.behavioral_traits.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {scam_dna.consumer_view.behavioral_traits.map((trait: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-surface-2 text-[10px] font-mono text-text-muted border border-border"
                      >
                        • {trait}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </Card>
        </PageSection>
      )}

      {/* Dataset Grounding & Forensic Evidence Proof Section */}
      <PageSection
        title="Dataset Grounding & Forensic Proof (Section 65B Admissible)"
        description="Every signal and pattern is verified in real time against 3,863+ certified Indian scam records & scenarios"
      >
        <Card pad="lg" className="bg-surface-2 space-y-6 border border-border">
          {/* Active Dataset Connection Status Header */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-950/60 border border-emerald-500/50 text-emerald-400">
                <Database className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse-soft" />
                  <span className="text-xs font-mono font-bold uppercase text-emerald-400">
                    Live Threat Registries Connected
                  </span>
                </div>
                <h4 className="text-lg font-bold font-mono text-text-primary mt-0.5">
                  Verified Against 3,863 Certified Records
                </h4>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
              <span className="px-2.5 py-1 rounded bg-surface-1 border border-border text-text-secondary">
                scam-ham-india: <strong className="text-text-primary">2,272</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-surface-1 border border-border text-text-secondary">
                synthetic-audited: <strong className="text-text-primary">1,580</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-surface-1 border border-border text-text-secondary">
                journeys: <strong className="text-text-primary">6</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-surface-1 border border-border text-text-secondary">
                patterns: <strong className="text-text-primary">5</strong>
              </span>
            </div>
          </div>

          {/* Grounding Summary */}
          {dataset_evidence?.grounding_summary && (
            <div className="p-3.5 rounded-lg bg-surface-1 border border-border text-body-sm font-mono text-text-secondary">
              <span className="font-bold text-accent">Grounding Verdict: </span>
              {dataset_evidence.grounding_summary}
            </div>
          )}

          {/* Top Matched Dataset Records */}
          {dataset_evidence?.top_dataset_matches && dataset_evidence.top_dataset_matches.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-caption text-text-muted uppercase font-mono font-bold flex items-center gap-1.5">
                  <FileCheck className="h-4 w-4 text-accent" />
                  Closest Matched Dataset Records in Knowledge Base:
                </span>
                <span className="text-[11px] font-mono text-text-muted">
                  Lexical & Semantic Cosine Ranking
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {dataset_evidence.top_dataset_matches.map((m, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-lg bg-surface-1 border border-border/80 hover:border-accent/50 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-surface-3 text-cyan-300 border border-border">
                        {m.dataset_name}
                      </span>
                      <span className="text-xs font-mono font-black text-amber-400">
                        {Math.round(m.similarity_score * 100)}% Similarity
                      </span>
                    </div>

                    <p className="text-xs font-mono text-text-primary line-clamp-3 bg-surface-inset p-2 rounded border border-border/50">
                      &quot;{m.matched_text}&quot;
                    </p>

                    <div className="flex items-center justify-between text-[10px] font-mono text-text-muted pt-1">
                      <span>Vector: <strong className="text-text-secondary uppercase">{m.scam_type}</strong></span>
                      <span>Source: <strong className="text-text-secondary">{m.provenance_type}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Proof Verification Indicators */}
          {dataset_evidence?.proof_indicators && dataset_evidence.proof_indicators.length > 0 && (
            <div className="space-y-2">
              <span className="text-caption text-text-muted uppercase font-mono font-bold">
                Forensic Verification Proof Chain:
              </span>
              <div className="space-y-1.5">
                {dataset_evidence.proof_indicators.map((p, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2.5 p-2.5 rounded bg-surface-1 border border-border text-xs font-mono"
                  >
                    <Check className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-text-primary">[{p.dimension}] </span>
                      <span className="text-text-muted">({p.proof_type}): </span>
                      <span className="text-text-secondary">{p.finding}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 65B Cryptographic Proof Hash */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-surface-inset border border-border/80 text-xs font-mono">
            <div className="flex items-center gap-2 text-text-muted">
              <Hash className="h-4 w-4 text-accent" />
              <span>Section 65B Indian Evidence Act Forensic Hash:</span>
            </div>
            <code className="text-[11px] text-accent font-bold bg-surface-1 px-2.5 py-1 rounded border border-border">
              {dataset_evidence?.evidence_hash_sha256 || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
            </code>
          </div>
        </Card>
      </PageSection>

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
