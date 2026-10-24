import { NextRequest, NextResponse } from "next/server";
import { analyzeInput, getIncident, saveIncident } from "@/lib/investigationStore";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const queryText = body.message_text || body.content || body.url || body.vpa || body.query || "";
    const entityType = body.type || body.entity_type || "Message with a link";
    const attachedFiles = body.attached_files || [];

    // Extract identifiers from text if not provided explicitly
    const phoneMatch = queryText.match(/(?:\+91[-\s]?)?[6789]\d{9}/);
    const vpaMatch = queryText.match(/[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}/);
    const urlMatch = queryText.match(/https?:\/\/[^\s]+|bit\.ly\/[^\s]+|tinyurl\.com\/[^\s]+|[a-zA-Z0-9-]+\.(?:tk|ml|ga|cf|gq|xyz|top|site|club|work|vip)[^\s]*/i);

    const targetUrl = body.url || (urlMatch ? urlMatch[0] : null);
    const targetVpa = body.vpa || (vpaMatch ? vpaMatch[0] : null);
    const targetPhone = body.sender_phone || (phoneMatch ? phoneMatch[0] : null);

    // 1. Try forwarding to Python FastAPI backend (with 6s timeout)
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      const response = await fetch(`${BACKEND_URL}/api/v1/investigate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message_text: queryText,
          url: targetUrl,
          vpa: targetVpa,
          sender_phone: targetPhone,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const backendData = await response.json();
        const localFormat = analyzeInput(queryText, entityType, attachedFiles);

        // Merge full real backend response with journey and local format
        const mergedResult = {
          ...backendData,
          query_content: queryText,
          entity_type: entityType,
          attached_files: attachedFiles,
          journey: localFormat.journey,
          assessment: {
            ...localFormat.assessment,
            ...backendData.assessment,
            risk_score: backendData.assessment?.risk_score ?? localFormat.assessment.risk_score,
            risk_level: backendData.assessment?.risk_level ?? localFormat.assessment.risk_level,
            evidence_confidence: backendData.assessment?.evidence_confidence ?? localFormat.assessment.evidence_confidence,
            detected_pattern_name: backendData.pattern_match?.pattern_name || backendData.assessment?.detected_pattern_name || localFormat.assessment.pattern_name,
            reason_codes: backendData.assessment?.reason_codes && backendData.assessment.reason_codes.length > 0
              ? backendData.assessment.reason_codes
              : localFormat.assessment.reason_codes,
            explainability: localFormat.assessment.explainability || {
              what_happened: queryText.slice(0, 100),
              why_suspicious: backendData.signals?.map((s: any) => s.description).join("; ") || "Corroborated by intelligence engines.",
              what_to_do_next: "Do not authorize payment or disclose OTP credentials. Verify independently."
            }
          },
          pattern_match: backendData.pattern_match || localFormat.pattern_match,
          signals: (backendData.signals && backendData.signals.length > 0) ? backendData.signals : localFormat.signals,
          tripartite_decision: backendData.tripartite_decision,
          contextual_intervention: backendData.contextual_intervention,
          multilingual_text: backendData.multilingual_text,
          unified_assessment: backendData.unified_assessment,
          graph_correlation: backendData.graph_correlation,
          dataset_evidence: backendData.dataset_evidence,
          is_simulated: false,
        };

        saveIncident(mergedResult as any);
        return NextResponse.json(mergedResult);
      }
    } catch (e) {
      // Backend not running or timed out; seamlessly fall back to local real-time forensic engine
      console.warn("FastAPI backend forward error or timeout, using local forensic engine:", e);
    }

    // 2. Local ScamGraph Forensic Engine (evaluates patterns, signals, and dual-axis risk)
    const result = analyzeInput(queryText, entityType, attachedFiles);
    return NextResponse.json(result);
  } catch (error) {
    console.error("Investigation API error:", error);
    return NextResponse.json(
      { error: "Failed to process investigation request" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id") || "SG-2026-89412";
  const incident = getIncident(id);
  return NextResponse.json(incident);
}
