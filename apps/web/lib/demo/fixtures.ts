import type {
  ScamJourney,
  ScamAssessment,
  CytoscapeGraph,
  EvidenceSignal,
} from "@/lib/api/types";

export const demoCampaigns = [
  {
    id: "camp-kyc-01",
    name: "SBI / HDFC KYC Expiry Phishing Wave",
    severity: "CRITICAL",
    pattern_type: "IMPERSONATION_URGENCY",
    incidents_count: 24,
    shared_infrastructure_count: 5,
    first_seen: new Date(Date.now() - 86400000 * 3).toISOString(),
    sample_domain: "sbi-kyc-update-portal.click",
    similarity: {
      semantic_similarity: 0.92,
      journey_similarity: 0.88,
      pattern_similarity: 0.95,
      infrastructure_similarity: 0.74,
      payment_similarity: 0.82,
      identifier_overlap: 0.65,
    },
  },
  {
    id: "camp-elec-02",
    name: "State Electricity Power Disconnect SMS Ring",
    severity: "HIGH",
    pattern_type: "UTILITY_BILL_COERCION",
    incidents_count: 17,
    shared_infrastructure_count: 3,
    first_seen: new Date(Date.now() - 86400000 * 5).toISOString(),
    sample_domain: "quick-bill-pay-support.top",
    similarity: {
      semantic_similarity: 0.84,
      journey_similarity: 0.79,
      pattern_similarity: 0.89,
      infrastructure_similarity: 0.62,
      payment_similarity: 0.75,
      identifier_overlap: 0.5,
    },
  },
  {
    id: "camp-job-03",
    name: "Telegram Part-Time Task & Deposit Syndicate",
    severity: "CRITICAL",
    pattern_type: "PART_TIME_JOB_DEPOSIT",
    incidents_count: 38,
    shared_infrastructure_count: 8,
    first_seen: new Date(Date.now() - 86400000 * 7).toISOString(),
    sample_domain: "amazon-review-earnings.xyz",
    similarity: {
      semantic_similarity: 0.78,
      journey_similarity: 0.91,
      pattern_similarity: 0.94,
      infrastructure_similarity: 0.83,
      payment_similarity: 0.96,
      identifier_overlap: 0.72,
    },
  },
];

export const demoSignals: EvidenceSignal[] = [
  {
    signal_id: "sig-001",
    signal_type: "URGENCY_KEYWORD_DETECTED",
    dimension: "SEMANTIC",
    severity: "HIGH",
    confidence: 0.95,
    weight: 1.5,
    description: "Urgent electricity disconnection ultimatum detected within message text.",
    observed_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    provenance: {
      source_service: "services.pattern-engine",
      extraction_method: "regex_urgency_extractor",
    },
  },
  {
    signal_id: "sig-002",
    signal_type: "SUSPICIOUS_TLD_HOSTED",
    dimension: "URL",
    severity: "CRITICAL",
    confidence: 0.98,
    weight: 2.0,
    description: "URL hosted on high-abuse TLD (.top) registered less than 48 hours ago.",
    observed_at: new Date(Date.now() - 3600000 * 1.5).toISOString(),
    provenance: {
      source_service: "services.investigation.tinyfish",
      extraction_method: "domain_whois_rdap",
    },
  },
  {
    signal_id: "sig-003",
    signal_type: "CREDENTIAL_HARVEST_FORM",
    dimension: "WEB_DOM",
    severity: "CRITICAL",
    confidence: 0.92,
    weight: 2.5,
    description: "Headless browser observed netbanking password and OTP input fields.",
    observed_at: new Date(Date.now() - 3600000 * 1.2).toISOString(),
    provenance: {
      source_service: "services.investigation.tinyfish",
      extraction_method: "dom_input_inspector",
    },
  },
  {
    signal_id: "sig-004",
    signal_type: "VPA_MISMATCH",
    dimension: "PAYMENT",
    severity: "HIGH",
    confidence: 0.89,
    weight: 1.8,
    description: "Payment recipient VPA fasttransfer88@axisbank does not match stated utility electricity board.",
    observed_at: new Date(Date.now() - 1800000).toISOString(),
    provenance: {
      source_service: "services.api.payment",
      extraction_method: "vpa_handle_adjudicator",
    },
  },
];

