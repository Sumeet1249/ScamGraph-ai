import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/webhooks/deliveries`, {
      headers: {
        "Authorization": "Bearer sg_test_apex_sandbox_key_112233"
      },
      cache: "no-store"
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {}

  return NextResponse.json([
    {
      id: "del_99812_a",
      event: "guard.intervention.triggered",
      status: 200,
      latencyMs: 84,
      timestamp: "14:28:11 IST",
      signature: "t=1747829400,v1=98fc1a890b22a012e84c9f1823d8b4c2",
      payload: {
        event: "guard.intervention.triggered",
        incident_id: "inc_2026_89104",
        user_masked_vpa: "vijay.sharma@okaxis",
        risk_state: "HIGH_RISK",
        concern: "State 6 / 7",
        action: "STOP_AND_VERIFY",
        detected_vector: "spoofed_header_BESCOM"
      }
    },
    {
      id: "del_99811_b",
      event: "check.completed",
      status: 200,
      latencyMs: 112,
      timestamp: "14:24:05 IST",
      signature: "t=1747829150,v1=a12bf098e98214fa770214bdce99018",
      payload: {
        event: "check.completed",
        check_id: "chk_98214fae902b",
        silhouette: "triangle_exclamation",
        concern: "suspicious",
        evaluation_ms: 118
      }
    },
    {
      id: "del_99810_c",
      event: "radar.outbreak.candidate",
      status: 504,
      latencyMs: 5002,
      timestamp: "14:19:42 IST",
      signature: "t=1747828890,v1=88fa01b223400a12e84c9f1823d8b4c",
      payload: {
        event: "radar.outbreak.candidate",
        campaign_cluster: "syn_raj_power_utility_burst_08",
        velocity: "412 reports/hour",
        first_observed_circle: "KA",
        retry_attempt: 1
      }
    }
  ]);
}
