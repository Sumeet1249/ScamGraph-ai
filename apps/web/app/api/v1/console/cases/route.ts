import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/console/cases`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Console cases fetch error:", err);
  }

  return NextResponse.json([
    {
      case_id: "CASE-2026-KA-0941",
      title: "State of Karnataka vs. Electricity Cutoff Extortion Syndicate",
      priority: "CRITICAL",
      status: "UNDER_INVESTIGATION",
      assigned_analyst: "Inspector Raghavendra M.",
      linked_incident_ids: ["SG-2026-89412", "SG-2026-89413"],
      linked_campaign_ids: ["camp-power-urgent"],
      linked_entities: ["util-power-84920@okaxis"],
      total_loss: 4500000,
      lien_recovered: 1850000,
      created_at: new Date().toISOString(),
    },
  ]);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/v1/console/cases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Create case error:", err);
  }

  return NextResponse.json({
    case_id: `CASE-${Date.now()}`,
    status: "CREATED",
    created_at: new Date().toISOString(),
  });
}
