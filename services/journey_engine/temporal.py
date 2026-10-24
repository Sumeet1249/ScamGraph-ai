"""Temporal Reasoning & Out-of-Order Sequence Alignment for ScamGraph AI V2.

Reconstructs chronological event streams using evidence timestamps, handles delayed or out-of-order
evidence submissions, validates sequence monotonicity, and computes warning lead times.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from packages.schemas.journey import JourneyEvent


class TemporalReasoningEngine:
    """Manages event ordering, timestamp reconciliation, and warning lead-time calculations."""

    @staticmethod
    def order_events(events: List[JourneyEvent]) -> List[JourneyEvent]:
        """Sorts events chronologically using evidence timestamp, sequence number, and fallback order.
        
        Handles out-of-order evidence ingestion (e.g. user uploads payment screenshot today,
        and earlier WhatsApp transcript tomorrow).
        """
        if not events:
            return []

        # Sort key: (timestamp, sequence_number)
        # For events with identical timestamps, sequence_number breaks ties
        sorted_events = sorted(
            events,
            key=lambda ev: (
                ev.timestamp if ev.timestamp.tzinfo else ev.timestamp.replace(tzinfo=timezone.utc),
                ev.sequence_number,
            )
        )

        # Reassign sequence numbers to maintain monotonic integer index
        for idx, ev in enumerate(sorted_events):
            ev.sequence_number = idx

        return sorted_events

    @staticmethod
    def calculate_warning_lead_time(
        warning_time: Optional[datetime],
        loss_time: Optional[datetime],
        warning_confidence: str = "EXACT",
        loss_confidence: str = "EXACT",
    ) -> Optional[float]:
        """Calculates warning lead time in seconds: T_loss - T_warning.
        
        Enforces Section 43 rule: Never calculate when timestamp evidence is insufficient
        (e.g., ORDER_ONLY or UNKNOWN).
        """
        if not warning_time or not loss_time:
            return None

        # Disallow calculation on synthetic order-only timestamps
        if warning_confidence in ("ORDER_ONLY", "UNKNOWN") or loss_confidence in ("ORDER_ONLY", "UNKNOWN"):
            return None

        # Ensure timezone awareness
        w_time = warning_time if warning_time.tzinfo else warning_time.replace(tzinfo=timezone.utc)
        l_time = loss_time if loss_time.tzinfo else loss_time.replace(tzinfo=timezone.utc)

        lead_seconds = (l_time - w_time).total_seconds()
        return round(lead_seconds, 2)
