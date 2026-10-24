"""Campaign Velocity Engine (Phase 3C - Sections 17-21, 71-76).

Calculates normalized velocity, acceleration, and growth multipliers relative to
a rolling 14-day baseline. Enforces ingestion spike resistance (via observed_at)
and duplicate report deduplication to prevent false outbreaks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from packages.schemas.campaign import CampaignVelocityState, ScamCampaign
from packages.schemas.radar import OutbreakSignalType, RadarSeverity
from services.campaign_engine.config import CampaignConfig, campaign_config

logger = logging.getLogger("campaign_engine.velocity")


class CampaignVelocityEngine:
    """Computes robust velocity metrics and flags emerging / surging outbreaks."""

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or campaign_config

    def calculate_velocity(
        self,
        campaign: ScamCampaign,
        incidents: List[Dict[str, Any]],
        current_time: Optional[datetime] = None,
    ) -> Tuple[CampaignVelocityState, float, float, float, float, List[str]]:
        """Calculates velocity state, current velocity, baseline, growth multiplier, acceleration,
        and reason codes for a given campaign and its incident timeline.
        
        CRITICAL RULES:
        1. Uses `observed_at` to prevent bulk-import ingestion spikes from triggering fake outbreaks.
        2. Deduplicates reports using report hash/content before counting.
        """
        now = current_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Step 1: Deduplicate reports (Section 76)
        seen_fingerprints: Set[str] = set()
        deduped_incidents: List[Dict[str, Any]] = []
        for inc in incidents:
            fp = inc.get("fingerprint") or inc.get("content_hash") or inc.get("id")
            if fp and fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                deduped_incidents.append(inc)

        # Step 2: Filter by observed_at time (Section 74)
        one_day_ago = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        baseline_start = now - timedelta(days=self.config.baseline_window_days)

        window_24h_count = 0
        window_prev_24h_count = 0
        baseline_total_count = 0

        for inc in deduped_incidents:
            obs = inc.get("observed_at")
            if not obs:
                obs = inc.get("created_at") or now
            if isinstance(obs, str):
                try:
                    obs = datetime.fromisoformat(obs.replace("Z", "+00:00"))
                except Exception:
                    obs = now
            if obs.tzinfo is None:
                obs = obs.replace(tzinfo=timezone.utc)

            if obs > one_day_ago and obs <= now:
                window_24h_count += 1
            elif obs > two_days_ago and obs <= one_day_ago:
                window_prev_24h_count += 1

            if obs >= baseline_start and obs <= one_day_ago:
                baseline_total_count += 1

        # Current velocity (reports/day)
        current_velocity = float(window_24h_count)

        # Historical baseline: average daily volume over the baseline window (excluding last 24h)
        baseline_days = max(1.0, float(self.config.baseline_window_days - 1))
        baseline_velocity = baseline_total_count / baseline_days

        # Normalized growth multiplier
        effective_baseline = max(0.5, baseline_velocity)
        growth_multiplier = round(current_velocity / effective_baseline, 2)

        # Acceleration: rate of change between current 24h and previous 24h
        acceleration = float(window_24h_count - window_prev_24h_count)

        # Determine Velocity State with multi-factor evidence (Section 19-21)
        reasons: List[str] = []
        state = CampaignVelocityState.NORMAL

        # Low-volume emerging threat detection (Section 21)
        is_emerging_threat = (
            baseline_velocity < 1.0
            and window_24h_count >= self.config.emerging_min_volume_24h
            and campaign.confidence >= 0.70
        )
        if is_emerging_threat:
            reasons.append("LOW_VOLUME_EMERGING_THREAT")

        # Outbreak determination (Section 20: requires high multiplier + minimum volume)
        if (
            growth_multiplier >= self.config.outbreak_growth_multiplier
            and window_24h_count >= self.config.outbreak_min_volume_24h
            and campaign.confidence >= 0.75
        ):
            state = CampaignVelocityState.OUTBREAK
            reasons.append("ABNORMAL_SURGE_OVER_BASELINE")
            reasons.append(f"OUTBREAK_VOLUME_{window_24h_count}_REPORTS_24H")
        elif growth_multiplier >= self.config.surging_growth_multiplier and window_24h_count >= 5:
            state = CampaignVelocityState.SURGING
            reasons.append(f"GROWTH_MULTIPLIER_{growth_multiplier}X")
        elif (growth_multiplier >= self.config.rising_growth_multiplier and window_24h_count >= 2) or is_emerging_threat:
            state = CampaignVelocityState.RISING
            reasons.append("ACCELERATING_REPORT_VOLUME")

        return state, current_velocity, baseline_velocity, growth_multiplier, acceleration, reasons
