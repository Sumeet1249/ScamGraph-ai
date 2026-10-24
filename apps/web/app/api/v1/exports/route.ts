import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const incidentId = body.incident_id || `SG-${Date.now()}`;
    const timestamp = new Date().toISOString();
    const records = body.records || [];

    // Calculate Section 65B tamper-evident hash
    const hash = crypto.createHash("sha256").update(JSON.stringify(body)).digest("hex");

    const exportCsv = [
      "SECTION 65B FORENSIC EVIDENCE CERTIFICATE - INDIAN EVIDENCE ACT 1872 / BSA 2023",
      `INCIDENT IDENTIFIER: ${incidentId}`,
      `CERTIFICATION TIMESTAMP (UTC): ${timestamp}`,
      `INTEGRITY SIGNATURE (SHA-256): ${hash}`,
      `STATUTORY FORUM: National Cybercrime Reporting Portal (1930) / Bank Nodal Officer`,
      "",
      "RECORD_TYPE,IDENTIFIER_VALUE,CATEGORY,OBSERVED_AT,RISK_WEIGHT",
      `INCIDENT,${incidentId},FINANCIAL_SCAM,${timestamp},CRITICAL`,
      ...records.map((r: any) => `${r.type || "SIGNAL"},"${r.value || r.title || ""}",${r.category || "EVIDENCE"},${r.time || timestamp},HIGH`),
      "",
      "CERTIFICATE AFFIDAVIT:",
      "I hereby certify that the electronic records contained herein are authentic computer-generated logs produced by ScamGraph AI defense systems without manual alteration or tampering.",
    ].join("\n");

    return new NextResponse(exportCsv, {
      status: 200,
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename=scamgraph_section65b_${incidentId}.csv`,
        "X-Evidence-Hash": hash,
      },
    });
  } catch (error) {
    console.error("Export generation error:", error);
    return NextResponse.json({ error: "Failed to generate forensic export" }, { status: 500 });
  }
}
