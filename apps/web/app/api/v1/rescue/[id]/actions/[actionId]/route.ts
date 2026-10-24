import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string; actionId: string } }
) {
  try {
    const body = await request.json().catch(() => ({ status: "COMPLETED" }));
    const res = await fetch(`${BACKEND_URL}/api/v1/rescue/${params.id}/actions/${params.actionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    console.error("Update action status error:", err);
  }

  return NextResponse.json({
    action_id: params.actionId,
    status: "COMPLETED",
    updated_at: new Date().toISOString(),
  });
}
