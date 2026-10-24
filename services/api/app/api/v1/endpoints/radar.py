"""Scam Outbreak Radar REST API (Phase 3C - Part J, Sections 78-81)."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from packages.schemas.radar import (
    ConsumerCampaignSignal,
    OutbreakSignal,
    RadarBlip,
    RadarSummary,
)
from services.campaign_engine.service import campaign_service

router = APIRouter()


@router.get("/summary", response_model=RadarSummary)
async def get_radar_summary(demo_mode: bool = False):
    """Returns aggregated high-level network surveillance numbers."""
    return campaign_service.get_radar_summary(demo_mode=demo_mode)


@router.get("/blips", response_model=List[RadarBlip])
async def get_radar_blips(demo_mode: bool = False):
    """Returns geometric and analytical campaign blips across the 3 radar rings."""
    return campaign_service.get_radar_blips(demo_mode=demo_mode)


@router.get("/signals", response_model=List[OutbreakSignal])
async def get_outbreak_signals(
    limit: int = Query(default=50, ge=1, le=100),
    demo_mode: bool = False,
):
    """Returns chronological outbreak signals and emerging threat escalations."""
    return campaign_service.get_outbreak_signals(limit=limit, demo_mode=demo_mode)


@router.get("/consumer-warning", response_model=ConsumerCampaignSignal)
async def get_consumer_campaign_warning(incident_id: str):
    """Provides privacy-safe campaign network warning for consumer scam check."""
    return campaign_service.get_consumer_warning(incident_id)
