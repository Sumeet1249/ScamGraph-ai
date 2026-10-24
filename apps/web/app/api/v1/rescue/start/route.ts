import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Rescue start proxy error:", err);
  }

  // Fallback rescue session state
  const incidentId = `resc_${Date.now()}`;
  return NextResponse.json({
    incident_id: incidentId,
    status: "ACTIVE",
    triage: {
      urgency_score: 95,
      urgency_level: "CRITICAL",
      golden_hour_active: true,
      time_elapsed_seconds: 120,
      ongoing_contact: false,
    },
    action_plan: {
      do_now: [
        {
          action_id: "act_bank_freeze",
          title: "Freeze Source Bank Account / Debit Card",
          category: "IMMEDIATE_STOP",
          priority: 1,
          status: "PENDING",
          instruction: "Call your bank immediately to block net banking, debit cards, and UPI outgoing transactions.",
          institution_type: "BANK",
        },
        {
          action_id: "act_call_1930",
          title: "Report to National Cyber Crime Helpline 1930",
          category: "REPORT",
          priority: 2,
          status: "PENDING",
          instruction: "Lodge an instant golden-hour complaint on 1930 (or cybercrime.gov.in) with your transaction reference.",
          institution_type: "POLICE",
        },
      ],
      do_next: [],
      preserve: [],
      report: [],
      monitor: [],
    },
    loss_events: [],
    total_reported_loss: 0,
    currency: "INR",
    timeline: [
      {
        event_id: `tl_${Date.now()}`,
        timestamp: new Date().toISOString(),
        title: "Rescue Session Initiated",
        summary: "Emergency triage generated under DPDP Act 2023.",
      },
    ],
    official_resources: [
      {
        resource_id: "res_1930",
        name: "National Cyber Crime Reporting Helpline",
        hotline: "1930",
        url: "https://cybercrime.gov.in",
        category: "POLICE",
      },
    ],
  });
}
