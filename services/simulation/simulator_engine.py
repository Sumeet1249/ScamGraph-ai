"""Interactive Scam Journey Simulator Engine.

Provides step-by-step branching simulation with user decisions,
evidence tracking, and counterfactual outcome comparison.

Design:
- Simulation sessions are separate from live incident records
- Every decision creates a new event with user choice and outcome
- Evidence is accumulated across steps and fed through real risk engine
- Outcomes are deterministic and reproducible (session_id + step + decision → outcome)
- Session state is preserved across decisions; users can replay branches
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from packages.schemas import (
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    RiskLevel,
)


class SimulationDecision(str, Enum):
    """User action at a decision point in simulation."""
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


class SimulationOutcome(str, Enum):
    """Result of a decision in simulation context."""
    SAFE_PATH_RECOMMENDED = "safe_path_recommended"
    PAYMENT_BLOCKED = "payment_blocked"
    CREDENTIAL_COMPROMISED = "credential_compromised"
    OTP_CAPTURED = "otp_captured"
    SYNTHETIC_PAYMENT_COMPLETED = "synthetic_payment_completed"
    EARLY_INTERVENTION_SUGGESTED = "early_intervention_suggested"
    ACCOUNT_COMPROMISED = "account_compromised"


@dataclass
class DecisionNode:
    """A single decision point in user's journey."""
    step_id: str
    decision: SimulationDecision
    timestamp: datetime
    outcome: SimulationOutcome
    risk_score_before: int
    risk_score_after: int
    signals_generated: List[EvidenceSignal]
    is_branch_point: bool  # Can user replay from here?


@dataclass
class JourneyPath:
    """Complete decision path through scenario."""
    path_id: str
    decisions: List[DecisionNode]
    final_risk_score: int
    final_outcome: str
    completed: bool


