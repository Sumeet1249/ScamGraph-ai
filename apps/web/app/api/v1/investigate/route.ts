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
        // Base structure with attached files forensic signals
        const localFormat = analyzeInput(queryText, entityType, attachedFiles);
        localFormat.incident_id = backendData.incident_id || localFormat.incident_id;

        if (backendData.assessment) {
          localFormat.assessment.risk_score = Math.round(backendData.assessment.risk_score ?? localFormat.assessment.risk_score);
          localFormat.assessment.risk_level = backendData.assessment.risk_level ?? localFormat.assessment.risk_level;
          localFormat.assessment.evidence_confidence = backendData.assessment.evidence_confidence ?? localFormat.assessment.evidence_confidence;
          if (backendData.assessment.reason_codes && backendData.assessment.reason_codes.length > 0) {
            localFormat.assessment.reason_codes = backendData.assessment.reason_codes;
          }
        }

        if (backendData.pattern_match) {
          localFormat.pattern_match = {
            pattern_id: backendData.pattern_match.pattern_name || localFormat.pattern_match.pattern_id,
            pattern_name: backendData.pattern_match.pattern_name || localFormat.pattern_match.pattern_name,
            match_score: backendData.pattern_match.match_score ?? localFormat.pattern_match.match_score,
            is_strong_match: true,
          };
          localFormat.assessment.pattern_name = backendData.pattern_match.pattern_name || localFormat.assessment.pattern_name;
        }

        // Map any signals returned by backend
        if (backendData.signals && Array.isArray(backendData.signals)) {
          backendData.signals.forEach((s: any, idx: number) => {
            localFormat.signals.push({
              signal_id: `be_sig_${idx}`,
              dimension: (s.dimension || "SEMANTIC").toUpperCase() as any,
              category: s.signal_type || "Corroborated Engine Signal",
              title: s.signal_type ? s.signal_type.replace(/_/g, " ") : "Backend Detection",
              desc: s.description || "Identified by ScamGraph multi-modal risk engine.",
              severity: (s.severity || "high").toLowerCase() as any,
              confidence: s.confidence > 0.8 ? "HIGH" : s.confidence > 0.5 ? "MEDIUM" : "LOW",
              provenance: {
                source_service: s.provenance?.source_service || "services.investigation",
                timestamp: new Date().toISOString(),
              },
            });
          });
        }

        saveIncident(localFormat);
        return NextResponse.json(localFormat);
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
