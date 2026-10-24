/**
 * Proxy endpoint for frontend to communicate with backend investigation service.
 * Forwards requests to: http://127.0.0.1:8001/api/v1/investigate
 */

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward to backend
    const response = await fetch(`${BACKEND_URL}/api/v1/investigate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error (${response.status}):`, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Investigation proxy error:", error);
    return NextResponse.json(
      { error: "Failed to process investigation request" },
      { status: 500 }
    );
  }
}
