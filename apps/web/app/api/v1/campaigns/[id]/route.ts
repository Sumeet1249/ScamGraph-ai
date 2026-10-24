import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";

const DEFAULT_CAMPAIGNS: Record<string, any> = {
  camp_da_cbi_01: {
    campaign_id: "camp_da_cbi_01",
    schema_version: "2.0.0",
    title: "Digital Arrest CBI / Mumbai Police Extortion",
    scam_family: "DIGITAL_ARREST",
    family_confidence: 0.96,
    lifecycle_state: "OUTBREAK",
    velocity_state: "OUTBREAK",
    review_state: "INVESTIGATING",
    first_seen: new Date(Date.now() - 86400000 * 20).toISOString(),
    last_seen: new Date().toISOString(),
    incident_count: 48,
    strongly_related_incident_count: 36,
    unique_entity_count: 22,
    unique_payment_identifier_count: 14,
    unique_domain_count: 6,
    unique_phone_count: 12,
    languages: ["English", "Hindi"],
    channels: ["WhatsApp", "Skype", "IVR"],
    regions: ["Delhi NCR", "Maharashtra", "Karnataka"],
    journey_profile: [
      "INITIAL_CONTACT_IVR",
      "AUTHORITY_IMPERSONATION",
      "DIGITAL_ARREST_ISOLATION",
      "ASSET_DECLARATION",
      "DEMAND_SAFE_TRANSFER",
    ],
    tactic_profile: [
      "AUTHORITY_IMPERSONATION",
      "EXTREME_URGENCY",
      "LEGAL_CONSEQUENCES_THREAT",
      "SECRECY_ISOLATION",
    ],
    infrastructure_profile: [
      "+919876543210",
      "+919811223344",
      "cbi-verification-portal.org",
      "mumbai-police-cybercell.net",
    ],
    payment_profile: [
      "mumbai.police.audit@sbi",
      "cbi.investigation.funds@icici",
      "rbi.clearing.supervision@hdfc",
    ],
    confidence: 0.94,
    current_velocity: 18.0,
    baseline_velocity: 4.2,
    growth_multiplier: 4.28,
    acceleration: 8.0,
    mutation_count: 4,
    active_mutations: [
      "PHONE_ROTATION(+919876543210)",
      "PAYMENT_ROTATION(mumbai.police.audit@sbi)",
      "DOMAIN_ROTATION(cbi-verification-portal.org)",
    ],
  },
  camp_task_job_02: {
    campaign_id: "camp_task_job_02",
    schema_version: "2.0.0",
    title: "YouTube Video Like / Telegram VIP Task Scam",
    scam_family: "TASK_SCAM",
    family_confidence: 0.92,
    lifecycle_state: "SURGING",
    velocity_state: "SURGING",
    review_state: "ACKNOWLEDGED",
    first_seen: new Date(Date.now() - 86400000 * 12).toISOString(),
    last_seen: new Date().toISOString(),
    incident_count: 34,
    strongly_related_incident_count: 25,
    unique_entity_count: 18,
    unique_payment_identifier_count: 11,
    unique_domain_count: 8,
    unique_phone_count: 9,
    languages: ["English", "Hinglish"],
    channels: ["Telegram", "WhatsApp", "Instagram"],
    regions: ["West Bengal", "Uttar Pradesh", "Telangana"],
    journey_profile: [
      "UNSOLICITED_JOB_OFFER",
      "SMALL_PAYOUT_ESTABLISHED",
      "PREPAID_VIP_TASK",
      "WITHDRAWAL_BLOCK_PENALTY",
    ],
    tactic_profile: ["FINANCIAL_REWARD", "PREPAID_DEPOSIT", "SUNKEN_COST"],
    infrastructure_profile: ["task-earning-hub.xyz", "+919888777666"],
    payment_profile: ["vip.task.earning@paytm", "fastpay.merchant@oksbi"],
    confidence: 0.88,
    current_velocity: 12.0,
    baseline_velocity: 5.0,
    growth_multiplier: 2.4,
    acceleration: 4.0,
    mutation_count: 2,
    active_mutations: ["CHANNEL_MIGRATION(Instagram DM -> Telegram)"],
  },
};

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const backendRes = await fetch(`${BACKEND_URL}/api/v1/campaigns/${params.id}`, {
      next: { revalidate: 0 },
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (e) {
    // Backend offline fallback
  }

  const camp = DEFAULT_CAMPAIGNS[params.id] || DEFAULT_CAMPAIGNS["camp_da_cbi_01"];
  return NextResponse.json(camp);
}
