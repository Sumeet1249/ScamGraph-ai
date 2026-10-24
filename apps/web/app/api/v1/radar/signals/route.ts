import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

const DEFAULT_SIGNALS = [
  {
    signal_id: "sig_da_surge_01",
    campaign_id: "camp_da_cbi_01",
    signal_type: "HIGH_RISK_OUTBREAK",
    severity: "CRITICAL",
    confidence: 0.94,
    current_velocity: 18.0,
    baseline_velocity: 4.2,
    acceleration: 8.0,
    incident_count_window: 48,
    unique_entity_count_window: 22,
    regions: ["Delhi NCR", "Maharashtra", "Karnataka"],
    channels: ["WhatsApp", "Skype", "IVR"],
    languages: ["English", "Hindi"],
    strongest_evidence: [
      "Report volume surged +428% over 14-day baseline",
      "Repeated extortion script citing Mumbai Police & Supreme Court",
      "14 collection VPAs rotated across private banks",
    ],
    reason_codes: ["HIGH_RISK_OUTBREAK", "RAPID_INCIDENT_GROWTH", "PAYMENT_REUSE_SPIKE"],
    first_detected: new Date(Date.now() - 86400000 * 2).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    signal_id: "sig_task_growth_02",
    campaign_id: "camp_task_job_02",
    signal_type: "RAPID_GROWTH",
    severity: "HIGH",
    confidence: 0.88,
    current_velocity: 12.0,
    baseline_velocity: 5.0,
    acceleration: 4.0,
    incident_count_window: 34,
    unique_entity_count_window: 18,
    regions: ["West Bengal", "Uttar Pradesh", "Telangana"],
    channels: ["Telegram", "WhatsApp", "Instagram"],
    languages: ["English", "Hinglish"],
    strongest_evidence: [
      "Accelerating report volume (12.0 reports/day)",
      "Channel migration from Instagram DMs into encrypted Telegram group",
    ],
    reason_codes: ["RAPID_GROWTH", "CHANNEL_MIGRATION"],
    first_detected: new Date(Date.now() - 86400000 * 4).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    signal_id: "sig_fedex_resurge_03",
    campaign_id: "camp_fedex_resurgent_04",
    signal_type: "RESURGENCE",
    severity: "HIGH",
    confidence: 0.87,
    current_velocity: 6.0,
    baseline_velocity: 0.5,
    acceleration: 5.0,
    incident_count_window: 21,
    unique_entity_count_window: 14,
    regions: ["Tamil Nadu", "Maharashtra"],
    channels: ["IVR", "WhatsApp"],
    languages: ["English"],
    strongest_evidence: [
      "Dormant campaign reappeared after 65 days of zero activity",
      "Identical fake customs notice PDF with rotated phone numbers",
    ],
    reason_codes: ["CAMPAIGN_RESURGENCE", "PHONE_ROTATION"],
    first_detected: new Date(Date.now() - 86400000 * 1).toISOString(),
    last_updated: new Date().toISOString(),
  },
  {
    signal_id: "sig_elec_emerg_04",
    campaign_id: "camp_elec_kyc_03",
    signal_type: "NEW_CAMPAIGN",
    severity: "WATCH",
    confidence: 0.82,
    current_velocity: 5.0,
    baseline_velocity: 1.2,
    acceleration: 3.0,
    incident_count_window: 11,
    unique_entity_count_window: 9,
    regions: ["Haryana", "Punjab", "Delhi NCR"],
    channels: ["SMS", "Phone Call"],
    languages: ["Hindi", "English"],
    strongest_evidence: [
      "Emerging cluster coercive SMS threatening power disconnection tonight at 9:30 PM",
    ],
    reason_codes: ["NEW_CAMPAIGN", "COHESIVE_SCAM_DNA"],
    first_detected: new Date(Date.now() - 86400000 * 3).toISOString(),
    last_updated: new Date().toISOString(),
  },
];

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const demo = url.searchParams.get("demo_mode");
    const backendRes = await fetch(`${BACKEND_URL}/api/v1/radar/signals?demo_mode=${demo || "true"}`, {
      next: { revalidate: 0 },
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend offline fallback to canonical surveillance data
  }
  return NextResponse.json(DEFAULT_SIGNALS);
}
