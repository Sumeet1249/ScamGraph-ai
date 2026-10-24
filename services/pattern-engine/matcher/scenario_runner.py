"""Scenario Runner for ScamGraph AI (Step 15).

Loads safe synthetic scenarios, runs the full analytical pipeline:
Incident -> Events -> Timeline -> PatternEngine -> RiskEngine -> InterventionEngine,
and produces comprehensive structured audit results without hardcoding answers.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services.api.app.domain.enums import (
    ConfidenceLevel,
    EventType,
    EvidenceSource,
    InterventionType,
    MatchLevel,
    RiskLevel,
)
from services.api.app.domain.models import Event, Evidence, Incident, PatternMatch, RiskAssessment
from services.pattern_engine.matcher.intervention_engine import (
    AdaptiveInterventionEngine,
    InterventionDecision,
    intervention_engine,
)
from services.pattern_engine.matcher.pattern_engine_v1 import (
    PatternEngineV1,
    pattern_engine_v1,
)
from services.pattern_engine.matcher.risk_engine_v1 import (
    RiskEngineV1,
    risk_engine_v1,
)


@dataclass
class ScenarioRunResult:
    """Structured output produced by running a scenario through ScamGraph engines."""
    scenario_id: str
    scenario_title: str
    description: str
    incident_id: str
    timeline: List[Dict[str, Any]]
    pattern_matched: Optional[PatternMatch]
    risk_assessment: RiskAssessment
    intervention: InterventionDecision
    reasons: List[str] = field(default_factory=list)

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario": self.scenario_title,
            "pattern": self.pattern_matched.pattern_name if self.pattern_matched else "NONE",
            "match_level": self.pattern_matched.match_level.value if self.pattern_matched else "NONE",
            "current_stage": self.pattern_matched.current_stage if self.pattern_matched else "INITIAL_CONTACT",
            "threat_risk_index": self.risk_assessment.risk_score,
            "risk_level": self.risk_assessment.risk_level.value,
            "evidence_confidence": self.risk_assessment.confidence_level.value,
            "intervention_action": self.intervention.action.value,
            "friction_seconds": self.intervention.friction_delay_seconds,
            "payment_blocked": self.intervention.payment_blocked,
            "reasons": self.reasons,
        }


class ScenarioRunner:
    """Executes end-to-end synthetic scenarios across all ScamGraph analytical engines."""

    def __init__(
        self,
        patterns: Optional[PatternEngineV1] = None,
        risk: Optional[RiskEngineV1] = None,
        intervention: Optional[AdaptiveInterventionEngine] = None,
    ):
        self.pattern_engine = patterns or pattern_engine_v1
        self.risk_engine = risk or risk_engine_v1
        self.intervention_engine = intervention or intervention_engine

    def run_scenario(self, scenario_data: Dict[str, Any]) -> ScenarioRunResult:
        """Runs an end-to-end scenario from dictionary definition."""
        base_time = datetime.now(timezone.utc)
        scenario_id = scenario_data.get("id", str(uuid4()))
        scenario_title = scenario_data.get("scenario", "Synthetic Scenario")
        description = scenario_data.get("description", "")

        # 1. Create Incident
        incident = Incident(
            id=f"inc-{uuid4().hex[:8]}",
            created_at=base_time,
            updated_at=base_time,
            title=f"Scenario: {scenario_title}",
            metadata={"scenario_id": scenario_id, "safe_synthetic": True},
        )

        # 2. Ingest and Chronologically Sequence Events
        raw_events = scenario_data.get("events", [])
        events: List[Event] = []
        timeline_records: List[Dict[str, Any]] = []

        for ev in raw_events:
            offset = ev.get("timestamp_offset_seconds", 0)
            ev_time = base_time + timedelta(seconds=offset)
            etype = EventType(ev["event_type"])
            event_obj = Event(
                id=f"ev-{uuid4().hex[:8]}",
                incident_id=incident.id,
                timestamp=ev_time,
                event_type=etype,
                description=ev.get("description", ""),
                metadata={"channel": ev.get("channel", "UNKNOWN"), "offset_s": offset},
            )
            events.append(event_obj)
            timeline_records.append({
                "offset": f"T+{offset:02d}s",
                "event_type": etype.value,
                "description": ev.get("description", ""),
                "channel": ev.get("channel", "UNKNOWN"),
            })

        # Ensure timeline is strictly chronological
        events.sort(key=lambda x: x.timestamp)
        timeline_records.sort(key=lambda x: int(x["offset"][2:-1]))

        # 3. Ingest Evidence
        raw_evidence = scenario_data.get("evidence", [])
        evidence_list: List[Evidence] = []
        observed_signals: List[str] = []

        for e in raw_evidence:
            ev_id = f"evi-{uuid4().hex[:8]}"
            source = EvidenceSource(e["source"])
            sig = e["signal"]
            observed_signals.append(sig)
            evidence_obj = Evidence(
                id=ev_id,
                incident_id=incident.id,
                source=source,
                signal=sig,
                observation=e.get("observation", ""),
                confidence=float(e.get("confidence", 0.8)),
                timestamp=base_time,
            )
            evidence_list.append(evidence_obj)

        # Also incorporate event types as signals
        for ev in events:
            observed_signals.append(ev.event_type.value)

        # 4. Run Pattern Engine V1 (Deterministic Sequence Matching)
        event_types_seq = [ev.event_type.value for ev in events]
        evidence_ids = [e.id for e in evidence_list]
        pattern_match = self.pattern_engine.match_best_pattern(
            observed_signals=observed_signals,
            observed_events=event_types_seq,
            evidence_ids=evidence_ids,
        )

        pattern_matches_list = [pattern_match] if pattern_match else []

        # 5. Run Risk Engine V1 (Threat Risk Index + Evidence Confidence)
        risk_assessment = self.risk_engine.evaluate(
            incident=incident,
            events=events,
            evidence_list=evidence_list,
            pattern_matches=pattern_matches_list,
        )

        # 6. Run Adaptive Intervention Engine (Context & Anti-Alert-Fatigue Friction)
        payment_proximity = any(
            ev.event_type in (EventType.PAYMENT_REQUEST, EventType.PAYMENT_INTENT)
            for ev in events
        )
        current_stage = (
            pattern_match.current_stage
            if pattern_match
            else ("PAYMENT_REQUEST" if payment_proximity else "INITIAL_CONTACT")
        )

        intervention_decision = self.intervention_engine.decide_intervention(
            risk_score=risk_assessment.risk_score,
            evidence_confidence=risk_assessment.confidence_level,
            journey_stage=current_stage,
            payment_proximity=payment_proximity,
            pattern_match=pattern_match,
            counter_evidence=risk_assessment.counter_evidence,
            num_events=len(events),
        )

        # Consolidate consolidated explainable reasons
        consolidated_reasons = []
        if pattern_match:
            consolidated_reasons.append(f"Pattern: {pattern_match.pattern_name} ({pattern_match.match_level.value})")
        consolidated_reasons.extend(risk_assessment.reason_codes[:4])
        consolidated_reasons.extend(intervention_decision.reasons[:2])

        return ScenarioRunResult(
            scenario_id=scenario_id,
            scenario_title=scenario_title,
            description=description,
            incident_id=incident.id,
            timeline=timeline_records,
            pattern_matched=pattern_match,
            risk_assessment=risk_assessment,
            intervention=intervention_decision,
            reasons=consolidated_reasons,
        )

    def run_scenario_file(self, file_path: Path) -> ScenarioRunResult:
        """Reads scenario JSON file and executes it."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.run_scenario(data)

    def run_all_scenarios(self, directory: Path) -> List[ScenarioRunResult]:
        """Runs all scenario files in the given directory sorted by filename."""
        results: List[ScenarioRunResult] = []
        files = sorted(directory.glob("*.json"))
        for f in files:
            results.append(self.run_scenario_file(f))
        return results
