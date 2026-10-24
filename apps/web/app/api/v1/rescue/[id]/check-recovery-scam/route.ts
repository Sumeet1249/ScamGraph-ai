import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/${params.id}/check-recovery-scam`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Check recovery scam error:", err);
  }

  return NextResponse.json({
    is_recovery_scam: true,
    confidence: "HIGH",
    warning: "Warning: Legitimate law enforcement or banks never ask for upfront legal fees or recovery commissions on WhatsApp/Telegram.",
    recommended_action: "DISCONNECT_AND_REPORT",
  });
}
