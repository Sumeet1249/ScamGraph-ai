"""Declarative Scam Pattern Definitions & Pattern Matcher (Step 17 & 18).

Defines structured taxonomies for the 5 canonical Indian digital finance scam patterns:
- KYC_IMPERSONATION
- ELECTRICITY_DISCONNECTION_FRAUD
- PART_TIME_JOB_FRAUD
- COURIER_PARCEL_HOLD
- QR_COLLECT_INVERSION
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas import EvidenceSignal, JourneyStage


class ScamPatternDefinition(BaseModel):
    id: str
    name: str
    required_signals: List[str]
    supporting_signals: List[str]
    expected_sequence: List[str]
    preferred_intervention_before: List[JourneyStage]
    description: str


# Declarative catalog of known patterns
SCAM_PATTERNS: Dict[str, ScamPatternDefinition] = {
    "KYC_IMPERSONATION": ScamPatternDefinition(
        id="KYC_IMPERSONATION",
        name="Bank / KYC Suspension Impersonation",
        required_signals=["OFFICIAL_ENTITY_IMPERSONATION"],
        supporting_signals=[
            "URGENCY_PRESSURE_DETECTED",
            "BRAND_TYPOSQUATTING_DETECTED",
            "CREDENTIAL_HARVEST_FORM_OBSERVED",
            "OTP_INPUT_FORM_OBSERVED",
            "INDIVIDUAL_VPA_PAYMENT_TARGETED",
        ],
        expected_sequence=[
            "INITIAL_CONTACT",
            "IMPERSONATION",
            "SUSPICIOUS_LINK",
            "CREDENTIAL_OTP_HARVEST",
            "PAYMENT_REQUEST",
        ],
        preferred_intervention_before=[JourneyStage.PAYMENT_INTENT],
        description="Scammer impersonates a bank or official KYC department threatening account freeze.",
    ),
    "ELECTRICITY_DISCONNECTION_FRAUD": ScamPatternDefinition(
        id="ELECTRICITY_DISCONNECTION_FRAUD",
        name="Electricity Bill Disconnection Threat",
        required_signals=["OFFICIAL_ENTITY_IMPERSONATION", "URGENCY_PRESSURE_DETECTED"],
        supporting_signals=[
            "SUSPICIOUS_TLD_USED",
            "BRAND_TYPOSQUATTING_DETECTED",
            "INDIVIDUAL_VPA_PAYMENT_TARGETED",
            "SHARED_PAYMENT_ENTITY_ACROSS_INCIDENTS",
        ],
        expected_sequence=[
            "INITIAL_CONTACT",
            "IMPERSONATION",
            "URGENCY_PRESSURE",
            "SUSPICIOUS_LINK",
            "PAYMENT_REQUEST",
        ],
        preferred_intervention_before=[JourneyStage.PAYMENT_INTENT],
        description="Disconnection notice claiming light/power will be cut tonight unless immediate fee is paid.",
    ),
    "PART_TIME_JOB_FRAUD": ScamPatternDefinition(
        id="PART_TIME_JOB_FRAUD",
        name="Work-From-Home Task / Deposit Fraud",
        required_signals=["UNSOLICITED_TASK_JOB_LURE"],
        supporting_signals=[
            "MULTI_HOP_REDIRECT_CHAIN",
            "INDIVIDUAL_VPA_PAYMENT_TARGETED",
            "PAGE_LEVEL_PAYMENT_PROMPT",
        ],
        expected_sequence=[
            "INITIAL_CONTACT",
            "SUSPICIOUS_LINK",
            "PAYMENT_REQUEST",
        ],
        preferred_intervention_before=[JourneyStage.PAYMENT_REQUEST],
        description="Lure offering daily earnings for simple tasks, escalating into crypto/UPI deposit requests.",
    ),
    "COURIER_PARCEL_HOLD": ScamPatternDefinition(
        id="COURIER_PARCEL_HOLD",
        name="Courier Delivery Hold / Redirection Fee",
        required_signals=["OFFICIAL_ENTITY_IMPERSONATION"],
        supporting_signals=[
            "SUSPICIOUS_TLD_USED",
            "PAGE_LEVEL_PAYMENT_PROMPT",
            "INDIVIDUAL_VPA_PAYMENT_TARGETED",
        ],
        expected_sequence=[
            "INITIAL_CONTACT",
            "SUSPICIOUS_LINK",
            "PAYMENT_REQUEST",
        ],
        preferred_intervention_before=[JourneyStage.PAYMENT_INTENT],
        description="Claims undelivered package from India Post/courier demanding nominal redelivery charge.",
    ),
    "QR_COLLECT_INVERSION": ScamPatternDefinition(
        id="QR_COLLECT_INVERSION",
        name="QR Code / UPI Collect Request Inversion",
        required_signals=["INDIVIDUAL_VPA_PAYMENT_TARGETED"],
        supporting_signals=[
            "SHARED_PAYMENT_ENTITY_ACROSS_INCIDENTS",
            "URGENCY_PRESSURE_DETECTED",
        ],
        expected_sequence=[
            "INITIAL_CONTACT",
            "PAYMENT_REQUEST",
            "PAYMENT_INTENT",
        ],
        preferred_intervention_before=[JourneyStage.PAYMENT_INTENT],
        description="Victim is tricked into believing approving a collect request or scanning QR receives money.",
    ),
}


class PatternMatch(BaseModel):
    pattern_id: str
    pattern_name: str
    match_score: float = Field(..., ge=0.0, le=1.0)
    matched_required: List[str]
    matched_supporting: List[str]
    missing_required: List[str]
    is_strong_match: bool


class PatternMatcher:
    """Matches observed evidence signals against declarative scam patterns."""

    @staticmethod
    def match(signals: List[EvidenceSignal]) -> Optional[PatternMatch]:
        signal_types = {s.signal_type for s in signals if not s.is_counter_evidence}
        best_match = None
        best_score = 0.0

        for pattern_id, p_def in SCAM_PATTERNS.items():
            matched_req = [r for r in p_def.required_signals if r in signal_types]
            missing_req = [r for r in p_def.required_signals if r not in signal_types]
            matched_sup = [s for s in p_def.supporting_signals if s in signal_types]

            # If all required signals are absent, score is 0
            if not matched_req:
                continue

            req_ratio = len(matched_req) / len(p_def.required_signals)
            sup_ratio = len(matched_sup) / max(1, len(p_def.supporting_signals))
            combined_score = round(0.6 * req_ratio + 0.4 * sup_ratio, 2)

            if combined_score > best_score:
                best_score = combined_score
                best_match = PatternMatch(
                    pattern_id=pattern_id,
                    pattern_name=p_def.name,
                    match_score=combined_score,
                    matched_required=matched_req,
                    matched_supporting=matched_sup,
                    missing_required=missing_req,
                    is_strong_match=(len(missing_req) == 0 and combined_score >= 0.60),
                )

        return best_match
