"""Journey Template Matching, Sequence Alignment & Progress Intelligence for ScamGraph AI V2.

Compares observed stage sequences against declarative family templates (Task Scam, Digital Arrest,
Investment, KYC Bank, Fake Support), derives family hypotheses, and computes progress metrics.
"""

from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.journey import (
    JourneyEvent,
    JourneyFeatureVector,
    JourneyProgress,
    JourneyStage,
    StageCategory,
    get_stage_category,
)
from services.journey_engine.templates import (
    JOURNEY_TEMPLATES,
    JourneyTemplate,
)


class JourneyTemplateMatcher:
    """Evaluates sequence alignment against declarative templates and computes progress vectors."""

    def match_family(
        self,
        observed_stages: List[JourneyStage],
        observed_tactics: Set[str],
    ) -> Tuple[str, Dict[str, float], float]:
        """Aligns the observed stage sequence against known scam templates.
        
        Enforces Section 31 rule: If sequence does not match known templates with sufficient
        confidence, returns 'UNKNOWN' (Emerging Journey).
        Separates Family Confidence from Journey Suspicion (Section 61).
        """
        if not observed_stages:
            return "UNKNOWN", {"UNKNOWN": 1.0}, 0.0

        stage_set = set(observed_stages)
        scores: Dict[str, float] = {}

        # If only generic non-monetization stages observed without tactics, return UNKNOWN
        if len(stage_set - {JourneyStage.CONTACT, JourneyStage.UNKNOWN}) == 0 and not observed_tactics:
            return "UNKNOWN", {"UNKNOWN": 1.0}, 0.0

        for family_id, tmpl in JOURNEY_TEMPLATES.items():
            # 1. Required stages match (Weight: 40%)
            matched_req = tmpl.required_stages.intersection(stage_set)
            req_ratio = len(matched_req) / len(tmpl.required_stages) if tmpl.required_stages else 1.0

            # 2. Sequence order alignment (Weight: 30%)
            # Count ordered subsequence matches
            matched_seq_count = 0
            curr_tmpl_idx = 0
            for stg in observed_stages:
                while curr_tmpl_idx < len(tmpl.expected_sequence) and tmpl.expected_sequence[curr_tmpl_idx] != stg:
                    curr_tmpl_idx += 1
                if curr_tmpl_idx < len(tmpl.expected_sequence):
                    matched_seq_count += 1
                    curr_tmpl_idx += 1

            seq_ratio = matched_seq_count / max(1, len(observed_stages))

            # 3. Family-specific tactic affinity (Weight: 30%)
            tactic_bonus = 0.0
            if family_id == "DIGITAL_ARREST" and ("AUTHORITY" in observed_tactics or "ISOLATION" in observed_tactics):
                tactic_bonus += 0.30
            elif family_id == "JOB_TASK" and ("TRUST_BUILDING" in observed_tactics or "PLATFORM_MIGRATION" in observed_tactics):
                tactic_bonus += 0.30
            elif family_id == "INVESTMENT" and ("GREED" in observed_tactics or "RECIPROCITY" in observed_tactics):
                tactic_bonus += 0.30
            elif family_id == "KYC_BANK" and ("CREDENTIAL_PRESSURE" in observed_tactics or "IMPERSONATION" in observed_tactics):
                tactic_bonus += 0.30
            elif family_id == "FAKE_SUPPORT_REFUND" and ("REMOTE_ACCESS_PRESSURE" in observed_tactics or "IMPERSONATION" in observed_tactics):
                tactic_bonus += 0.30

            # Composite score
            composite = (0.40 * req_ratio) + (0.30 * seq_ratio) + tactic_bonus
            # If template requires monetization or multiple distinct stages that are not present and no tactics matched, damp score
            if len(tmpl.required_stages) > 1 and req_ratio < 0.6 and tactic_bonus == 0.0:
                composite = min(0.35, composite)

            scores[family_id] = round(min(1.0, composite), 3)

        # Normalize hypotheses to probability distribution
        total_score = sum(scores.values())
        hypotheses: Dict[str, float] = {}
        if total_score > 0:
            for fid, sc in scores.items():
                hypotheses[fid] = round(sc / total_score, 3)
        else:
            hypotheses = {"UNKNOWN": 1.0}

        # Select highest scoring family
        sorted_families = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_family, top_score = sorted_families[0]

        if top_score < 0.45:
            # Low match against known templates -> mark UNKNOWN emerging journey
            return "UNKNOWN", hypotheses, round(top_score, 2)

        return top_family, hypotheses, round(top_score, 2)

    def compute_progress(
        self,
        current_stage: JourneyStage,
        observed_stages: List[JourneyStage],
        scam_family: str,
    ) -> JourneyProgress:
        """Calculates multi-dimensional progress intelligence without naive stage-index counting."""
        category = get_stage_category(current_stage)

        # Monetization proximity
        if category == StageCategory.MONETIZATION:
            monetization_prox = 1.0
        elif current_stage in (JourneyStage.CREDENTIAL_REQUEST, JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.URGENCY):
            monetization_prox = 0.75
        elif current_stage in (JourneyStage.TRUST_BUILDING, JourneyStage.PLATFORM_MIGRATION):
            monetization_prox = 0.45
        else:
            monetization_prox = 0.20

        # Loss proximity
        if current_stage in (JourneyStage.PAYMENT_ESCALATION, JourneyStage.WITHDRAWAL_BLOCK, JourneyStage.RECOVERY_FEE):
            loss_prox = 1.0
        elif current_stage in (JourneyStage.INITIAL_PAYMENT, JourneyStage.CREDENTIAL_REQUEST):
            loss_prox = 0.80
        elif current_stage in (JourneyStage.URGENCY, JourneyStage.THREAT_OR_PRESSURE):
            loss_prox = 0.60
        else:
            loss_prox = 0.15

        # Escalation level
        if current_stage in (JourneyStage.WITHDRAWAL_BLOCK, JourneyStage.RECOVERY_FEE, JourneyStage.PAYMENT_ESCALATION):
            escalation_level = "CRITICAL"
        elif current_stage in (JourneyStage.INITIAL_PAYMENT, JourneyStage.CREDENTIAL_REQUEST, JourneyStage.THREAT_OR_PRESSURE):
            escalation_level = "HIGH"
        elif current_stage in (JourneyStage.URGENCY, JourneyStage.PLATFORM_MIGRATION):
            escalation_level = "MEDIUM"
        else:
            escalation_level = "LOW"

        # Unique completed steps
        completed: List[str] = []
        for s in observed_stages:
            name = s.value.replace("_", " ").title()
            if name not in completed:
                completed.append(name)

        # Possible future steps from template
        template = JOURNEY_TEMPLATES.get(scam_family)
        future_steps: List[str] = []
        if template and current_stage in template.allowed_transitions:
            future_steps = [
                stg.value.replace("_", " ").title()
                for stg in template.allowed_transitions[current_stage]
            ]
        elif not future_steps:
            future_steps = ["Potential payment demand", "Potential credential request"]

        display_stage = current_stage.value.replace("_", " ").title()

        return JourneyProgress(
            current_phase=category,
            monetization_proximity=monetization_prox,
            loss_proximity=loss_prox,
            escalation_level=escalation_level,
            evidence_completeness=round(min(1.0, len(observed_stages) / 5.0), 2),
            display_stage=display_stage,
            completed_steps=completed,
            current_step=display_stage,
            possible_future_steps=future_steps[:3],
        )

    def extract_feature_vector(
        self,
        events: List[JourneyEvent],
        observed_stages: List[JourneyStage],
        scam_family: str,
        family_hypotheses: Dict[str, float],
    ) -> JourneyFeatureVector:
        """Extracts privacy-safe structural representation for future ScamDNA without raw PII."""
        tactic_vector: Dict[str, float] = {}
        channels: List[str] = []
        actions: List[str] = []

        for ev in events:
            if ev.channel not in channels:
                channels.append(ev.channel)
            for a in ev.requested_actions:
                if a not in actions:
                    actions.append(a)
            for t in ev.tactics:
                tactic_vector[t] = max(tactic_vector.get(t, 0.0), 0.90)

        duration = 0.0
        if len(events) >= 2:
            first_t = events[0].timestamp
            last_t = events[-1].timestamp
            duration = max(0.0, (last_t - first_t).total_seconds())

        return JourneyFeatureVector(
            stage_sequence=[s.value for s in observed_stages],
            tactic_vector=tactic_vector,
            channel_sequence=channels,
            requested_action_sequence=actions,
            monetization_velocity=round(len([s for s in observed_stages if get_stage_category(s) == StageCategory.MONETIZATION]) / max(1, len(events)), 2),
            family_distribution=family_hypotheses,
            event_count=len(events),
            total_duration_seconds=duration,
        )
