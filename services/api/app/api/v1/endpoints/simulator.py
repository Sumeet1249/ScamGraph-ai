"""Interactive Scam Journey Simulator API Endpoints.

Provides:
- Scenario listing and loading
- Session initialization
- Interactive step-by-step decision processing
- Debrief and learning feedback
- What-if replay and comparison
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
import yaml
import json
from pathlib import Path
from datetime import datetime, timezone

from packages.schemas.simulation import (
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationStepResponse,
    SimulationDecisionRequest,
    SimulationDecisionResponse,
    SimulationDebrief,
    StimulusType,
    SimulationDecisionEnum,
)
from services.api.app.core.config import settings
from services.pattern_engine.matcher.risk_engine import RiskEngine

router = APIRouter()

# Global in-memory session store (will migrate to PostgreSQL)
SIMULATION_SESSIONS: Dict[str, Dict[str, Any]] = {}


class ScenarioNotFound(Exception):
    pass


def get_scenarios_dir() -> Path:
    """Find the data/scenarios directory regardless of execution working directory."""
    candidates = [
        Path("data/scenarios"),
        Path(__file__).resolve().parents[6] / "data" / "scenarios",
        Path(__file__).resolve().parents[5] / "data" / "scenarios",
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path("data/scenarios")


def load_scenario_yaml(scenario_id: str) -> Dict[str, Any]:
    """Load scenario definition from YAML file."""
    scenarios_dir = get_scenarios_dir()
    direct_path = scenarios_dir / f"simulator_{scenario_id}.yaml"
    if direct_path.exists():
        with open(direct_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # Search all simulator_*.yaml files by scenario_id
    for scenario_file in scenarios_dir.glob("simulator_*.yaml"):
        try:
            with open(scenario_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and data.get("scenario_id") == scenario_id:
                    return data
        except Exception:
            continue

    raise ScenarioNotFound(f"Scenario {scenario_id} not found in {scenarios_dir}")


@router.get("/scenarios", tags=["Simulator"])
async def list_scenarios():
    """List available training scenarios."""
    scenarios_dir = get_scenarios_dir()
    scenario_files = list(scenarios_dir.glob("simulator_*.yaml"))
    
    scenarios = []
    for scenario_file in scenario_files:
        try:
            with open(scenario_file, "r", encoding="utf-8") as f:
                scenario_def = yaml.safe_load(f)
            scenarios.append({
                "scenario_id": scenario_def.get("scenario_id"),
                "title": scenario_def.get("title"),
                "category": scenario_def.get("category"),
                "difficulty": scenario_def.get("difficulty"),
                "estimated_duration_minutes": scenario_def.get("estimated_duration_minutes"),
                "description": scenario_def.get("description"),
                "expected_risk_level": scenario_def.get("expected_risk_level"),
            })
        except Exception as e:
            print(f"Error loading {scenario_file}: {e}")
            continue
    
    return {
        "scenarios": scenarios,
        "total": len(scenarios),
    }


@router.post("/start", response_model=SimulationStartResponse, tags=["Simulator"])
async def start_simulation(req: SimulationStartRequest):
    """Initialize new simulation session with first step."""
    try:
        scenario_def = load_scenario_yaml(req.scenario_id)
    except ScenarioNotFound:
        raise HTTPException(status_code=404, detail=f"Scenario {req.scenario_id} not found")
    
    # Create session
    session_id = f"SIM-{req.scenario_id[:12]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    first_step_id = scenario_def.get("first_step_id")
    first_step_def = scenario_def["steps"].get(first_step_id)
    
    if not first_step_def:
        raise HTTPException(status_code=400, detail="Invalid scenario: missing first step")
    
    # Store session state
    SIMULATION_SESSIONS[session_id] = {
        "scenario_id": req.scenario_id,
        "scenario_def": scenario_def,
        "user_id": req.user_id,
        "language": req.language,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "current_step_id": first_step_id,
        "decisions_history": [],
        "cumulative_signals": [],
        "current_risk_score": 20,  # Start low; increases with risky decisions
        "current_risk_level": "LOW",
        "current_confidence": 0.3,
    }
    
    # Build first step response
    first_step_response = _build_step_response(
        session_id=session_id,
        scenario_id=req.scenario_id,
        step_def=first_step_def,
        step_index=1,
        total_steps=len(scenario_def["steps"]),
    )
    
    return SimulationStartResponse(
        session_id=session_id,
        scenario_id=req.scenario_id,
        first_step=first_step_response,
    )


@router.post("/decision", response_model=SimulationDecisionResponse, tags=["Simulator"])
async def process_decision(req: SimulationDecisionRequest):
    """Process user decision at current step and return outcome."""
    session = SIMULATION_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {req.session_id} not found")
    
    scenario_def = session["scenario_def"]
    current_step_def = scenario_def["steps"].get(req.step_id)
    
    if not current_step_def:
        raise HTTPException(status_code=400, detail=f"Invalid step: {req.step_id}")
    
    # Find branch for this decision
    matching_branch = None
    for branch in current_step_def.get("branches", []):
        if SimulationDecisionEnum(branch["decision"]) == req.decision:
            matching_branch = branch
            break
    
    if not matching_branch:
        raise HTTPException(status_code=400, detail=f"Invalid decision: {req.decision}")
    
    # Determine outcome and next step
    outcome_text = matching_branch.get("outcome_description", "")
    next_step_id = matching_branch.get("next_step_id")
    risk_multiplier = matching_branch.get("risk_multiplier", 1.0)
    
    # Update risk score
    old_risk = session.get("current_risk_score", 20)
    new_risk = min(100, int(old_risk * risk_multiplier))
    session["current_risk_score"] = new_risk
    session["current_risk_level"] = _risk_int_to_level(new_risk)
    
    # Simulate evidence signals for this decision (in production, use real signal extraction)
    new_signals = _generate_signals_for_decision(req.step_id, req.decision)
    session["cumulative_signals"].extend(new_signals)
    
    # Record decision
    session["decisions_history"].append({
        "step_id": req.step_id,
        "decision": req.decision.value,
        "outcome": outcome_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_score": new_risk,
        "risk_level": session["current_risk_level"],
    })
    
    # Determine if this was a safer decision
    is_safer = _is_safer_decision(req.step_id, req.decision)
    
    # Generate counterfactuals (what-if scenarios)
    counterfactuals = {}
    for alt_decision in SimulationDecisionEnum:
        if alt_decision == req.decision:
            continue
        alt_branch = next(
            (b for b in current_step_def.get("branches", []) 
             if SimulationDecisionEnum(b["decision"]) == alt_decision),
            None
        )
        if alt_branch:
            alt_risk = int(old_risk * alt_branch.get("risk_multiplier", 1.0))
            counterfactuals[alt_decision.value] = {
                "risk_score": min(100, alt_risk),
                "risk_level": _risk_int_to_level(alt_risk),
                "outcome": alt_branch.get("outcome_description", ""),
            }
    
    # Build next step if scenario continues
    next_step_response = None
    if next_step_id:
        next_step_def = scenario_def["steps"].get(next_step_id)
        if next_step_def:
            step_index = _count_prior_steps(scenario_def, next_step_id)
            total_steps = len(scenario_def["steps"])
            next_step_response = _build_step_response(
                session_id=req.session_id,
                scenario_id=session["scenario_id"],
                step_def=next_step_def,
                step_index=step_index,
                total_steps=total_steps,
            )
    
    # Check if session is complete
    session_completed = next_step_id is None
    if session_completed:
        session["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Determine intervention recommendation
    intervention = None
    if new_risk >= 70:
        intervention = "PRE_PAYMENT_INTERVENTION"
    elif new_risk >= 50:
        intervention = "STRONG_WARNING"
    
    return SimulationDecisionResponse(
        session_id=req.session_id,
        step_id=req.step_id,
        decision=req.decision,
        outcome_text=outcome_text,
        is_safer_decision=is_safer,
        signals_generated=[
            {
                "signal_type": s.signal_type,
                "severity": s.severity.value,
                "description": s.description,
            }
            for s in new_signals
        ],
        risk_score=new_risk,
        risk_level=session["current_risk_level"],
        evidence_confidence=session.get("current_confidence", 0.5),
        intervention_recommended=intervention,
        feedback=_generate_feedback(req.step_id, req.decision, is_safer),
        counterfactual_outcomes=counterfactuals,
        next_step=next_step_response,
        session_completed=session_completed,
    )


@router.get("/journey/{session_id}", tags=["Simulator"])
async def get_journey_graph(session_id: str):
    """Get complete journey graph for a session showing all steps visited and decisions made."""
    session = SIMULATION_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return {
        "session_id": session_id,
        "scenario_id": session["scenario_id"],
        "journey_steps": session.get("journey_graph", []),
        "total_decisions": len(session.get("all_decisions", [])),
        "current_risk_score": session.get("current_risk_score", 20),
        "paths_explored": len(session.get("paths", {})),
    }


@router.post("/replay", tags=["Simulator"])
async def replay_from_step(request: Dict[str, str]):
    """Replay scenario from a previous step with different decision."""
    session_id = request.get("session_id")
    step_id = request.get("step_id")
    
    session = SIMULATION_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Find the decision at this step
    matching_decision = None
    for decision in session["all_decisions"]:
        if decision["step_id"] == step_id:
            matching_decision = decision
            break
    
    if not matching_decision:
        raise HTTPException(status_code=400, detail=f"Step {step_id} not found in session")
    
    # Create new branch path
    new_path_id = f"PATH-{uuid4().hex[:8]}"
    new_path = {
        "path_id": new_path_id,
        "decisions": [],
        "completed": False,
        "branch_from_step": step_id,
    }
    
    session["paths"][new_path_id] = new_path
    session["current_path_id"] = new_path_id
    
    # Reset to state before this step
    step_index = session["all_decisions"].index(matching_decision)
    session["cumulative_signals"] = []
    for i, d in enumerate(session["all_decisions"][:step_index]):
        session["cumulative_signals"].extend(d.get("signals_generated", []))
    
    session["current_risk_score"] = matching_decision["risk_score_before"]
    
    return {
        "session_id": session_id,
        "new_path_id": new_path_id,
        "branch_step": step_id,
        "message": "Replay mode active. Choose a different decision.",
        "risk_score_reset_to": matching_decision["risk_score_before"],
    }


@router.post("/compare-paths", tags=["Simulator"])
async def compare_decision_paths(request: Dict[str, Any]):
    """Compare two different decision paths through the same scenario."""
    session_id = request.get("session_id")
    path_id_1 = request.get("path_1")
    path_id_2 = request.get("path_2")
    
    session = SIMULATION_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    path1 = session["paths"].get(path_id_1)
    path2 = session["paths"].get(path_id_2)
    
    if not path1 or not path2:
        raise HTTPException(status_code=400, detail="One or both paths not found")
    
    # Find divergence point
    divergence_step = None
    for i, (d1, d2) in enumerate(zip(path1["decisions"], path2["decisions"])):
        if d1["step_id"] != d2["step_id"] or d1["decision"] != d2["decision"]:
            divergence_step = d1["step_id"]
            break
    
    return {
        "session_id": session_id,
        "path_1": {
            "path_id": path_id_1,
            "decisions": len(path1["decisions"]),
            "final_risk": path1.get("final_risk_score", "ongoing"),
        },
        "path_2": {
            "path_id": path_id_2,
            "decisions": len(path2["decisions"]),
            "final_risk": path2.get("final_risk_score", "ongoing"),
        },
        "divergence_at_step": divergence_step,
        "risk_difference": abs(
            (path1.get("final_risk_score") or 0) - (path2.get("final_risk_score") or 0)
        ),
    }
async def get_debrief(session_id: str):
    """Generate post-scenario debrief and learning feedback."""
    session = SIMULATION_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.get("completed_at"):
        raise HTTPException(status_code=400, detail="Scenario not yet completed")
    
    scenario_def = session["scenario_def"]
    
    # Calculate performance score
    safe_decisions = sum(1 for d in session["decisions_history"] if _is_safer_decision(d["step_id"], SimulationDecisionEnum(d["decision"])))
    total_decisions = len(session["decisions_history"])
    performance_score = int((safe_decisions / total_decisions * 100)) if total_decisions > 0 else 0
    
    # Duration
    started = datetime.fromisoformat(session["started_at"])
    completed = datetime.fromisoformat(session["completed_at"])
    duration_seconds = int((completed - started).total_seconds())
    
    # Generate learning points
    learning_points = []
    for decision_record in session["decisions_history"]:
        step_id = decision_record["step_id"]
        decision = SimulationDecisionEnum(decision_record["decision"])
        if decision == SimulationDecisionEnum.VERIFY_INDEPENDENTLY:
            learning_points.append("✓ You correctly verified independently—this is the safest approach.")
        elif decision == SimulationDecisionEnum.OPEN_LINK:
            learning_points.append("✗ Opening unverified links exposed you to credential theft.")
        elif decision == SimulationDecisionEnum.APPROVE_PAYMENT:
            learning_points.append("✗ Approving the payment transferred money to the attacker.")
    
    # Recommend next scenario
    recommended_next = None
    if performance_score >= 80:
        recommended_next = "advanced_scenario_id"  # Recommend harder scenario
    
    return SimulationDebrief(
        session_id=session_id,
        scenario_id=session["scenario_id"],
        scenario_title=scenario_def.get("title"),
        completed=True,
        decision_count=total_decisions,
        final_risk_score=session.get("current_risk_score", 50),
        final_risk_level=session.get("current_risk_level", "MEDIUM"),
        duration_seconds=duration_seconds,
        decisions_timeline=session["decisions_history"],
        learning_points=learning_points,
        performance_score=performance_score,
        recommended_next_scenario=recommended_next,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


def _build_step_response(
    session_id: str,
    scenario_id: str,
    step_def: Dict[str, Any],
    step_index: int,
    total_steps: int,
) -> SimulationStepResponse:
    """Build response object for a scenario step."""
    return SimulationStepResponse(
        session_id=session_id,
        scenario_id=scenario_id,
        step_id=step_def.get("step_id"),
        title=step_def.get("title"),
        description=step_def.get("description"),
        stimulus_type=StimulusType(step_def.get("stimulus_type", "message")),
        stimulus_content=step_def.get("stimulus_content", {}),
        decision_prompt=step_def.get("decision_prompt", "What would you do?"),
        decision_options=step_def.get("decision_options", []),
        risk_context=None,  # Will be populated from session
        progress={
            "current_step": step_index,
            "total_steps": total_steps,
            "percentage": int(step_index / total_steps * 100),
        },
    )


def _risk_int_to_level(risk_score: int) -> str:
    """Convert numeric risk score to level."""
    if risk_score < 30:
        return "LOW"
    elif risk_score < 60:
        return "MEDIUM"
    elif risk_score < 85:
        return "HIGH"
    else:
        return "CRITICAL"


def _is_safer_decision(step_id: str, decision: SimulationDecisionEnum) -> bool:
    """Determine if decision was safer than alternatives."""
    safer_by_step = {
        "step_1_message_arrival": [
            SimulationDecisionEnum.VERIFY_INDEPENDENTLY,
            SimulationDecisionEnum.IGNORE_OR_REPORT,
        ],
        "step_2_suspicious_website": [
            SimulationDecisionEnum.CLOSE_PAGE,
            SimulationDecisionEnum.VERIFY_INDEPENDENTLY,
        ],
        "step_3_credential_harvesting": [
            SimulationDecisionEnum.CANCEL_PAYMENT,
            SimulationDecisionEnum.QUESTION_SENDER,
        ],
        "step_4_payment_request": [
            SimulationDecisionEnum.CANCEL_PAYMENT,
            SimulationDecisionEnum.QUESTION_SENDER,
        ],
    }
    return decision in safer_by_step.get(step_id, [])


def _generate_signals_for_decision(
    step_id: str,
    decision: SimulationDecisionEnum,
) -> list:
    """Generate evidence signals for this decision."""
    from packages.schemas import (
        EvidenceSignal,
        SignalDimension,
        SignalSeverity,
        ProvenanceRecord,
    )
    
    signals = []
    
    if decision == SimulationDecisionEnum.OPEN_LINK:
        signals.append(
            EvidenceSignal(
                incident_id="",
                dimension=SignalDimension.BEHAVIORAL,
                signal_type="SUSPICIOUS_LINK_OPENED",
                severity=SignalSeverity.HIGH,
                confidence=0.95,
                weight=2.0,
                description="User clicked unverified link",
                provenance=ProvenanceRecord(
                    source_service="simulator",
                    detector_name="SimulationBehaviorTracker",
                    target_artifact=step_id,
                ),
            )
        )
    elif decision == SimulationDecisionEnum.ENTER_CREDENTIALS:
        signals.append(
            EvidenceSignal(
                incident_id="",
                dimension=SignalDimension.BEHAVIORAL,
                signal_type="CREDENTIALS_ENTERED_ON_PHISHING_PAGE",
                severity=SignalSeverity.CRITICAL,
                confidence=0.99,
                weight=5.0,
                description="Credentials entered on unverified website",
                provenance=ProvenanceRecord(
                    source_service="simulator",
                    detector_name="SimulationBehaviorTracker",
                    target_artifact=step_id,
                ),
            )
        )
    
    return signals


def _generate_feedback(
    step_id: str,
    decision: SimulationDecisionEnum,
    is_safer: bool,
) -> str:
    """Generate user-friendly feedback."""
    if is_safer:
        return "Good decision. You avoided falling for the scam at this step."
    else:
        return "This decision increased your risk. The attacker gained more access."


def _count_prior_steps(scenario_def: Dict[str, Any], step_id: str) -> int:
    """Count steps before this one (approximate index)."""
    steps_list = list(scenario_def.get("steps", {}).keys())
    try:
        return steps_list.index(step_id) + 1
    except ValueError:
        return len(steps_list)
