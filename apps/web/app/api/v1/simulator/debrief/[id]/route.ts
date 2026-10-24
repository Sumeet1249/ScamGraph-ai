import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/simulator/debrief/${params.id}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Simulator debrief fetch error:", err);
  }

  return NextResponse.json({
    session_id: params.id,
    performance_score: 85,
    safe_decisions: 3,
    total_decisions: 4,
    duration_seconds: 140,
    risk_trajectory: [20, 35, 65, 20],
    learning_points: [
      "Verified that entering a UPI PIN is only required to send money, never to receive refunds.",
      "Identified that official utility providers never disconnect power outside formal regulatory hours.",
    ],
  });
}
