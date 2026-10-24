"""Scam Outbreak Radar Schemas (Phase 3C - Part C, Sections 31-35, 56-58, 78).

Provides typed models for outbreak signals, radar blip geometric projections,
radar summary metrics, and consumer network warning signals.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OutbreakSignalType(str, Enum):
    """Categorical trigger for outbreak radar signals."""
    NEW_CAMPAIGN = "NEW_CAMPAIGN"
    RAPID_GROWTH = "RAPID_GROWTH"
    ENTITY_REUSE_SPIKE = "ENTITY_REUSE_SPIKE"
    PAYMENT_REUSE_SPIKE = "PAYMENT_REUSE_SPIKE"
    INFRASTRUCTURE_ROTATION = "INFRASTRUCTURE_ROTATION"
    CHANNEL_MIGRATION = "CHANNEL_MIGRATION"
    DNA_MUTATION = "DNA_MUTATION"
    REGIONAL_EXPANSION = "REGIONAL_EXPANSION"
    RESURGENCE = "RESURGENCE"
    HIGH_RISK_OUTBREAK = "HIGH_RISK_OUTBREAK"


class RadarSeverity(str, Enum):
    """Urgency / severity band for radar visualization and alerts."""
    INFO = "INFO"
    WATCH = "WATCH"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OutbreakSignal(BaseModel):
    """Specific anomalous event or velocity escalation emitted by the Outbreak Radar."""
    signal_id: str
    campaign_id: str
    signal_type: OutbreakSignalType
    severity: RadarSeverity = RadarSeverity.WATCH
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)

    current_velocity: float = 0.0
    baseline_velocity: float = 0.0
    acceleration: float = 0.0

    incident_count_window: int = 0
    unique_entity_count_window: int = 0

    regions: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    strongest_evidence: List[str] = Field(default_factory=list)
    reason_codes: List[str] = Field(default_factory=list)

    first_detected: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    review_state: str = "UNREVIEWED"
    engine_version: str = "3.3.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RadarBlip(BaseModel):
    """Geometric and analytical representation of a campaign on the Outbreak Radar."""
    blip_id: str
    campaign_id: str
    title: str
    scam_family: str
    
    # Radar geometry (ring: CRITICAL=inner, SURGING=middle, EMERGING=outer)
    ring: str  # "CRITICAL", "SURGING", "EMERGING", "WATCH"
    radius_norm: float = Field(default=0.5, ge=0.0, le=1.0)  # 0.0=center, 1.0=perimeter
    angle_rad: float = Field(default=0.0, ge=0.0, le=6.283185307179586) # radians
    
    # Blip visual attributes
    size: float = Field(default=12.0, ge=4.0, le=36.0) # volume/impact encoding
    pulse_speed: float = Field(default=1.0, ge=0.0, le=5.0) # velocity encoding (0=none)
    severity: RadarSeverity = RadarSeverity.WATCH
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    
    # Quick metadata
    incident_count: int = 0
    growth_percent: float = 0.0
    is_resurgent: bool = False
    is_mutating: bool = False
    top_reason: str = "Active campaign activity"


class RadarSummary(BaseModel):
    """Top-level network surveillance summary across all tracked scam campaigns."""
    active_campaigns: int = 0
    emerging_count: int = 0
    surging_count: int = 0
    outbreak_count: int = 0
    critical_count: int = 0
    new_incidents_24h: int = 0
    high_risk_signals: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "3.3.0"
    demo_mode: bool = False


class ConsumerCampaignSignal(BaseModel):
    """Privacy-safe consumer warning contribution derived from campaign network intelligence."""
    campaign_matched: bool = False
    warning_message: Optional[str] = None
    urgency_level: str = "LOW"
    confidence_level: str = "LOW"
    pre_loss_warning: bool = False
    reason_summary: Optional[str] = None
