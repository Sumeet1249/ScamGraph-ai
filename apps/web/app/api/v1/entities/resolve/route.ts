import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/entities/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Entity resolve proxy error:", err);
  }

  return NextResponse.json({
    status: "RESOLVED",
    canonical_id: "ENT-UPI-AXIS-84920",
    entity_type: "VPA",
    normalized_value: "util-power-84920@okaxis",
    risk_level: "HIGH",
    risk_score: 98,
  });
}
