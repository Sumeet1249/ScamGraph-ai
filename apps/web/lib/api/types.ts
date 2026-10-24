export type RiskLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL"
  | "INSUFFICIENT_EVIDENCE"
  | string;

export type EvidenceConfidence = "LOW" | "MEDIUM" | "HIGH" | string;

export interface EvidenceSignal {
  signal_id: string;
  signal_type: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  confidence: number;
  description: string;
  source?: string;
  timestamp?: string;
  is_counter_evidence?: boolean;
  provenance?: {
    source_service?: string;
    [key: string]: any;
  };
  metadata?: Record<string, any>;
  [key: string]: any;
}

export interface FingerprintSimilarityResult {
  score?: number;
  confidence?: number;
  matched_features?: string[];
  cluster_id?: string;
  similarity?: number;
  explanation?: string;
  semantic_similarity: number;
  journey_similarity: number;
  pattern_similarity: number;
  infrastructure_similarity: number;
  payment_similarity: number;
  identifier_overlap: number;
  [key: string]: any;
}

export interface CytoscapeNodeData {
  id: string;
  label: string;
  node_type?: string;
  type?: string;
  severity?: string;
  risk_score?: number;
  nature?: string;
  stage?: string;
  [key: string]: any;
}

export interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  label?: string;
  relationship?: string;
  relation_type?: string;
  nature?: string;
  [key: string]: any;
}

export interface CytoscapeGraph {
  nodes: { data: CytoscapeNodeData }[];
  edges: { data: CytoscapeEdgeData }[];
}

export type GraphNodeType =
  | "MESSAGE"
  | "URL"
  | "PAYMENT_INTENT"
  | "VOICE_CALL"
  | "OTP_EVENT"
  | "MULE_ACCOUNT"
  | "IP"
  | "DOMAIN"
  | string;

export type JourneyStage =
  | "INITIAL_CONTACT"
  | "IMPERSONATION"
  | "URGENCY_INDUCEMENT"
  | "MALICIOUS_LINK"
  | "CREDENTIAL_HARVEST"
  | "REMOTE_ACCESS"
  | "PAYMENT_INTENT"
  | "SETTLEMENT"
  | string;

export interface JourneyStep {
  step_id: string;
  stage: JourneyStage;
  label?: string;
  timestamp?: string;
  description?: string;
  severity?: string;
  offset_seconds?: number;
  time_delta_seconds?: number;
  evidence_signals?: EvidenceSignal[];
  associated_signals?: EvidenceSignal[];
  [key: string]: any;
}

export interface JourneyPrediction {
  predicted_next_stage: JourneyStage;
  rationale: string;
  recommended_preventive_action: string;
}

export interface ScamJourney {
  journey_id: string;
  incident_id?: string;
  current_stage: JourneyStage;
  steps: JourneyStep[];
  prediction?: JourneyPrediction;
}

export type InterventionAction =
  | "NONE"
  | "PASSIVE"
  | "CAUTION"
  | "STRONG_WARNING"
  | "PRE_PAYMENT_INTERVENTION"
  | "MONITOR"
  | "WARN_BANNER"
  | "DELAY_SETTLEMENT"
  | "STEP_UP_AUTH"
  | "BLOCK_INTENT"
  | "FREEZE_ACCOUNT"
  | string;

export interface AdaptiveIntervention {
  action: InterventionAction;
  friction_delay_seconds: number;
  friction_level?: "NONE" | "LOW" | "MEDIUM" | "HIGH" | "BLOCK" | string;
  banner_title?: string;
  banner_message?: string;
  reason_codes?: string[];
  [key: string]: any;
}
