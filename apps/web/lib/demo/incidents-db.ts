import { demoGraph } from "./fixtures";
import type {
  RiskLevel,
  EvidenceConfidence,
  ScamJourney,
  CytoscapeGraph,
} from "@/lib/api/types";

export interface UnifiedIncident {
  id: string;
  pattern: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: EvidenceConfidence;
  current_stage: string;
  last_activity: string;
  isRecent?: boolean;
  journey: ScamJourney;
  assessment: {
    risk_score: number;
    risk_level: string;
    confidence: string;
    evidence_confidence: string;
    pattern_name?: string;
    detected_pattern_name?: string;
    emerging_status?: string;
    reason_codes: string[];
    counter_evidence: Array<{ signal_id: string; description: string; [key: string]: any }>;
    signals?: any[];
    intervention: {
      action: string;
      friction_level: string;
      banner_message: string;
      friction_delay_seconds: number;
      banner_title?: string;
      [key: string]: any;
    };
    [key: string]: any;
  };
  graph: CytoscapeGraph;
  [key: string]: any;
}

export const CANONICAL_INCIDENTS: Record<string, UnifiedIncident> = {
  "INC-SBI-KYC-01": {
    id: "INC-SBI-KYC-01",
    pattern: "SBI Mandatory PAN-Aadhaar KYC Suspension Lure",
    risk_score: 92,
    risk_level: "CRITICAL",
    confidence: "HIGH",
    current_stage: "PAYMENT_INTENT",
    last_activity: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
    isRecent: true,
    journey: {
      journey_id: "JRN-SBI-01",
      incident_id: "INC-SBI-KYC-01",
      current_stage: "PAYMENT_INTENT",
      steps: [
        {
          step_id: "step_1",
          stage: "INITIAL_CONTACT",
          label: "Inbound SMS Warning",
          description: "SMS claiming bank account deactivation within 24h.",
          severity: "MEDIUM",
          offset_seconds: 0,
        },
        {
          step_id: "step_2",
          stage: "MALICIOUS_LINK",
          label: "Phishing Link Clicked",
          description: "User navigated to http://xn--pple-43d.com/sbi-verify.",
          severity: "HIGH",
          offset_seconds: 140,
        },
        {
          step_id: "step_3",
          stage: "CREDENTIAL_HARVEST",
          label: "Credential & OTP Form",
          description: "Target requested netbanking password and SMS OTP.",
          severity: "CRITICAL",
          offset_seconds: 320,
        },
        {
          step_id: "step_4",
          stage: "PAYMENT_INTENT",
          label: "Reverse-Collect UPI Request",
          description: "₹4,500 collect debit request masquerading as verification fee.",
          severity: "CRITICAL",
          offset_seconds: 480,
        },
      ],
      prediction: {
        predicted_next_stage: "SETTLEMENT",
        rationale: "Immediate fund withdrawal to layer-1 mule network once PIN is confirmed.",
        recommended_preventive_action: "Block outgoing collect transaction and suspend destination VPA.",
      },
    },
    assessment: {
      risk_score: 92,
      risk_level: "CRITICAL",
      confidence: "HIGH",
      evidence_confidence: "HIGH",
      pattern_name: "SBI Mandatory PAN-Aadhaar KYC Suspension Lure",
      detected_pattern_name: "SBI KYC Phishing & Reverse-Collect",
      emerging_status: "MUTATED_VARIANT",
      reason_codes: [
        "PUNYCODE_HOMOGRAPH_SPOOFING",
        "REVERSE_COLLECT_FRAUD",
        "PSYCHOLOGICAL_URGENCY_COERCION",
        "KNOWN_MULE_CLUSTER_OVERLAP",
      ],
      counter_evidence: [],
      signals: [],
      intervention: {
        action: "PRE_PAYMENT_INTERVENTION",
        friction_level: "BLOCK",
        friction_delay_seconds: 0,
        banner_message: "CRITICAL FRAUD: High-risk reverse collect request from unverified VPA.",
      },
    },
    graph: demoGraph,
  },
  "INC-ELEC-DISCON-02": {
    id: "INC-ELEC-DISCON-02",
    pattern: "Urgent Electricity Power Cutoff Threat",
    risk_score: 84,
    risk_level: "HIGH",
    confidence: "HIGH",
    current_stage: "CREDENTIAL_HARVEST",
    last_activity: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    isRecent: false,
    journey: {
      journey_id: "JRN-ELEC-02",
      incident_id: "INC-ELEC-DISCON-02",
      current_stage: "CREDENTIAL_HARVEST",
      steps: [
        {
          step_id: "step_1",
          stage: "INITIAL_CONTACT",
          label: "Electricity Cutoff SMS",
          description: "Power will be cut at 9:30 PM tonight due to unpaid bill.",
          severity: "HIGH",
          offset_seconds: 0,
        },
        {
          step_id: "step_2",
          stage: "IMPERSONATION",
          label: "Helpline Caller Connect",
          description: "Caller instructed victim to install remote assistance APK.",
          severity: "HIGH",
          offset_seconds: 210,
        },
        {
          step_id: "step_3",
          stage: "CREDENTIAL_HARVEST",
          label: "Live OTP Solicitation",
          description: "Caller requested OTP arrived on phone during active call.",
          severity: "CRITICAL",
          offset_seconds: 400,
        },
      ],
      prediction: {
        predicted_next_stage: "PAYMENT_INTENT",
        rationale: "Attacker prepares immediate wallet drain using extracted OTP.",
        recommended_preventive_action: "Terminate call immediately and lock UPI authorization credentials.",
      },
    },
    assessment: {
      risk_score: 84,
      risk_level: "HIGH",
      confidence: "HIGH",
      evidence_confidence: "HIGH",
      pattern_name: "Urgent Electricity Power Cutoff Threat",
      detected_pattern_name: "Electricity Power Disconnection Vishing",
      emerging_status: "ACTIVE_OUTBREAK",
      reason_codes: [
        "ACTIVE_CALL_OTP_CORRELATION",
        "UTILITY_IMPERSONATION_LURE",
        "REMOTE_APP_SOLICITATION",
      ],
      counter_evidence: [],
      signals: [],
      intervention: {
        action: "WARN_BANNER",
        friction_level: "HIGH",
        friction_delay_seconds: 15,
        banner_message: "VISHING ALERT: Never share SMS OTP over phone call with utility callers.",
      },
    },
    graph: demoGraph,
  },
};

