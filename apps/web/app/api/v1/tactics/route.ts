import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: NextRequest) {
  try {
    const rootDir = process.cwd();
    const manifestJsonPath = path.resolve(rootDir, "../../data/tactics/manifest.json");
    let manifestData = null;

    if (fs.existsSync(manifestJsonPath)) {
      manifestData = JSON.parse(fs.readFileSync(manifestJsonPath, "utf-8"));
    } else {
      const altPath = path.resolve(rootDir, "data/tactics/manifest.json");
      if (fs.existsSync(altPath)) {
        manifestData = JSON.parse(fs.readFileSync(altPath, "utf-8"));
      }
    }

    if (!manifestData) {
      manifestData = {
        schema_version: "2.0.0",
        tactics_taxonomy: {
          version: "2.0",
          total_tactics: 20,
          tactics: [
            { name: "AUTHORITY", severity: "HIGH", languages: ["en", "hi", "hinglish"], primary_actions: ["DO_NOT_DISCONNECT", "REPLY"] },
            { name: "URGENCY", severity: "MEDIUM", languages: ["en", "hi", "hinglish"], primary_actions: ["CLICK_LINK", "SEND_PAYMENT"] },
            { name: "FEAR", severity: "HIGH", languages: ["en", "hi", "hinglish"], primary_actions: ["DO_NOT_DISCONNECT", "SEND_PAYMENT"] },
            { name: "ISOLATION", severity: "CRITICAL", languages: ["en", "hi", "hinglish"], primary_actions: ["DO_NOT_DISCONNECT", "KEEP_SECRET"] },
            { name: "PAYMENT_PRESSURE", severity: "CRITICAL", languages: ["en", "hi", "hinglish"], primary_actions: ["SEND_PAYMENT", "APPROVE_UPI_REQUEST"] },
            { name: "CREDENTIAL_PRESSURE", severity: "CRITICAL", languages: ["en", "hi", "hinglish"], primary_actions: ["SHARE_OTP", "SHARE_CREDENTIAL"] },
            { name: "REMOTE_ACCESS_PRESSURE", severity: "CRITICAL", languages: ["en", "hi", "hinglish"], primary_actions: ["INSTALL_APP", "SHARE_SCREEN"] },
          ]
        }
      };
    }

    return NextResponse.json(manifestData);
  } catch (error) {
    console.error("Tactics API error:", error);
    return NextResponse.json({ error: "Failed to load tactics" }, { status: 500 });
  }
}
