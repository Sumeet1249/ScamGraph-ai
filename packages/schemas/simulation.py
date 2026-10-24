"""Shared Simulation Schemas for ScamGraph AI Simulator.

Defines:
- Scenario definitions (steps, branches, evidence)
- Simulation requests and responses
- Debrief and comparison schemas
- Event models for simulation tracking
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SimulationDecisionEnum(str, Enum):
    """User actions available at simulation decision points."""
    TRUST_AND_CONTINUE = "trust_and_continue"
    VERIFY_INDEPENDENTLY = "verify_independently"
    IGNORE_OR_REPORT = "ignore_or_report"
    OPEN_LINK = "open_link"
    CLOSE_PAGE = "close_page"
    REPLY_TO_SENDER = "reply_to_sender"
    ENTER_CREDENTIALS = "enter_credentials"
    ENTER_OTP = "enter_otp"
    APPROVE_PAYMENT = "approve_payment"
    CANCEL_PAYMENT = "cancel_payment"
    QUESTION_SENDER = "question_sender"


class StimulusType(str, Enum):
    """Type of stimulus presented to user."""
    MESSAGE = "message"
    WEBSITE = "website"
    PHONE_CALL = "phone_call"
    PAYMENT_REQUEST = "payment_request"
    VERIFICATION_FORM = "verification_form"
    AGENT_CONVERSATION = "agent_conversation"


class StepBranch(BaseModel):
    """Branching logic from current step based on decision."""
    decision: SimulationDecisionEnum
    next_step_id: Optional[str] = None  # None = end scenario
    outcome_description: str
    generates_signals: bool = True
    risk_multiplier: float = Field(default=1.0, description="How much does this decision amplify risk?")


class SimulationStepDef(BaseModel):
    """Definition of a single step in an interactive simulation."""
    step_id: str
    title: str
    description: str
    stimulus_type: StimulusType
    stimulus_content: Dict[str, Any] = Field(description="Message text, URL, form fields, etc.")
    decision_prompt: str = Field(description="What should the user decide?")
    decision_options: List[Dict[str, str]] = Field(description=[{"decision": "...", "label": "...", "hint": "..."}])
    branches: List[StepBranch] = Field(description="Outcome for each decision")
    evidence_present_at_step: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Signals that should be visible to user at this step"
    )
    teaching_points: List[str] = Field(
        default_factory=list,
        description="Key lessons if user chooses the safer path"
    )


class ScenarioDef(BaseModel):
    """Complete branching scenario definition."""
    scenario_id: str
    title: str
    category: str = Field(description="electricity_scam, kyc_fraud, investment_scam, etc.")
    difficulty: str = Field(description="beginner, intermediate, advanced")
    estimated_duration_minutes: int
    description: str
    steps: Dict[str, SimulationStepDef] = Field(description="step_id → step definition")
    first_step_id: str
    expected_risk_level: str = Field(description="LOW, MEDIUM, HIGH")
    learning_objectives: List[str]
    languages_supported: List[str] = Field(default_factory=list, description=["en", "hi", "hinglish"])


# ─────────────────────────────────────────────────────────────────────────────
# Simulation Session and Response Models
# ─────────────────────────────────────────────────────────────────────────────


class SimulationStepResponse(BaseModel):
    """Response with current step and decision options."""
    session_id: str
    scenario_id: str
    step_id: str
    title: str
    description: str
    stimulus_type: StimulusType
    stimulus_content: Dict[str, Any]
    decision_prompt: str
    decision_options: List[Dict[str, str]]
    risk_context: Optional[Dict[str, Any]] = Field(
        description="Current risk score, confidence, signals so far"
    )
    progress: Dict[str, Any] = Field(
        description="Simulation progress (current_step, total_steps, percentage)"
    )


class SimulationDecisionRequest(BaseModel):
    """User submits their decision at a step."""
    session_id: str
    step_id: str
    decision: SimulationDecisionEnum


class SimulationDecisionResponse(BaseModel):
    """Response after user decision with outcome and next step."""
    session_id: str
    step_id: str
    decision: SimulationDecisionEnum
    outcome_text: str
    is_safer_decision: bool
    signals_generated: List[Dict[str, Any]] = Field(description="New evidence from this decision")
    risk_score: int
    risk_level: str
    evidence_confidence: float
    intervention_recommended: Optional[str]
    feedback: str
    counterfactual_outcomes: Dict[str, Dict[str, Any]] = Field(
        description="Outcomes for each decision path (e.g. trust_and_continue, report_to_authorities, seek_help)"
    )
    next_step: Optional[SimulationStepResponse]
    session_completed: bool = False


class SimulationDebrief(BaseModel):
    """Post-scenario learning debrief."""
    session_id: str
    scenario_id: str
    scenario_title: str
    completed: bool
    decision_count: int
    final_risk_score: int
    final_risk_level: str
    duration_seconds: int
    decisions_timeline: List[Dict[str, Any]]
    earliest_intervention_point: Optional[Dict[str, Any]] = Field(
        description="First step where system recommended intervention"
    )
    learning_points: List[str]
    performance_score: int = Field(description="0-100, where 100 = all safe decisions")
    comparison_scenarios: Optional[List[Dict[str, Any]]] = Field(
        description="What-if alternatives with different decision paths"
    )
    recovery_checklist: Optional[List[str]] = Field(
        description="If money was lost in scenario, steps to report or recover"
    )
    recommended_next_scenario: Optional[str] = Field(
        description="Suggest harder scenario if user scored well"
    )


class SimulationStartRequest(BaseModel):
    """Request to start new simulation session."""
    scenario_id: str
    user_id: Optional[str] = None
    language: str = Field(default="en")


class SimulationStartResponse(BaseModel):
    """Response when simulation session starts."""
    session_id: str
    scenario_id: str
    first_step: SimulationStepResponse


# ─────────────────────────────────────────────────────────────────────────────
# Replay and What-If Models
# ─────────────────────────────────────────────────────────────────────────────


class SimulationReplayRequest(BaseModel):
    """Replay same scenario with different decision path."""
    session_id: str
    alternative_decision_path: List[SimulationDecisionEnum]


class SimulationComparisonResult(BaseModel):
    """Compare two decision paths through same scenario."""
    original_path: List[Dict[str, Any]]
    alternative_path: List[Dict[str, Any]]
    original_final_risk: int
    alternative_final_risk: int
    risk_difference: int
    earliest_divergence_step: str
    learning_delta: str


# ─────────────────────────────────────────────────────────────────────────────
# Detection Rule Testing (Analyst Feature)
# ─────────────────────────────────────────────────────────────────────────────


class RuleTestRequest(BaseModel):
    """Test detection rule on fixed synthetic scenario."""
    rule_definition: Dict[str, Any]
    scenario_id: str
    decision_path: Optional[List[SimulationDecisionEnum]] = None


class RuleTestResult(BaseModel):
    """Metrics from testing a detection rule on synthetic data."""
    rule_name: str
    scenario_id: str
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    intervention_timing: str = Field(description="Early, timely, late")
