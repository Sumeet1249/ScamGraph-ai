/**
 * Catch-all proxy endpoint for all ScamGraph Rescue API calls
 * Forwards requests from Next.js (port 3001) to FastAPI backend (port 8001)
 */

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const subpath = params.path ? params.path.join("/") : "";
    const searchParams = request.nextUrl.search;
    const targetUrl = `${BACKEND_URL}/api/v1/rescue/${subpath}${searchParams}`;

    const res = await fetch(targetUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      const errText = await res.text();
      return NextResponse.json(
        { error: `Backend error ${res.status}: ${errText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Rescue proxy GET error:", error);
    return NextResponse.json(
      { error: "Failed to connect to Rescue backend service", details: error?.message },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const subpath = params.path ? params.path.join("/") : "";
    const searchParams = request.nextUrl.search;
    const targetUrl = `${BACKEND_URL}/api/v1/rescue/${subpath}${searchParams}`;

    let body = null;
    try {
      body = await request.json();
    } catch {
      // Body might be empty
    }

    const res = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const errText = await res.text();
      return NextResponse.json(
        { error: `Backend error ${res.status}: ${errText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Rescue proxy POST error:", error);
    return NextResponse.json(
      { error: "Failed to connect to Rescue backend service", details: error?.message },
      { status: 500 }
    );
  }
}
