"""Campaign Lifecycle Manager (Phase 3C - Sections 7, 22-30, 67-70).

Governs campaign state transitions, resurgence detection, mutation tracking (DNA,
tactic, channel, and entity rotation), and auditable merge/split proposals.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from packages.schemas.campaign import (
    CampaignLifecycleState,
    CampaignMergeSplitProposal,
    CampaignVelocityState,
    ScamCampaign,
)
from services.campaign_engine.config import CampaignConfig, campaign_config

logger = logging.getLogger("campaign_engine.lifecycle")


class CampaignLifecycleManager:
    """Manages lifecycle transitions, resurgence, drift, and lineage operations."""

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or campaign_config

    def evaluate_lifecycle_transition(
        self,
        campaign: ScamCampaign,
        new_incidents_count: int,
        velocity_state: CampaignVelocityState,
        latest_incident_time: Optional[datetime] = None,
    ) -> Tuple[CampaignLifecycleState, List[str]]:
        """Determines the next lifecycle state following strict transition rules.
        
        Rule 1: Never jump directly from CANDIDATE to OUTBREAK.
        Rule 2: Detect DORMANT if inactivity exceeds dormant_inactivity_days.
        Rule 3: Detect RESURGING if dormant campaign receives new verified incidents.
        """
        now = latest_incident_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        current_state = campaign.lifecycle_state
        reasons: List[str] = []

        # Check for dormancy
        inactivity_days = (now - campaign.last_seen).total_seconds() / 86400.0
        if current_state in (CampaignLifecycleState.ACTIVE, CampaignLifecycleState.DECLINING) and inactivity_days >= self.config.dormant_inactivity_days:
            reasons.append(f"INACTIVITY_{int(inactivity_days)}_DAYS")
            return CampaignLifecycleState.DORMANT, reasons

        # Check for resurgence (Section 22)
        if current_state == CampaignLifecycleState.DORMANT and new_incidents_count > 0:
            reasons.append(f"RESURGENCE_AFTER_{int(inactivity_days)}_DAYS_DORMANCY")
            return CampaignLifecycleState.RESURGING, reasons

        # Velocity-driven progression (Section 7: Candidacy requires progression)
        if velocity_state == CampaignVelocityState.OUTBREAK:
            if current_state == CampaignLifecycleState.CANDIDATE:
                # Do NOT jump straight from CANDIDATE to OUTBREAK
                reasons.append("PROMOTED_CANDIDATE_TO_EMERGING_BEFORE_OUTBREAK")
                return CampaignLifecycleState.EMERGING, reasons
            else:
                reasons.append("ESCALATED_TO_OUTBREAK_ON_VELOCITY")
                return CampaignLifecycleState.OUTBREAK, reasons

        if velocity_state == CampaignVelocityState.SURGING:
            if current_state in (CampaignLifecycleState.CANDIDATE, CampaignLifecycleState.EMERGING):
                reasons.append("ESCALATED_TO_SURGING")
                return CampaignLifecycleState.SURGING, reasons
            elif current_state == CampaignLifecycleState.OUTBREAK:
                # De-escalating slightly
                return CampaignLifecycleState.SURGING, ["DE-ESCALATED_FROM_OUTBREAK"]

        if velocity_state == CampaignVelocityState.RISING:
            if current_state == CampaignLifecycleState.CANDIDATE:
                return CampaignLifecycleState.EMERGING, ["EMERGING_ACTIVITY"]
            elif current_state in (CampaignLifecycleState.SURGING, CampaignLifecycleState.OUTBREAK):
                return CampaignLifecycleState.ACTIVE, ["DECELERATING_ACTIVITY"]

        if velocity_state == CampaignVelocityState.NORMAL:
            if current_state == CampaignLifecycleState.OUTBREAK:
                return CampaignLifecycleState.DECLINING, ["OUTBREAK_DECLINED_TO_NORMAL"]
            elif current_state == CampaignLifecycleState.SURGING:
                return CampaignLifecycleState.ACTIVE, ["SURGE_NORMALIZED"]

        return current_state, reasons

    def track_mutations(
        self,
        campaign: ScamCampaign,
        new_entities: List[Dict[str, Any]],
        new_channels: List[str],
        new_tactics: List[str],
    ) -> List[str]:
        """Detects infrastructure rotation, channel migration, and tactic drift (Sections 26-30)."""
        detected_mutations: List[str] = []

        # Payment & Phone rotation
        existing_payments = set(campaign.payment_profile)
        existing_phones = set(campaign.infrastructure_profile)
        for ent in new_entities:
            val = str(ent.get("canonical_value") or ent.get("raw_value") or "")
            etype = str(ent.get("entity_type", ""))
            if "PAYMENT" in etype or "UPI" in etype:
                if val and val not in existing_payments:
                    detected_mutations.append(f"PAYMENT_ROTATION({val})")
                    campaign.payment_profile.append(val)
                    campaign.unique_payment_identifier_count += 1
            elif "PHONE" in etype:
                if val and val not in existing_phones:
                    detected_mutations.append(f"PHONE_ROTATION({val})")
                    campaign.infrastructure_profile.append(val)
                    campaign.unique_phone_count += 1
            elif "DOMAIN" in etype or "URL" in etype:
                if val and val not in existing_phones:
                    detected_mutations.append(f"DOMAIN_ROTATION({val})")
                    campaign.infrastructure_profile.append(val)
                    campaign.unique_domain_count += 1

        # Channel migration (Section 29)
        existing_channels = set(campaign.channels)
        for ch in new_channels:
            if ch not in existing_channels:
                detected_mutations.append(f"CHANNEL_MIGRATION({ch})")
                campaign.channels.append(ch)

        # Tactic drift (Section 28)
        existing_tactics = set(campaign.tactic_profile)
        for tac in new_tactics:
            if tac not in existing_tactics:
                detected_mutations.append(f"TACTIC_DRIFT({tac})")
                campaign.tactic_profile.append(tac)

        if detected_mutations:
            campaign.mutation_count += len(detected_mutations)
            campaign.active_mutations.extend(detected_mutations)
            logger.info(f"Campaign {campaign.campaign_id} recorded {len(detected_mutations)} mutations.")

        return detected_mutations

    def propose_merge(
        self,
        source_campaign_a: ScamCampaign,
        source_campaign_b: ScamCampaign,
        reason: str,
        evidence: List[str],
    ) -> CampaignMergeSplitProposal:
        """Creates a formal proposal to merge two campaigns (Section 24, 68)."""
        proposal = CampaignMergeSplitProposal(
            proposal_id=f"prop_merge_{uuid4().hex[:10]}",
            proposal_type="MERGE",
            source_campaign_ids=[source_campaign_a.campaign_id, source_campaign_b.campaign_id],
            reason=reason,
            supporting_evidence=evidence,
            status="PENDING_REVIEW",
        )
        logger.info(f"Created merge proposal {proposal.proposal_id} for campaigns {proposal.source_campaign_ids}.")
        return proposal

    def propose_split(
        self,
        campaign: ScamCampaign,
        reason: str,
        evidence: List[str],
    ) -> CampaignMergeSplitProposal:
        """Creates a formal proposal to split a bifurcated campaign (Section 23, 69)."""
        proposal = CampaignMergeSplitProposal(
            proposal_id=f"prop_split_{uuid4().hex[:10]}",
            proposal_type="SPLIT",
            source_campaign_ids=[campaign.campaign_id],
            reason=reason,
            supporting_evidence=evidence,
            status="PENDING_REVIEW",
        )
        logger.info(f"Created split proposal {proposal.proposal_id} for campaign {campaign.campaign_id}.")
        return proposal