export const demoJourney: ScamJourney = {
  incident_id: "inc-demo-8841",
  current_stage: "PAYMENT_REQUEST",
  steps: [
    {
      step_id: "step-1",
      stage: "INITIAL_CONTACT",
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      time_delta_seconds: 0,
      description: "Unsolicited SMS from unverified alphanumeric header VM-DISCOM.",
      associated_signals: [demoSignals[0]],
    },
    {
      step_id: "step-2",
      stage: "URGENCY_FEAR",
      timestamp: new Date(Date.now() - 5400000).toISOString(),
      time_delta_seconds: 1800,
      description: "Notice states power will be disconnected at 9:30 PM tonight unless bill is cleared immediately.",
      associated_signals: [demoSignals[0]],
    },
    {
      step_id: "step-3",
      stage: "SUSPICIOUS_URL",
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      time_delta_seconds: 3600,
      description: "User tapped phishing link to sbi-kyc-update-portal.click.",
      associated_signals: [demoSignals[1]],
    },
    {
      step_id: "step-4",
      stage: "CREDENTIAL_REQUEST",
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      time_delta_seconds: 5400,
      description: "Landing page requested customer mobile number, net banking credentials, and OTP.",
      associated_signals: [demoSignals[2]],
    },
    {
      step_id: "step-5",
      stage: "PAYMENT_REQUEST",
      timestamp: new Date(Date.now() - 600000).toISOString(),
      time_delta_seconds: 6600,
      description: "UPI collect request for ₹14,000 sent to user VPA from fasttransfer88@axisbank.",
      associated_signals: [demoSignals[3]],
    },
  ],
  prediction: {
    predicted_next_stage: "PAYMENT_INTENT",
    confidence: 0.94,
    rationale: "Scam progression reached terminal stage 5. Rapid transition observed across grooming stages.",
    recommended_preventive_action: "Trigger immediate UPI pre-payment caution banner and impose 60s friction delay.",
  },
};

export const demoAssessment: ScamAssessment = {
  incident_id: "inc-demo-8841",
  risk_score: 87,
  risk_level: "HIGH",
  confidence: "HIGH",
  evidence_confidence: "HIGH",
  counter_evidence: [],
  reasons: [
    "REASON_URGENCY_ULTIMATUM_DETECTED",
    "REASON_NEW_UNVERIFIED_PHISHING_DOMAIN",
    "REASON_CREDENTIAL_HARVEST_FORM_PRESENT",
    "REASON_PAYMENT_ENTITY_MISMATCH",
  ],
  signals: demoSignals,
  intervention: {
    action: "STRONG_WARNING",
    friction_delay_seconds: 45,
    banner_title: "High Risk of Electricity Bill Impersonation Scam",
    banner_message:
      "This request claims to be from your electricity provider, but directs payment to a private personal VPA. Do not authorize payment or enter your UPI PIN.",
    recommendations: [
      "Verify directly on your official state electricity board portal.",
      "Electricity providers never send personal mobile numbers or personal VPAs for bill settlement.",
      "Report this message to 1930 / cybercrime.gov.in.",
    ],
  },
  journey: demoJourney,
  created_at: new Date().toISOString(),
};

export const demoGraph: CytoscapeGraph = {
  nodes: [
    {
      data: {
        id: "inc-demo-8841",
        label: "Incident #8841",
        type: "incident",
        severity: "CRITICAL",
        risk_score: 87,
      },
    },
    {
      data: {
        id: "node-msg",
        label: "VM-DISCOM SMS",
        type: "message",
        severity: "HIGH",
      },
    },
    {
      data: {
        id: "node-url",
        label: "sbi-kyc-update-portal.click",
        type: "url",
        severity: "CRITICAL",
      },
    },
    {
      data: {
        id: "node-vpa",
        label: "fasttransfer88@axisbank",
        type: "upi_handle",
        severity: "HIGH",
      },
    },
    {
      data: {
        id: "node-camp",
        label: "KYC Expiry Wave #01",
        type: "campaign",
        severity: "CRITICAL",
      },
    },
  ],
  edges: [
    {
      data: {
        id: "e1",
        source: "inc-demo-8841",
        target: "node-msg",
        label: "TRIGGERED_BY",
      },
    },
    {
      data: {
        id: "e2",
        source: "node-msg",
        target: "node-url",
        label: "CONTAINS_URL",
      },
    },
    {
      data: {
        id: "e3",
        source: "inc-demo-8841",
        target: "node-vpa",
        label: "PAYMENT_INTENT",
      },
    },
    {
      data: {
        id: "e4",
        source: "inc-demo-8841",
        target: "node-camp",
        label: "MEMBER_OF_CAMPAIGN",
      },
    },
  ],
};
