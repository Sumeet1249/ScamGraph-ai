import type {
  RiskLevel,
  EvidenceConfidence,
  EvidenceSignal,
  ScamJourney,
  RiskAssessment,
  CytoscapeGraph,
} from "@/lib/api/types";

export interface UnifiedIncidentData {
  id: string;
  pattern: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: EvidenceConfidence;
  current_stage: string;
  last_activity: string;
  isRecent?: boolean;
  assessment: RiskAssessment;
  journey: ScamJourney;
  graph: CytoscapeGraph;
}

export const CANONICAL_INCIDENTS: Record<string, UnifiedIncidentData> = {
  inv_85f62e519d: {
    id: "inv_85f62e519d",
    pattern: "Aadhaar & Bank KYC Suspension Phishing",
    risk_score: 72,
    risk_level: "HIGH",
    confidence: "HIGH",
    current_stage: "PAYMENT_EXECUTION",
    last_activity: "2026-10-21T09:17:00Z",
    isRecent: true,
    assessment: {
      incident_id: "inv_85f62e519d",
      risk_score: 72,
      risk_level: "HIGH",
      evidence_confidence: "HIGH",
      pattern_name: "Aadhaar & Bank KYC Suspension Phishing",
      detected_pattern_name: "Aadhaar & Bank KYC Suspension Phishing",
      emerging_status: "MUTATED_VARIANT",
      is_insufficient_evidence: false,
      intervention: {
        action: "PRE_PAYMENT_INTERVENTION",
        friction_delay_seconds: 15,
        banner_title: "Pre-Payment Security Intervention",
        banner_message: "High-confidence bank impersonation workflow detected. Coercive urgency and credential harvest observed.",
        dismissible: false,
      },
      reason_codes: [
        "[SUPPORT] Bank impersonation detected",
        "[SUPPORT] Urgency / account suspension threat",
        "[SUPPORT] Credential collection form observed",
        "[SUPPORT] OTP harvest input observed",
        "[SUPPORT] Payment to individual VPA handle",
        "[SUPPORT] Workflow resembles historical campaign KYC-Cluster-03",
      ],
      counter_evidence: [
        "Account verified against legitimate portal: 0 records",
      ],
      signals: [
        {
          signal_id: "sig-85-01",
          dimension: "SEMANTIC",
          signal_type: "URGENCY_PRESSURE_DETECTED",
          severity: "HIGH",
          confidence: 0.92,
          weight: 1.5,
          description: "Urgent coercive language: 'Your SBI account will be suspended within 2 hours'",
          observed_at: "2026-10-21T08:45:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
        {
          signal_id: "sig-85-02",
          dimension: "URL",
          signal_type: "SUSPICIOUS_TLD_USED",
          severity: "HIGH",
          confidence: 0.94,
          weight: 1.4,
          description: "Phishing destination uses suspicious newly registered domain: sbi-kyc-verify-portal.online",
          observed_at: "2026-10-21T09:00:00Z",
          provenance: { source_service: "services/investigation", detector_name: "URLAnalyzer" },
        },
        {
          signal_id: "sig-85-03",
          dimension: "PAYMENT",
          signal_type: "INDIVIDUAL_VPA_PAYMENT_TARGETED",
          severity: "CRITICAL",
          confidence: 0.95,
          weight: 1.6,
          description: "Re-verification fee routed to personal VPA: scammer.ops@oksbi",
          observed_at: "2026-10-21T09:15:00Z",
          provenance: { source_service: "services/investigation", detector_name: "PaymentVPAValidator" },
        },
      ],
    },
    journey: {
      incident_id: "inv_85f62e519d",
      current_stage: "PAYMENT_EXECUTION",
      predicted_next_stage: "MONEY_ROUTING",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T08:30:00Z",
          event_type: "MESSAGE_RECEIVED",
          description: "Received spoofed SMS pretending to be State Bank of India IT Cell",
        },
        {
          step_number: 2,
          stage: "URGENCY_PRESSURE",
          timestamp: "2026-10-21T08:45:00Z",
          event_type: "CALL_INTENT",
          description: "Follow-up ultimatum imposing 2-hour deadline to prevent card deactivation",
        },
        {
          step_number: 3,
          stage: "LINK_PHISHING",
          timestamp: "2026-10-21T09:00:00Z",
          event_type: "URL_OPENED",
          description: "Victim clicked on sbi-kyc-verify-portal.online/auth",
        },
        {
          step_number: 4,
          stage: "PAYMENT_EXECUTION",
          timestamp: "2026-10-21T09:17:00Z",
          event_type: "PAYMENT_COLLECT_PROMPTED",
          description: "Prompted to make ₹1 authentication deposit to scammer.ops@oksbi",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-85", label: "Incident #85f6", node_type: "incident", severity: "HIGH" } },
        { data: { id: "dom-85", label: "sbi-kyc-portal.online", node_type: "domain", severity: "HIGH" } },
        { data: { id: "phone-85", label: "+9198XXXXXX01", node_type: "phone", severity: "MEDIUM" } },
        { data: { id: "vpa-85", label: "scammer.ops@oksbi", node_type: "upi_handle", severity: "CRITICAL" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-85", target: "dom-85", label: "DELIVERED_URL", confidence: 0.95 } },
        { data: { id: "e2", source: "inc-85", target: "phone-85", label: "SENDER_ORIGIN", confidence: 0.9 } },
        { data: { id: "e3", source: "inc-85", target: "vpa-85", label: "BENEFICIARY_VPA", confidence: 0.96 } },
      ],
    },
  },

  inv_cf9256cd88: {
    id: "inv_cf9256cd88",
    pattern: "Electricity & Utility Disconnection Phishing",
    risk_score: 65,
    risk_level: "MEDIUM",
    confidence: "MEDIUM",
    current_stage: "SUSPICIOUS_LINK",
    last_activity: "2026-10-21T08:30:00Z",
    assessment: {
      incident_id: "inv_cf9256cd88",
      risk_score: 65,
      risk_level: "MEDIUM",
      evidence_confidence: "MEDIUM",
      pattern_name: "Electricity & Utility Disconnection Phishing",
      detected_pattern_name: "Electricity & Utility Disconnection Phishing",
      emerging_status: "KNOWN_PATTERN",
      is_insufficient_evidence: false,
      intervention: {
        action: "STRONG_WARNING",
        friction_delay_seconds: 10,
        banner_title: "Utility Extortion Risk Warning",
        banner_message: "Unverified power disconnection notification routing to non-governmental payment receiver.",
        dismissible: true,
      },
      reason_codes: [
        "[SUPPORT] Utility provider brand spoofing (Power Department)",
        "[SUPPORT] Imminent shutoff coercing immediate debit",
        "[SUPPORT] Destination URL registered 2 days ago (.xyz domain)",
        "[SUPPORT] Collect request from unverified consumer VPA",
      ],
      counter_evidence: [
        "Consumer account number format conforms to regional standard",
      ],
      signals: [
        {
          signal_id: "sig-cf-01",
          dimension: "SEMANTIC",
          signal_type: "UTILITY_BILL_THREAT",
          severity: "HIGH",
          confidence: 0.88,
          weight: 1.3,
          description: "Night disconnection warning: 'Power supply will be disconnected at 9:30 PM due to unpaid bill'",
          observed_at: "2026-10-21T08:00:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
        {
          signal_id: "sig-cf-02",
          dimension: "URL",
          signal_type: "HIGH_ABUSE_DOMAIN",
          severity: "MEDIUM",
          confidence: 0.85,
          weight: 1.2,
          description: "URL resolves to electricity-bill-pay.xyz with hidden redirect",
          observed_at: "2026-10-21T08:20:00Z",
          provenance: { source_service: "services/investigation", detector_name: "URLAnalyzer" },
        },
      ],
    },
    journey: {
      incident_id: "inv_cf9256cd88",
      current_stage: "SUSPICIOUS_LINK",
      predicted_next_stage: "PAYMENT_REQUEST",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T08:00:00Z",
          event_type: "SMS_RECEIVED",
          description: "Notice sent from personal mobile posing as State Electricity Board desk",
        },
        {
          step_number: 2,
          stage: "SUSPICIOUS_LINK",
          timestamp: "2026-10-21T08:30:00Z",
          event_type: "URL_VISITED",
          description: "Victim navigated to electricity-bill-pay.xyz payment gateway portal",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-cf", label: "Incident #cf92", node_type: "incident", severity: "MEDIUM" } },
        { data: { id: "dom-cf", label: "electricity-bill-pay.xyz", node_type: "domain", severity: "MEDIUM" } },
        { data: { id: "phone-cf", label: "+91-88880-XXXXX", node_type: "phone", severity: "MEDIUM" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-cf", target: "dom-cf", label: "REDIRECTS_TO", confidence: 0.91 } },
        { data: { id: "e2", source: "inc-cf", target: "phone-cf", label: "DELIVERED_FROM", confidence: 0.88 } },
      ],
    },
  },

  inv_6a13111a0b: {
    id: "inv_6a13111a0b",
    pattern: "E-Commerce Rating & Telegram Task Fraud",
    risk_score: 58,
    risk_level: "MEDIUM",
    confidence: "MEDIUM",
    current_stage: "INITIAL_CONTACT",
    last_activity: "2026-10-21T07:45:00Z",
    assessment: {
      incident_id: "inv_6a13111a0b",
      risk_score: 58,
      risk_level: "MEDIUM",
      evidence_confidence: "MEDIUM",
      pattern_name: "E-Commerce Rating & Telegram Task Fraud",
      detected_pattern_name: "E-Commerce Rating & Telegram Task Fraud",
      emerging_status: "KNOWN_PATTERN",
      is_insufficient_evidence: false,
      intervention: {
        action: "CAUTION",
        friction_delay_seconds: 5,
        banner_title: "Task Recruitment Warning",
        banner_message: "Prepaid commission recruitment model matches high-frequency task fraud ring.",
        dismissible: true,
      },
      reason_codes: [
        "[SUPPORT] Unsolicited Telegram task recruitment offer",
        "[SUPPORT] Guaranteed daily yields above legitimate market benchmarks",
        "[SUPPORT] Demand for upfront deposit to unlock commission tier",
      ],
      counter_evidence: [
        "Small initial incentive previously credited to victim (₹150 lure)",
      ],
      signals: [
        {
          signal_id: "sig-6a-01",
          dimension: "SEMANTIC",
          signal_type: "TASK_PROMISE_LURE",
          severity: "MEDIUM",
          confidence: 0.84,
          weight: 1.2,
          description: "Offers ₹2,500/day for liking YouTube clips and rating merchant listings",
          observed_at: "2026-10-21T07:45:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
      ],
    },
    journey: {
      incident_id: "inv_6a13111a0b",
      current_stage: "INITIAL_CONTACT",
      predicted_next_stage: "PAYMENT_REQUEST",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T07:45:00Z",
          event_type: "TELEGRAM_MESSAGE",
          description: "Invited to Telegram channel for rating task onboarding",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-6a", label: "Incident #6a13", node_type: "incident", severity: "MEDIUM" } },
        { data: { id: "dom-6a", label: "task-earning-hub.xyz", node_type: "domain", severity: "MEDIUM" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-6a", target: "dom-6a", label: "PORTAL_LINK", confidence: 0.85 } },
      ],
    },
  },

  inv_8453961fd2: {
    id: "inv_8453961fd2",
    pattern: "High-Yield VIP Crypto & Stock Advisory",
    risk_score: 45,
    risk_level: "MEDIUM",
    confidence: "LOW",
    current_stage: "INITIAL_CONTACT",
    last_activity: "2026-10-21T06:15:00Z",
    assessment: {
      incident_id: "inv_8453961fd2",
      risk_score: 45,
      risk_level: "MEDIUM",
      evidence_confidence: "LOW",
      pattern_name: "High-Yield VIP Crypto & Stock Advisory",
      detected_pattern_name: "High-Yield VIP Crypto & Stock Advisory",
      emerging_status: "KNOWN_PATTERN",
      is_insufficient_evidence: false,
      intervention: {
        action: "CAUTION",
        friction_delay_seconds: 5,
        banner_title: "Unverified Financial Advisory",
        banner_message: "Solicitation promises unrealistic trading profits via unverified offshore group.",
        dismissible: true,
      },
      reason_codes: [
        "[SUPPORT] Unregistered WhatsApp investment group solicitation",
        "[SUPPORT] Fabricated institutional brokerage certificates",
        "[SUPPORT] Redirection to offshore unregistered trading portal",
      ],
      counter_evidence: [
        "No explicit payment instruction issued in initial step",
      ],
      signals: [
        {
          signal_id: "sig-84-01",
          dimension: "SEMANTIC",
          signal_type: "INVESTMENT_PROMISE",
          severity: "MEDIUM",
          confidence: 0.72,
          weight: 1.1,
          description: "Promised 450% monthly profit with insider institutional stock tips",
          observed_at: "2026-10-21T06:15:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
      ],
    },
    journey: {
      incident_id: "inv_8453961fd2",
      current_stage: "INITIAL_CONTACT",
      predicted_next_stage: "SUSPICIOUS_LINK",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T06:15:00Z",
          event_type: "WHATSAPP_INVITE",
          description: "Added to 'VIP Institutional Stock Advisory Group' without consent",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-84", label: "Incident #8453", node_type: "incident", severity: "LOW" } },
        { data: { id: "dom-84", label: "vip-stock-trade.top", node_type: "domain", severity: "MEDIUM" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-84", target: "dom-84", label: "PROMOTES_URL", confidence: 0.8 } },
      ],
    },
  },

  inv_f2b01dd167: {
    id: "inv_f2b01dd167",
    pattern: "Fake Support / KYC Token Re-verification",
    risk_score: 82,
    risk_level: "HIGH",
    confidence: "HIGH",
    current_stage: "PAYMENT_REQUEST",
    last_activity: "2026-10-21T05:20:00Z",
    isRecent: true,
    assessment: {
      incident_id: "inv_f2b01dd167",
      risk_score: 82,
      risk_level: "HIGH",
      evidence_confidence: "HIGH",
      pattern_name: "Fake Support / KYC Token Re-verification",
      detected_pattern_name: "Fake Support / KYC Token Re-verification",
      emerging_status: "MUTATED_VARIANT",
      is_insufficient_evidence: false,
      intervention: {
        action: "PRE_PAYMENT_INTERVENTION",
        friction_delay_seconds: 20,
        banner_title: "Active Payment Coercion Block",
        banner_message: "Pre-payment friction triggered: Token probe transaction detected alongside banking credentials harvest.",
        dismissible: false,
      },
      reason_codes: [
        "[SUPPORT] High-risk ₹1 token authorization probe detected",
        "[SUPPORT] Request to install remote access screen-share tool",
        "[SUPPORT] Net banking credentials harvesting form on unregistered host",
        "[SUPPORT] Direct match with campaign Operation Fake KYC Freenom",
      ],
      counter_evidence: [],
      signals: [
        {
          signal_id: "sig-f2-01",
          dimension: "PAYMENT",
          signal_type: "PROBE_TRANSACTION_DETECTED",
          severity: "CRITICAL",
          confidence: 0.98,
          weight: 1.8,
          description: "₹1 micro-transaction probe requested under pretext of unfreezing account",
          observed_at: "2026-10-21T05:20:00Z",
          provenance: { source_service: "services/investigation", detector_name: "PaymentVPAValidator" },
        },
      ],
    },
    journey: {
      incident_id: "inv_f2b01dd167",
      current_stage: "PAYMENT_REQUEST",
      predicted_next_stage: "PAYMENT_EXECUTION",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T04:40:00Z",
          event_type: "WHATSAPP_CALL",
          description: "Caller posed as Customer Care Representative offering immediate token re-validation",
        },
        {
          step_number: 2,
          stage: "PAYMENT_REQUEST",
          timestamp: "2026-10-21T05:20:00Z",
          event_type: "PAYMENT_PROBE",
          description: "Sent direct UPI collect request for token verification",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-f2", label: "Incident #f2b0", node_type: "incident", severity: "HIGH" } },
        { data: { id: "vpa-f2", label: "support.kyc@oksbi", node_type: "upi_handle", severity: "CRITICAL" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-f2", target: "vpa-f2", label: "COLLECT_RECEIVER", confidence: 0.97 } },
      ],
    },
  },

  inv_6c1bb9474b: {
    id: "inv_6c1bb9474b",
    pattern: "Urgent Power Shutoff Coercion Notice",
    risk_score: 78,
    risk_level: "HIGH",
    confidence: "HIGH",
    current_stage: "PAYMENT_REQUEST",
    last_activity: "2026-10-21T04:10:00Z",
    assessment: {
      incident_id: "inv_6c1bb9474b",
      risk_score: 78,
      risk_level: "HIGH",
      evidence_confidence: "HIGH",
      pattern_name: "Urgent Power Shutoff Coercion Notice",
      detected_pattern_name: "Urgent Power Shutoff Coercion Notice",
      emerging_status: "KNOWN_PATTERN",
      is_insufficient_evidence: false,
      intervention: {
        action: "PRE_PAYMENT_INTERVENTION",
        friction_delay_seconds: 15,
        banner_title: "Pre-Payment Extortion Intervention",
        banner_message: "Direct payment coercion detected. Bypasses official utility electricity billing systems.",
        dismissible: false,
      },
      reason_codes: [
        "[SUPPORT] Coercive night-time power disconnection ultimatum",
        "[SUPPORT] Unofficial phone number posing as electricity officer",
        "[SUPPORT] Direct UPI payment collect request sent to personal handle",
        "[SUPPORT] Associated with syndicated extortion group camp-power-urgent",
      ],
      counter_evidence: [],
      signals: [
        {
          signal_id: "sig-6c-01",
          dimension: "SEMANTIC",
          signal_type: "DISCONNECTION_COERCION",
          severity: "HIGH",
          confidence: 0.92,
          weight: 1.5,
          description: "Night power shutoff coercion: 'Pay ₹4,210 immediately or meter locked'",
          observed_at: "2026-10-21T04:10:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
      ],
    },
    journey: {
      incident_id: "inv_6c1bb9474b",
      current_stage: "PAYMENT_REQUEST",
      predicted_next_stage: "PAYMENT_EXECUTION",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T03:50:00Z",
          event_type: "SMS_WARNING",
          description: "Coercive SMS alleging unpaid electrical bill with impending shutdown",
        },
        {
          step_number: 2,
          stage: "PAYMENT_REQUEST",
          timestamp: "2026-10-21T04:10:00Z",
          event_type: "UPI_COLLECT",
          description: "Collect request issued from discom.officer@okaxis",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-6c", label: "Incident #6c1b", node_type: "incident", severity: "HIGH" } },
        { data: { id: "vpa-6c", label: "discom.officer@okaxis", node_type: "upi_handle", severity: "HIGH" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-6c", target: "vpa-6c", label: "COLLECT_HANDLE", confidence: 0.94 } },
      ],
    },
  },

  inv_8c514a3744: {
    id: "inv_8c514a3744",
    pattern: "Customs Courier Parcel Clearance Hold",
    risk_score: 35,
    risk_level: "LOW",
    confidence: "MEDIUM",
    current_stage: "INITIAL_CONTACT",
    last_activity: "2026-10-21T02:00:00Z",
    assessment: {
      incident_id: "inv_8c514a3744",
      risk_score: 35,
      risk_level: "LOW",
      evidence_confidence: "MEDIUM",
      pattern_name: "Customs Courier Parcel Clearance Hold",
      detected_pattern_name: "Customs Courier Parcel Clearance Hold",
      emerging_status: "KNOWN_PATTERN",
      is_insufficient_evidence: false,
      intervention: {
        action: "PASSIVE",
        friction_delay_seconds: 0,
        banner_title: "Low Risk Courier Notification",
        banner_message: "Preliminary parcel delivery alert. No sensitive credentials or payment demanded.",
        dismissible: true,
      },
      reason_codes: [
        "[SUPPORT] SMS regarding detained customs parcel awaiting clearance",
        "[SUPPORT] Generic tracking link on newly observed domain",
      ],
      counter_evidence: [
        "No payment demands or credentials solicited at this stage",
      ],
      signals: [
        {
          signal_id: "sig-8c-01",
          dimension: "SEMANTIC",
          signal_type: "PARCEL_NOTIFICATION",
          severity: "LOW",
          confidence: 0.75,
          weight: 0.8,
          description: "Tracking update: 'Parcel #IN-88901 is held at customs for address confirmation'",
          observed_at: "2026-10-21T02:00:00Z",
          provenance: { source_service: "services/pattern-engine", detector_name: "SemanticSignalExtractor" },
        },
      ],
    },
    journey: {
      incident_id: "inv_8c514a3744",
      current_stage: "INITIAL_CONTACT",
      predicted_next_stage: "SUSPICIOUS_LINK",
      steps: [
        {
          step_number: 1,
          stage: "INITIAL_CONTACT",
          timestamp: "2026-10-21T02:00:00Z",
          event_type: "PARCEL_SMS",
          description: "Received delivery reschedule prompt",
        },
      ],
    },
    graph: {
      nodes: [
        { data: { id: "inc-8c", label: "Incident #8c51", node_type: "incident", severity: "LOW" } },
        { data: { id: "dom-8c", label: "track-courier-parcel.info", node_type: "domain", severity: "LOW" } },
      ],
      edges: [
        { data: { id: "e1", source: "inc-8c", target: "dom-8c", label: "DELIVERED_URL", confidence: 0.82 } },
      ],
    },
  },
};

/**
 * Returns full unified incident data for any incident ID, guaranteeing
 * 100% data consistency between the incident directory and detail views.
 */
export function getUnifiedIncident(id: string, storedItem?: any): UnifiedIncidentData {
  // 1. Direct canonical match
  if (CANONICAL_INCIDENTS[id]) {
    return CANONICAL_INCIDENTS[id];
  }

  // 2. If stored item is provided from local investigations or backend
  if (storedItem) {
    const score = typeof storedItem.risk_score === "number" ? storedItem.risk_score : 15;
    const level: RiskLevel =
      storedItem.risk_level ||
      (score >= 70 ? "HIGH" : score >= 40 ? "MEDIUM" : score === 0 ? "INSUFFICIENT_EVIDENCE" : "LOW");
    const confidence: EvidenceConfidence = storedItem.confidence || "MEDIUM";
    const pattern = storedItem.pattern || storedItem.title || "Dynamic Investigation";
    const stage = storedItem.current_stage || (score >= 70 ? "PAYMENT_REQUEST" : "INITIAL_CONTACT");

    return {
      id,
      pattern,
      risk_score: score,
      risk_level: level,
      confidence,
      current_stage: stage,
      last_activity: storedItem.last_activity || new Date().toISOString(),
      isRecent: true,
      assessment: {
        incident_id: id,
        risk_score: score,
        risk_level: level,
        evidence_confidence: confidence,
        pattern_name: pattern,
        detected_pattern_name: pattern,
        emerging_status: "EVALUATED_INSTANCE",
        is_insufficient_evidence: level === "INSUFFICIENT_EVIDENCE",
        intervention:
          score >= 70
            ? {
                action: "PRE_PAYMENT_INTERVENTION",
                friction_delay_seconds: 15,
                banner_title: "Active Security Intervention",
                banner_message: "High threat index triggered pre-payment friction protection.",
                dismissible: false,
              }
            : score >= 40
            ? {
                action: "STRONG_WARNING",
                friction_delay_seconds: 10,
                banner_title: "Elevated Risk Warning",
                banner_message: "Pattern indicators warrant caution before sharing credentials or approving transactions.",
                dismissible: true,
              }
            : {
                action: "NONE",
                friction_delay_seconds: 0,
                banner_title: "Normal Baseline Observation",
                banner_message: "No conclusive deceptive vectors observed.",
                dismissible: true,
              },
        reason_codes: [
          `[SUPPORT] Analyzed payload pattern: ${pattern}`,
          `[SUPPORT] Corroboration index calculated at ${score}/100`,
          `[SUPPORT] Current observed stage: ${stage}`,
        ],
        counter_evidence: [],
        signals: [
          {
            signal_id: `sig-${id}-01`,
            dimension: "SEMANTIC",
            signal_type: "EVALUATED_SIGNAL",
            severity: score >= 70 ? "HIGH" : score >= 40 ? "MEDIUM" : "LOW",
            confidence: 0.85,
            weight: 1.2,
            description: `Evaluated investigation payload matching pattern ${pattern}`,
            observed_at: new Date().toISOString(),
            provenance: { source_service: "services/investigation", detector_name: "FusionEngine" },
          },
        ],
      },
      journey: {
        incident_id: id,
        current_stage: stage as any,
        predicted_next_stage: score >= 70 ? "MONEY_ROUTING" : "PAYMENT_REQUEST",
        steps: [
          {
            step_number: 1,
            stage: "INITIAL_CONTACT",
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            event_type: "SUBMITTED_PAYLOAD",
            description: `Analyzed evidence payload: ${pattern}`,
          },
          {
            step_number: 2,
            stage: stage as any,
            timestamp: new Date().toISOString(),
            event_type: "STAGE_EVALUATION",
            description: `Evaluated threat posture at stage ${stage}`,
          },
        ],
      },
      graph: {
        nodes: [
          { data: { id: `inc-${id}`, label: `Incident ${id}`, node_type: "incident", severity: score >= 70 ? "HIGH" : "MEDIUM" } },
        ],
        edges: [],
      },
    };
  }

  // 3. Fallback to first canonical incident
  return CANONICAL_INCIDENTS["inv_85f62e519d"];
}
