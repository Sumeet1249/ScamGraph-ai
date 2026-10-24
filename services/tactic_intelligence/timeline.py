"""Conversation Timeline and Psychological Escalation Analyzer for ScamGraph AI V2.

Reconstructs the chronological progression of tactics across conversation turns,
computes manipulation density and normalized tactic vectors (ScamDNA foundation),
and derives proactive candidate intervention signals.
"""

from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.tactics import (
    TacticSignal,
    TacticTimeline,
    TacticType,
)


class TacticTimelineAnalyzer:
    """Analyzes a chronological series of tactic signals across message turns."""

    def build_timeline(
        self,
        signals: List[TacticSignal],
        conversation_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        total_turns: int = 1,
    ) -> TacticTimeline:
        """Constructs an integrated TacticTimeline from ordered signals."""
        # 1. Normalized Tactic Vector (ScamDNA foundation)
        tactic_vector: Dict[str, float] = {}
        for sig in signals:
            if not sig.is_negated:
                t_name = sig.tactic.value
                tactic_vector[t_name] = max(tactic_vector.get(t_name, 0.0), round(sig.confidence, 3))

        # 2. Manipulation Density
        active_signals = [s for s in signals if not s.is_negated and not s.is_quoted]
        effective_turns = max(1, total_turns)
        manipulation_density = round(len(active_signals) / effective_turns, 2)

        # 3. Escalation Analysis
        is_escalating, escalation_desc = self.detect_escalation(signals)

        # 4. Proactive Candidate Interventions
        interventions = self.generate_intervention_candidates(signals)

        return TacticTimeline(
            conversation_id=conversation_id,
            incident_id=incident_id,
            signals=signals,
            tactic_vector=tactic_vector,
            manipulation_density=manipulation_density,
            escalation_signal=is_escalating,
            escalation_description=escalation_desc,
            intervention_candidates=interventions,
        )

    def detect_escalation(self, signals: List[TacticSignal]) -> Tuple[bool, Optional[str]]:
        """Detects whether coercive pressure escalates chronologically across turns."""
        if len(signals) < 2:
            return False, None

        # Sort signals by turn_index if available
        ordered_signals = sorted(signals, key=lambda s: s.turn_index if s.turn_index is not None else 0)

        # Stage buckets:
        # Early: TRUST_BUILDING, GREED, SCARCITY, PLATFORM_MIGRATION
        # Middle: FAKE_REWARD, RECIPROCITY, SOCIAL_PROOF, URGENCY
        # Coercive/Late: PAYMENT_PRESSURE, CREDENTIAL_PRESSURE, REMOTE_ACCESS_PRESSURE, FEAR, THREAT, ISOLATION, SECRECY
        early_tactics = {
            TacticType.AUTHORITY,
            TacticType.IMPERSONATION,
            TacticType.TRUST_BUILDING,
            TacticType.GREED,
            TacticType.SCARCITY,
            TacticType.PLATFORM_MIGRATION,
        }
        middle_tactics = {
            TacticType.FAKE_REWARD,
            TacticType.RECIPROCITY,
            TacticType.SOCIAL_PROOF,
            TacticType.URGENCY,
        }
        coercive_tactics = {
            TacticType.PAYMENT_PRESSURE,
            TacticType.CREDENTIAL_PRESSURE,
            TacticType.REMOTE_ACCESS_PRESSURE,
            TacticType.FEAR,
            TacticType.THREAT,
            TacticType.ISOLATION,
            TacticType.SECRECY,
        }

        has_early = False
        has_coercive_late = False
        early_names: List[str] = []
        coercive_names: List[str] = []

        # Split turns into halves
        midpoint = len(ordered_signals) // 2
        first_half = ordered_signals[:midpoint]
        second_half = ordered_signals[midpoint:]

        for s in first_half:
            if s.tactic in early_tactics or s.tactic in middle_tactics:
                has_early = True
                early_names.append(s.tactic.value)

        for s in second_half:
            if s.tactic in coercive_tactics:
                has_coercive_late = True
                coercive_names.append(s.tactic.value)

        if has_early and has_coercive_late:
            desc = (
                f"Tactic escalation detected: shifted from early grooming/reward "
                f"({', '.join(set(early_names))}) to aggressive pressure/coercion "
                f"({', '.join(set(coercive_names))})."
            )
            return True, desc

        return False, None

    def generate_intervention_candidates(self, signals: List[TacticSignal]) -> List[str]:
        """Identifies proactive intervention candidates based on active manipulation tactics."""
        active_tactics: Set[TacticType] = {s.tactic for s in signals if not s.is_negated and not s.is_quoted}
        candidates: List[str] = []

        # 1. Anti-Isolation Candidate (SECRECY or ISOLATION + high-impact demand)
        has_isolation = TacticType.ISOLATION in active_tactics or TacticType.SECRECY in active_tactics
        has_high_impact = any(
            t in active_tactics
            for t in (TacticType.PAYMENT_PRESSURE, TacticType.CREDENTIAL_PRESSURE, TacticType.REMOTE_ACCESS_PRESSURE)
        )
        if has_isolation and has_high_impact:
            candidates.append("ANTI_ISOLATION_INTERVENTION_CANDIDATE")

        # 2. Payment Protection Candidate
        if TacticType.PAYMENT_PRESSURE in active_tactics:
            candidates.append("PAYMENT_INTERVENTION_CANDIDATE")

        # 3. Credential Protection Candidate
        if TacticType.CREDENTIAL_PRESSURE in active_tactics:
            candidates.append("CREDENTIAL_PROTECTION_CANDIDATE")

        # 4. Remote Access Warning Candidate
        if TacticType.REMOTE_ACCESS_PRESSURE in active_tactics:
            candidates.append("REMOTE_ACCESS_WARNING_CANDIDATE")

        # 5. General Verification Advice Candidate
        if TacticType.AUTHORITY in active_tactics or TacticType.IMPERSONATION in active_tactics:
            candidates.append("INDEPENDENT_VERIFICATION_CANDIDATE")

        return candidates

    @staticmethod
    def map_tactics_to_pattern_signals(signals: List[TacticSignal]) -> List[str]:
        """Translates tactic signals into pattern engine signal codes."""
        out: Set[str] = set()
        for s in signals:
            if s.is_negated or s.is_quoted:
                continue
            out.add(s.tactic.value)
            if s.tactic in (TacticType.AUTHORITY, TacticType.IMPERSONATION):
                out.add("LAW_ENFORCEMENT_IMPERSONATION")
                out.add("CBI_POLICE_CUSTOMS_IDENTITY")
            elif s.tactic in (TacticType.FEAR, TacticType.THREAT):
                out.add("LEGAL_PENALTY_FEAR_THREAT")
            elif s.tactic == TacticType.ISOLATION:
                out.add("VIDEO_CALL_ISOLATION_REQUEST")
            elif s.tactic == TacticType.SECRECY:
                out.add("SECRECY_COERCION")
            elif s.tactic == TacticType.PAYMENT_PRESSURE:
                out.add("SECURITY_DEPOSIT_DEMAND")
            elif s.tactic == TacticType.CREDENTIAL_PRESSURE:
                out.add("OTP_HARVEST_DEMAND")
            elif s.tactic == TacticType.REMOTE_ACCESS_PRESSURE:
                out.add("REMOTE_ACCESS_APP_DEMAND")
            elif s.tactic == TacticType.PLATFORM_MIGRATION:
                out.add("TELEGRAM_MIGRATION")
            elif s.tactic in (TacticType.TRUST_BUILDING, TacticType.FAKE_REWARD, TacticType.RECIPROCITY):
                out.add("SMALL_TASK_REWARD")
            elif s.tactic == TacticType.GREED:
                out.add("GUARANTEED_PROFIT_LURE")
        return sorted(out)

