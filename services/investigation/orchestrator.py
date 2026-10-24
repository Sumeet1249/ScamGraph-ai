"""ScamGraph Unified Investigation Orchestrator V1 (Step 18).

Coordinates:
Incident -> Event Timeline -> URL Safety/Intel -> TinyFish WebInvestigator
-> Evidence Fusion -> PatternEngine V1 -> RiskEngine V1 -> AdaptiveInterventionEngine.

Enforces:
- Strict idempotency (re-assessing does not duplicate evidence).
- Resilience against provider timeouts or network degradation.
- Zero external dependency for core risk and pattern evaluation.
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4
from pydantic import BaseModel, Field

from services.api.app.domain.enums import (
    ConfidenceLevel,
    EventType,
    InterventionType,
    MatchLevel,
    RiskLevel,
)
from services.api.app.domain.models import Entity, Event, Evidence, Incident, PatternMatch, RiskAssessment
from services.api.app.repository import IncidentRepository, get_incident_repository
from services.investigation.tinyfish.service import TinyFishWebInvestigator, tinyfish_investigator
from services.investigation.url_analysis.service import URLInvestigationService, url_investigation_service
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

logger = logging.getLogger("investigation.orchestrator")


class IncidentAssessment(BaseModel):
    """Authoritative outcome of an end-to-end incident assessment."""
    incident_id: str
    incident: Incident
    timeline: List[Event]
    investigation_status: Dict[str, str] = Field(default_factory=dict)
    entities: List[Entity] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    pattern_matches: List[PatternMatch] = Field(default_factory=list)
    risk_assessment: RiskAssessment
    intervention: InterventionDecision
    reason_codes: List[str] = Field(default_factory=list)
    tripartite_decision: Optional[Any] = None
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationOrchestrator:
    """Orchestrates end-to-end investigation across all ScamGraph engines."""

    def __init__(
        self,
        repository: Optional[IncidentRepository] = None,
        url_service: Optional[URLInvestigationService] = None,
        web_investigator: Optional[TinyFishWebInvestigator] = None,
        patterns: Optional[PatternEngineV1] = None,
        risk: Optional[RiskEngineV1] = None,
        intervention: Optional[AdaptiveInterventionEngine] = None,
    ):
        self.repo = repository or get_incident_repository()
        self.url_service = url_service or url_investigation_service
        self.web_investigator = web_investigator or tinyfish_investigator
        self.pattern_engine = patterns or pattern_engine_v1
        self.risk_engine = risk or risk_engine_v1
        self.intervention_engine = intervention or intervention_engine

    async def assess_incident(self, incident_id: str) -> IncidentAssessment:
        """Executes full idempotent assessment of an incident."""
        # 1. Load Incident
        incident = await self.repo.get_incident(incident_id)
        if not incident:
            # Check session metadata fallback
            from services.api.app.api.v1.endpoints.incidents import _INCIDENTS_METADATA
            if incident_id in _INCIDENTS_METADATA:
                meta = _INCIDENTS_METADATA[incident_id]
                now = datetime.now(timezone.utc)
                incident = Incident(
                    id=incident_id,
                    created_at=meta.get("created_at", now),
                    updated_at=meta.get("created_at", now),
                    title=meta.get("metadata", {}).get("title", f"Incident {incident_id}"),
                    metadata=meta,
                )
                await self.repo.create_incident(incident)
            else:
                raise ValueError(f"Incident '{incident_id}' not found.")

        # 2. Load and Chronologically Sequence Events
        raw_events = await self.repo.get_events(incident_id)
        timeline = sorted(raw_events, key=lambda e: e.timestamp)

        # 3. Load Existing Evidence (for Idempotency Check)
        existing_evidence = await self.repo.get_evidence(incident_id)
        existing_signals: Set[str] = {f"{e.source.value}_{e.signal}" for e in existing_evidence}
        already_investigated_urls: Set[str] = {
            e.observation for e in existing_evidence if "URL" in e.signal
        }

        investigation_status: Dict[str, str] = {
            "url_analysis": "not_applicable",
            "tinyfish": "not_applicable",
        }
        new_evidence: List[Evidence] = []
        entities: List[Entity] = []

        # 4. Extract and Investigate URLs
        discovered_urls = self._extract_urls_from_events(timeline)

        for url in discovered_urls:
            # Idempotency guard: skip if this exact URL was already analyzed in this incident
            if any(url in inv_url for inv_url in already_investigated_urls):
                investigation_status["url_analysis"] = "already_completed"
                investigation_status["tinyfish"] = "already_completed"
                continue

            # 4a. URL Safety & Infrastructure Analysis
            try:
                inv_res = await self.url_service.investigate_url(incident_id, url)
                investigation_status["url_analysis"] = inv_res.status
                entities.extend(inv_res.entities)

                for ev in inv_res.evidence:
                    sig_key = f"{ev.source.value}_{ev.signal}"
                    if sig_key not in existing_signals:
                        new_evidence.append(ev)
                        existing_signals.add(sig_key)
                        await self.repo.add_evidence(incident_id, ev)
            except Exception as url_err:
                logger.warning("URL investigation error on %s: %s", url, url_err)
                investigation_status["url_analysis"] = "unavailable"
                inv_res = None

            # 4b. TinyFish Web Investigation (Only if safe public URL)
            if inv_res and inv_res.safety.is_safe:
                try:
                    tf_res = await self.web_investigator.investigate(incident_id, url)
                    investigation_status["tinyfish"] = tf_res.status
                    entities.extend(tf_res.entities)

                    for ev in tf_res.evidence:
                        sig_key = f"{ev.source.value}_{ev.signal}"
                        if sig_key not in existing_signals:
                            new_evidence.append(ev)
                            existing_signals.add(sig_key)
                            await self.repo.add_evidence(incident_id, ev)
                except Exception as tf_err:
                    logger.warning("TinyFish investigation error on %s: %s", url, tf_err)
                    investigation_status["tinyfish"] = "unavailable"
            elif inv_res and not inv_res.safety.is_safe:
                investigation_status["tinyfish"] = "blocked_by_ssrf"

        # 5. Consolidate Total Incident Evidence
        all_evidence = existing_evidence + new_evidence

        # 6. Extract Observed Signals & Sequences for Pattern Engine
        observed_signals = [ev.signal for ev in all_evidence]
        observed_signals.extend([ev.event_type.value for ev in timeline])
        event_sequence = [ev.event_type.value for ev in timeline]
        evidence_ids = [ev.id for ev in all_evidence]

        # Bridge: map EventType values to canonical evidence signal names so
        # pattern YAML files can reference meaningful signals rather than raw
        # event type strings. This is deterministic and requires no ML.
        _EVENT_TYPE_SIGNAL_MAP = {
            "PAYMENT_REQUEST": "FINANCIAL_CONTEXT",
            "PAYMENT_INTENT": "FINANCIAL_CONTEXT",
            "OTP_REQUEST": "OTP_INPUT_FORM_OBSERVED",
            "CREDENTIAL_REQUEST": "CREDENTIAL_FORM_OBSERVED",
            "URL_OPENED": "SUSPICIOUS_URL_PRESENT",
            "SCREEN_SHARE_REQUESTED": "REMOTE_ACCESS_DETECTED",
        }
        for ev in timeline:
            mapped = _EVENT_TYPE_SIGNAL_MAP.get(ev.event_type.value)
            if mapped and mapped not in observed_signals:
                observed_signals.append(mapped)

        # 7. Run Deterministic Pattern Engine V1
        pattern_match = self.pattern_engine.match_best_pattern(
            observed_signals=observed_signals,
            observed_events=event_sequence,
            evidence_ids=evidence_ids,
        )
        pattern_matches = [pattern_match] if pattern_match else []

        # 8. Run Evidence Fusion & Risk Engine V1
        risk_assessment = self.risk_engine.evaluate(
            incident=incident,
            events=timeline,
            evidence_list=all_evidence,
            pattern_matches=pattern_matches,
        )

        # 9. Evidence Confidence Calibration
        # If TinyFish or URL analysis was requested but unavailable, step down confidence
        if investigation_status.get("tinyfish") == "unavailable" and risk_assessment.confidence_level == ConfidenceLevel.HIGH:
            risk_assessment.confidence_level = ConfidenceLevel.MEDIUM
            risk_assessment.evidence_confidence = ConfidenceLevel.MEDIUM
            risk_assessment.reason_codes.append("[RC_WEB_INVESTIGATION_UNAVAILABLE] Web investigation timed out; confidence reduced.")

        # 10. Run Adaptive Intervention Engine
        payment_proximity = any(
            e.event_type in (EventType.PAYMENT_REQUEST, EventType.PAYMENT_INTENT)
            for e in timeline
        )
        current_stage = (
            pattern_match.current_stage
            if pattern_match
            else ("PAYMENT_REQUEST" if payment_proximity else "INITIAL_CONTACT")
        )

        decision = self.intervention_engine.decide_intervention(
            risk_score=risk_assessment.risk_score,
            evidence_confidence=risk_assessment.confidence_level,
            journey_stage=current_stage,
            payment_proximity=payment_proximity,
            pattern_match=pattern_match,
            counter_evidence=risk_assessment.counter_evidence,
            num_events=len(timeline),
        )

        # Consolidate transparent reason codes
        consolidated_reasons = []
        if pattern_match:
            consolidated_reasons.append(f"Pattern: {pattern_match.pattern_name} ({pattern_match.match_level.value})")
        consolidated_reasons.extend(risk_assessment.reason_codes[:4])
        consolidated_reasons.extend(decision.reasons[:2])

        # 11. Connect to Journey, ScamDNA, and Cross-Incident Correlation Ecosystem
        try:
            from services.dna_engine.service import scam_dna_service
            from services.correlation_engine.service import correlation_service
            scam_family = pattern_match.pattern_name.upper() if pattern_match else "UNKNOWN"
            ent_dicts = [
                {
                    "entity_type": e.entity_type.value if hasattr(e.entity_type, "value") else str(e.entity_type),
                    "canonical_value": getattr(e, "value", str(e)),
                }
                for e in entities
            ]
            dna = scam_dna_service.create_or_update_dna(
                incident_id=incident_id,
                entities=ent_dicts,
                family_hypotheses={scam_family: 1.0} if scam_family != "UNKNOWN" else {"UNKNOWN": 1.0},
            )
            correlation_service.register_incident(
                incident_id=incident_id,
                entities=ent_dicts,
                scam_family=scam_family,
                dna=dna,
                observed_at=incident.created_at,
            )
        except Exception as conn_err:
            logger.debug("Optional intelligence pipeline auto-index skipped: %s", conn_err)

        # 12. Run Unified Decision Engine (Phase 4A)
        tripartite = None
        try:
            from services.decision_engine.service import unified_decision_service
            sample_text = " ".join([str(getattr(e, "description", "") or "") for e in timeline])
            first_url = urls_to_investigate[0] if urls_to_investigate else None
            first_vpa = None
            first_phone = None
            for ent in entities:
                etype = getattr(getattr(ent, "entity_type", None), "value", str(getattr(ent, "entity_type", "")))
                if etype in ("UPI_HANDLE", "VPA"):
                    first_vpa = getattr(ent, "canonical_value", getattr(ent, "raw_value", None))
                elif etype == "PHONE":
                    first_phone = getattr(ent, "canonical_value", getattr(ent, "raw_value", None))

            tripartite = unified_decision_service.evaluate(
                incident_id=incident_id,
                message_text=sample_text if sample_text.strip() else None,
                url=first_url,
                vpa=first_vpa,
                phone=first_phone,
                journey_stage=current_stage,
                tactics_observed=[p.pattern_id for p in pattern_matches],
            )
        except Exception as dec_err:
            logger.debug("Tripartite decision evaluation skipped: %s", dec_err)

        return IncidentAssessment(
            incident_id=incident_id,
            incident=incident,
            timeline=timeline,
            investigation_status=investigation_status,
            entities=entities,
            evidence=all_evidence,
            pattern_matches=pattern_matches,
            risk_assessment=risk_assessment,
            intervention=decision,
            reason_codes=consolidated_reasons,
            tripartite_decision=tripartite,
        )

    @staticmethod
    def _extract_urls_from_events(events: List[Event]) -> List[str]:
        """Finds URLs embedded in event payloads or description text."""
        urls: List[str] = []
        url_pattern = re.compile(r"https?://[^\s<>\"']+")

        for ev in events:
            # Check payload dictionary
            payload = getattr(ev, "payload", {})
            if isinstance(payload, dict):
                if "url" in payload:
                    urls.append(str(payload["url"]).strip())
                for field in ("text", "description", "raw_url"):
                    if field in payload:
                        for m in url_pattern.findall(str(payload[field])):
                            clean = m.rstrip(".,;!?:")
                            if clean not in urls:
                                urls.append(clean)

            # Check direct description attribute if present
            desc = getattr(ev, "description", None)
            if desc and isinstance(desc, str):
                for m in url_pattern.findall(desc):
                    clean = m.rstrip(".,;!?:")
                    if clean not in urls:
                        urls.append(clean)

        return urls


# Global singleton instance
investigation_orchestrator = InvestigationOrchestrator()
