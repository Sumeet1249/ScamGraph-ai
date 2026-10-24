"""Scam Outbreak Radar Service (Phase 3C - Part C, Sections 31-45, 56-59).

Translates campaign dynamics and velocity into OutbreakSignal alerts,
generates geometric radar blips for the visual canvas across 3 concentric rings
(Critical inner, Surging middle, Emerging outer), produces network summaries,
and outputs privacy-safe consumer protection signals.
"""

from __future__ import annotations

import hashlib
import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.campaign import CampaignLifecycleState, CampaignVelocityState, ScamCampaign
from packages.schemas.radar import (
    ConsumerCampaignSignal,
    OutbreakSignal,
    OutbreakSignalType,
    RadarBlip,
    RadarSeverity,
    RadarSummary,
)
from services.campaign_engine.config import CampaignConfig, campaign_config

logger = logging.getLogger("campaign_engine.radar")


class ScamOutbreakRadarService:
    """Manages outbreak signals, analytical radar blip coordinates, and consumer alerts."""

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or campaign_config

    def generate_outbreak_signals(
        self,
        campaign: ScamCampaign,
        velocity_reasons: List[str],
    ) -> List[OutbreakSignal]:
        """Synthesizes granular OutbreakSignal events from campaign metrics."""
        signals: List[OutbreakSignal] = []

        # 1. High-risk outbreak signal
        if campaign.lifecycle_state == CampaignLifecycleState.OUTBREAK:
            signals.append(
                OutbreakSignal(
                    signal_id=f"sig_{uuid4().hex[:10]}",
                    campaign_id=campaign.campaign_id,
                    signal_type=OutbreakSignalType.HIGH_RISK_OUTBREAK,
                    severity=RadarSeverity.CRITICAL,
                    confidence=campaign.confidence,
                    current_velocity=campaign.current_velocity,
                    baseline_velocity=campaign.baseline_velocity,
                    acceleration=campaign.acceleration,
                    incident_count_window=campaign.incident_count,
                    unique_entity_count_window=campaign.unique_entity_count,
                    regions=campaign.regions,
                    channels=campaign.channels,
                    languages=campaign.languages,
                    strongest_evidence=[f"Velocity {campaign.growth_multiplier}x over baseline"],
                    reason_codes=["HIGH_RISK_OUTBREAK", "RAPID_INCIDENT_GROWTH"] + velocity_reasons,
                )
            )

        # 2. Resurgence signal
        if campaign.lifecycle_state == CampaignLifecycleState.RESURGING:
            signals.append(
                OutbreakSignal(
                    signal_id=f"sig_{uuid4().hex[:10]}",
                    campaign_id=campaign.campaign_id,
                    signal_type=OutbreakSignalType.RESURGENCE,
                    severity=RadarSeverity.HIGH,
                    confidence=campaign.confidence,
                    current_velocity=campaign.current_velocity,
                    baseline_velocity=campaign.baseline_velocity,
                    acceleration=campaign.acceleration,
                    incident_count_window=campaign.incident_count,
                    unique_entity_count_window=campaign.unique_entity_count,
                    regions=campaign.regions,
                    channels=campaign.channels,
                    languages=campaign.languages,
                    strongest_evidence=["Dormant campaign reappeared with new active incidents"],
                    reason_codes=["CAMPAIGN_RESURGENCE"],
                )
            )

        # 3. Rapid growth / Surging signal
        if campaign.lifecycle_state == CampaignLifecycleState.SURGING:
            signals.append(
                OutbreakSignal(
                    signal_id=f"sig_{uuid4().hex[:10]}",
                    campaign_id=campaign.campaign_id,
                    signal_type=OutbreakSignalType.RAPID_GROWTH,
                    severity=RadarSeverity.HIGH,
                    confidence=campaign.confidence,
                    current_velocity=campaign.current_velocity,
                    baseline_velocity=campaign.baseline_velocity,
                    acceleration=campaign.acceleration,
                    incident_count_window=campaign.incident_count,
                    unique_entity_count_window=campaign.unique_entity_count,
                    regions=campaign.regions,
                    channels=campaign.channels,
                    languages=campaign.languages,
                    strongest_evidence=[f"Accelerating report volume ({campaign.current_velocity}/day)"],
                    reason_codes=["RAPID_GROWTH"] + velocity_reasons,
                )
            )

        # 4. Emerging threat signal
        if campaign.lifecycle_state == CampaignLifecycleState.EMERGING:
            signals.append(
                OutbreakSignal(
                    signal_id=f"sig_{uuid4().hex[:10]}",
                    campaign_id=campaign.campaign_id,
                    signal_type=OutbreakSignalType.NEW_CAMPAIGN,
                    severity=RadarSeverity.WATCH,
                    confidence=campaign.confidence,
                    current_velocity=campaign.current_velocity,
                    baseline_velocity=campaign.baseline_velocity,
                    acceleration=campaign.acceleration,
                    incident_count_window=campaign.incident_count,
                    unique_entity_count_window=campaign.unique_entity_count,
                    regions=campaign.regions,
                    channels=campaign.channels,
                    languages=campaign.languages,
                    strongest_evidence=["Emerging incident cluster with cohesive ScamDNA pattern"],
                    reason_codes=["NEW_CAMPAIGN", "COHESIVE_SCAM_DNA"],
                )
            )

        # 5. Infrastructure / Payment rotation signals
        for mut in campaign.active_mutations:
            if "PAYMENT_ROTATION" in mut:
                signals.append(
                    OutbreakSignal(
                        signal_id=f"sig_{uuid4().hex[:10]}",
                        campaign_id=campaign.campaign_id,
                        signal_type=OutbreakSignalType.PAYMENT_REUSE_SPIKE,
                        severity=RadarSeverity.ELEVATED,
                        confidence=campaign.confidence,
                        incident_count_window=campaign.incident_count,
                        unique_entity_count_window=campaign.unique_entity_count,
                        strongest_evidence=[mut],
                        reason_codes=["REPEATED_PAYMENT_IDENTIFIER"],
                    )
                )
            elif "CHANNEL_MIGRATION" in mut:
                signals.append(
                    OutbreakSignal(
                        signal_id=f"sig_{uuid4().hex[:10]}",
                        campaign_id=campaign.campaign_id,
                        signal_type=OutbreakSignalType.CHANNEL_MIGRATION,
                        severity=RadarSeverity.WATCH,
                        confidence=campaign.confidence,
                        strongest_evidence=[mut],
                        reason_codes=["CHANNEL_MIGRATION"],
                    )
                )

        return signals

    def map_campaign_to_blip(self, campaign: ScamCampaign) -> RadarBlip:
        """Projects a ScamCampaign onto the 3-ring analytical radar canvas.
        
        RINGS:
        - Inner Ring (0.15 - 0.35 norm): CRITICAL / OUTBREAK
        - Middle Ring (0.45 - 0.65 norm): SURGING / HIGH
        - Outer Ring (0.75 - 0.95 norm): EMERGING / WATCH / ACTIVE
        
        Angle is deterministically derived from scam_family & campaign_id hash
        to maintain visual stability without fabricating real-world geography.
        """
        # Determine ring and severity
        if campaign.lifecycle_state == CampaignLifecycleState.OUTBREAK:
            ring = "CRITICAL"
            severity = RadarSeverity.CRITICAL
            base_radius = 0.25
        elif campaign.lifecycle_state in (CampaignLifecycleState.SURGING, CampaignLifecycleState.RESURGING):
            ring = "SURGING"
            severity = RadarSeverity.HIGH
            base_radius = 0.55
        elif campaign.lifecycle_state == CampaignLifecycleState.EMERGING:
            ring = "EMERGING"
            severity = RadarSeverity.WATCH
            base_radius = 0.85
        else:
            ring = "WATCH"
            severity = RadarSeverity.INFO
            base_radius = 0.80

        # Stable angle derivation
        hash_seed = f"{campaign.scam_family}:{campaign.campaign_id}"
        hash_val = int(hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:8], 16)
        angle_rad = (hash_val % 3600) / 3600.0 * 2.0 * math.pi

        # Small radius jitter within ring boundary based on velocity
        jitter = min(0.08, (hash_val % 100) / 1000.0)
        radius_norm = max(0.10, min(0.95, base_radius + jitter))

        # Visual encoding: Size reflects incident count (6 to 28 px)
        size = float(min(28, max(8, 8 + int(math.sqrt(campaign.incident_count) * 3))))

        # Visual encoding: Pulse speed reflects growth multiplier
        pulse_speed = round(min(4.0, max(0.5, campaign.growth_multiplier * 0.8)), 2)
        if campaign.lifecycle_state == CampaignLifecycleState.OUTBREAK:
            pulse_speed = max(2.5, pulse_speed)

        top_reason = "Stable pattern"
        if campaign.lifecycle_state == CampaignLifecycleState.OUTBREAK:
            top_reason = f"+{int(campaign.growth_multiplier * 100)}% surge over baseline"
        elif campaign.lifecycle_state == CampaignLifecycleState.RESURGING:
            top_reason = "Reappeared after 30+ days dormancy"
        elif campaign.lifecycle_state == CampaignLifecycleState.SURGING:
            top_reason = f"Accelerating report volume ({campaign.current_velocity}/day)"
        elif campaign.lifecycle_state == CampaignLifecycleState.EMERGING:
            top_reason = "Emerging threat pattern"

        return RadarBlip(
            blip_id=f"blip_{campaign.campaign_id}",
            campaign_id=campaign.campaign_id,
            title=campaign.title,
            scam_family=campaign.scam_family,
            ring=ring,
            radius_norm=round(radius_norm, 3),
            angle_rad=round(angle_rad, 3),
            size=size,
            pulse_speed=pulse_speed,
            severity=severity,
            confidence=campaign.confidence,
            incident_count=campaign.incident_count,
            growth_percent=round(campaign.growth_multiplier * 100, 1),
            is_resurgent=(campaign.lifecycle_state == CampaignLifecycleState.RESURGING),
            is_mutating=(campaign.mutation_count > 0),
            top_reason=top_reason,
        )

    def generate_radar_summary(
        self,
        campaigns: List[ScamCampaign],
        signals: List[OutbreakSignal],
        demo_mode: bool = False,
    ) -> RadarSummary:
        """Computes top-level network surveillance metrics across all campaigns."""
        active_count = 0
        emerging_count = 0
        surging_count = 0
        outbreak_count = 0
        critical_count = 0
        new_24h = 0

        for c in campaigns:
            if c.lifecycle_state in (
                CampaignLifecycleState.ACTIVE,
                CampaignLifecycleState.EMERGING,
                CampaignLifecycleState.SURGING,
                CampaignLifecycleState.OUTBREAK,
                CampaignLifecycleState.RESURGING,
            ):
                active_count += 1

            if c.lifecycle_state == CampaignLifecycleState.EMERGING:
                emerging_count += 1
            elif c.lifecycle_state == CampaignLifecycleState.SURGING:
                surging_count += 1
            elif c.lifecycle_state == CampaignLifecycleState.OUTBREAK:
                outbreak_count += 1
                critical_count += 1

            new_24h += int(c.current_velocity)

        high_risk_signals = sum(
            1 for s in signals if s.severity in (RadarSeverity.HIGH, RadarSeverity.CRITICAL)
        )

        return RadarSummary(
            active_campaigns=active_count,
            emerging_count=emerging_count,
            surging_count=surging_count,
            outbreak_count=outbreak_count,
            critical_count=critical_count,
            new_incidents_24h=new_24h,
            high_risk_signals=high_risk_signals,
            last_updated=datetime.now(timezone.utc),
            engine_version=self.config.engine_version,
            demo_mode=demo_mode,
        )

    def create_consumer_signal(
        self,
        matched_campaign: Optional[ScamCampaign],
    ) -> ConsumerCampaignSignal:
        """Produces a privacy-safe consumer warning contribution (Sections 56-59).
        
        Contains NO victim PII, internal graph identifiers, or analyst notes.
        """
        if not matched_campaign:
            return ConsumerCampaignSignal(
                campaign_matched=False,
                warning_message=None,
                urgency_level="LOW",
                confidence_level="LOW",
                pre_loss_warning=False,
            )

        family_readable = matched_campaign.scam_family.replace("_", " ").title()
        is_surge = matched_campaign.lifecycle_state in (
            CampaignLifecycleState.SURGING,
            CampaignLifecycleState.OUTBREAK,
        )

        msg = f"Active scam campaign detected matching this pattern ({family_readable})."
        if is_surge:
            msg += " Similar scam activity is currently surging across digital channels."

        urgency = "HIGH" if is_surge else "MEDIUM"
        confidence = "HIGH" if matched_campaign.confidence >= 0.80 else "MEDIUM"

        return ConsumerCampaignSignal(
            campaign_matched=True,
            warning_message=msg,
            urgency_level=urgency,
            confidence_level=confidence,
            pre_loss_warning=True,
            reason_summary=f"Matched active network cluster with {matched_campaign.incident_count} reports.",
        )
