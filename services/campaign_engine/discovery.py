"""Campaign Discovery Engine (Phase 3C - Sections 8-15).

Evolves CandidateIncidentGroup instances into verified ScamCampaign objects
using multi-signal validation: relationship density, strong edges, ScamDNA consistency,
journey overlap, entity/infrastructure links, and false-link prevention.
Same scam family alone CANNOT form a campaign.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from packages.schemas.campaign import (
    CampaignLifecycleState,
    CampaignMembership,
    CampaignReviewState,
    CampaignVelocityState,
    ScamCampaign,
)
from packages.schemas.correlation import CandidateIncidentGroup
from services.campaign_engine.config import CampaignConfig, campaign_config
from services.graph_engine.campaigns.clusterer import CampaignClusterer

logger = logging.getLogger("campaign_engine.discovery")


class CampaignDiscoveryEngine:
    """Discovers and validates scam campaigns from multi-signal correlation groups."""

    def __init__(self, config: Optional[CampaignConfig] = None):
        self.config = config or campaign_config
        # DBSCAN retained for auxiliary vector candidate clustering
        self.embedding_clusterer = CampaignClusterer(eps=0.35, min_samples=2)

    def evaluate_candidate_group(
        self,
        group: CandidateIncidentGroup,
        incidents_data: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Optional[ScamCampaign]:
        """Evaluates a CandidateIncidentGroup against multi-signal criteria.
        
        Returns a ScamCampaign if criteria are met; None if rejected (e.g., family-only).
        """
        # Multi-signal check 1: Minimum incident count
        if len(group.member_incident_ids) < self.config.candidate_min_incidents:
            logger.info(
                f"Group {group.group_id} has {len(group.member_incident_ids)} incidents, "
                f"below minimum {self.config.candidate_min_incidents}. Rejected."
            )
            return None

        # Multi-signal check 2: Same scam family != same campaign
        # If evidence diversity contains ONLY family matching or pure text similarity with zero
        # independent entity, infra, DNA, or journey evidence, reject.
        independent_evidence = [
            e for e in group.evidence_diversity
            if not e.startswith("SAME_FAMILY") and not e.startswith("TEXT_ONLY")
        ]
        if not independent_evidence:
            logger.info(
                f"Group {group.group_id} contains only family/text similarity without "
                "independent corroboration. Refusing to form campaign."
            )
            return None

        # Multi-signal check 3: Relationship density & strong edges
        total_possible_edges = len(group.member_incident_ids) * (len(group.member_incident_ids) - 1) / 2
        strong_edge_ratio = (group.strong_edge_count / max(1, total_possible_edges)) if total_possible_edges > 0 else 0.0

        if group.relationship_density < self.config.relationship_density_threshold and strong_edge_ratio < self.config.strong_edge_min_ratio:
            logger.info(
                f"Group {group.group_id} failed connectivity check: density={group.relationship_density}, "
                f"strong_edge_ratio={strong_edge_ratio}."
            )
            return None

        # Aggregate incident profiles if full data provided
        entities: Set[str] = set()
        payment_ids: Set[str] = set()
        domains: Set[str] = set()
        phones: Set[str] = set()
        socials: Set[str] = set()
        languages: Set[str] = {"English"}
        channels: Set[str] = set()
        regions: Set[str] = set()
        journey_stages: List[str] = []
        tactics: List[str] = []

        if incidents_data:
            for inc_id in group.member_incident_ids:
                inc = incidents_data.get(inc_id, {})
                for ent in inc.get("entities", []):
                    val = ent.get("canonical_value") or ent.get("raw_value")
                    etype = ent.get("entity_type", "")
                    if val:
                        entities.add(str(val))
                        if "PAYMENT" in etype or "UPI" in etype or "VPA" in etype or "ACCOUNT" in etype:
                            payment_ids.add(str(val))
                        elif "DOMAIN" in etype or "URL" in etype:
                            domains.add(str(val))
                        elif "PHONE" in etype:
                            phones.add(str(val))
                        elif "HANDLE" in etype or "TELEGRAM" in etype or "SOCIAL" in etype:
                            socials.add(str(val))
                for lang in inc.get("languages", []):
                    languages.add(str(lang))
                for ch in inc.get("channels", []):
                    channels.add(str(ch))
                for reg in inc.get("regions", []):
                    regions.add(str(reg))
                if inc.get("journey_stage"):
                    journey_stages.append(str(inc["journey_stage"]))
                for tac in inc.get("tactics", []):
                    tactics.append(str(tac))

        # Determine initial lifecycle state based on volume and density
        lifecycle = CampaignLifecycleState.CANDIDATE
        if len(group.member_incident_ids) >= self.config.active_min_incidents and group.relationship_density >= self.config.relationship_density_threshold:
            lifecycle = CampaignLifecycleState.ACTIVE
        elif len(group.member_incident_ids) >= self.config.candidate_min_incidents:
            lifecycle = CampaignLifecycleState.EMERGING

        # Calculate campaign confidence based on evidence diversity & strong edges
        diversity_factor = min(1.0, len(independent_evidence) / 3.0)
        confidence = round(0.50 + 0.30 * group.relationship_density + 0.20 * diversity_factor, 2)
        confidence = min(0.98, max(0.40, confidence))

        campaign_id = f"camp_{uuid4().hex[:10]}"
        title = f"{group.primary_family.replace('_', ' ').title()} Campaign ({len(group.member_incident_ids)} nodes)"

        campaign = ScamCampaign(
            campaign_id=campaign_id,
            title=title,
            scam_family=group.primary_family,
            family_confidence=0.88,
            lifecycle_state=lifecycle,
            velocity_state=CampaignVelocityState.NORMAL,
            review_state=CampaignReviewState.UNREVIEWED,
            first_seen=group.first_seen,
            last_seen=group.last_seen,
            incident_count=len(group.member_incident_ids),
            strongly_related_incident_count=group.strong_edge_count,
            unique_entity_count=len(entities),
            unique_payment_identifier_count=len(payment_ids),
            unique_domain_count=len(domains),
            unique_phone_count=len(phones),
            unique_social_account_count=len(socials),
            languages=sorted(list(languages)),
            channels=sorted(list(channels)),
            regions=sorted(list(regions)),
            journey_profile=journey_stages[:6],
            tactic_profile=tactics[:6],
            confidence=confidence,
            current_velocity=group.growth_velocity,
            metadata={
                "source_group_id": group.group_id,
                "relationship_density": group.relationship_density,
                "evidence_diversity": group.evidence_diversity,
            },
        )

        logger.info(
            f"Successfully formed campaign {campaign.campaign_id} ({campaign.lifecycle_state}) "
            f"with {campaign.incident_count} incidents and confidence {campaign.confidence}."
        )
        return campaign

    def cluster_embeddings_fallback(
        self,
        incident_ids: List[str],
        embeddings: List[List[float]],
    ) -> Dict[str, Any]:
        """Harvests DBSCAN clustering for embedding-based candidate grouping.
        
        NOTE: DBSCAN clusters are merely candidate pools and must undergo
        evaluate_candidate_group before becoming production campaigns.
        """
        return self.embedding_clusterer.cluster_fingerprints(incident_ids, embeddings)
