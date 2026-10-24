"""Incident Reconstruction and Loss Timeline Engine for ScamGraph Rescue (Phase 5B).

Enables progressive, forgiving reconstruction of what happened:
- Who contacted them, channel migration (e.g., Instagram -> Telegram/WhatsApp)
- Multiple sequential loss events (₹500 -> ₹5,000 -> ₹20,000)
- Preserves occurred_at vs recorded_at, supports approximate / order-only time
- Deduplicates identical submissions
- Detects secondary fee escalation ('pay tax to unlock') and recovery scam contact
- Integrates directly into canonical Journey events
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from packages.schemas.journey import JourneyEvent, JourneyStage
from packages.schemas.rescue import (
    LossEvent,
    LossStatus,
    RescueTimelineEvent,
    RescueTimelineEventType,
    TimeGranularity,
)


class IncidentReconstructionService:
    """Reconstructs the victim's encounter and loss sequence progressively."""

    def __init__(self):
        # In-memory storage for active sessions (backed by canonical Incident store)
        self._loss_events_by_incident: Dict[str, List[LossEvent]] = {}
        self._timeline_by_incident: Dict[str, List[RescueTimelineEvent]] = {}

    def record_loss_event(
        self,
        incident_id: str,
        amount: float,
        currency: str = "INR",
        payment_method: str = "UPI",
        recipient_identifier: Optional[str] = None,
        transaction_reference: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        time_granularity: TimeGranularity = TimeGranularity.EXACT,
        evidence_ids: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[LossEvent, bool]:
        """
        Records a loss event. Deduplicates identical payments.
        Returns (LossEvent, is_new).
        """
        now = datetime.now(timezone.utc)
        event_time = occurred_at or now

        # Tokenize / mask transaction reference if provided (e.g., preserve last 4 digits)
        masked_ref = None
        if transaction_reference:
            clean = transaction_reference.strip()
            if len(clean) > 4:
                masked_ref = f"UTR-****{clean[-4:]}"
            else:
                masked_ref = clean

        new_event = LossEvent(
            incident_id=incident_id,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            amount_confidence="USER_REPORTED",
            recipient_identifier=recipient_identifier,
            transaction_reference_tokenized=masked_ref,
            occurred_at=event_time,
            recorded_at=now,
            time_granularity=time_granularity,
            status=LossStatus.PAYMENT_COMPLETED if amount > 0 else LossStatus.NO_CONFIRMED_LOSS,
            evidence_ids=evidence_ids or [],
            metadata=metadata or {},
        )

        existing_events = self._loss_events_by_incident.setdefault(incident_id, [])
        new_key = new_event.deduplication_key()

        # Deduplication check
        for existing in existing_events:
            if existing.deduplication_key() == new_key:
                # Duplicate detected: return existing without double-counting
                return existing, False

        existing_events.append(new_event)

        # Add corresponding timeline event
        timeline_event = RescueTimelineEvent(
            event_type=RescueTimelineEventType.PAYMENT_SENT,
            title=f"Payment Sent ({currency} {amount:,.2f})",
            description=f"User transferred {currency} {amount:,.2f} via {payment_method} to {recipient_identifier or 'unknown recipient'}.",
            occurred_at=event_time,
            recorded_at=now,
            time_granularity=time_granularity,
            loss_event_id=new_event.loss_event_id,
            amount=amount,
            currency=currency,
            evidence_ids=evidence_ids or [],
            source="USER_REPORTED",
        )
        self.add_timeline_event(incident_id, timeline_event)

        return new_event, True

    def get_loss_events(self, incident_id: str) -> List[LossEvent]:
        """Returns all recorded loss events sorted chronologically."""
        events = self._loss_events_by_incident.get(incident_id, [])
        return sorted(events, key=lambda e: e.occurred_at)

    def calculate_reported_loss(self, incident_id: str) -> Tuple[float, str, int]:
        """
        Calculates total user-reported financial loss.
        Returns (total_amount, currency, count).
        """
        events = self.get_loss_events(incident_id)
        if not events:
            return 0.0, "INR", 0
        total = sum(e.amount for e in events)
        currency = events[0].currency if events else "INR"
        return round(total, 2), currency, len(events)

    def add_timeline_event(self, incident_id: str, event: RescueTimelineEvent) -> None:
        """Appends a timeline event, ensuring chronological ordering."""
        events = self._timeline_by_incident.setdefault(incident_id, [])
        # Check duplicate
        for ex in events:
            if ex.event_type == event.event_type and ex.title == event.title and ex.occurred_at == event.occurred_at:
                return
        events.append(event)
        events.sort(key=lambda e: e.occurred_at)

    def get_timeline(self, incident_id: str) -> List[RescueTimelineEvent]:
        """Retrieves ordered timeline for the rescue case."""
        return self._timeline_by_incident.get(incident_id, [])

    def map_to_journey_events(self, incident_id: str) -> List[JourneyEvent]:
        """Converts Rescue timeline events into canonical JourneyEngine events."""
        journey_events: List[JourneyEvent] = []
        timeline = self.get_timeline(incident_id)

        type_to_stage = {
            RescueTimelineEventType.SCAM_CONTACT: JourneyStage.CONTACT,
            RescueTimelineEventType.PLATFORM_MOVE: JourneyStage.PLATFORM_MIGRATION,
            RescueTimelineEventType.PAYMENT_REQUEST: JourneyStage.INITIAL_PAYMENT,
            RescueTimelineEventType.PAYMENT_SENT: JourneyStage.INITIAL_PAYMENT,
            RescueTimelineEventType.CREDENTIAL_SHARED: JourneyStage.CREDENTIAL_REQUEST,
            RescueTimelineEventType.REMOTE_ACCESS_GRANTED: JourneyStage.CREDENTIAL_REQUEST,
            RescueTimelineEventType.LOSS_DISCOVERED: JourneyStage.WITHDRAWAL_BLOCK,
            RescueTimelineEventType.ADDITIONAL_SCAM_CONTACT: JourneyStage.PAYMENT_ESCALATION,
            RescueTimelineEventType.RECOVERY_SCAM_CONTACT: JourneyStage.RECOVERY_FEE,
        }

        # Track multiple payments to classify payment escalation
        payment_count = 0
        for idx, te in enumerate(timeline):
            stage = type_to_stage.get(te.event_type, JourneyStage.UNKNOWN)
            if te.event_type == RescueTimelineEventType.PAYMENT_SENT:
                payment_count += 1
                if payment_count > 1:
                    stage = JourneyStage.PAYMENT_ESCALATION

            jev = JourneyEvent(
                sequence_number=idx,
                event_type=te.event_type.value,
                timestamp=te.occurred_at,
                channel="RESCUE_TIMELINE",
                speaker_role="VICTIM" if "SENT" in te.event_type.value or "SHARED" in te.event_type.value else "SCAMMER",
                stage_candidates=[stage] if stage != JourneyStage.UNKNOWN else [],
                evidence_ids=te.evidence_ids,
                timestamp_confidence=te.time_granularity.value,
                metadata={"title": te.title, "description": te.description, "amount": te.amount},
            )
            journey_events.append(jev)

        return journey_events


incident_reconstruction_service = IncidentReconstructionService()
