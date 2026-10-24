import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const DEFAULT_BLIPS = [
  {
    blip_id: "blip_camp_da_cbi_01",
    campaign_id: "camp_da_cbi_01",
    title: "Digital Arrest CBI / Mumbai Police Extortion",
    scam_family: "DIGITAL_ARREST",
    ring: "CRITICAL",
    radius_norm: 0.28,
    angle_rad: 0.85,
    size: 24,
    pulse_speed: 3.5,
    severity: "CRITICAL",
    confidence: 0.94,
    incident_count: 48,
    growth_percent: 428.0,
    is_resurgent: false,
    is_mutating: true,
    top_reason: "+428% surge over 14-day baseline across Maharashtra & Delhi NCR",
  },
  {
    blip_id: "blip_camp_task_job_02",
    campaign_id: "camp_task_job_02",
    title: "YouTube Video Like / Telegram VIP Task Scam",
    scam_family: "TASK_SCAM",
    ring: "SURGING",
    radius_norm: 0.58,
    angle_rad: 2.45,
    size: 20,
    pulse_speed: 2.2,
    severity: "HIGH",
    confidence: 0.88,
    incident_count: 34,
    growth_percent: 240.0,
    is_resurgent: false,
    is_mutating: true,
    top_reason: "Accelerating report volume (12.0/day) with prepaid VIP tasks",
  },
  {
    blip_id: "blip_camp_elec_kyc_03",
    campaign_id: "camp_elec_kyc_03",
    title: "State Electricity Power Disconnection Threat",
    scam_family: "FAKE_SUPPORT",
    ring: "EMERGING",
    radius_norm: 0.84,
    angle_rad: 4.12,
    size: 14,
    pulse_speed: 1.2,
    severity: "WATCH",
    confidence: 0.82,
    incident_count: 11,
    growth_percent: 180.0,
    is_resurgent: false,
    is_mutating: true,
    top_reason: "Emerging threat pattern: SMS alert coercing remote access APK install",
  },
  {
    blip_id: "blip_camp_fedex_resurgent_04",
    campaign_id: "camp_fedex_resurgent_04",
    title: "FedEx Narcotics Customs Detention Resurgence",
    scam_family: "CUSTOMS_PARCEL",
    ring: "SURGING",
    radius_norm: 0.54,
    angle_rad: 5.65,
    size: 18,
    pulse_speed: 2.8,
    severity: "HIGH",
    confidence: 0.87,
    incident_count: 21,
    growth_percent: 310.0,
    is_resurgent: true,
    is_mutating: true,
    top_reason: "Reappeared with fresh IVR robocalls after 60+ days dormancy",
  },
];

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const demo = url.searchParams.get("demo_mode");
    const backendRes = await fetch(`${BACKEND_URL}/api/v1/radar/blips?demo_mode=${demo || "true"}`, {
      next: { revalidate: 0 },
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend offline fallback to canonical surveillance data
  }
  return NextResponse.json(DEFAULT_BLIPS);
}
