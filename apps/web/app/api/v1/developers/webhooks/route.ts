import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/webhooks`, {
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
      id: "ep-1",
      name: "Apex Core Checkout Pipeline (Staging)",
      url: "https://api.apexfintech.in/v1/scamgraph/events",
      targetType: "Staging Target",
      status: "healthy",
      events: ["check.completed", "guard.intervention.triggered", "radar.outbreak.candidate"],
      delivered24h: 2840,
      failed24h: 0,
      secret: "whsec_99a8f4c1e828d19a770214b",
      revealed: false
    },
    {
      id: "ep-2",
      name: "Local Docker Simulation Daemon",
      url: "https://sandbox-relay.apexfintech.internal:8443/webhook",
      targetType: "Internal Daemon",
      status: "warning",
      warningText: "Endpoint domain resolves to RFC 1918 internal loopback during fallback lookup. Outbound dispatch paused pending validation.",
      events: ["check.*", "artifacts.ocr.ready"],
      delivered24h: 572,
      failed24h: 6,
      secret: "whsec_33fc790b41aa8939c1e881a",
      revealed: false
    }
  ]);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/webhooks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer sg_test_apex_sandbox_key_112233"
      },
      body: JSON.stringify({
        url: body.url,
        event_types: body.events || ["analysis.completed", "high_risk.detected"]
      })
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {}

  const secret = `whsec_${Math.random().toString(36).substring(2, 10)}${Math.random().toString(36).substring(2, 14)}`;
  return NextResponse.json({
    endpoint_id: `ep_${Date.now()}`,
    url: "https://api.apexfintech.in/v1/scamgraph/events",
    secret: secret,
    event_types: ["check.completed"],
    status: "ACTIVE"
  });
}
