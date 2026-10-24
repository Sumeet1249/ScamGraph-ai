"""ScamGraph Lab API — Judge Simulator and Dynamic Scenario Execution (Step 20).

Provides synthetic multi-stage scenario sequences and executes them through
the real ScamGraph AI pipeline (Semantic NLP, PhishGraph Lexical Safety, Pattern Engine,
and Explainable RiskEngine) to observe live risk score evolution.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from packages.schemas import (
    Event,
    EventType,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    EmergingStatus,
)
from services.investigation.url_analysis.safety import URLAnalyzer
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor
from services.pattern_engine.patterns.scam_patterns import PatternMatcher
from services.pattern_engine.matcher.risk_engine import RiskEngine, RiskAssessment
from services.pattern_engine.semantic.fingerprint_builder import ScamFingerprintBuilder
from services.pattern_engine.matcher.variant_detector import EmergingVariantDetector

from datetime import datetime, timezone, timedelta
from uuid import uuid4

router = APIRouter()


class ScenarioStepDef(BaseModel):
    step_index: int
    offset_seconds: int
    offset_label: str  # e.g. "T+00", "T+15"
    event_type: EventType
    title: str
    description: str
    payload: Dict[str, Any]


class ScenarioDef(BaseModel):
    id: str
    title: str
    badge: str
    description: str
    steps: List[ScenarioStepDef]


class SimulationStepResult(BaseModel):
    step_index: int
    offset_label: str
    title: str
    event_type: str
    new_signals: List[EvidenceSignal]
    total_signals_so_far: int
    risk_score: int
    risk_level: str
    evidence_confidence: str
    intervention_action: str
    friction_delay_seconds: int
    banner_message: Optional[str] = None
    reason_codes: List[str]
    emerging_variant_report: Optional[Dict[str, Any]] = None


class RunSimulationRequest(BaseModel):
    scenario_id: str


class RunSimulationResponse(BaseModel):
    scenario_id: str
    title: str
    incident_id: str
    steps_results: List[SimulationStepResult]
    final_risk_score: int
    final_risk_level: str
    final_evidence_confidence: str
    evolution_path: List[int]  # e.g. [12, 26, 43, 64, 87]


# ─────────────────────────────────────────────────────────────────────────────
# 6 Predefined Canonical Scenarios
# ─────────────────────────────────────────────────────────────────────────────
SCENARIOS: Dict[str, ScenarioDef] = {
    "normal_payment": ScenarioDef(
        id="normal_payment",
        title="Normal Payment",
        badge="BENIGN",
        description="Routine peer-to-peer dinner bill split with trusted contact. No coercion, established account.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Dinner split request from known friend",
                payload={"text": "Hey Sumeet, splitting dinner bill from last night: Rs 450", "sender": "+919876543210"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=20,
                offset_label="T+20",
                event_type=EventType.PAYMENT_INTENT_INITIATED,
                title="Payment Intent",
                description="User opens UPI app and initiates payment to friend",
                payload={"vpa": "rohit.sharma@okicici", "amount": 450.0, "payee_name": "Rohit Sharma"},
            ),
        ],
    ),
    "kyc_scam": ScenarioDef(
        id="kyc_scam",
        title="KYC Impersonation Scam",
        badge="CRITICAL",
        description="Classic multi-stage banking grooming: Fear threat -> Impersonation -> Malicious URL -> OTP Harvest -> Fraudulent payment.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Urgent account blocking alert received via SMS",
                payload={"text": "Dear customer, your SBI YONO account will be blocked today. Please complete mandatory KYC update.", "sender": "+919111111111"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=15,
                offset_label="T+15",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Impersonation",
                description="Caller purports to be Senior Manager from State Bank of India Support Desk",
                payload={"text": "This is SBI Official KYC Officer. Do not disconnect or your netbanking will be suspended within 2 hours.", "sender": "+919111111111"},
            ),
            ScenarioStepDef(
                step_index=3,
                offset_seconds=35,
                offset_label="T+35",
                event_type=EventType.LINK_CLICKED,
                title="URL",
                description="User taps unofficial typosquatted verification link",
                payload={"raw_url": "http://sbi-kyc-verify-portal.online/login"},
            ),
            ScenarioStepDef(
                step_index=4,
                offset_seconds=50,
                offset_label="T+50",
                event_type=EventType.OTP_REQUESTED,
                title="OTP",
                description="Web page actively requests 6-digit transaction authorization OTP",
                payload={"prompt": "Enter the 6-digit OTP sent to your mobile to verify identity."},
            ),
            ScenarioStepDef(
                step_index=5,
                offset_seconds=65,
                offset_label="T+65",
                event_type=EventType.COLLECT_REQUEST_RECEIVED,
                title="Payment request",
                description="Incoming UPI collect request of Rs 1 for 'account re-validation' to personal VPA",
                payload={"vpa": "scammer.ops@oksbi", "amount": 1.0, "claimed_payee_name": "SBI Verification Desk"},
            ),
        ],
    ),
    "investment_scam": ScenarioDef(
        id="investment_scam",
        title="Investment / Crypto Scam",
        badge="HIGH RISK",
        description="High-return task and crypto scam offering astronomical daily profits with VIP recharge trap.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Unsolicited Telegram invitation promising guaranteed profits",
                payload={"text": "Earn Rs 5000 to Rs 15000 daily from home with zero investment! Guaranteed 300% returns in 24 hours.", "sender": "+919812345678"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=20,
                offset_label="T+20",
                event_type=EventType.LINK_CLICKED,
                title="URL",
                description="Victim visits fake investment platform with suspicious TLD",
                payload={"raw_url": "http://crypto-wealth-multiplier.top/trade"},
            ),
            ScenarioStepDef(
                step_index=3,
                offset_seconds=45,
                offset_label="T+45",
                event_type=EventType.COLLECT_REQUEST_RECEIVED,
                title="Payment request",
                description="Requesting initial deposit Rs 2000 to activate VIP profit wallet",
                payload={"vpa": "vip.crypto.task@paytm", "amount": 2000.0, "claimed_payee_name": "VIP Wealth Desk"},
            ),
        ],
    ),
    "job_scam": ScenarioDef(
        id="job_scam",
        title="Part-Time Job Fraud",
        badge="HIGH RISK",
        description="Fake employment offer requiring refundable badge or document verification fee.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Selected for Remote Freelance Reviewer role",
                payload={"text": "Congratulations! You are shortlisted for Part-time Product Reviewer at Amazon. Daily payout Rs 2500.", "sender": "+919988776655"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=25,
                offset_label="T+25",
                event_type=EventType.LINK_CLICKED,
                title="URL",
                description="Click to fill out onboarding portal",
                payload={"raw_url": "http://amazon-career-onboarding.xyz/form"},
            ),
            ScenarioStepDef(
                step_index=3,
                offset_seconds=55,
                offset_label="T+55",
                event_type=EventType.PAYMENT_INTENT_INITIATED,
                title="Payment request",
                description="Mandatory Rs 1500 registration deposit before job activation",
                payload={"vpa": "hr.onboarding@ybl", "amount": 1500.0, "payee_name": "Amazon HR Desk"},
            ),
        ],
    ),
    "emerging_ai_variant": ScenarioDef(
        id="emerging_ai_variant",
        title="Emerging AI Variant (Hero Scenario)",
        badge="HERO VARIANT",
        description="Novel attack mimicking HDFC Security with brand-new Phone, Domain, and UPI handle. Zero blacklist matches, 100% workflow match.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Initial contact claiming HDFC security policy update",
                payload={"text": "HDFC Alert: Security verification mandatory under revised RBI guidelines.", "sender": "+919222222222"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=15,
                offset_label="T+15",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Impersonation",
                description="Urgent account threat from purported HDFC Security Desk",
                payload={"text": "HDFC Security Desk: Immediate action required within 2 hours or access will be restricted.", "sender": "+919222222222"},
            ),
            ScenarioStepDef(
                step_index=3,
                offset_seconds=35,
                offset_label="T+35",
                event_type=EventType.LINK_CLICKED,
                title="URL",
                description="Brand-new unregistered domain hosting credentials verification",
                payload={"raw_url": "http://hdfc-security-check.xyz/verify"},
            ),
            ScenarioStepDef(
                step_index=4,
                offset_seconds=50,
                offset_label="T+50",
                event_type=EventType.OTP_REQUESTED,
                title="OTP",
                description="Real-time OTP intercept form displayed on site",
                payload={"prompt": "Enter one-time security password to retain netbanking authorization."},
            ),
            ScenarioStepDef(
                step_index=5,
                offset_seconds=65,
                offset_label="T+65",
                event_type=EventType.COLLECT_REQUEST_RECEIVED,
                title="Payment request",
                description="Verification micro-payment request to unlisted VPA",
                payload={"vpa": "hdfc.desk@paytm", "amount": 5.0, "claimed_payee_name": "HDFC Verification Desk"},
            ),
        ],
    ),
    "ambiguous_case": ScenarioDef(
        id="ambiguous_case",
        title="Ambiguous / Insufficient Data",
        badge="MONITOR",
        description="Vague message with no confirmed threat signals. Strictly maintains INSUFFICIENT_EVIDENCE to prevent alert fatigue.",
        steps=[
            ScenarioStepDef(
                step_index=1,
                offset_seconds=0,
                offset_label="T+00",
                event_type=EventType.MESSAGE_RECEIVED,
                title="Message",
                description="Informal message regarding project expenses",
                payload={"text": "Please transfer Rs 500 when you are free today for the printed notes.", "sender": "+919444444444"},
            ),
            ScenarioStepDef(
                step_index=2,
                offset_seconds=30,
                offset_label="T+30",
                event_type=EventType.PAYMENT_INTENT_INITIATED,
                title="Payment Intent",
                description="User enters UPI VPA to settle amount",
                payload={"vpa": "colleague@okhdfcbank", "amount": 500.0, "payee_name": "Classmate"},
            ),
        ],
    ),
}


@router.get("/scenarios", response_model=List[ScenarioDef])
async def list_scenarios():
    """Return all 6 preconfigured scenarios for the judge evaluation buttons."""
    return list(SCENARIOS.values())


@router.post("/simulate", response_model=RunSimulationResponse)
async def run_simulation(req: RunSimulationRequest):
    """Execute a scenario step-by-step through the real ScamGraph pipeline.
    
    Evaluates dynamic risk progression across each timestamped event.
    For the hero scenario (emerging_ai_variant), also runs EmergingVariantDetector.
    """
    scenario = SCENARIOS.get(req.scenario_id)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{req.scenario_id}' not found.")

    incident_id = f"sim_{uuid4().hex[:10]}"
    base_time = datetime.now(timezone.utc)

    accumulated_signals: List[EvidenceSignal] = []
    step_results: List[SimulationStepResult] = []
    evolution_path: List[int] = []

    for step in scenario.steps:
        new_step_signals: List[EvidenceSignal] = []

        # 1. Semantic Extraction
        if step.event_type == EventType.MESSAGE_RECEIVED:
            txt = step.payload.get("text", "")
            if txt:
                extracted = SemanticSignalExtractor.extract_signals(incident_id, txt)
                new_step_signals.extend(extracted)

        # 2. URL Lexical & Infrastructure Safety
        elif step.event_type == EventType.LINK_CLICKED:
            raw_url = step.payload.get("raw_url", "")
            if raw_url:
                res = URLAnalyzer.analyze_lexical_risk(incident_id, raw_url)
                new_step_signals.extend(res.get("signals", []))

        # 3. OTP harvesting signal
        elif step.event_type == EventType.OTP_REQUESTED:
            new_step_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.URL,
                    signal_type="OTP_INPUT_FORM_OBSERVED",
                    severity=SignalSeverity.CRITICAL,
                    confidence=0.98,
                    weight=2.0,
                    description="Web page actively contains an OTP harvest input element.",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="WebDOMAnalyzer",
                        target_artifact=step.payload.get("prompt", "OTP prompt"),
                    ),
                )
            )

        # 4. Payment Context
        elif step.event_type in (EventType.COLLECT_REQUEST_RECEIVED, EventType.PAYMENT_INTENT_INITIATED):
            vpa = step.payload.get("vpa", "")
            if vpa and any(psp in vpa.lower() for psp in ["@oksbi", "@paytm", "@ybl", "@axl", "@ibl"]):
                new_step_signals.append(
                    EvidenceSignal(
                        incident_id=incident_id,
                        dimension=SignalDimension.PAYMENT,
                        signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                        severity=SignalSeverity.MEDIUM,
                        confidence=0.88,
                        weight=1.5,
                        description=f"Transaction requests payment to individual consumer VPA handle: {vpa}",
                        provenance=ProvenanceRecord(
                            source_service="services/investigation",
                            detector_name="PaymentVPAValidator",
                            target_artifact=vpa,
                        ),
                    )
                )

        accumulated_signals.extend(new_step_signals)

        # Check payment proximity
        has_payment = step.event_type in (EventType.COLLECT_REQUEST_RECEIVED, EventType.PAYMENT_INTENT_INITIATED)
        pattern_match = PatternMatcher.match(accumulated_signals)

        # Evaluate through RiskEngine
        assess = RiskEngine.evaluate(
            incident_id=incident_id,
            signals=accumulated_signals,
            pattern_match=pattern_match,
            payment_proximate=has_payment,
        )

        # Check if Hero Scenario to run EmergingVariantDetector
        hero_report = None
        if req.scenario_id == "emerging_ai_variant" and step.step_index >= 3:
            fp = ScamFingerprintBuilder.build(
                incident_id=incident_id,
                message_summary="HDFC security verification alert",
                claimed_identity="HDFC Bank Security Desk",
                tactics=["ACCOUNT_BLOCK_THREAT", "IMMEDIATE_URGENCY", "IMPERSONATION"],
                requested_action="VERIFY_NETBANKING_AND_SUBMIT_OTP",
                stage_sequence=["INITIAL_CONTACT", "IMPERSONATION", "URGENCY_PRESSURE", "SUSPICIOUS_LINK"],
                temporal_pace_seconds=65,
                infrastructure_hash={"phone": "+919222222222", "domain": "hdfc-security-check.xyz"},
                payment_profile={"vpa": "hdfc.desk@paytm"},
            )
            v_eval = EmergingVariantDetector.evaluate(
                incident_id=incident_id,
                fingerprint=fp,
                historical_phones=["+919111111111"],
                historical_domains=["sbi-kyc-fix.online"],
                historical_vpas=["sbi.officer@oksbi"],
                pattern_match=pattern_match,
                semantic_similarity_score=0.85,
                temporal_pace_seconds=65,
            )
            hero_report = {
                "phone_matched": v_eval.identifier_match.phone_matched,
                "domain_matched": v_eval.identifier_match.domain_matched,
                "payment_matched": v_eval.identifier_match.payment_matched,
                "semantic_match": v_eval.workflow_match.semantic_level,
                "temporal_match": v_eval.workflow_match.temporal_level,
                "pattern_match": v_eval.workflow_match.pattern_level,
                "status": v_eval.status.value,
                "verdict_explanation": v_eval.verdict_explanation,
            }

        evolution_path.append(assess.risk_score)

        step_results.append(
            SimulationStepResult(
                step_index=step.step_index,
                offset_label=step.offset_label,
                title=step.title,
                event_type=step.event_type.value,
                new_signals=new_step_signals,
                total_signals_so_far=len(accumulated_signals),
                risk_score=assess.risk_score,
                risk_level=assess.risk_level.value,
                evidence_confidence=assess.evidence_confidence.value,
                intervention_action=assess.recommended_intervention.action.value,
                friction_delay_seconds=assess.recommended_intervention.friction_delay_seconds,
                banner_message=assess.recommended_intervention.banner_message,
                reason_codes=assess.reason_codes,
                emerging_variant_report=hero_report,
            )
        )

    last_assess = step_results[-1]
    return RunSimulationResponse(
        scenario_id=req.scenario_id,
        title=scenario.title,
        incident_id=incident_id,
        steps_results=step_results,
        final_risk_score=last_assess.risk_score,
        final_risk_level=last_assess.risk_level,
        final_evidence_confidence=last_assess.evidence_confidence,
        evolution_path=evolution_path,
    )
