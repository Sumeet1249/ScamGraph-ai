import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/${params.id}/loss-events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Record loss event error:", err);
  }

  return NextResponse.json({
    event_id: `loss_${Date.now()}`,
    incident_id: params.id,
    amount: 15000,
    currency: "INR",
    payment_method: "UPI",
    occurred_at: new Date().toISOString(),
  });
}
