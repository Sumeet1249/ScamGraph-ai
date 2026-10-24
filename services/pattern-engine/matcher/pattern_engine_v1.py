"""Deterministic & Explainable Scam Pattern Engine V1 (Step 12).

Implements weighted partial and temporal sequence matching without ML or LLMs.
Consumes declarative YAML pattern definitions and outputs canonical PatternMatch objects.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from services.api.app.domain import (
    PatternMatch,
    MatchLevel,
    EventType,
    Evidence,
)


class PatternDefinition:
    """Represents a validated declarative scam pattern loaded from YAML."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.name = data["name"]
        self.description = data.get("description", "")
        self.required_signals = set(data.get("required_signals", []))
        self.supporting_signals = set(data.get("supporting_signals", []))
        self.event_sequence = data.get("event_sequence", [])
        self.optional_signals = set(data.get("optional_signals", []))
        self.contradictory_signals = set(data.get("contradictory_signals", []))
        self.stages = data.get("stages", [])
        self.common_next_stage = data.get("common_next_stage", "PAYMENT_INTENT")
        self.intervention_guidance = data.get("intervention_guidance", {})


class PatternEngineV1:
    """Evaluates incidents against deterministic YAML patterns."""

    def __init__(self, patterns_dir: Optional[Path] = None):
        if patterns_dir is None:
            # Default to data/patterns
            patterns_dir = Path(__file__).resolve().parents[3] / "data" / "patterns"
        self.patterns_dir = patterns_dir
        self.patterns: Dict[str, PatternDefinition] = {}
        self.load_patterns()

    def load_patterns(self):
        """Loads all YAML pattern files from the patterns directory."""
        if not self.patterns_dir.exists():
            return

        for p_file in self.patterns_dir.glob("*.yaml"):
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "id" in data:
                        self.patterns[data["id"]] = PatternDefinition(data)
            except Exception as e:
                print(f"Warning: Failed loading pattern file {p_file}: {e}")

    def evaluate_pattern(
        self,
        pattern_id: str,
        observed_signals: List[str],
        observed_events: List[str],
        evidence_ids: Optional[List[str]] = None,
    ) -> Optional[PatternMatch]:
        """Evaluates observed signals and event sequences against a specific pattern."""
        pat = self.patterns.get(pattern_id)
        if not pat:
            return None

        obs_signal_set = set(observed_signals)
        obs_evidence_ids = evidence_ids or []

        # 1. Signal Match Calculation (Weight: 50% Required, 30% Supporting)
        matched_required = pat.required_signals.intersection(obs_signal_set)
        matched_supporting = pat.supporting_signals.intersection(obs_signal_set)
        matched_contradictory = pat.contradictory_signals.intersection(obs_signal_set)

        req_score = len(matched_required) / len(pat.required_signals) if pat.required_signals else 1.0
        sup_score = len(matched_supporting) / len(pat.supporting_signals) if pat.supporting_signals else 0.0

        # Contradictory penalty (e.g. verified merchant domain deducts points)
        contra_penalty = 0.35 if matched_contradictory else 0.0

        # 2. Temporal Sequence Match Calculation (Weight: 20%)
        # Checks if observed events appear in the defined event_sequence order
        seq_score, matched_seq_events, missing_seq_events = self._compute_sequence_alignment(
            pat.event_sequence, observed_events
        )

        # 3. Composite Weighted Score (0.0 to 1.0)
        # Required signals: 0.50, Supporting signals: 0.30, Sequence order: 0.20
        raw_score = (0.50 * req_score) + (0.30 * sup_score) + (0.20 * seq_score) - contra_penalty
        final_score = max(0.0, min(1.0, raw_score))

        # 4. Discrete Match Level (Explainable index, NOT a probability)
        # Rule: A STRONG match strictly requires all required signals and at least 2 sequence events
        all_required_present = len(matched_required) == len(pat.required_signals)
        has_multi_stage_progression = len(matched_seq_events) >= 2 if pat.event_sequence else True

        if final_score >= 0.70 and all_required_present and has_multi_stage_progression:
            match_level = MatchLevel.STRONG
        elif final_score >= 0.40:
            match_level = MatchLevel.MODERATE
        elif final_score >= 0.18:
            match_level = MatchLevel.WEAK
        else:
            match_level = MatchLevel.NONE

        # Determine current stage from matched events
        current_stage = "INITIAL_CONTACT"
        if matched_seq_events:
            last_ev = matched_seq_events[-1]
            if "PAYMENT" in last_ev:
                current_stage = "PAYMENT_REQUEST"
            elif "OTP" in last_ev:
                current_stage = "CREDENTIAL_OTP_HARVEST"
            elif "URL" in last_ev:
                current_stage = "SUSPICIOUS_LINK"

        return PatternMatch(
            pattern_id=pat.id,
            pattern_name=pat.name,
            matched_events=matched_seq_events,
            missing_events=missing_seq_events,
            supporting_evidence_ids=obs_evidence_ids,
            match_level=match_level,
            current_stage=current_stage,
            common_next_stage=pat.common_next_stage,
            confidence=round(final_score, 2),
        )

    def match_best_pattern(
        self,
        observed_signals: List[str],
        observed_events: List[str],
        evidence_ids: Optional[List[str]] = None,
    ) -> Optional[PatternMatch]:
        """Finds the highest-scoring matching pattern."""
        best_match: Optional[PatternMatch] = None
        for pid in self.patterns.keys():
            match = self.evaluate_pattern(pid, observed_signals, observed_events, evidence_ids)
            if match and match.match_level != MatchLevel.NONE:
                if best_match is None or match.confidence > best_match.confidence:
                    best_match = match
        return best_match

    @staticmethod
    def _compute_sequence_alignment(
        expected_seq: List[str],
        observed_events: List[str],
    ) -> Tuple[float, List[str], List[str]]:
        """Calculates order-aware sequence match score.
        
        Returns:
            (sequence_score, matched_events, missing_events)
        """
        if not expected_seq or not observed_events:
            return 0.0, [], expected_seq

        matched_events = [ev for ev in observed_events if ev in expected_seq]
        missing_events = [ev for ev in expected_seq if ev not in observed_events]

        if not matched_events:
            return 0.0, [], expected_seq

        # Check relative temporal order: count strictly increasing index matches
        last_found_idx = -1
        in_order_count = 0
        for ev in observed_events:
            if ev in expected_seq:
                curr_idx = expected_seq.index(ev)
                if curr_idx > last_found_idx:
                    in_order_count += 1
                    last_found_idx = curr_idx

        order_ratio = in_order_count / len(matched_events) if matched_events else 0.0
        coverage_ratio = len(set(matched_events)) / len(expected_seq)

        # Sequence score is high only when events appear both in sequence and coverage
        seq_score = (0.6 * order_ratio) + (0.4 * coverage_ratio)
        return round(seq_score, 2), matched_events, missing_events


# Global instance
pattern_engine_v1 = PatternEngineV1()
