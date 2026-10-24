"""Campaign Intelligence V2 & Scam Outbreak Radar Package (Phase 3C)."""

from services.campaign_engine.config import CampaignConfig, campaign_config
from services.campaign_engine.discovery import CampaignDiscoveryEngine
from services.campaign_engine.lifecycle import CampaignLifecycleManager
from services.campaign_engine.radar import ScamOutbreakRadarService
from services.campaign_engine.service import CampaignIntelligenceService, campaign_service
from services.campaign_engine.velocity import CampaignVelocityEngine

__all__ = [
    "CampaignConfig",
    "campaign_config",
    "CampaignDiscoveryEngine",
    "CampaignLifecycleManager",
    "CampaignVelocityEngine",
    "ScamOutbreakRadarService",
    "CampaignIntelligenceService",
    "campaign_service",
]
