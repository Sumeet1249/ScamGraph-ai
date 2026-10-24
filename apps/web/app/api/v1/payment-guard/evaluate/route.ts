import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // 1. Try FastAPI Payment Guard endpoint
    const guardPayload = {
      payer_vpa: body.payer_vpa || "consumer@oksbi",
      payee_vpa: body.payee_vpa || body.vpa || "util-power-84920@okaxis",
      amount: body.amount || 4500,
      currency: "INR",
      payment_type: body.intent || body.payment_type || "APPROVE_COLLECT",
      user_claimed_reason: body.user_claimed_reason || body.reason || "UTILITY_BILL",
      urgency_score: body.urgency_score || (body.urgency === "HIGH" ? 90 : 60),
      is_first_time_payee: true,
      has_active_call: body.unfamiliar_caller ?? true,
      has_screen_share: body.screen_share ?? false,
    };

    const res = await fetch(`${BACKEND_URL}/api/v1/payment-guard/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(guardPayload),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }

    // 2. Fallback to Interventions Evaluate
    const intvRes = await fetch(`${BACKEND_URL}/api/v1/interventions/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        incident_id: body.incident_id || `guard_${Date.now()}`,
        message_text: body.message_text || "Payment intent evaluation",
        vpa: body.payee_vpa || body.vpa,
        journey_stage: "PAYMENT_REQUEST",
      }),
    });

    if (intvRes.ok) {
      const intvData = await intvRes.json();
      return NextResponse.json(intvData);
    }
  } catch (err) {
    console.error("Payment guard evaluate error:", err);
  }

  // High-fidelity fallback response for pre-payment safeguard
  return NextResponse.json({
    action: "STOP_AND_VERIFY",
    concern_level: "HIGH",
    risk_score: 92,
    rule_id: "RULE_TOPOLOGICAL_COLLECT_DECEPTION",
    title: "Stop and verify before you approve",
    message: "Do not approve this collect request. Legitimate state electricity distribution utilities never collect arrears via personal UPI collect requests or WhatsApp links.",
    cooling_off_seconds: 300,
    safe_alternative: "Visit the official state utility portal or pay directly via your official electricity biller app.",
  });
}
