"""Rescue Intelligence Flywheel & Prevention Feedback Loop (Phase 5B).

Closes the learning loop:
Post-Loss Evidence -> Canonical Entities -> Journey Recomputation -> ScamDNA ->
Knowledge Graph Projection -> Correlation Engine -> Campaign Candidate -> Unified Reassessment.

Enforces strict Pre-Loss vs Post-Loss Isolation:
Pre-loss prevention metrics MUST NOT leak post-loss evidence.
Generates MissedPreventionReview without future data leakage.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from packages.schemas.common import generate_id
from packages.schemas.entity import Entity, EntityType, TrustLevel
from packages.schemas.incident import Incident
from packages.schemas.journey import JourneyStage
from packages.schemas.rescue import (
    LossEvent,
    MissedPreventionReview,
    RescueTimelineEvent,
)


class RescueIntelligenceFeedbackLoop:
    """Transforms post-loss rescue evidence into network intelligence while maintaining evaluation integrity."""

    def __init__(self):
        self._reviews: Dict[str, MissedPreventionReview] = {}

    def _mask_value(self, val: str) -> str:
        if "@" in val:
            parts = val.split("@", 1)
            return f"{parts[0][:1]}***@{parts[1]}"
        elif len(val) > 4:
            return f"******{val[-4:]}"
        return "***"

    def _hash_value(self, val: str) -> str:
        import hashlib
        return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()

    def extract_rescue_entities(
        self,
        loss_events: List[LossEvent],
        contact_entities: Optional[List[Dict[str, Any]]] = None,
        urls: Optional[List[str]] = None,
    ) -> List[Entity]:
        """Extracts canonical Entity objects from post-loss evidence."""
        extracted: List[Entity] = []

        # 1. From loss events (e.g., UPI VPAs, bank accounts)
        for le in loss_events:
            if le.recipient_identifier:
                ident = le.recipient_identifier.strip()
                ent_type = EntityType.UPI_VPA if "@" in ident else EntityType.BANK_ACCOUNT_TOKEN
                ent = Entity(
                    entity_id=generate_id("ent"),
                    canonical_value=ident,
                    display_value=self._mask_value(ident),
                    masked_value=self._mask_value(ident),
                    canonical_hash=self._hash_value(ident),
                    entity_type=ent_type,
                    source_context={"origin": "RESCUE_LOSS_EVENT", "payment_method": le.payment_method},
                    metadata={"reported_loss_amount": le.amount, "currency": le.currency},
                )
                extracted.append(ent)

        # 2. From contact entities (phone, telegram, email)
        if contact_entities:
            for c in contact_entities:
                val = c.get("value", "").strip()
                t_str = c.get("type", "PHONE").upper()
                if not val:
                    continue
                if "PHONE" in t_str:
                    e_type = EntityType.PHONE
                elif "TELEGRAM" in t_str or "HANDLE" in t_str:
                    e_type = EntityType.SOCIAL_ACCOUNT
                elif "EMAIL" in t_str:
                    e_type = EntityType.EMAIL
                else:
                    e_type = EntityType.ORGANIZATION

                ent = Entity(
                    entity_id=generate_id("ent"),
                    canonical_value=val,
                    display_value=self._mask_value(val),
                    masked_value=self._mask_value(val),
                    canonical_hash=self._hash_value(val),
                    entity_type=e_type,
                    source_context={"origin": "RESCUE_CONTACT_IDENTIFIER"},
                    metadata={"claimed_role": c.get("role", "suspect")},
                )
                extracted.append(ent)

        # 3. From suspect URLs
        if urls:
            for u in urls:
                if u.strip():
                    ent = Entity(
                        entity_id=generate_id("ent"),
                        canonical_value=u.strip(),
                        display_value=u.strip(),
                        masked_value=u.strip(),
                        canonical_hash=self._hash_value(u.strip()),
                        entity_type=EntityType.DOMAIN,
                        source_context={"origin": "RESCUE_SUSPECT_URL"},
                    )
                    extracted.append(ent)

        return extracted

    def determine_loss_boundary(self, loss_events: List[LossEvent]) -> Optional[datetime]:
        """Identifies the temporal boundary of the first financial loss event."""
        if not loss_events:
            return None
        return min(le.occurred_at for le in loss_events)

    def partition_evidence(
        self,
        evidence_timeline: List[Tuple[str, datetime]],  # (evidence_id, occurred_at)
        loss_boundary: Optional[datetime],
    ) -> Tuple[List[str], List[str]]:
        """
        Partitions evidence into pre-loss and post-loss buckets based on the loss boundary.
        Ensures strict non-leakage for historical evaluation.
        """
        if not loss_boundary:
            # No loss recorded; all evidence is pre-loss
            return [eid for eid, _ in evidence_timeline], []

        pre_loss: List[str] = []
        post_loss: List[str] = []

        for eid, ts in evidence_timeline:
            if ts <= loss_boundary:
                pre_loss.append(eid)
            else:
                post_loss.append(eid)

        return pre_loss, post_loss

    def generate_missed_prevention_review(
        self,
        incident_id: str,
        loss_events: List[LossEvent],
        pre_loss_evidence: List[str],
        post_loss_evidence: List[str],
        had_preloss_check: bool = False,
        preloss_warning_shown: bool = False,
        preloss_risk_level: Optional[str] = None,
    ) -> MissedPreventionReview:
        """
        Conducts post-incident audit to see why loss occurred and what could be learned.
        STRICT: Uses ONLY pre_loss_evidence to evaluate pre-loss warning capability.
        """
        boundary = self.determine_loss_boundary(loss_events) or datetime.now(timezone.utc)

        if not had_preloss_check:
            category = "NO_PRELOSS_CHECK"
            notes = "User only interacted with ScamGraph after payment occurred ('I already paid')."
        elif preloss_warning_shown:
            category = "USER_CONTINUED_AFTER_WARNING"
            notes = "ScamGraph displayed pre-loss intervention, but victim proceeded under severe adversarial pressure."
        elif len(pre_loss_evidence) == 0:
            category = "INSUFFICIENT_EVIDENCE"
            notes = "No pre-loss indicators were submitted prior to payment execution."
        elif preloss_risk_level in ("LOW", "UNKNOWN"):
            category = "MODEL_MISS"
            notes = "Pre-loss analysis underestimated risk due to stealth groomer tactics."
        else:
            category = "JOURNEY_MISS"
            notes = "Journey progression did not trigger payment proximity block in time."

        review = MissedPreventionReview(
            incident_id=incident_id,
            loss_boundary=boundary,
            pre_loss_signals_count=len(pre_loss_evidence),
            post_loss_signals_count=len(post_loss_evidence),
            earliest_possible_warning_stage="INITIAL_CONTACT",
            actual_warning_stage="POST_LOSS_RESCUE",
            failure_category=category,
            pre_loss_evidence_ids=pre_loss_evidence,
            post_loss_evidence_ids=post_loss_evidence,
            notes=notes,
        )
        self._reviews[incident_id] = review
        return review

    def get_review(self, incident_id: str) -> Optional[MissedPreventionReview]:
        return self._reviews.get(incident_id)


rescue_intelligence_feedback = RescueIntelligenceFeedbackLoop()
