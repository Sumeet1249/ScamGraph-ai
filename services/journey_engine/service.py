"""Central Orchestration Service for ScamGraph Journey Engine V1.

Coordinates event ingestion, chronological reconciliation, stage inference,
template matching, monetization tracking, early warnings, and consumer/analyst views.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from packages.schemas.journey import (
    ConsumerJourneyView,
    EarlyWarningCandidate,
    JourneyEvent,
    JourneyProgress,
    JourneyStage,
    LossStatus,
    MonetizationStatus,
    ScamJourney,
    StageObservation,
)
from services.journey_engine.early_warning import EarlyWarningEngine
from services.journey_engine.inference import StageInferenceEngine
from services.journey_engine.matcher import JourneyTemplateMatcher
from services.journey_engine.monetization import MonetizationTracker
from services.journey_engine.serializer import JourneySerializer
from services.journey_engine.temporal import TemporalReasoningEngine


class JourneyEngineService:
    """Production service orchestrating scam journey reconstruction and pre-loss early warning."""

    def __init__(
        self,
        inference_engine: Optional[StageInferenceEngine] = None,
        template_matcher: Optional[JourneyTemplateMatcher] = None,
        early_warning_engine: Optional[EarlyWarningEngine] = None,
    ):
        self.inference_engine = inference_engine or StageInferenceEngine()
        self.template_matcher = template_matcher or JourneyTemplateMatcher()
        self.early_warning_engine = early_warning_engine or EarlyWarningEngine()

    def create_journey(
        self,
        incident_id: str,
        events: Optional[List[JourneyEvent]] = None,
    ) -> ScamJourney:
        """Initializes a new ScamJourney, processing events if provided."""
        journey = ScamJourney(
            incident_id=incident_id,
            events=[],
            stage_observations=[],
            stage_history=[],
        )
        if events:
            for ev in events:
                journey = self.add_event(journey, ev)
        return journey

    def add_event(
        self,
        journey: ScamJourney,
        event: JourneyEvent,
    ) -> ScamJourney:
        """Incrementally ingests an event into the journey with strict idempotency and temporal ordering."""
        # 1. Idempotency Check (Section 54)
        if any(ev.event_id == event.event_id for ev in journey.events):
            return journey

        # 2. Append & Reconcile Temporal Ordering (Section 20-21)
        updated_events = list(journey.events)
        updated_events.append(event)
        ordered_events = TemporalReasoningEngine.order_events(updated_events)
        journey.events = ordered_events

        # 3. Incremental Stage Inference
        prior_stages = [so.stage for so in journey.stage_observations]
        prior_payment_count = sum(
            1 for ev in journey.events[:-1]
            if "PAYMENT_PRESSURE" in ev.tactics or "SEND_PAYMENT" in ev.requested_actions or "PAYMENT_REQUESTED" in ev.event_type
        )
        new_observations = self.inference_engine.infer_event_stages(
            event=event,
            prior_stages=prior_stages,
            prior_payment_count=prior_payment_count,
        )
        journey.stage_observations.extend(new_observations)

        # Update observed stage history maintaining chronological order
        observed_stages: List[JourneyStage] = []
        for so in journey.stage_observations:
            if so.stage not in observed_stages:
                observed_stages.append(so.stage)
        journey.stage_history = observed_stages

        # 4. Current Stage Determination
        curr_stage, conf, _ = self.inference_engine.determine_current_stage(journey.stage_observations)
        journey.current_stage = curr_stage
        journey.current_stage_confidence = conf

        # 5. Template Matching & Scam Family Alignment
        all_tactics: Set[str] = {t for ev in journey.events for t in ev.tactics}
        family, hypotheses, fam_conf = self.template_matcher.match_family(
            observed_stages=journey.stage_history,
            observed_tactics=all_tactics,
        )
        journey.scam_family = family
        journey.family_hypotheses = hypotheses

        # 6. Monetization & Loss Status Tracking
        m_status, l_status, boundary_id, boundary_ts = MonetizationTracker.evaluate_monetization_and_loss(
            events=journey.events,
            current_stage=curr_stage,
        )
        journey.monetization_status = m_status
        journey.loss_status = l_status
        if boundary_id and not journey.monetization_boundary_event_id:
            journey.monetization_boundary_event_id = boundary_id

        # 7. Early Warnings Generation
        warnings = self.early_warning_engine.generate_early_warnings(
            events=journey.events,
            current_stage=curr_stage,
            scam_family=family,
        )
        journey.early_warnings = warnings
        if warnings and not journey.first_actionable_warning_event_id:
            first_w = warnings[0]
            journey.first_actionable_warning_event_id = first_w.trigger_event_id
            journey.first_actionable_warning_timestamp = first_w.timestamp
            journey.pre_loss_warning_issued = MonetizationTracker.is_pre_loss_warning(
                warning_time=first_w.timestamp,
                boundary_time=boundary_ts,
                loss_time=journey.major_loss_timestamp,
            )

        # 8. Lead Time Calculation
        if journey.first_actionable_warning_timestamp and journey.major_loss_timestamp:
            journey.warning_lead_time_seconds = TemporalReasoningEngine.calculate_warning_lead_time(
                warning_time=journey.first_actionable_warning_timestamp,
                loss_time=journey.major_loss_timestamp,
            )

        # 9. Multi-Dimensional Progress Intelligence
        journey.progress = self.template_matcher.compute_progress(
            current_stage=curr_stage,
            observed_stages=journey.stage_history,
            scam_family=family,
        )

        # 10. Aggregations & Temporal Bounds
        journey.tactics = sorted(list(all_tactics))
        journey.channels = sorted(list({ev.channel for ev in journey.events if ev.channel != "UNKNOWN"}))
        journey.entities = sorted(list({eid for ev in journey.events for eid in ev.entities}))
        if journey.events:
            journey.first_observed_at = journey.events[0].timestamp
            journey.last_observed_at = journey.events[-1].timestamp

        return journey

    def recompute_journey(self, journey: ScamJourney) -> ScamJourney:
        """Performs full recomputation of the journey across all events."""
        recomputed = ScamJourney(
            incident_id=journey.incident_id,
            session_id=journey.session_id,
            major_loss_event_id=journey.major_loss_event_id,
            major_loss_timestamp=journey.major_loss_timestamp,
            events=[],
        )
        for ev in journey.events:
            recomputed = self.add_event(recomputed, ev)
        return recomputed

    def evaluate_prefix(
        self,
        events: List[JourneyEvent],
        prefix_k: int,
        incident_id: str = "prefix_eval",
    ) -> ScamJourney:
        """Evaluates prefix 1..k strictly without data leakage from events k+1..N (Section 86-87)."""
        prefix_slice = events[:prefix_k]
        journey = ScamJourney(incident_id=incident_id, events=[])
        for ev in prefix_slice:
            journey = self.add_event(journey, ev)
        return journey

    def serialize_consumer_view(self, journey: ScamJourney) -> ConsumerJourneyView:
        """Produces consumer plain-language progress representation."""
        return JourneySerializer.serialize_consumer_view(journey)

    def serialize_analyst_view(self, journey: ScamJourney) -> Dict[str, Any]:
        """Produces comprehensive forensic representation for analysts."""
        return JourneySerializer.serialize_analyst_view(journey)
