import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

const DEFAULT_CAMPAIGNS = [
  {
    id: "camp-kyc-freenom",
    name: "State Bank & Aadhaar KYC Suspension Syndicate",
    pattern_type: "KYC_IMPERSONATION",
    severity: "CRITICAL",
    incidents_count: 24,
    shared_infrastructure_count: 7,
    first_seen: "2026-10-15T08:30:00Z",
    last_seen: "2026-10-20T17:45:00Z",
    sample_domain: "sbi-kyc-verify-portal.online",
    sample_vpa: "sbi.helpdesk.kyc@oksbi",
    tactics: ["AUTHORITY_IMPERSONATION", "EXTREME_URGENCY", "CREDENTIAL_HARVEST"],
    description: "Coordinated cluster targeting banking customers using spoofed SMS, KYC warnings, and malicious domains.",
  },
  {
    id: "camp-power-urgent",
    name: "Electricity & Utility Disconnection Phishing Ring",
    pattern_type: "UTILITY_BILL_COERCION",
    severity: "HIGH",
    incidents_count: 18,
    shared_infrastructure_count: 4,
    first_seen: "2026-10-12T10:00:00Z",
    last_seen: "2026-10-20T19:00:00Z",
    sample_domain: "electricity-bill-pay.xyz",
    sample_vpa: "billdesk.utility.pay@paytm",
    tactics: ["UTILITY_BLACKOUT_THREAT", "IMMEDIATE_DISCONNECT_PRESSURE"],
    description: "Urgent electricity shutoff notices redirecting to unauthorized merchant collect requests.",
  },
  {
    id: "camp-work-from-home",
    name: "E-Commerce Rating & Telegram Task Fraud Network",
    pattern_type: "PART_TIME_JOB_FRAUD",
    severity: "HIGH",
    incidents_count: 12,
    shared_infrastructure_count: 5,
    first_seen: "2026-10-16T11:00:00Z",
    last_seen: "2026-10-20T20:15:00Z",
    sample_domain: "task-earning-hub.xyz",
    sample_vpa: "daily.rewards.vip@ybl",
    tactics: ["ADVANCE_FEE_TRAP", "COMMISSION_LURE", "MULE_ACCOUNT_EXFILTRATION"],
    description: "Deceptive part-time job lures promising daily returns for rating videos.",
  },
  {
    id: "camp-investment-vip",
    name: "High-Yield VIP Crypto & Stock Advisory Syndicate",
    pattern_type: "INVESTMENT_LURE",
    severity: "MEDIUM",
    incidents_count: 10,
    shared_infrastructure_count: 3,
    first_seen: "2026-10-14T09:00:00Z",
    last_seen: "2026-10-22T09:37:00Z",
    sample_domain: "vip-stock-trade.top",
    sample_vpa: "vip.advisory.funds@axl",
    tactics: ["PUMP_AND_DUMP", "FAKE_PORTFOLIO_DASHBOARD"],
    description: "WhatsApp group pump-and-dump scheme mimicking institutional stock brokerages.",
  },
];

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.toString();
    const url = `${BACKEND_URL}/api/v1/campaigns${query ? `?${query}` : "?demo_mode=true"}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      if (Array.isArray(data) && data.length > 0) {
        return NextResponse.json(data);
      }
    }
  } catch (err) {
    console.warn("Backend campaigns fetch error, serving sovereign defaults:", err);
  }

  return NextResponse.json(DEFAULT_CAMPAIGNS);
}
