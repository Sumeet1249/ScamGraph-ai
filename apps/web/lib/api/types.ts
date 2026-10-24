export type EvidenceConfidence = "LOW" | "MEDIUM" | "HIGH" | "VERY_HIGH";

export type InterventionAction = "BLOCK_IMMEDIATE" | "HOLD_30M" | "DELIBERATE" | "ALLOW_WITH_LOG";

export interface AdaptiveIntervention {
  action: InterventionAction;
  title: string;
  description: string;
  reasons: string[];
  urgencyScore?: number;
  statutoryReference?: string;
}

export type JourneyStage =
  | "INITIAL_CONTACT"
  | "IMPERSONATION"
  | "PRESSURE_COERCION"
  | "FAKE_INTENT"
  | "MULE_EXFILTRATION";

export interface JourneyStep {
  id: string;
  stage: JourneyStage | string;
  name?: string;
  label?: string;
  timestamp?: string;
  offsetMinutes?: number;
  channel?: string;
  sourceConfidence?: string;
  certainty?: "observed" | "reported" | "inferred" | "projected";
  severity?: string;
  description?: string;
  signals?: string[];
  isCurrent?: boolean;
}

export interface ScamJourney {
  id: string;
  caseId?: string;
  currentStage: JourneyStage | string;
  velocityPerHour?: number;
  steps: JourneyStep[];
  paymentBoundaryPassed?: boolean;
}