class SimulationEngine:
    """
    Core engine for interactive branching simulations with session preservation.
    
    Responsibilities:
    - Load scenario definitions
    - Execute step transitions based on user decisions
    - Generate evidence signals for each path
    - Calculate risk scores using real risk engine
    - **Preserve session state across multiple playthroughs**
    - **Track multiple decision paths (for replay/comparison)**
    - Produce counterfactual comparisons (what-if)
    - Generate user-friendly feedback
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.scenarios: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, scenario_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create new simulation session for a scenario."""
        session_id = f"SIM-{scenario_id[:12]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        session = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "current_path_id": str(uuid4()),  # Track which path user is on
            "paths": {},  # Multiple paths for replay comparison
            "all_decisions": [],  # Global decision history
            "current_step_id": None,
            "cumulative_signals": [],
            "current_risk_score": 20,
            "current_risk_level": "LOW",
            "journey_graph": [],  # Timeline of steps visited
        }
        
        # Initialize first path
        session["paths"][session["current_path_id"]] = {
            "path_id": session["current_path_id"],
            "decisions": [],
            "completed": False,
            "final_risk_score": None,
        }
        
        self.sessions[session_id] = session
        return session
    
    def get_session_journey_graph(self, session_id: str) -> Dict[str, Any]:
        """Return visualization-ready journey graph showing all visited steps."""
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "journey_steps": session.get("journey_graph", []),
            "decision_history": [
                {
                    "step_id": d["step_id"],
                    "decision": d["decision"].value,
                    "risk_before": d.get("risk_score_before"),
                    "risk_after": d.get("risk_score_after"),
                    "timestamp": d.get("timestamp", "").isoformat() if isinstance(d.get("timestamp"), datetime) else d.get("timestamp"),
                }
                for d in session.get("all_decisions", [])
            ],
            "total_paths_explored": len(session.get("paths", {})),
            "current_risk_score": session.get("current_risk_score", 20),
        }
    
    def replay_from_step(self, session_id: str, branch_step_id: str) -> Dict[str, Any]:
        """Allow user to replay scenario from a previous step with different decision."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Find the decision node at this step
        matching_decision = None
        for decision in session["all_decisions"]:
            if decision["step_id"] == branch_step_id:
                matching_decision = decision
                break
        
        if not matching_decision:
            return {"error": f"Step {branch_step_id} not found in history"}
        
        # Create new path starting from this point
        new_path_id = str(uuid4())
        new_path = {
            "path_id": new_path_id,
            "decisions": [],
            "completed": False,
            "parent_step": branch_step_id,
            "branch_point_index": session["all_decisions"].index(matching_decision),
        }
        
        session["paths"][new_path_id] = new_path
        session["current_path_id"] = new_path_id
        
        # Reset cumulative state to just before this branch point
        cumulative_signals = []
        for i, d in enumerate(session["all_decisions"]):
            if i < session["all_decisions"].index(matching_decision):
                cumulative_signals.extend(d.get("signals_generated", []))
        
        session["cumulative_signals"] = cumulative_signals
        session["current_risk_score"] = matching_decision["risk_score_before"]
        
        return {
            "session_id": session_id,
            "new_path_id": new_path_id,
            "branch_point_step": branch_step_id,
            "message": "Replay mode active. Choose a different decision at this step.",
        }
    
    def compare_paths(self, session_id: str, path_id_1: str, path_id_2: str) -> Dict[str, Any]:
        """Compare two decision paths taken through same scenario."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        path1 = session["paths"].get(path_id_1)
        path2 = session["paths"].get(path_id_2)
        
        if not path1 or not path2:
            return {"error": "One or both paths not found"}
        
        # Find where paths diverge
        divergence_index = 0
        for i, (d1, d2) in enumerate(zip(path1["decisions"], path2["decisions"])):
            if d1["step_id"] != d2["step_id"] or d1["decision"] != d2["decision"]:
                divergence_index = i
                break
        
        return {
            "path_1": {
                "path_id": path_id_1,
                "decision_count": len(path1["decisions"]),
                "final_risk_score": path1.get("final_risk_score"),
            },
            "path_2": {
                "path_id": path_id_2,
                "decision_count": len(path2["decisions"]),
                "final_risk_score": path2.get("final_risk_score"),
            },
            "divergence_at_step": path1["decisions"][divergence_index]["step_id"] if divergence_index < len(path1["decisions"]) else None,
            "risk_difference": abs(
                (path1.get("final_risk_score") or 0) - (path2.get("final_risk_score") or 0)
            ),
            "learning_insight": "Compare the two paths to see how different decisions led to different outcomes.",
        }
    
    def record_decision(
        self,
        session_id: str,
        step_id: str,
        decision: SimulationDecision,
        outcome: SimulationOutcome,
        signals_generated: List[EvidenceSignal],
        new_risk_score: int,
        next_step_id: Optional[str],
    ) -> Dict[str, Any]:
        """Record decision in session and update journey graph."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        current_path_id = session["current_path_id"]
        old_risk = session["current_risk_score"]
        
        decision_node = {
            "step_id": step_id,
            "decision": decision.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "outcome": outcome.value,
            "risk_score_before": old_risk,
            "risk_score_after": new_risk,
            "signals_generated": [s.dict() if hasattr(s, "dict") else s for s in signals_generated],
            "next_step_id": next_step_id,
        }
        
        # Add to current path
        session["paths"][current_path_id]["decisions"].append(decision_node)
        
        # Add to global decision history
        session["all_decisions"].append(decision_node)
        
        # Update journey graph (timeline of steps)
        if not any(j["step_id"] == step_id for j in session["journey_graph"]):
            session["journey_graph"].append({
                "step_id": step_id,
                "title": step_id.replace("_", " ").title(),
                "risk_score": new_risk,
                "timestamp": decision_node["timestamp"],
            })
        
        # Update session state
        session["current_step_id"] = next_step_id
        session["cumulative_signals"].extend(signals_generated)
        session["current_risk_score"] = new_risk
        session["current_risk_level"] = self._risk_int_to_level(new_risk)
        
        # Mark path as complete if no next step
        if next_step_id is None:
            session["paths"][current_path_id]["completed"] = True
            session["paths"][current_path_id]["final_risk_score"] = new_risk
        
        return {
            "decision_recorded": True,
            "path_id": current_path_id,
            "session_id": session_id,
            "next_step_id": next_step_id,
            "journey_graph": self.get_session_journey_graph(session_id),
        }
    
    def _risk_int_to_level(self, score: int) -> str:
        """Convert numeric risk to level."""
        if score < 30:
            return "LOW"
        elif score < 60:
            return "MEDIUM"
        elif score < 85:
            return "HIGH"
        else:
            return "CRITICAL"
