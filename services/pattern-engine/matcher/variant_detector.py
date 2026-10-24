"""Emerging Scam Variant Detector (Step 26).

Detects novel scam mutations and emerging campaigns where surface infrastructure
identifiers (phone numbers, domains, IPs, UPI VPAs) have rotated or are completely unseen,
yet the underlying semantic grooming, temporal event sequence, and deceptive tactics remain invariant.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field

from packages.schemas.assessment import EmergingStatus
from packages.schemas.fingerprint import (
    FingerprintSimilarityResult,
    ScamFingerprint,
    ScamFingerprintV2,
)
from services.pattern_engine.patterns.scam_patterns import PatternMatch
from services.pattern_engine.semantic.similarity_engine import ScamFingerprintSimilarityEngine

logger = logging.getLogger("pattern_engine.variant_detector")


class IdentifierMatchResult(BaseModel):
    """Details of known entity/infrastructure overlap."""
    phone_matched: bool = False
    domain_matched: bool = False
    payment_matched: bool = False
    ip_matched: bool = False
    matched_identifiers: List[str] = Field(default_factory=list)

    @property
    def has_any_match(self) -> bool:
        return self.phone_matched or self.domain_matched or self.payment_matched or self.ip_matched


class WorkflowMatchResult(BaseModel):
    """Categorical alignment across structural scam dimensions."""
    semantic_level: str = "LOW"  # HIGH, MEDIUM, LOW
    temporal_level: str = "LOW"  # HIGH, MEDIUM, LOW
    pattern_level: str = "LOW"   # HIGH, MEDIUM, LOW
    composite_similarity: float = 0.0


class EmergingVariantEvaluation(BaseModel):
    """Final assessment of whether an incident represents a known, mutated, or emerging campaign."""
    incident_id: str
    status: EmergingStatus
    identifier_match: IdentifierMatchResult
    workflow_match: WorkflowMatchResult
    matched_incident_id: Optional[str] = None
    matched_campaign: Optional[str] = None
    similarity_breakdown: Dict[str, float] = Field(default_factory=dict)
    verdict_explanation: str


class EmergingVariantDetector:
    """Evaluates whether an incident is KNOWN_PATTERN, MUTATED_VARIANT, POSSIBLE_EMERGING_CAMPAIGN,

    NO_SIGNIFICANT_MATCH, or INSUFFICIENT_EVIDENCE.
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "thresholds": {
            "mutated_variant_threshold": 0.65,
            "known_pattern_similarity_threshold": 0.80,
            "semantic_workflow_threshold": 0.70,
            "journey_workflow_threshold": 0.70,
            "no_match_threshold": 0.40,
            "min_events_for_evaluation": 2,
        },
        "identifiers": {
            "check_phone": True,
            "check_domain": True,
            "check_vpa": True,
            "check_ip": True,
            "check_bank_account": True,
        },
        "temporal_bounds": {
            "min_grooming_seconds": 15,
            "max_grooming_seconds": 1200,
        },
    }

    _config_cache: Optional[Dict[str, Any]] = None

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if cls._config_cache is not None:
            return cls._config_cache

        config_path = Path("config/emerging_variant.yaml")
        if not config_path.exists():
            config_path = Path(__file__).resolve().parents[3] / "config" / "emerging_variant.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if isinstance(cfg, dict):
                        cls._config_cache = cfg
                        return cls._config_cache
            except Exception as e:
                logger.warning(f"Failed to load {config_path}: {e}. Using defaults.")

        cls._config_cache = cls.DEFAULT_CONFIG
        return cls._config_cache

    @classmethod
    def evaluate(
        cls,
        incident_id: str,
        fingerprint: Union[ScamFingerprint, ScamFingerprintV2],
        historical_phones: Optional[List[str]] = None,
        historical_domains: Optional[List[str]] = None,
        historical_vpas: Optional[List[str]] = None,
        historical_ips: Optional[List[str]] = None,
        historical_fingerprints: Optional[List[ScamFingerprintV2]] = None,
        pattern_match: Optional[PatternMatch] = None,
        semantic_similarity_score: Optional[float] = None,
        temporal_pace_seconds: Optional[int] = None,
        graph_correlation: Optional[Any] = None,
    ) -> EmergingVariantEvaluation:
        """Evaluates incident fingerprint against known indicators and historical fingerprints."""
        config = cls._load_config()
        thresholds = config.get("thresholds", cls.DEFAULT_CONFIG["thresholds"])
        temporal_bounds = config.get("temporal_bounds", cls.DEFAULT_CONFIG["temporal_bounds"])

        min_grooming = temporal_bounds.get("min_grooming_seconds", 15)
        max_grooming = temporal_bounds.get("max_grooming_seconds", 1200)

        hist_phones = set(historical_phones or [])
        hist_domains = set(historical_domains or [])
        hist_vpas = set(historical_vpas or [])
        hist_ips = set(historical_ips or [])

        # 1. Extract endpoint identifiers & metadata based on fingerprint model
        matched_ids: List[str] = []
        current_phone = ""
        current_domain = ""
        current_vpa = ""
        current_ip = ""
        event_count = 0
        computed_pace = temporal_pace_seconds

        if isinstance(fingerprint, ScamFingerprintV2):
            event_count = len(fingerprint.ordered_event_sequence)
            current_phone = str(fingerprint.infrastructure_entities.get("phone") or "")
            current_domain = str(
                fingerprint.infrastructure_entities.get("domain")
                or fingerprint.URL_features.get("domain")
                or ""
            )
            current_vpa = str(
                fingerprint.payment_entities.get("vpa")
                or fingerprint.payment_entities.get("upi_id")
                or ""
            )
            current_ip = str(fingerprint.infrastructure_entities.get("ip") or "")

            if computed_pace is None:
                if fingerprint.event_time_gaps:
                    computed_pace = sum(fingerprint.event_time_gaps)
                else:
                    computed_pace = 180
        elif isinstance(fingerprint, ScamFingerprint):
            event_count = len(fingerprint.stage_sequence)
            current_phone = str(fingerprint.infrastructure_hash.get("phone") or "")
            current_domain = str(fingerprint.infrastructure_hash.get("domain") or "")
            current_vpa = str(fingerprint.payment_profile.get("vpa") or "")
            current_ip = str(fingerprint.infrastructure_hash.get("ip") or "")
            if computed_pace is None:
                computed_pace = getattr(fingerprint, "temporal_pace_seconds", 180)
        else:
            computed_pace = 180 if computed_pace is None else computed_pace

        # 2. Check identifier overlap
        phone_matched = bool(current_phone and current_phone in hist_phones)
        if phone_matched:
            matched_ids.append(f"phone:{current_phone}")

        domain_matched = bool(current_domain and current_domain in hist_domains)
        if domain_matched:
            matched_ids.append(f"domain:{current_domain}")

        payment_matched = bool(current_vpa and current_vpa in hist_vpas)
        if payment_matched:
            matched_ids.append(f"payment:{current_vpa}")

        ip_matched = bool(current_ip and current_ip in hist_ips)
        if ip_matched:
            matched_ids.append(f"ip:{current_ip}")

        id_match = IdentifierMatchResult(
            phone_matched=phone_matched,
            domain_matched=domain_matched,
            payment_matched=payment_matched,
            ip_matched=ip_matched,
            matched_identifiers=matched_ids,
        )

        # 3. Evaluate Similarity against Historical Fingerprints
        best_match_incident_id: Optional[str] = None
        best_match_campaign: Optional[str] = None
        similarity_breakdown: Dict[str, float] = {}

        semantic_score = semantic_similarity_score or 0.0
        sequence_score = 0.0
        pattern_score = 0.0
        composite_score = semantic_score

        if historical_fingerprints and isinstance(fingerprint, ScamFingerprintV2):
            best_sim_result: Optional[FingerprintSimilarityResult] = None
            best_overall = -1.0
            sim_engine = ScamFingerprintSimilarityEngine()

            for hist_fp in historical_fingerprints:
                sim_res = sim_engine.compare(fingerprint, hist_fp)
                if sim_res.overall_similarity > best_overall:
                    best_overall = sim_res.overall_similarity
                    best_sim_result = sim_res
                    best_match_incident_id = hist_fp.incident_id
                    best_match_campaign = hist_fp.graph_community

            if best_sim_result:
                semantic_score = max(semantic_score, best_sim_result.semantic_similarity)
                sequence_score = best_sim_result.sequence_similarity
                pattern_score = best_sim_result.pattern_similarity
                composite_score = best_sim_result.overall_similarity
                similarity_breakdown = {
                    "overall": best_sim_result.overall_similarity,
                    "semantic": best_sim_result.semantic_similarity,
                    "journey": best_sim_result.sequence_similarity,
                    "pattern": best_sim_result.pattern_similarity,
                    "infrastructure": best_sim_result.infrastructure_similarity,
                    "payment": best_sim_result.payment_similarity,
                }

        # 4. Evaluate Workflow Match Levels
        sem_thresh = thresholds.get("semantic_workflow_threshold", 0.70)
        semantic_level = (
            "HIGH"
            if semantic_score >= sem_thresh
            else ("MEDIUM" if semantic_score >= 0.45 else "LOW")
        )

        temporal_level = (
            "HIGH"
            if (min_grooming <= (computed_pace or 180) <= max_grooming)
            else "MEDIUM"
        )

        pattern_strong = bool(pattern_match and pattern_match.is_strong_match)
        pattern_level = (
            "HIGH"
            if (pattern_strong or pattern_score >= 0.70)
            else ("MEDIUM" if (pattern_match or pattern_score >= 0.40) else "LOW")
        )

        wf_match = WorkflowMatchResult(
            semantic_level=semantic_level,
            temporal_level=temporal_level,
            pattern_level=pattern_level,
            composite_similarity=composite_score,
        )

        # 5. Evaluate Decision Matrix
        min_events = thresholds.get("min_events_for_evaluation", 2)
        mutated_thresh = thresholds.get("mutated_variant_threshold", 0.65)
        known_thresh = thresholds.get("known_pattern_similarity_threshold", 0.80)
        no_match_thresh = thresholds.get("no_match_threshold", 0.40)

        # Check for insufficient evidence first
        if event_count < min_events and not pattern_match and composite_score < 0.30 and not id_match.has_any_match:
            status = EmergingStatus.INSUFFICIENT_EVIDENCE
            explanation = (
                f"Telemetry too sparse ({event_count} events) with no corroborating patterns "
                "or recognized identifiers to evaluate variant classification."
            )
        # Check for Known Pattern (reused infrastructure)
        elif id_match.has_any_match and (pattern_level in ("HIGH", "MEDIUM") or composite_score >= known_thresh):
            status = EmergingStatus.KNOWN_PATTERN
            explanation = (
                f"Incident utilizes previously identified scam infrastructure "
                f"({', '.join(id_match.matched_identifiers)}) and established workflow."
            )
        # Check for Hero Possible Emerging Campaign (zero identifiers, multi-stage workflow match)
        elif not id_match.has_any_match and semantic_level == "HIGH" and pattern_level == "HIGH" and temporal_level == "HIGH":
            status = EmergingStatus.POSSIBLE_EMERGING_CAMPAIGN
            explanation = (
                "HERO MATCH: All identifiers (Phone, Domain, VPA) are brand-new/unseen, "
                "yet the psychological coercion, temporal transition speed, and multi-stage workflow "
                "exhibit high structural similarity to known banking scam campaigns."
            )
        # Check for Mutated Variant (zero identifiers, high composite similarity or semantic/pattern alignment)
        elif not id_match.has_any_match and (composite_score >= mutated_thresh or (semantic_level == "HIGH" and pattern_level == "MEDIUM")):
            status = EmergingStatus.MUTATED_VARIANT
            explanation = (
                "Incident mutates key endpoint identifiers while preserving core deceptive tactics "
                f"and journey blueprint (similarity: {composite_score:.2f})."
            )
        # Check for No Significant Match (benign or unrelated novel journey)
        elif not id_match.has_any_match and composite_score < no_match_thresh:
            status = EmergingStatus.NO_SIGNIFICANT_MATCH
            explanation = "Standard or low-risk interaction with no significant correlation to known scam blueprints."
        else:
            status = EmergingStatus.NO_SIGNIFICANT_MATCH
            explanation = "Interaction does not exhibit sufficient characteristics of a known or mutated fraud campaign."

        return EmergingVariantEvaluation(
            incident_id=incident_id,
            status=status,
            identifier_match=id_match,
            workflow_match=wf_match,
            matched_incident_id=best_match_incident_id,
            matched_campaign=best_match_campaign,
            similarity_breakdown=similarity_breakdown,
            verdict_explanation=explanation,
        )
