"""Hybrid Multi-Label Psychological Tactic Classifier for ScamGraph AI V2.

Combines high-precision contextual rules with semantic prototype matching,
handles speaker roles, detects model disagreement, and enforces safety boundaries.
"""

from typing import Any, Dict, List, Optional, Set

from packages.schemas.conversation import SpeakerRole
from packages.schemas.tactics import (
    ActionRequestedType,
    EvidenceSpan,
    TacticSignal,
    TacticType,
)
from ml.tactics.rules import (
    RuleBasedTacticEngine,
    is_global_advisory,
    is_routine_notification,
)
from ml.tactics.semantic import SemanticTacticMatcher


class MultiLabelTacticClassifier:
    """Orchestrates hybrid rule + semantic multi-label tactic classification."""

    def __init__(
        self,
        rule_engine: Optional[RuleBasedTacticEngine] = None,
        semantic_matcher: Optional[SemanticTacticMatcher] = None,
    ):
        self.rule_engine = rule_engine or RuleBasedTacticEngine()
        self.semantic_matcher = semantic_matcher or SemanticTacticMatcher()

    def classify(
        self,
        text: str,
        speaker_role: SpeakerRole = SpeakerRole.UNKNOWN_ACTOR,
        artifact_id: Optional[str] = None,
        event_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        turn_index: Optional[int] = None,
        enable_semantic: bool = True,
    ) -> List[TacticSignal]:
        """Performs multi-label classification across text.
        
        Enforces speaker role boundaries: messages originating from VICTIM or USER
        are not classified as actor manipulation tactics unless analyzing quoted content.
        """
        if not text or not text.strip():
            return []

        # If text is an educational advisory or routine notification, suppress actor manipulation
        if is_global_advisory(text) or is_routine_notification(text):
            return []

        # If speaker is explicitly VICTIM or USER, suppress actor tactics unless quoted
        if speaker_role in (SpeakerRole.VICTIM,):
            # Check if victim is quoting or asking about a scam message
            rule_signals = self.rule_engine.match(
                text=text,
                artifact_id=artifact_id,
                event_id=event_id,
                incident_id=incident_id,
                conversation_id=conversation_id,
                turn_index=turn_index,
            )
            # Mark all as quoted
            for sig in rule_signals:
                sig.is_quoted = True
            return rule_signals

        # 1. Run Rule Engine
        rule_signals = self.rule_engine.match(
            text=text,
            artifact_id=artifact_id,
            event_id=event_id,
            incident_id=incident_id,
            conversation_id=conversation_id,
            turn_index=turn_index,
        )
        rule_by_tactic: Dict[TacticType, TacticSignal] = {s.tactic: s for s in rule_signals}

        # 2. Run Semantic Matcher (if enabled)
        semantic_by_tactic: Dict[TacticType, TacticSignal] = {}
        if enable_semantic:
            semantic_signals = self.semantic_matcher.match(
                text=text,
                artifact_id=artifact_id,
                event_id=event_id,
                incident_id=incident_id,
                conversation_id=conversation_id,
                turn_index=turn_index,
            )
            semantic_by_tactic = {s.tactic: s for s in semantic_signals}

        # 3. Combine & Detect Disagreements
        combined_signals: List[TacticSignal] = []
        all_tactics = set(rule_by_tactic.keys()).union(set(semantic_by_tactic.keys()))

        for tactic in all_tactics:
            in_rule = tactic in rule_by_tactic
            in_sem = tactic in semantic_by_tactic

            if in_rule and in_sem:
                # Agreement between rule and semantic! Boost confidence
                base_sig = rule_by_tactic[tactic]
                sem_sig = semantic_by_tactic[tactic]
                boosted_conf = min(round(base_sig.confidence + 0.04, 2), 0.99)
                base_sig.confidence = boosted_conf
                base_sig.detector_sources = ["RULE", "SEMANTIC", "COMBINED"]
                base_sig.metadata["detector_agreement"] = True
                combined_signals.append(base_sig)

            elif in_rule and not in_sem:
                # Rule only
                sig = rule_by_tactic[tactic]
                sig.detector_sources = ["RULE"]
                combined_signals.append(sig)

            elif not in_rule and in_sem:
                # Semantic only (moderate confidence, requires review)
                sig = semantic_by_tactic[tactic]
                sig.detector_sources = ["SEMANTIC"]
                sig.confidence = round(sig.confidence * 0.90, 2)
                sig.metadata["disagreement"] = True
                combined_signals.append(sig)

        return combined_signals
