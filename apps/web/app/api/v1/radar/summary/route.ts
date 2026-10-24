import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

const DEFAULT_SUMMARY = {
  active_campaigns: 24,
  emerging_count: 7,
  surging_count: 4,
  outbreak_count: 2,
  critical_count: 2,
  new_incidents_24h: 1284,
  high_risk_signals: 9,
  last_updated: new Date().toISOString(),
  engine_version: "3.3.0",
  demo_mode: true,
};

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const demo = url.searchParams.get("demo_mode");
    const backendRes = await fetch(`${BACKEND_URL}/api/v1/radar/summary?demo_mode=${demo || "true"}`, {
      next: { revalidate: 0 },
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend offline fallback to canonical surveillance data
  }
  return NextResponse.json(DEFAULT_SUMMARY);
}
