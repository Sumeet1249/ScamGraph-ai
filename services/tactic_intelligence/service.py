"""Central Orchestration Service for Tactic Intelligence in ScamGraph AI V2.

Unifies single-message evaluation, multi-turn conversation timelines, entity linking,
caching, consumer/analyst serialization, and graceful degraded-mode execution.
"""

from typing import Any, Dict, List, Optional

from packages.schemas.conversation import Conversation, ConversationMessage, SpeakerRole
from packages.schemas.entity import Entity
from packages.schemas.tactics import (
    ConsumerTacticWarning,
    TacticSignal,
    TacticTimeline,
)
from ml.tactics.classifier import MultiLabelTacticClassifier
from ml.tactics.rules import RuleBasedTacticEngine
from services.tactic_intelligence.cache import TacticCache
from services.tactic_intelligence.entity_link import TacticEntityLinker
from services.tactic_intelligence.serializer import TacticSerializer
from services.tactic_intelligence.timeline import TacticTimelineAnalyzer


class TacticIntelligenceService:
    """Production service for human manipulation and psychological tactic detection."""

    def __init__(
        self,
        classifier: Optional[MultiLabelTacticClassifier] = None,
        cache: Optional[TacticCache] = None,
        timeline_analyzer: Optional[TacticTimelineAnalyzer] = None,
        entity_linker: Optional[TacticEntityLinker] = None,
    ):
        self.classifier = classifier or MultiLabelTacticClassifier()
        self.fallback_rule_engine = RuleBasedTacticEngine()
        self.cache = cache or TacticCache()
        self.timeline_analyzer = timeline_analyzer or TacticTimelineAnalyzer()
        self.entity_linker = entity_linker or TacticEntityLinker()

    def analyze_text(
        self,
        text: str,
        speaker_role: SpeakerRole = SpeakerRole.UNKNOWN_ACTOR,
        artifact_id: Optional[str] = None,
        event_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        turn_index: Optional[int] = None,
        entities: Optional[List[Entity]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[TacticSignal]:
        """Analyzes text for manipulation tactics with caching and degraded fallback."""
        if not text or not text.strip():
            return []

        # Check Cache
        cached = self.cache.get(text, context)
        if cached is not None:
            if entities:
                cached = self.entity_linker.link_entities_to_tactics(cached, entities)
            return cached

        try:
            # Primary path: hybrid classifier
            signals = self.classifier.classify(
                text=text,
                speaker_role=speaker_role,
                artifact_id=artifact_id,
                event_id=event_id,
                incident_id=incident_id,
                conversation_id=conversation_id,
                turn_index=turn_index,
                enable_semantic=True,
            )
        except Exception as e:
            # Degraded path: fallback to deterministic rule engine
            signals = self.fallback_rule_engine.match(
                text=text,
                artifact_id=artifact_id,
                event_id=event_id,
                incident_id=incident_id,
                conversation_id=conversation_id,
                turn_index=turn_index,
            )
            for s in signals:
                s.metadata["degraded"] = True
                s.metadata["error"] = str(e)

        # Link entities if provided
        if entities:
            signals = self.entity_linker.link_entities_to_tactics(signals, entities)

        # Store in Cache
        self.cache.set(text, signals, context)
        return signals

    def analyze_conversation(
        self,
        conversation: Conversation,
        entities: Optional[List[Entity]] = None,
    ) -> TacticTimeline:
        """Analyzes an ordered multi-turn dialogue to construct an integrated timeline."""
        all_signals: List[TacticSignal] = []

        for msg in conversation.messages:
            msg_signals = self.analyze_text(
                text=msg.text,
                speaker_role=msg.speaker_role,
                conversation_id=conversation.conversation_id,
                turn_index=msg.turn_index,
                entities=entities,
            )
            # Update turn tactics metadata on the message
            msg.tactics = [s.tactic.value for s in msg_signals]
            msg.requested_actions = [a.value for s in msg_signals for a in s.requested_actions]
            all_signals.extend(msg_signals)

        timeline = self.timeline_analyzer.build_timeline(
            signals=all_signals,
            conversation_id=conversation.conversation_id,
            total_turns=len(conversation.messages),
        )
        return timeline

    def serialize_consumer_warning(self, timeline: TacticTimeline) -> ConsumerTacticWarning:
        """Generates privacy-safe consumer warning."""
        return TacticSerializer.serialize_consumer_warning(timeline)

    def serialize_analyst_view(self, timeline: TacticTimeline) -> Dict[str, Any]:
        """Generates forensic analyst timeline."""
        return TacticSerializer.serialize_analyst_view(timeline)
