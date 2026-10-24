"use client";

import { useState } from "react";
import { Button, Input, Textarea, Select, Card, Badge, PageSection } from "@/components/ui";
import { AlertCircle, Check, AlertTriangle } from "lucide-react";

interface QuickCheckResult {
  riskLevel: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  confidenceScore: number;
  detectedPattern?: string;
  signals: string[];
  recommendation: string;
  isAnalyzing?: boolean;
}

const riskColors: Record<string, "success" | "caution" | "danger" | "neutral"> = {
  LOW: "success",
  MEDIUM: "caution",
  HIGH: "danger",
  CRITICAL: "danger",
};

export function ShieldQuickCheck() {
  const [message, setMessage] = useState("");
  const [url, setUrl] = useState("");
  const [threatType, setThreatType] = useState("");
  const [senderInfo, setSenderInfo] = useState("");
  const [result, setResult] = useState<QuickCheckResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!message && !url) {
      setError("Please paste at least a message or URL to analyze");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Call the investigate API
      const response = await fetch("/api/v1/investigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_text: message || null,
          url: url || null,
          sender_phone: senderInfo || null,
        }),
      });

      if (!response.ok) throw new Error("Analysis failed");

      const data = await response.json();
      const assessment = data.assessment;

      const signalsList = Array.isArray(data.signals) ? data.signals : [];
      const detectedSignalsConf = signalsList.length > 0
        ? Math.max(
            ...signalsList.map((s: any) => {
              const c = typeof s.confidence === "number" ? s.confidence : 0;
              return c <= 1 ? Math.round(c * 100) : Math.round(c);
            })
          )
        : 0;
      const patternConf = typeof data.pattern_match?.match_score === "number"
        ? Math.round(data.pattern_match.match_score * 100)
        : 0;
      const rawScore = typeof assessment?.risk_score === "number" ? assessment.risk_score : 0;
      const riskScore = detectedSignalsConf > 0
        ? Math.max(detectedSignalsConf, patternConf, rawScore)
        : (rawScore > 0 ? rawScore : patternConf);
      const riskLevel = riskScore >= 70 ? "HIGH" : riskScore >= 40 ? "MEDIUM" : (assessment?.risk_level || "LOW");

      // Calibrated confidence calculation
      let conf = Math.max(detectedSignalsConf, patternConf, 35);
      if (typeof assessment?.confidence_score === "number" && !isNaN(assessment.confidence_score)) {
        conf = Math.round(assessment.confidence_score * 100);
      } else if (assessment?.evidence_confidence === "HIGH" || riskScore >= 70) {
        conf = Math.max(conf, 92);
      } else if (assessment?.evidence_confidence === "MEDIUM" || riskScore >= 40) {
        conf = Math.max(conf, 70);
      }

      const action = assessment?.intervention?.action || assessment?.recommended_intervention?.action;
      const recommendationText =
        action === "PRE_PAYMENT_INTERVENTION"
          ? "⚠️ Critical Threat: Block this transaction immediately. Do not proceed or authorize payments."
          : action === "STRONG_WARNING" || riskScore >= 70
          ? "⚠️ High Risk: Strong warning. Do not click links, share OTPs, or transfer funds."
          : action === "CAUTION" || riskScore >= 40
          ? "⚠️ Moderate Risk: Potential scam indicators identified. Verify through official telephone directories."
          : "✓ Low Risk: No overt malicious indicators found. Remain vigilant and never disclose OTPs.";

      const checkResult: any = {
        incidentId: data.incident_id,
        riskLevel,
        riskScore,
        confidenceScore: conf,
        detectedPattern: assessment?.detected_pattern_name || data.pattern_match?.pattern_name,
        signals: Array.isArray(data.signals)
          ? data.signals.slice(0, 6).map((s: any) => s.signal_type || s.description)
          : [],
        recommendation: recommendationText,
        explanation: assessment?.explainability
          ? {
              whatHappened: assessment.explainability.what_happened,
              whySuspicious: assessment.explainability.why_suspicious,
              whatToDoNext: assessment.explainability.what_to_do_next,
            }
          : undefined,
      };

      setResult(checkResult);

      // Save to local storage for instant multi-tab and real-time page sync
      try {
        const newIncident = {
          id: data.incident_id,
          pattern: checkResult.detectedPattern || (url ? "Suspicious URL Check" : "Quick Security Check"),
          risk_score: riskScore,
          risk_level: riskLevel,
          confidence: assessment?.evidence_confidence || "LOW",
          current_stage: riskScore >= 70 ? "PAYMENT_REQUEST" : "INITIAL_CONTACT",
          last_activity: data.analyzed_at || new Date().toISOString(),
          isRecent: true,
        };
        const existing = JSON.parse(localStorage.getItem("recent_investigations") || "[]");
        const updated = [newIncident, ...existing.filter((x: any) => x.id !== newIncident.id)].slice(0, 50);
        localStorage.setItem("recent_investigations", JSON.stringify(updated));

        // Notify active Command Center and Campaigns tabs in real time
        window.dispatchEvent(new Event("storage"));
      } catch (err) {
        console.warn("Storage sync error:", err);
      }
    } catch (err) {
      setError("Unable to analyze. Please try again or check the backend.");
      setResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setMessage("");
    setUrl("");
    setThreatType("");
    setSenderInfo("");
    setResult(null);
    setError(null);
  };

  const formatRiskDisplay = (level: string) => {
    switch (level?.toUpperCase()) {
      case "CRITICAL":
        return "Critical Threat";
      case "HIGH":
        return "High Risk";
      case "MEDIUM":
        return "Medium Risk";
      case "LOW":
        return "Low Risk";
      case "INSUFFICIENT_EVIDENCE":
        return "Insufficient Evidence";
      default:
        return level?.replace(/_/g, " ") || "Assessed";
    }
  };

  const riskTone = (level: string) => {
    switch (level?.toUpperCase()) {
      case "CRITICAL":
      case "HIGH":
        return "danger";
      case "MEDIUM":
        return "caution";
      case "LOW":
        return "success";
      case "INSUFFICIENT_EVIDENCE":
      default:
        return "neutral";
    }
  };

  return (
    <div className="space-y-8">
      {/* Input Section */}
      <PageSection
        title="Quick Security Check"
        description="Paste suspicious content to analyze for scam patterns and threats"
      >
        <Card pad="lg" className="space-y-6">
          <Textarea
            label="Suspicious Message"
            placeholder="Paste the message text here..."
            help="We'll analyze this for scam keywords, urgency patterns, and known threats"
            value={message}
            onChange={(e) => setMessage(e.currentTarget.value)}
            rows={5}
            disabled={isAnalyzing}
          />

          <Input
            label="Suspicious URL or Link"
            placeholder="https://example.com or link from message"
            help="We'll check domain age, SSL certificate, and known phishing patterns"
            value={url}
            onChange={(e) => setUrl(e.currentTarget.value)}
            disabled={isAnalyzing}
          />

          <Select
            label="Type of Threat (optional)"
            placeholder="Select if you know the type..."
            value={threatType}
            onChange={(e) => setThreatType(e.currentTarget.value)}
            disabled={isAnalyzing}
          >
            <option value="">-- Select --</option>
            <option value="kyc">KYC/Bank verification</option>
            <option value="investment">Investment/Crypto opportunity</option>
            <option value="job">Job/Task offer</option>
            <option value="refund">Refund/Support scam</option>
            <option value="payment">Payment request/UPI</option>
            <option value="other">Other/Unknown</option>
          </Select>

          <Input
            label="Sender Phone or UPI ID (optional)"
            placeholder="+91 or upi@handle"
            help="Helps us identify the threat actor across incidents"
            value={senderInfo}
            onChange={(e) => setSenderInfo(e.currentTarget.value)}
            disabled={isAnalyzing}
          />

          {error && (
            <div className="flex items-center gap-2 rounded-lg bg-danger/10 p-3 text-danger">
              <AlertCircle className="h-4 w-4" />
              <p className="text-body-sm">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              variant="primary"
              size="lg"
              onClick={handleAnalyze}
              loading={isAnalyzing}
              disabled={!message && !url}
            >
              {isAnalyzing ? "Analyzing..." : "Analyze for Threats"}
            </Button>
            <Button variant="secondary" size="lg" onClick={handleClear} disabled={isAnalyzing}>
              Clear
            </Button>
          </div>

          <p className="text-caption text-text-muted">
            Your analysis is private and encrypted. We never store personal information.
          </p>
        </Card>
      </PageSection>

      {/* Result Section */}
      {result && (
        <PageSection
          title="Analysis Result"
          description="Threat assessment and recommended actions"
        >
          <Card pad="lg" className="space-y-6">
            {/* Risk Level */}
            <div className="flex items-end justify-between">
              <div>
                <p className="text-label text-text-muted uppercase">Risk Level</p>
                <h3 className="text-h2 font-bold text-text-primary mt-2">
                  {result.riskLevel}
                </h3>
              </div>
              <Badge tone={riskColors[result.riskLevel]}>
                {result.confidenceScore}% Confidence
              </Badge>
            </div>

            {/* Pattern Match */}
            {result.detectedPattern && (
              <div>
                <p className="text-label text-text-muted uppercase">Detected Pattern</p>
                <p className="text-body text-text-primary mt-2 font-semibold">
                  {result.detectedPattern}
                </p>
              </div>
            )}

            {/* Signals */}
            {result.signals.length > 0 && (
              <div>
                <p className="text-label text-text-muted uppercase mb-2">Detected Signals</p>
                <div className="flex flex-wrap gap-2">
                  {result.signals.map((signal) => (
                    <Badge key={signal} tone="caution">
                      {signal}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            <div className="rounded-lg bg-surface-2 p-4">
              <div className="flex items-start gap-3">
                {result.riskLevel === "LOW" ? (
                  <Check className="h-5 w-5 text-success flex-shrink-0 mt-1" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0 mt-1" />
                )}
                <div>
                  <p className="font-semibold text-text-primary">{result.recommendation}</p>
                  <p className="text-body-sm text-text-secondary mt-2">
                    {result.riskLevel === "LOW"
                      ? "This appears to be a legitimate message. Always verify payment details through official channels."
                      : "Do not share personal information, OTPs, or payment details. Always verify independently with official support numbers."}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </PageSection>
      )}

      {/* No Result Yet */}
      {!result && !error && (
        <PageSection
          title="Analysis Result"
          description="Results will appear here after submission"
        >
          <Card pad="lg" className="text-center py-12">
            <p className="text-body text-text-secondary">
              Submit a check above to see threat assessment, detected patterns, and recommended actions.
            </p>
          </Card>
        </PageSection>
      )}
    </div>
  );
}
