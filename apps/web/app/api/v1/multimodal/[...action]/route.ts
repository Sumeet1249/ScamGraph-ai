import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const subpath = url.pathname.replace(/^\/api\/v1\/multimodal/, "");
    const body = await request.json();

    const response = await fetch(`${BACKEND_URL}/api/v1/multimodal${subpath}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errText = await response.text();
      return NextResponse.json({ error: errText }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Multimodal proxy error:", error);
    return NextResponse.json({ error: "Failed to process multimodal request" }, { status: 500 });
  }
}
