import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const { searchParams } = new URL(request.url);
  const accessTier = searchParams.get("access_tier") || "ANALYST";

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/entities/${params.id}?access_tier=${accessTier}`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Entity fetch error:", err);
  }

  // Fallback enriched canonical entity
  return NextResponse.json({
    id: params.id,
    type: "VPA",
    identifier: accessTier === "CONSUMER" ? "u***0@okaxis" : "util-power-84920@okaxis",
    psp: "Axis Bank Ltd",
    associated_phone: accessTier === "CONSUMER" ? "+91 98******10" : "+91 9845012310",
    name: "Karnataka Discom Collection Mule #14",
    risk_score: 98,
    risk_level: "HIGH",
    verified_bad: true,
    total_incidents: 14,
    total_loss_attributed: 450000,
    active_campaign: "camp-power-urgent",
    statutory_restraint: "Section 102 CrPC Lien Notice Served (FIR No. 0142/2026)",
    created_at: new Date().toISOString(),
  });
}
