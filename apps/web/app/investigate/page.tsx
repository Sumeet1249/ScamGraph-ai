"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { InvestigationComposer } from "@/components/investigation/InvestigationComposer";
import { InvestigationResults } from "@/components/investigation/InvestigationResults";

export default function InvestigatePage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState<string | null>(null);

  const handleStartInvestigation = async (data: {
    message_text?: string;
    url?: string;
    vpa?: string;
    qr_payload?: string;
  }) => {
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/v1/investigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error("Investigation failed");

      const result = await response.json();
      setResult(result);
      // Save to local storage for immediate persistence across tab navigation
      try {
        const signals = Array.isArray(result.signals) ? result.signals : [];
        const detectedSignalsConf = signals.length > 0
          ? Math.max(
              ...signals.map((s: any) => {
                const c = typeof s.confidence === "number" ? s.confidence : 0;
                return c <= 1 ? Math.round(c * 100) : Math.round(c);
              })
            )
          : 0;
        const patternConf = typeof result.pattern_match?.match_score === "number"
          ? Math.round(result.pattern_match.match_score * 100)
          : 0;
        const rawScore = typeof result.assessment?.risk_score === "number"
          ? result.assessment.risk_score
          : 0;
        const finalRiskScore = detectedSignalsConf > 0
          ? Math.max(detectedSignalsConf, patternConf, rawScore)
          : (rawScore > 0 ? rawScore : patternConf);
        const computedRiskLevel =
          finalRiskScore >= 70
            ? "HIGH"
            : finalRiskScore >= 40
            ? "MEDIUM"
            : (result.assessment?.risk_level || "LOW");
        const computedConfidence =
          finalRiskScore >= 70
            ? "HIGH"
            : finalRiskScore >= 40
            ? "MEDIUM"
            : (result.assessment?.evidence_confidence || "LOW");

        const newIncident = {
          id: result.incident_id,
          pattern:
            result.assessment?.detected_pattern_name ||
            result.pattern_match?.pattern_name ||
            (data.url ? "Suspicious Link Analysis" : data.vpa ? "Payment Context Check" : "Multi-Signal Investigation"),
          risk_score: finalRiskScore,
          risk_level: computedRiskLevel,
          confidence: computedConfidence,
          current_stage: finalRiskScore >= 70 ? "PAYMENT_REQUEST" : "INITIAL_CONTACT",
          last_activity: result.analyzed_at || new Date().toISOString(),
          signals: signals,
        };
        const saved = JSON.parse(localStorage.getItem("recent_investigations") || "[]");
        const updated = [newIncident, ...saved.filter((x: any) => x.id !== newIncident.id)];
        localStorage.setItem("recent_investigations", JSON.stringify(updated.slice(0, 50)));
      } catch (storageErr) {
        console.warn("Could not save to localStorage:", storageErr);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to complete investigation. Please check the backend."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Shield"
        title="Advanced Investigation"
        description="Combine multiple signals for a comprehensive threat analysis. Message, URL, payment context, and metadata are fused into a single risk assessment."
        actions={<DemoDataBadge />}
      />

      {/* Main Layout: Form on left, Results on right (or stacked on mobile) */}
      <div className="grid gap-8 lg:grid-cols-[400px_1fr]">
        {/* Investigation Composer Form */}
        <div className="lg:sticky lg:top-20 h-fit">
          <InvestigationComposer
            onSubmit={handleStartInvestigation}
            isLoading={isAnalyzing}
            hasResult={!!result}
            onReset={handleReset}
          />
        </div>

        {/* Results Area */}
        <div>
          {isAnalyzing && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center space-y-4">
                <div className="flex justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-border-strong border-t-brand-primary" />
                </div>
                <p className="text-body text-text-secondary">Analyzing incident...</p>
                <p className="text-body-sm text-text-muted">
                  Scanning signals across semantic, URL, payment, and infrastructure dimensions.
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg bg-danger/10 p-6 border border-danger/30">
              <h3 className="font-semibold text-danger">Analysis Error</h3>
              <p className="text-body-sm text-danger/80 mt-2">{error}</p>
            </div>
          )}

          {result && !isAnalyzing && (
            <InvestigationResults data={result} />
          )}

          {!result && !isAnalyzing && !error && (
            <div className="rounded-lg border-2 border-dashed border-border-strong p-8 text-center">
              <p className="text-body text-text-secondary">
                Submit a combined investigation above to see comprehensive results.
              </p>
              <p className="text-body-sm text-text-muted mt-2">
                Include message, URL, or payment information for stronger analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
