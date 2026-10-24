"""Tripartite Decision Fusion Engine (Phase 4A).

Coordinates Message NLP, URL Safety, Entity Trust, Tactic Intelligence,
Journey Progress, ScamDNA, and Campaign Outbreak signals into a calibrated
Tripartite Decision (Risk + Confidence + Urgency) with an actionable disposition.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from packages.schemas.unified_decision import (
    ActionDecision,
    DecisionDimension,
    SignalContribution,
    TripartiteConfidenceBand,
    TripartiteDecision,
    TripartiteRiskBand,
    TripartiteUrgencyBand,
)
from services.campaign_engine.service import campaign_service
from services.decision_engine.config import DecisionConfig, decision_config
from services.investigation.url_analysis.safety import URLAnalyzer
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor

logger = logging.getLogger("decision_engine.fusion")


class TripartiteDecisionFusionEngine:
    """Fuses multi-engine signals into an interpretable tripartite decision."""

    def __init__(self, config: Optional[DecisionConfig] = None):
        self.config = config or decision_config

    def evaluate_tripartite_decision(
        self,
        incident_id: Optional[str] = None,
        message_text: Optional[str] = None,
        url: Optional[str] = None,
        vpa: Optional[str] = None,
        phone: Optional[str] = None,
        journey_stage: Optional[str] = None,
        tactics_observed: Optional[List[str]] = None,
        known_dna_similarity: Optional[float] = None,
        entity_trust_score: Optional[float] = None,
        counter_evidence_signals: Optional[List[str]] = None,
    ) -> TripartiteDecision:
        """Evaluates inputs across all specialized engines and yields an action-ready decision."""
        contributions: List[SignalContribution] = []
        dimensions_evaluated = 0

        # 1. Message NLP Dimension
        msg_risk = 0.0
        msg_summary = "No message provided."
        if message_text:
            dimensions_evaluated += 1
            signals = SemanticSignalExtractor.extract_signals(incident_id or "tmp", message_text)
            if signals:
                msg_risk = min(1.0, 0.40 + (len(signals) * 0.20))
                sig_types = [s.signal_type for s in signals[:3]]
                msg_summary = f"Detected {len(signals)} semantic markers: {', '.join(sig_types)}"
            elif any(w in message_text.lower() for w in ["congratulations", "won", "lottery", "coupon", "prize", "cashback", "reward"]):
                msg_risk = 0.25
                msg_summary = "Unverified prize/promotional lure pattern detected."
            else:
                msg_risk = 0.05
                msg_summary = "No high-risk semantic markers detected."

        w_msg = self.config.weight_message_nlp
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.MESSAGE_NLP,
                engine_name="SemanticSignalExtractor",
                raw_score=round(msg_risk, 3),
                weight=w_msg,
                weighted_score=round(msg_risk * w_msg, 3),
                confidence=0.85 if message_text else 0.30,
                evidence_summary=msg_summary,
            )
        )

        # 2. URL Safety Dimension
        url_risk = 0.0
        url_summary = "No URL inspected."
        is_official_domain = False
        if url:
            dimensions_evaluated += 1
            res = URLAnalyzer.analyze_lexical_risk(incident_id or "tmp", url)
            url_risk = float(res.get("lexical_risk_score", 0.0)) / 100.0 if res.get("lexical_risk_score") is not None else 0.0
            signals = res.get("signals", [])
            for s in signals:
                if getattr(s, "is_counter_evidence", False) or s.signal_type == "ESTABLISHED_LONG_TERM_DOMAIN":
                    is_official_domain = True
            if is_official_domain:
                url_risk = 0.02
                url_summary = "Verified established official domain."
            elif signals:
                url_summary = f"Identified {len(signals)} lexical/domain risk indicators: {', '.join(s.signal_type for s in signals[:2])}"
            else:
                url_summary = "No suspicious URL patterns flagged."

        w_url = self.config.weight_url_safety
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.URL_SAFETY,
                engine_name="URLAnalyzer",
                raw_score=round(url_risk, 3),
                weight=w_url,
                weighted_score=round(url_risk * w_url, 3),
                confidence=0.90 if url else 0.30,
                evidence_summary=url_summary,
            )
        )

        # 3. Entity Trust Dimension (VPA / Phone)
        entity_risk = 0.0
        entity_summary = "No untrusted entities identified."
        if vpa or phone:
            dimensions_evaluated += 1
            if entity_trust_score is not None:
                entity_risk = 1.0 - max(0.0, min(1.0, entity_trust_score))
                entity_summary = f"Entity trust model returned score {entity_trust_score:.2f}."
            elif vpa and any(k in vpa.lower() for k in ["police", "cbi", "arrest", "scam", "task", "refund", "kyc", "verify", "support", "help"]):
                entity_risk = 0.90
                entity_summary = f"High-risk suspicious VPA identifier observed: {vpa}."
            elif vpa or phone:
                entity_risk = 0.35
                entity_summary = f"Unregistered party identifier observed ({vpa or phone})."

        w_ent = self.config.weight_entity_trust
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.ENTITY_TRUST,
                engine_name="EntityIntelligenceV2",
                raw_score=round(entity_risk, 3),
                weight=w_ent,
                weighted_score=round(entity_risk * w_ent, 3),
                confidence=0.85 if (vpa or phone) else 0.40,
                evidence_summary=entity_summary,
            )
        )

        # 4. Tactic & Manipulation Dimension
        tactic_risk = 0.0
        tactic_urgency = 0.20
        tactic_summary = "No overt manipulation detected."
        if tactics_observed:
            dimensions_evaluated += 1
            high_urgency_tactics = {"EXTREME_URGENCY", "AUTHORITY_IMPERSONATION", "LEGAL_THREAT", "PREPAID_DEPOSIT"}
            matched_high = [t for t in tactics_observed if t in high_urgency_tactics]
            tactic_risk = min(1.0, 0.45 + len(tactics_observed) * 0.15)
            tactic_urgency = 0.85 if matched_high else 0.50
            tactic_summary = f"Active psychological manipulation: {', '.join(tactics_observed[:3])}."

        w_tac = self.config.weight_tactic_manipulation
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.TACTIC_MANIPULATION,
                engine_name="TacticIntelligenceEngine",
                raw_score=round(tactic_risk, 3),
                weight=w_tac,
                weighted_score=round(tactic_risk * w_tac, 3),
                confidence=0.88 if tactics_observed else 0.40,
                evidence_summary=tactic_summary,
            )
        )

        # 5. Journey Stage Dimension & Pre-Loss Risk
        stage_risk = 0.0
        stage_urgency = 0.20
        stage_name = journey_stage or "INITIAL_CONTACT"
        stage_summary = f"Lifecycle stage: {stage_name}."
        if journey_stage:
            dimensions_evaluated += 1
            multiplier = self.config.journey_urgency.get(journey_stage, 0.30)
            stage_urgency = multiplier
            if multiplier >= 0.80:
                stage_risk = 0.85
                stage_summary = f"Critical pre-loss stage reached: {journey_stage} (High loss potential)."
            else:
                stage_risk = multiplier * 0.60

        w_jrn = self.config.weight_journey_stage
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.JOURNEY_STAGE,
                engine_name="JourneyEngineService",
                raw_score=round(stage_risk, 3),
                weight=w_jrn,
                weighted_score=round(stage_risk * w_jrn, 3),
                confidence=0.85 if journey_stage else 0.40,
                evidence_summary=stage_summary,
            )
        )

        # 6. ScamDNA Similarity Dimension
        dna_risk = 0.0
        dna_summary = "No matching ScamDNA profile found."
        if known_dna_similarity is not None:
            dimensions_evaluated += 1
            dna_risk = max(0.0, min(1.0, known_dna_similarity))
            if dna_risk >= 0.70:
                dna_summary = f"High similarity ({dna_risk*100:.0f}%) to verified scam behavioral fingerprint."
            else:
                dna_summary = f"Moderate similarity ({dna_risk*100:.0f}%) to historical patterns."

        w_dna = self.config.weight_scam_dna
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.SCAM_DNA,
                engine_name="ScamDNAService",
                raw_score=round(dna_risk, 3),
                weight=w_dna,
                weighted_score=round(dna_risk * w_dna, 3),
                confidence=0.90 if known_dna_similarity is not None else 0.35,
                evidence_summary=dna_summary,
            )
        )

        # 7. Campaign Intelligence & Outbreak Radar Dimension
        campaign_risk = 0.0
        campaign_urgency = 0.20
        campaign_summary = "Not associated with any active scam campaign."
        matched_camp = None

        # Check in campaign service if entity or incident connects to active campaign
        for c in campaign_service._campaigns.values():
            if (vpa and (vpa in c.payment_profile or any(vpa in m for m in c.active_mutations))) or \
               (phone and (phone in c.infrastructure_profile or any(phone in m for m in c.active_mutations))) or \
               (url and any(u in url for u in c.infrastructure_profile)):
                matched_camp = c
                break

        if matched_camp:
            dimensions_evaluated += 1
            if matched_camp.lifecycle_state.value == "OUTBREAK":
                campaign_risk = 1.00
                campaign_urgency = 1.00
                campaign_summary = f"CRITICAL OUTBREAK: Connected to active campaign '{matched_camp.title}' (+{int(matched_camp.growth_multiplier*100)}% surge)."
            elif matched_camp.lifecycle_state.value == "SURGING":
                campaign_risk = 0.85
                campaign_urgency = 0.85
                campaign_summary = f"SURGING THREAT: Connected to active campaign '{matched_camp.title}'."
            elif matched_camp.lifecycle_state.value == "RESURGING":
                campaign_risk = 0.80
                campaign_urgency = 0.75
                campaign_summary = f"RESURGENT CAMPAIGN: Connected to revived campaign '{matched_camp.title}'."
            else:
                campaign_risk = 0.60
                campaign_urgency = 0.50
                campaign_summary = f"Connected to tracked campaign: {matched_camp.title}."

        w_camp = self.config.weight_campaign_outbreak
        contributions.append(
            SignalContribution(
                dimension=DecisionDimension.CAMPAIGN_OUTBREAK,
                engine_name="CampaignIntelligenceService",
                raw_score=round(campaign_risk, 3),
                weight=w_camp,
                weighted_score=round(campaign_risk * w_camp, 3),
                confidence=0.95 if matched_camp else 0.40,
                evidence_summary=campaign_summary,
            )
        )

        # 8. Contradictory Evidence Discounting
        counter_discount = 0.0
        counter_reasons: List[str] = []
        if is_official_domain:
            counter_discount += 0.30
            counter_reasons.append("Official established domain verified")
        if counter_evidence_signals:
            for s in counter_evidence_signals:
                counter_discount += 0.15
                counter_reasons.append(s)

        counter_discount = min(self.config.counter_discount_factor, counter_discount)
        if counter_discount > 0:
            contributions.append(
                SignalContribution(
                    dimension=DecisionDimension.COUNTER_EVIDENCE,
                    engine_name="EvidenceEngine",
                    raw_score=round(counter_discount, 3),
                    weight=1.0,
                    weighted_score=round(counter_discount, 3),
                    confidence=0.95,
                    evidence_summary=f"Counter-evidence discount applied: {', '.join(counter_reasons)}.",
                    is_counter_evidence=True,
                )
            )

        # ---------------------------------------------------------------------
        # Tripartite Scoring Calculations
        # ---------------------------------------------------------------------
        # Calibrate risk against actively evaluated dimensions
        evaluated_contributions = [
            c for c in contributions
            if not c.is_counter_evidence and c.raw_score > 0.0
        ]
        active_weight = sum(c.weight for c in evaluated_contributions)
        positive_weighted = sum(c.weighted_score for c in evaluated_contributions)

        if active_weight > 0:
            # Calibrate risk normalized by active dimensions
            raw_risk = positive_weighted / active_weight
        else:
            raw_risk = 0.05

        # If campaign outbreak matches, risk is pinned to critical
        if matched_camp and matched_camp.lifecycle_state.value == "OUTBREAK":
            raw_risk = max(raw_risk, 0.95)
        elif matched_camp and matched_camp.lifecycle_state.value == "SURGING":
            raw_risk = max(raw_risk, 0.75)

        # Apply counter-evidence discount
        calibrated_risk = max(0.0, min(1.0, raw_risk * (1.0 - counter_discount)))

        # Uncertainty penalty if too few dimensions evaluated
        missing_dimensions = max(0, 5 - dimensions_evaluated)
        uncertainty_penalty = missing_dimensions * self.config.uncertainty_penalty

        # Confidence calculation
        avg_signal_conf = sum(c.confidence for c in contributions if not c.is_counter_evidence) / max(1, len(contributions))
        confidence = max(0.10, min(0.98, avg_signal_conf - uncertainty_penalty))

        # Urgency calculation
        urgency = max(tactic_urgency, stage_urgency, campaign_urgency)
        if calibrated_risk < 0.25:
            urgency = min(urgency, 0.20)

        # ---------------------------------------------------------------------
        # Map to Tripartite Bands
        # ---------------------------------------------------------------------
        if calibrated_risk >= 0.85:
            risk_band = TripartiteRiskBand.CRITICAL
        elif calibrated_risk >= 0.65:
            risk_band = TripartiteRiskBand.HIGH
        elif calibrated_risk >= 0.40:
            risk_band = TripartiteRiskBand.MEDIUM
        elif calibrated_risk >= 0.20:
            risk_band = TripartiteRiskBand.LOW
        else:
            risk_band = TripartiteRiskBand.BENIGN

        if confidence >= 0.85:
            conf_band = TripartiteConfidenceBand.VERY_HIGH
        elif confidence >= 0.70:
            conf_band = TripartiteConfidenceBand.HIGH
        elif confidence >= 0.50:
            conf_band = TripartiteConfidenceBand.MEDIUM
        elif confidence >= 0.30:
            conf_band = TripartiteConfidenceBand.LOW
        else:
            conf_band = TripartiteConfidenceBand.VERY_LOW

        if urgency >= 0.85:
            urg_band = TripartiteUrgencyBand.IMMEDIATE_INTERVENTION
        elif urgency >= 0.60:
            urg_band = TripartiteUrgencyBand.URGENT
        elif urgency >= 0.35:
            urg_band = TripartiteUrgencyBand.ELEVATED
        else:
            urg_band = TripartiteUrgencyBand.LOW

        # ---------------------------------------------------------------------
        # Action Decision Synthesis
        # ---------------------------------------------------------------------
        primary_action = ActionDecision.ALLOW
        secondary_actions: List[ActionDecision] = []
        is_pre_loss = False

        if (matched_camp and matched_camp.lifecycle_state.value == "OUTBREAK") or (
            calibrated_risk >= self.config.block_min_risk
            and confidence >= self.config.block_min_conf
            and urgency >= self.config.block_min_urg
        ):
            primary_action = ActionDecision.BLOCK_PRE_LOSS
            secondary_actions = [ActionDecision.DELAY_PAYMENT, ActionDecision.STRONG_WARNING]
            is_pre_loss = True
            headline = "Pre-Loss Alert: Severe Scam Threat Detected"
            message = "This interaction matches an active high-velocity scam campaign. We strongly recommend aborting any fund transfers or credential sharing immediately."
            steps = [
                "Do NOT transfer money or share OTPs / PINs under any circumstances.",
                "Disconnect active calls or screen-sharing sessions (AnyDesk, TeamViewer).",
                "Report this identifier to cybercrime helpline (1930) or your bank.",
            ]
        elif calibrated_risk >= self.config.delay_min_risk and urgency >= self.config.delay_min_urg:
            primary_action = ActionDecision.DELAY_PAYMENT
            secondary_actions = [ActionDecision.STRONG_WARNING, ActionDecision.VERIFY_INDEPENDENTLY]
            is_pre_loss = True
            headline = "High Urgency Warning: Delay Transfer"
            message = "Signs of high-pressure social engineering and advance-fee fraud detected. Pause all payment actions for a cooling-off period."
            steps = [
                "Enforce a 2-hour cooling-off period before initiating payment.",
                "Verify payment beneficiary through official bank statements, not via WhatsApp or caller advice.",
                "Call the recipient on their known, verified personal contact number.",
            ]
        elif calibrated_risk >= self.config.strong_warn_min_risk and confidence >= self.config.strong_warn_min_conf:
            primary_action = ActionDecision.STRONG_WARNING
            secondary_actions = [ActionDecision.VERIFY_INDEPENDENTLY]
            headline = "Strong Scam Warning"
            message = "Multiple confirmed deceptive markers observed across message semantics, link safety, and pressure tactics."
            steps = [
                "Do not click unsolicited links or download attachments.",
                "Be aware: Government agencies (CBI, Police, RBI) NEVER conduct digital arrests or demand money via UPI.",
            ]
        elif calibrated_risk >= self.config.warn_min_risk:
            primary_action = ActionDecision.WARN
            secondary_actions = [ActionDecision.VERIFY_INDEPENDENTLY]
            headline = "Caution Advised: Suspicious Indicators"
            message = "Unverified entities or moderate urgency detected in this interaction."
            steps = [
                "Proceed with caution. Do not share sensitive personal information.",
                "Double-check official domain URLs before entering passwords.",
            ]
        elif calibrated_risk >= self.config.verify_min_risk and confidence <= self.config.verify_max_conf:
            primary_action = ActionDecision.VERIFY_INDEPENDENTLY
            secondary_actions = [ActionDecision.EDUCATE]
            headline = "Verify Independently"
            message = "This communication could not be verified through official directory channels."
            steps = [
                "Contact the claimed organization directly using their official website or customer care app.",
                "Do not call back phone numbers provided inside SMS or email alerts.",
            ]
        elif calibrated_risk >= self.config.educate_min_risk:
            primary_action = ActionDecision.EDUCATE
            secondary_actions = [ActionDecision.ALLOW]
            headline = "Educational Notice"
            message = "Low risk detected, but common patterns resemble promotional or unverified outreach."
            steps = [
                "Remember: Reputable services never ask for UPI PIN to receive money.",
            ]
        else:
            primary_action = ActionDecision.ALLOW
            secondary_actions = []
            headline = "No High-Risk Threat Detected"
            message = "This interaction does not show signs of malicious coercion or scam operations."
            steps = ["Standard safe digital practices apply."]

        return TripartiteDecision(
            decision_id=f"dec_{uuid4().hex[:10]}",
            incident_id=incident_id,
            risk_score=round(calibrated_risk, 3),
            risk_band=risk_band,
            confidence_score=round(confidence, 3),
            confidence_band=conf_band,
            urgency_score=round(urgency, 3),
            urgency_band=urg_band,
            primary_action=primary_action,
            secondary_actions=secondary_actions,
            consumer_headline=headline,
            consumer_message=message,
            recommended_steps=steps,
            signal_contributions=contributions,
            contradictory_discount=round(counter_discount, 3),
            uncertainty_penalty=round(uncertainty_penalty, 3),
            matched_campaign_id=matched_camp.campaign_id if matched_camp else None,
            campaign_title=matched_camp.title if matched_camp else None,
            outbreak_status=matched_camp.lifecycle_state.value if matched_camp else None,
            pre_loss_intervention=is_pre_loss,
            scored_at=datetime.now(timezone.utc),
            engine_version=self.config.engine_version,
        )


# Global singleton
decision_fusion_engine = TripartiteDecisionFusionEngine()
