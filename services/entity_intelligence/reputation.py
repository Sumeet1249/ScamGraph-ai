"""Evidence-Aware Reputation and Temporal Decay Scoring for Entity Intelligence.

Rules (Prompt 6):
1. Do NOT create one permanent static "scam score".
2. Separate ENTITY REPUTATION from INCIDENT RISK.
3. Incorporate source reliability weighting (AUTHORITATIVE, HIGH, MEDIUM, LOW, UNKNOWN).
4. Apply configurable temporal decay: older observations decay in influence over time.
5. Support counter-evidence: evidence can support or contradict suspicion.
6. Produce nuanced TrustLevel (KNOWN_LEGITIMATE to HIGH_RISK, never binary).
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from packages.schemas.entity import (
    Entity,
    EntityObservation,
    EntityVerificationState,
    TrustAssessment,
    TrustLevel,
)

# Source reliability weights (Prompt 6: Do not treat crowdsourced reports as authoritative)
SOURCE_RELIABILITY_WEIGHTS: Dict[str, float] = {
    "AUTHORITATIVE": 1.0,     # Bank/DoT/I4C official feeds, verified registries
    "HIGH": 0.8,              # Verified analyst investigation, high-confidence honeypots
    "MEDIUM": 0.5,            # Telemetry, automated ML extraction with corroboration
    "LOW": 0.2,               # Single unvetted crowdsourced report
    "UNKNOWN": 0.1,           # Unverified third-party scraping
}


class EntityReputationEngine:
    """Calculates evidence-backed reputation and trust assessments."""

    def __init__(self, decay_half_life_days: float = 180.0):
        self.decay_half_life_days = decay_half_life_days

    def calculate_temporal_weight(self, observation_time: datetime, current_time: Optional[datetime] = None) -> float:
        """Calculates exponential decay weight based on age of observation."""
        now = current_time or datetime.now(timezone.utc)
        if observation_time.tzinfo is None:
            observation_time = observation_time.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        age_days = max(0.0, (now - observation_time).total_seconds() / 86400.0)
        # Exponential decay: w = 2^(-age / half_life)
        weight = math.pow(2.0, -age_days / self.decay_half_life_days)
        return round(max(0.05, weight), 4)

    def detect_observation_burst(
        self,
        observations: List[EntityObservation],
        window_hours: float = 48.0,
        threshold_count: int = 5,
    ) -> Dict[str, Any]:
        """Detects sudden velocity spikes of an entity appearing across independent incidents (Prompt 6)."""
        if len(observations) < threshold_count:
            return {"is_burst": False, "recent_count": len(observations), "velocity": 0.0}

        now = datetime.now(timezone.utc)
        recent_obs = []
        for o in observations:
            obs_dt = o.observed_at.replace(tzinfo=timezone.utc) if o.observed_at.tzinfo is None else o.observed_at
            if (now - obs_dt).total_seconds() <= window_hours * 3600.0:
                recent_obs.append(o)

        unique_incidents = len(set(o.incident_id for o in recent_obs))
        is_burst = unique_incidents >= threshold_count

        return {
            "is_burst": is_burst,
            "recent_count": len(recent_obs),
            "unique_incidents": unique_incidents,
            "window_hours": window_hours,
            "signal": "OBSERVATION_BURST" if is_burst else "NORMAL_VELOCITY",
        }

    def assess_trust(
        self,
        entity: Entity,
        observations: Optional[List[EntityObservation]] = None,
        is_officially_verified: bool = False,
    ) -> TrustAssessment:
        """Computes comprehensive TrustAssessment based on corroboration, counter-evidence, and decay."""
        obs = observations or []
        now = datetime.now(timezone.utc)

        # 1. Authoritative Override
        if is_officially_verified or entity.verification_state == EntityVerificationState.VERIFIED_LEGITIMATE:
            return TrustAssessment(
                entity_id=entity.entity_id,
                assessment=TrustLevel.KNOWN_LEGITIMATE,
                confidence=1.0,
                supporting_evidence_count=entity.supporting_evidence_count,
                contradicting_evidence_count=entity.contradicting_evidence_count,
                reputation_score=0.01,
                decay_applied=False,
                freshness_status="FRESH",
                assessed_at=now,
                summary_reason="Entity verified against authoritative government or banking directory.",
            )

        if entity.verification_state == EntityVerificationState.DISPUTED:
            return TrustAssessment(
                entity_id=entity.entity_id,
                assessment=TrustLevel.DISPUTED,
                confidence=0.75,
                supporting_evidence_count=entity.supporting_evidence_count,
                contradicting_evidence_count=entity.contradicting_evidence_count,
                reputation_score=0.50,
                decay_applied=False,
                freshness_status="FRESH",
                assessed_at=now,
                summary_reason="Entity reputation is actively disputed and under governance review.",
            )

        # 2. Evidence balance
        sup_cnt = entity.supporting_evidence_count
        con_cnt = entity.contradicting_evidence_count
        inc_cnt = entity.incident_count

        # Apply recency decay if last seen was long ago
        decay_weight = self.calculate_temporal_weight(entity.last_seen, now)
        effective_sup = sup_cnt * decay_weight

        # Check burst
        burst_info = self.detect_observation_burst(obs)
        if burst_info["is_burst"]:
            effective_sup *= 1.35  # Velocity multiplier

        # Compute raw reputation score [0.0 = completely safe, 1.0 = highly risky]
        total_evidence = effective_sup + con_cnt
        if total_evidence == 0:
            if inc_cnt <= 1:
                return TrustAssessment(
                    entity_id=entity.entity_id,
                    assessment=TrustLevel.UNKNOWN,
                    confidence=0.30,
                    supporting_evidence_count=0,
                    contradicting_evidence_count=0,
                    reputation_score=0.50,
                    decay_applied=False,
                    freshness_status="NEW_ENTITY",
                    assessed_at=now,
                    summary_reason="First observed identifier; insufficient historical evidence.",
                )
            rep_score = 0.50
            confidence = 0.40
        else:
            rep_score = effective_sup / (effective_sup + con_cnt + 1.0)
            # Confidence scales with total observations and diverse incidents
            confidence = min(0.95, 0.40 + (0.10 * math.log1p(inc_cnt + total_evidence)))

        # Map to TrustLevel
        if rep_score >= 0.75 and inc_cnt >= 2:
            level = TrustLevel.HIGH_RISK
            reason = f"Corroborated across {inc_cnt} incidents with {sup_cnt} supporting scam evidence signals."
        elif rep_score >= 0.55 or inc_cnt >= 2:
            level = TrustLevel.SUSPICIOUS
            reason = f"Observed in {inc_cnt} incidents with multiple suspicious context sightings."
        elif rep_score >= 0.35:
            level = TrustLevel.CAUTION
            reason = "Limited suspicious sightings; recommend caution and independent verification."
        elif con_cnt > sup_cnt:
            level = TrustLevel.LIKELY_LEGITIMATE
            reason = f"Predominantly counter-evidence observed ({con_cnt} legitimate signals)."
        else:
            level = TrustLevel.UNKNOWN
            reason = "Insufficient evidence to establish clear reputation."

        return TrustAssessment(
            entity_id=entity.entity_id,
            assessment=level,
            confidence=round(confidence, 3),
            supporting_evidence_count=sup_cnt,
            contradicting_evidence_count=con_cnt,
            reputation_score=round(rep_score, 3),
            decay_applied=decay_weight < 0.90,
            freshness_status="RESURGING" if burst_info["is_burst"] else "ACTIVE",
            assessed_at=now,
            summary_reason=reason,
        )
