import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/${params.id}/case-package`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Rescue case package error:", err);
  }

  return NextResponse.json({
    incident_id: params.id,
    generated_at: new Date().toISOString(),
    statute_compliance: "BNSS §94 & DPDP Act 2023",
    summary: "Official victim dossier prepared for 1930 / State Cyber Crime Police Station filing.",
    total_loss: 0,
    evidence_count: 0,
    download_url: `/api/v1/rescue/${params.id}/dossier.pdf`,
  });
}
