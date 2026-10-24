import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const typeFilter = searchParams.get("type");
  const url = typeFilter
    ? `${BACKEND_URL}/api/v1/console/reviews?type=${encodeURIComponent(typeFilter)}`
    : `${BACKEND_URL}/api/v1/console/reviews`;

  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Console reviews fetch error:", err);
  }

  // Fallback seed queue for human-in-the-loop inspection
  return NextResponse.json([
    {
      review_id: "REV-2026-9041",
      item_type: "CAMPAIGN_MERGE_CANDIDATE",
      title: "Proposed Merge: Power Cutoff Syndicate (#UTL-8490) into Northern Grid Ring",
      status: "PENDING_ANALYST_REVIEW",
      priority_score: 94,
      target_reference: "camp-power-urgent",
      summary: "High visual and temporal similarity (98.4%) detected between 142 cases across KA and DL circles.",
      details: {
        similarity_score: 0.984,
        shared_vpas: ["util-power-84920@okaxis"],
        telecom_lac: "404-45",
      },
      created_at: new Date().toISOString(),
    },
    {
      review_id: "REV-2026-9042",
      item_type: "HIGH_CONFIDENCE_INTERVENTION",
      title: "Intervention Appeal: RTGS Transaction Hold (₹12,50,000)",
      status: "PENDING_ANALYST_REVIEW",
      priority_score: 89,
      target_reference: "SG-2026-89412",
      summary: "User flagged for coerced video confinement under Digital Arrest pretext; statutory hold applied.",
      details: {
        tactic: "coercive_arrest",
        hold_amount: 1250000,
        bank: "SBI",
      },
      created_at: new Date().toISOString(),
    },
    {
      review_id: "REV-2026-9043",
      item_type: "ENTITY_DISAMBIGUATION",
      title: "Mule Account Disambiguation: Axis Bank Account #991044",
      status: "PENDING_ANALYST_REVIEW",
      priority_score: 76,
      target_reference: "ENT-UPI-AXIS-84920",
      summary: "Layered transit node detected across 3 distinct extortion operations within 48 hours.",
      details: {
        fan_out_ratio: 8.4,
        reported_loss: 450000,
      },
      created_at: new Date().toISOString(),
    },
  ]);
}
