"""Financial Monetization & Pre-Loss Boundary Intelligence for ScamGraph AI V2.

Tracks monetization progression, identifies the exact monetization boundary,
categorizes victim loss status, and determines whether actionable warnings preceded financial loss.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from packages.schemas.journey import (
    JourneyEvent,
    JourneyStage,
    LossStatus,
    MonetizationStatus,
)


class MonetizationTracker:
    """Evaluates monetization boundaries, payment sequences, and pre-loss early warning effectiveness."""

    @staticmethod
    def evaluate_monetization_and_loss(
        events: List[JourneyEvent],
        current_stage: JourneyStage,
    ) -> Tuple[MonetizationStatus, LossStatus, Optional[str], Optional[datetime]]:
        """Evaluates overall monetization status, loss state, and monetization boundary.
        
        Monetization Boundary: The first event where the interaction attempts to extract
        money, credentials with direct financial impact, or remote financial access.
        """
        if not events:
            return MonetizationStatus.NO_PAYMENT_SIGNAL, LossStatus.NO_KNOWN_LOSS, None, None

        payment_events: List[JourneyEvent] = []
        confirmed_loss_events: List[JourneyEvent] = []
        boundary_event_id: Optional[str] = None
        boundary_timestamp: Optional[datetime] = None

        for ev in events:
            tactics = set(ev.tactics)
            actions = set(ev.requested_actions)
            ev_type = ev.event_type.upper()
            pay_ctx = ev.payment_context or {}

            # Detect Monetization Boundary: first extraction attempt
            is_extraction_attempt = (
                "PAYMENT_PRESSURE" in tactics
                or "CREDENTIAL_PRESSURE" in tactics
                or "REMOTE_ACCESS_PRESSURE" in tactics
                or "SEND_PAYMENT" in actions
                or "SHARE_OTP" in actions
                or "INSTALL_APP" in actions
                or "PAYMENT_REQUESTED" in ev_type
                or "OTP_REQUESTED" in ev_type
                or ev.stage_candidates in ([JourneyStage.INITIAL_PAYMENT], [JourneyStage.CREDENTIAL_REQUEST])
            )

            if is_extraction_attempt and boundary_event_id is None:
                boundary_event_id = ev.event_id
                boundary_timestamp = ev.timestamp

            # Payment observations
            if (
                "PAYMENT_PRESSURE" in tactics
                or "SEND_PAYMENT" in actions
                or "APPROVE_UPI_REQUEST" in actions
                or "PAY_FEE" in actions
                or "PAYMENT_REQUESTED" in ev_type
                or "COLLECT_REQUEST_RECEIVED" in ev_type
            ):
                payment_events.append(ev)

            # Check confirmed user loss reported
            if (
                pay_ctx.get("payment_confirmed", False)
                or ev_type == "PAYMENT_COMPLETED"
                or pay_ctx.get("loss_amount_inr", 0.0) > 0.0
            ):
                confirmed_loss_events.append(ev)

        # 1. Determine Monetization Status
        num_payments = len(payment_events)
        if num_payments == 0:
            monetization_status = MonetizationStatus.NO_PAYMENT_SIGNAL
        elif num_payments == 1:
            if confirmed_loss_events:
                monetization_status = MonetizationStatus.PAYMENT_CONFIRMED
            else:
                monetization_status = MonetizationStatus.PAYMENT_REQUESTED
        else:
            if confirmed_loss_events:
                monetization_status = MonetizationStatus.MULTIPLE_PAYMENTS
            else:
                monetization_status = MonetizationStatus.ADDITIONAL_PAYMENT_REQUESTED

        # 2. Determine Loss Status
        if confirmed_loss_events:
            loss_status = LossStatus.CONFIRMED_USER_REPORTED_LOSS
        elif num_payments >= 1 or current_stage in (JourneyStage.PAYMENT_ESCALATION, JourneyStage.WITHDRAWAL_BLOCK):
            loss_status = LossStatus.AT_RISK
        elif boundary_event_id is not None:
            loss_status = LossStatus.POSSIBLE_LOSS
        else:
            loss_status = LossStatus.NO_KNOWN_LOSS

        return monetization_status, loss_status, boundary_event_id, boundary_timestamp

    @staticmethod
    def is_pre_loss_warning(
        warning_time: Optional[datetime],
        boundary_time: Optional[datetime],
        loss_time: Optional[datetime],
    ) -> bool:
        """Determines whether an actionable warning was issued strictly before financial loss occurred.
        
        Evaluated against major loss timestamp if known, otherwise against monetization boundary.
        """
        if not warning_time:
            return False

        effective_limit = loss_time or boundary_time
        if not effective_limit:
            # If no loss or boundary has occurred yet, warning is by definition pre-loss!
            return True

        # Ensure timezone awareness
        w = warning_time if warning_time.tzinfo else warning_time.replace(tzinfo=timezone.utc)
        lim = effective_limit if effective_limit.tzinfo else effective_limit.replace(tzinfo=timezone.utc)

        return w <= lim
