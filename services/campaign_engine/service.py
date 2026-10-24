"""Campaign Intelligence Service Orchestrator (Phase 3C).

Provides unified access to Campaign Discovery, Lifecycle Management,
Velocity Engine, Outbreak Radar, and Consumer-Facing Warning Signals.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.campaign import (
    CampaignLifecycleState,
    CampaignMembership,
    CampaignMergeSplitProposal,
    CampaignReviewState,
    CampaignVelocityState,
    ScamCampaign,
)
from packages.schemas.correlation import CandidateIncidentGroup
from packages.schemas.radar import (
    ConsumerCampaignSignal,
    OutbreakSignal,
    OutbreakSignalType,
    RadarBlip,
    RadarSeverity,
    RadarSummary,
)
from services.campaign_engine.config import CampaignConfig, campaign_config
from services.campaign_engine.discovery import CampaignDiscoveryEngine
from services.campaign_engine.lifecycle import CampaignLifecycleManager
from services.campaign_engine.radar import ScamOutbreakRadarService
from services.campaign_engine.velocity import CampaignVelocityEngine

logger = logging.getLogger("campaign_engine.service")


class CampaignIntelligenceService:
    """Unified service coordinating discovery, velocity, lifecycle, and radar."""

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or campaign_config
        self.discovery_engine = CampaignDiscoveryEngine(self.config)
        self.velocity_engine = CampaignVelocityEngine(self.config)
        self.lifecycle_manager = CampaignLifecycleManager(self.config)
        self.radar_service = ScamOutbreakRadarService(self.config)

        # In-memory primary store
        self._campaigns: Dict[str, ScamCampaign] = {}
        self._memberships: Dict[str, List[CampaignMembership]] = {}  # campaign_id -> memberships
        self._incident_to_campaign: Dict[str, str] = {}              # incident_id -> campaign_id
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._proposals: Dict[str, CampaignMergeSplitProposal] = {}
        self._outbreak_signals: List[OutbreakSignal] = []

    def register_incident(self, incident_data: Dict[str, Any]) -> None:
        """Stores or updates incident representation for campaign tracking."""
        inc_id = incident_data.get("id") or incident_data.get("incident_id")
        if inc_id:
            self._incidents[str(inc_id)] = incident_data

    def discover_campaign_from_group(
        self,
        group: CandidateIncidentGroup,
    ) -> Optional[ScamCampaign]:
        """Evaluates a CandidateIncidentGroup from correlation and establishes a campaign."""
        campaign = self.discovery_engine.evaluate_candidate_group(group, self._incidents)
        if not campaign:
            return None

        self._campaigns[campaign.campaign_id] = campaign

        # Create membership records
        memberships = []
        for inc_id in group.member_incident_ids:
            mem = CampaignMembership(
                incident_id=inc_id,
                campaign_id=campaign.campaign_id,
                membership_score=0.90,
                confidence=campaign.confidence,
                reasons=group.evidence_diversity,
            )
            memberships.append(mem)
            self._incident_to_campaign[inc_id] = campaign.campaign_id
        self._memberships[campaign.campaign_id] = memberships

        # Compute initial velocity & outbreak signals
        self.recompute_campaign_velocity(campaign.campaign_id)
        return campaign

    def recompute_campaign_velocity(
        self,
        campaign_id: str,
        current_time: Optional[datetime] = None,
    ) -> Optional[ScamCampaign]:
        """Recalculates velocity, lifecycle state, and outbreak signals for a campaign."""
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return None

        # Fetch incidents belonging to this campaign
        mems = self._memberships.get(campaign_id, [])
        incidents = [self._incidents[m.incident_id] for m in mems if m.incident_id in self._incidents]

        # 1. Velocity computation
        vel_state, cur_vel, base_vel, growth_mult, accel, vel_reasons = (
            self.velocity_engine.calculate_velocity(campaign, incidents, current_time)
        )
        campaign.velocity_state = vel_state
        campaign.current_velocity = cur_vel
        campaign.baseline_velocity = base_vel
        campaign.growth_multiplier = growth_mult
        campaign.acceleration = accel

        # 2. Lifecycle transition check
        new_lifecycle, lc_reasons = self.lifecycle_manager.evaluate_lifecycle_transition(
            campaign,
            new_incidents_count=len(incidents),
            velocity_state=vel_state,
            latest_incident_time=current_time,
        )
        campaign.lifecycle_state = new_lifecycle
        campaign.updated_at = datetime.now(timezone.utc)

        # 3. Generate Outbreak Signals
        signals = self.radar_service.generate_outbreak_signals(campaign, vel_reasons + lc_reasons)
        for s in signals:
            self._outbreak_signals.append(s)

        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[ScamCampaign]:
        """Retrieves a campaign by ID."""
        return self._campaigns.get(campaign_id)

    def list_campaigns(
        self,
        lifecycle_state: Optional[str] = None,
        family: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ScamCampaign]:
        """Lists tracked campaigns with optional filtering."""
        result = list(self._campaigns.values())
        if lifecycle_state:
            result = [c for c in result if c.lifecycle_state.value == lifecycle_state.upper()]
        if family:
            result = [c for c in result if c.scam_family.lower() == family.lower()]

        # Sort by urgency and current velocity
        result.sort(key=lambda c: (c.current_velocity, c.confidence), reverse=True)
        return result[offset : offset + limit]

    def get_radar_summary(self, demo_mode: bool = False) -> RadarSummary:
        """Produces top-level network outbreak surveillance summary."""
        if demo_mode and not self._campaigns:
            self.seed_demo_data()

        campaigns = list(self._campaigns.values())
        return self.radar_service.generate_radar_summary(campaigns, self._outbreak_signals, demo_mode)

    def get_radar_blips(self, demo_mode: bool = False) -> List[RadarBlip]:
        """Generates analytical radar blips for the visual radar canvas."""
        if demo_mode and not self._campaigns:
            self.seed_demo_data()

        blips: List[RadarBlip] = []
        for c in self._campaigns.values():
            blips.append(self.radar_service.map_campaign_to_blip(c))
        return blips

    def get_outbreak_signals(self, limit: int = 50, demo_mode: bool = False) -> List[OutbreakSignal]:
        """Returns recent outbreak signals chronologically."""
        if demo_mode and not self._outbreak_signals:
            self.seed_demo_data()

        sorted_sigs = sorted(self._outbreak_signals, key=lambda s: s.last_updated, reverse=True)
        return sorted_sigs[:limit]

    def get_consumer_warning(self, incident_id: str) -> ConsumerCampaignSignal:
        """Returns a privacy-safe consumer warning contribution if incident belongs to a campaign."""
        camp_id = self._incident_to_campaign.get(incident_id)
        if not camp_id:
            return ConsumerCampaignSignal(campaign_matched=False)
        camp = self._campaigns.get(camp_id)
        return self.radar_service.create_consumer_signal(camp)

    def propose_merge(
        self,
        campaign_a_id: str,
        campaign_b_id: str,
        reason: str,
        evidence: List[str],
    ) -> Optional[CampaignMergeSplitProposal]:
        """Creates an auditable merge proposal."""
        cA = self._campaigns.get(campaign_a_id)
        cB = self._campaigns.get(campaign_b_id)
        if not cA or not cB:
            return None
        proposal = self.lifecycle_manager.propose_merge(cA, cB, reason, evidence)
        self._proposals[proposal.proposal_id] = proposal
        return proposal

    def propose_split(
        self,
        campaign_id: str,
        reason: str,
        evidence: List[str],
    ) -> Optional[CampaignMergeSplitProposal]:
        """Creates an auditable split proposal."""
        c = self._campaigns.get(campaign_id)
        if not c:
            return None
        proposal = self.lifecycle_manager.propose_split(c, reason, evidence)
        self._proposals[proposal.proposal_id] = proposal
        return proposal

    def seed_demo_data(self) -> None:
        """Seeds realistic India-specific scam campaigns for demonstration & visual tests."""
        now = datetime.now(timezone.utc)

        # 1. Critical Outbreak: Digital Arrest CBI Impersonation
        camp1 = ScamCampaign(
            campaign_id="camp_da_cbi_01",
            title="Digital Arrest CBI / Mumbai Police Extortion",
            scam_family="DIGITAL_ARREST",
            family_confidence=0.96,
            lifecycle_state=CampaignLifecycleState.OUTBREAK,
            velocity_state=CampaignVelocityState.OUTBREAK,
            review_state=CampaignReviewState.INVESTIGATING,
            first_seen=now - timedelta(days=20),
            last_seen=now,
            incident_count=48,
            strongly_related_incident_count=36,
            unique_entity_count=22,
            unique_payment_identifier_count=14,
            unique_domain_count=6,
            unique_phone_count=12,
            unique_social_account_count=8,
            languages=["English", "Hindi"],
            channels=["WhatsApp", "Skype", "IVR"],
            regions=["Delhi NCR", "Maharashtra", "Karnataka"],
            journey_profile=["CONTACT", "AUTHORITY_FEAR", "ISOLATION", "DEMAND_TRANSFER"],
            tactic_profile=["AUTHORITY_IMPERSONATION", "EXTREME_URGENCY", "LEGAL_THREAT"],
            confidence=0.94,
            current_velocity=18.0,
            baseline_velocity=4.2,
            growth_multiplier=4.28,
            acceleration=8.0,
            mutation_count=4,
            active_mutations=["PHONE_ROTATION(+919876543210)", "PAYMENT_ROTATION(mumbai.police.audit@sbi)"],
        )

        # 2. Surging: Telegram Part-time Job Task Scam
        camp2 = ScamCampaign(
            campaign_id="camp_task_job_02",
            title="YouTube Video Like / Telegram VIP Task Scam",
            scam_family="TASK_SCAM",
            family_confidence=0.92,
            lifecycle_state=CampaignLifecycleState.SURGING,
            velocity_state=CampaignVelocityState.SURGING,
            review_state=CampaignReviewState.ACKNOWLEDGED,
            first_seen=now - timedelta(days=12),
            last_seen=now,
            incident_count=34,
            strongly_related_incident_count=25,
            unique_entity_count=18,
            unique_payment_identifier_count=11,
            unique_domain_count=8,
            unique_phone_count=9,
            unique_social_account_count=15,
            languages=["English", "Hinglish"],
            channels=["Telegram", "WhatsApp", "Instagram"],
            regions=["West Bengal", "Uttar Pradesh", "Telangana"],
            journey_profile=["UNSOLICITED_JOB", "SMALL_REWARD", "PREPAID_TASK", "WITHDRAWAL_BLOCK"],
            tactic_profile=["FINANCIAL_REWARD", "PREPAID_DEPOSIT", "SUNKEN_COST"],
            confidence=0.88,
            current_velocity=12.0,
            baseline_velocity=5.0,
            growth_multiplier=2.40,
            acceleration=4.0,
            mutation_count=2,
            active_mutations=["CHANNEL_MIGRATION(Instagram DM -> Telegram)"],
        )

        # 3. Emerging: Fake Electricity Disconnection SMS
        camp3 = ScamCampaign(
            campaign_id="camp_elec_kyc_03",
            title="State Electricity Power Disconnection Threat",
            scam_family="FAKE_SUPPORT",
            family_confidence=0.89,
            lifecycle_state=CampaignLifecycleState.EMERGING,
            velocity_state=CampaignVelocityState.RISING,
            review_state=CampaignReviewState.UNREVIEWED,
            first_seen=now - timedelta(days=4),
            last_seen=now,
            incident_count=11,
            strongly_related_incident_count=8,
            unique_entity_count=9,
            unique_payment_identifier_count=5,
            unique_domain_count=4,
            unique_phone_count=6,
            unique_social_account_count=1,
            languages=["Hindi", "English"],
            channels=["SMS", "Phone Call"],
            regions=["Haryana", "Punjab", "Delhi NCR"],
            journey_profile=["SMS_ALERT", "URGENT_CALL", "REMOTE_ACCESS_APP"],
            tactic_profile=["SERVICE_SUSPENSION_FEAR", "REMOTE_ACCESS_REQUEST"],
            confidence=0.82,
            current_velocity=5.0,
            baseline_velocity=1.2,
            growth_multiplier=4.16,
            acceleration=3.0,
            mutation_count=1,
            active_mutations=["PHONE_ROTATION(+918889991122)"],
        )

        # 4. Resurgent: FedEx Customs Narcotics Parcel Scam
        camp4 = ScamCampaign(
            campaign_id="camp_fedex_resurgent_04",
            title="FedEx Narcotics Customs Detention Resurgence",
            scam_family="CUSTOMS_PARCEL",
            family_confidence=0.91,
            lifecycle_state=CampaignLifecycleState.RESURGING,
            velocity_state=CampaignVelocityState.RISING,
            review_state=CampaignReviewState.MONITORING,
            first_seen=now - timedelta(days=65),
            last_seen=now,
            incident_count=21,
            strongly_related_incident_count=16,
            unique_entity_count=14,
            unique_payment_identifier_count=9,
            unique_domain_count=3,
            unique_phone_count=7,
            unique_social_account_count=4,
            languages=["English"],
            channels=["IVR", "WhatsApp"],
            regions=["Tamil Nadu", "Maharashtra"],
            journey_profile=["IVR_CALL", "CUSTOMS_THREAT", "POLICE_TRANSFER"],
            tactic_profile=["NARCOTICS_ACCUSATION", "EXTREME_URGENCY"],
            confidence=0.87,
            current_velocity=6.0,
            baseline_velocity=0.5,
            growth_multiplier=12.0,
            acceleration=5.0,
            mutation_count=3,
            active_mutations=["PHONE_ROTATION(+919112233445)"],
        )

        self._campaigns[camp1.campaign_id] = camp1
        self._campaigns[camp2.campaign_id] = camp2
        self._campaigns[camp3.campaign_id] = camp3
        self._campaigns[camp4.campaign_id] = camp4

        # Generate signals for each
        for camp in [camp1, camp2, camp3, camp4]:
            sigs = self.radar_service.generate_outbreak_signals(camp, [f"GROWTH_{camp.growth_multiplier}X"])
            for s in sigs:
                self._outbreak_signals.append(s)


# Global singleton instance
campaign_service = CampaignIntelligenceService()
