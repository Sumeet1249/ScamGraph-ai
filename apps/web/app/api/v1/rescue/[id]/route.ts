import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/${params.id}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Rescue state fetch error:", err);
  }

  return NextResponse.json({
    incident_id: params.id,
    status: "ACTIVE",
    triage: {
      urgency_score: 90,
      urgency_level: "HIGH",
      golden_hour_active: true,
      time_elapsed_seconds: 300,
      ongoing_contact: false,
    },
    action_plan: {
      do_now: [],
      do_next: [],
      preserve: [],
      report: [],
      monitor: [],
    },
    loss_events: [],
    total_reported_loss: 0,
    currency: "INR",
    timeline: [],
    official_resources: [],
  });
}