export function getUnifiedIncident(id: string, custom?: any): UnifiedIncident {
  if (CANONICAL_INCIDENTS[id]) {
    return CANONICAL_INCIDENTS[id];
  }

  if (custom) {
    return {
      id: custom.id || id,
      pattern: custom.pattern || custom.title || "Custom Investigated Incident",
      risk_score: custom.risk_score || 75,
      risk_level: custom.risk_level || "HIGH",
      confidence: custom.confidence || "MEDIUM",
      current_stage: custom.current_stage || "PAYMENT_INTENT",
      last_activity: custom.last_activity || new Date().toISOString(),
      isRecent: true,
      journey: custom.journey || CANONICAL_INCIDENTS["INC-SBI-KYC-01"].journey,
      assessment: custom.assessment
        ? {
            ...CANONICAL_INCIDENTS["INC-SBI-KYC-01"].assessment,
            ...custom.assessment,
            evidence_confidence:
              custom.assessment.evidence_confidence ||
              custom.assessment.confidence ||
              "MEDIUM",
            counter_evidence: custom.assessment.counter_evidence || [],
          }
        : CANONICAL_INCIDENTS["INC-SBI-KYC-01"].assessment,
      graph: custom.graph || demoGraph,
    };
  }

  // Fallback default
  return CANONICAL_INCIDENTS["INC-SBI-KYC-01"];
}
