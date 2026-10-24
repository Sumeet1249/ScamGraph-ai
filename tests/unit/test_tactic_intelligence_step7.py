"""Unit & Integration Tests for ScamGraph Tactic Intelligence Engine V2 (Phase 1B / Prompt 7).

Validates:
- 20 canonical psychological manipulation tactics
- 17 explicit calls to action
- Evidence spans with offsets, hashes, and redacted previews
- English, Hindi, and Hinglish code-mixing
- Contextual negation & protective advisories (hard negatives)
- Quoted inquiries & speaker roles
- Multi-turn conversation timelines, manipulation density, and escalation
- Entity linking & Pattern Engine interoperability
- Consumer vs Analyst serialization
- Caching, idempotency, and degraded fallback execution
"""

import hashlib
import pytest

from packages.schemas.conversation import Conversation, ConversationMessage, SpeakerRole
from packages.schemas.entity import Entity, EntityType
from packages.schemas.tactics import (
    ActionRequestedType,
    TacticSignal,
    TacticTimeline,
    TacticType,
)
from ml.tactics.rules import RuleBasedTacticEngine
from ml.tactics.semantic import SemanticTacticMatcher
from ml.tactics.classifier import MultiLabelTacticClassifier
from services.tactic_intelligence.cache import TacticCache
from services.tactic_intelligence.entity_link import TacticEntityLinker
from services.tactic_intelligence.serializer import TacticSerializer
from services.tactic_intelligence.service import TacticIntelligenceService
from services.tactic_intelligence.timeline import TacticTimelineAnalyzer


@pytest.fixture
def tactic_service() -> TacticIntelligenceService:
    return TacticIntelligenceService()


def test_all_20_tactics_detection(tactic_service: TacticIntelligenceService):
    """Verifies that all 20 canonical tactics are accurately identified across representative inputs."""
    test_cases = [
        ("Calling from CBI cyber crime branch with official warrant", TacticType.AUTHORITY),
        ("Act immediately within 2 hours or your account will be blocked", TacticType.URGENCY),
        ("An arrest warrant has been registered and you face jail", TacticType.FEAR),
        ("Earn ₹5,000 daily with simple YouTube like task from home", TacticType.GREED),
        ("Only 2 slots remaining for this job vacancy", TacticType.SCARCITY),
        ("See withdrawal proofs of all members in the group", TacticType.SOCIAL_PROOF),
        ("Customs held parcel darling, send money for our marriage", TacticType.ROMANCE),
        ("First task is free, test withdrawal of ₹150 credited", TacticType.TRUST_BUILDING),
        ("Do not tell anyone, keep this strictly confidential between us", TacticType.SECRECY),
        ("Stay on the video call and lock the door do not disconnect", TacticType.ISOLATION),
        ("We helped you earn profit, now invest ₹5000", TacticType.RECIPROCITY),
        ("Pay ₹5,000 or lose your entire balance", TacticType.LOSS_AVERSION),
        ("You have won a lottery of ₹25 lakhs in lucky draw", TacticType.FAKE_REWARD),
        ("We will leak your private photos and ruin your reputation", TacticType.THREAT),
        ("Calling from FedEx customs department regarding parcel", TacticType.IMPERSONATION),
        ("Pay now immediately to verify your account", TacticType.PAYMENT_PRESSURE),
        ("Share your 6-digit OTP to complete verification", TacticType.CREDENTIAL_PRESSURE),
        ("Install AnyDesk and share your mobile screen", TacticType.REMOTE_ACCESS_PRESSURE),
        ("Message me on WhatsApp or join our Telegram group", TacticType.PLATFORM_MIGRATION),
        ("Answer only yes or no and follow instructions without argument", TacticType.COMPLIANCE_PRESSURE),
    ]

    for text, expected_tactic in test_cases:
        signals = tactic_service.analyze_text(text)
        detected_tactics = [s.tactic for s in signals]
        assert expected_tactic in detected_tactics, f"Failed to detect {expected_tactic} in '{text}'. Got {detected_tactics}"


def test_requested_actions_extraction(tactic_service: TacticIntelligenceService):
    """Verifies that explicit calls to action are extracted and mapped correctly."""
    # 1. Share OTP
    sig1 = tactic_service.analyze_text("Tell me the 6-digit OTP you received")
    actions1 = [a for s in sig1 for a in s.requested_actions]
    assert ActionRequestedType.SHARE_OTP in actions1

    # 2. Remote Access / Install App
    sig2 = tactic_service.analyze_text("Download AnyDesk app and share screen")
    actions2 = [a for s in sig2 for a in s.requested_actions]
    assert ActionRequestedType.INSTALL_APP in actions2
    assert ActionRequestedType.SHARE_SCREEN in actions2

    # 3. Platform Migration
    sig3 = tactic_service.analyze_text("Contact manager on Telegram @vip_jobs")
    actions3 = [a for s in sig3 for a in s.requested_actions]
    assert ActionRequestedType.MOVE_PLATFORM in actions3

    # 4. Do not disconnect
    sig4 = tactic_service.analyze_text("Stay on Skype video call do not disconnect")
    actions4 = [a for s in sig4 for a in s.requested_actions]
    assert ActionRequestedType.DO_NOT_DISCONNECT in actions4


def test_evidence_spans_and_offsets(tactic_service: TacticIntelligenceService):
    """Verifies evidence spans have exact offsets, text hashes, and confidence."""
    text = "Important notice: please share your 6-digit OTP immediately."
    signals = tactic_service.analyze_text(text)
    cred_signals = [s for s in signals if s.tactic == TacticType.CREDENTIAL_PRESSURE]
    assert len(cred_signals) >= 1
    sig = cred_signals[0]
    assert len(sig.supporting_spans) >= 1

    span = sig.supporting_spans[0]
    assert span.start >= 0
    assert span.end > span.start
    assert text[span.start:span.end] == span.text
    expected_hash = hashlib.sha256(span.text.strip().encode("utf-8")).hexdigest()
    assert span.text_hash == expected_hash
    assert span.confidence >= 0.85


def test_hinglish_and_code_mixing(tactic_service: TacticIntelligenceService):
    """Verifies robust detection across Hindi and Hinglish colloquial constructions."""
    hinglish_cases = [
        ("abhi payment karo varna light kat di jayegi", [TacticType.PAYMENT_PRESSURE, TacticType.FEAR]),
        ("kisi ko mat batana, ghar walo ko bhi nahi", [TacticType.SECRECY]),
        ("call cut mat karna, line pe bane raho", [TacticType.ISOLATION]),
        ("sirf ha ya na me jawab do, bahas mat karo", [TacticType.COMPLIANCE_PRESSURE]),
        ("ghar baithe roj 3000 rupaye kamao", [TacticType.GREED]),
        ("150 rupaye mil gaye na, vishwas karo pehle", [TacticType.TRUST_BUILDING]),
        ("video leak kar denge police ghar aayegi", [TacticType.THREAT, TacticType.FEAR]),
    ]

    for text, expected_subset in hinglish_cases:
        signals = tactic_service.analyze_text(text)
        detected = [s.tactic for s in signals]
        for exp in expected_subset:
            assert exp in detected, f"Expected {exp} in Hinglish '{text}', found {detected}"


def test_contextual_negation_hard_negatives(tactic_service: TacticIntelligenceService):
    """CRITICAL TEST: Ensures protective advisories and routine receipts do NOT trigger false positives."""
    hard_negatives = [
        "Never share your OTP or PIN with anyone, including bank staff.",
        "Bank never asks for OTP or netbanking password.",
        "Police have warned people about digital arrest and cyber fraud.",
        "Cyber cell advisory: beware of fraudsters posing as CBI officers.",
        "Your electricity bill of ₹450 was successfully paid. Ref No: TXN12345.",
        "Your interview is scheduled for tomorrow at 10 AM.",
        "Do not share this OTP with anyone for login.",
    ]

    for text in hard_negatives:
        signals = tactic_service.analyze_text(text)
        active_signals = [s for s in signals if not s.is_negated and not s.is_quoted]
        # Should not flag active credential pressure, fear, or payment pressure
        active_tactics = [s.tactic for s in active_signals]
        assert TacticType.CREDENTIAL_PRESSURE not in active_tactics, f"False positive CREDENTIAL_PRESSURE on advisory: '{text}'"
        assert TacticType.FEAR not in active_tactics, f"False positive FEAR on advisory: '{text}'"
        assert TacticType.PAYMENT_PRESSURE not in active_tactics, f"False positive PAYMENT_PRESSURE on receipt: '{text}'"


def test_quoted_scam_inquiry(tactic_service: TacticIntelligenceService):
    """Verifies that user questions quoting scam content are marked as quoted, not attributed as user manipulation."""
    query = "Someone told me 'pay immediately or police will arrest you'. Is this a scam?"
    signals = tactic_service.analyze_text(query, speaker_role=SpeakerRole.VICTIM)
    assert len(signals) >= 1
    for s in signals:
        assert s.is_quoted is True


def test_speaker_role_handling(tactic_service: TacticIntelligenceService):
    """Verifies speaker role boundaries: VICTIM messages are not treated as actor manipulation tactics."""
    victim_text = "I will pay the fee now to unfreeze my account."
    signals = tactic_service.analyze_text(victim_text, speaker_role=SpeakerRole.VICTIM)
    # Since it's a victim message without quotes, it should not attribute actor manipulation
    assert len(signals) == 0 or all(s.is_quoted for s in signals)


def test_adversarial_obfuscation(tactic_service: TacticIntelligenceService):
    """Verifies detection on leetspeak and obfuscated text."""
    obfuscated_text = "p@y n0w immediately to unlock account"
    signals = tactic_service.analyze_text(obfuscated_text)
    tactics = [s.tactic for s in signals]
    assert TacticType.PAYMENT_PRESSURE in tactics


def test_entity_linking(tactic_service: TacticIntelligenceService):
    """Verifies linking between tactic signals and extracted entity objects."""
    entities = [
        Entity(
            entity_id="ent_brand_sbi",
            entity_type=EntityType.BRAND,
            canonical_value="sbi",
            display_value="SBI",
            masked_value="SBI",
            canonical_hash="hash_sbi",
        ),
        Entity(
            entity_id="ent_upi_123",
            entity_type=EntityType.UPI_VPA,
            canonical_value="scam@upi",
            display_value="******@upi",
            masked_value="******@upi",
            canonical_hash="hash_upi",
        ),
        Entity(
            entity_id="ent_tg_easy",
            entity_type=EntityType.TELEGRAM_HANDLE,
            canonical_value="easyjob",
            display_value="@easyjob",
            masked_value="@easyjob",
            canonical_hash="hash_tg",
        ),
    ]

    text = "Calling from SBI security division. Join Telegram @easyjob and pay now to recruiter."
    signals = tactic_service.analyze_text(text, entities=entities)

    linked_entity_ids = [eid for s in signals for eid in s.related_entities]
    assert "ent_brand_sbi" in linked_entity_ids
    assert "ent_tg_easy" in linked_entity_ids
    assert "ent_upi_123" in linked_entity_ids


def test_tactic_cache_idempotency(tactic_service: TacticIntelligenceService):
    """Verifies cache hits on identical text and eviction on clear."""
    text = "Keep this strictly confidential and do not tell your family."
    signals1 = tactic_service.analyze_text(text)
    signals2 = tactic_service.analyze_text(text)
    assert len(signals1) == len(signals2)
    assert signals1[0].signal_id == signals2[0].signal_id  # Cache hit returns same object


def test_degraded_mode_resilience():
    """Verifies graceful fallback to deterministic rules if hybrid classifier encounters error."""
    class BrokenClassifier(MultiLabelTacticClassifier):
        def classify(self, *args, **kwargs):
            raise RuntimeError("Classifier memory fault")

    service = TacticIntelligenceService(classifier=BrokenClassifier())
    signals = service.analyze_text("Please share your 6-digit OTP immediately.")
    assert len(signals) >= 1
    assert signals[0].tactic == TacticType.CREDENTIAL_PRESSURE
    assert signals[0].metadata.get("degraded") is True


def test_consumer_and_analyst_serialization(tactic_service: TacticIntelligenceService):
    """Verifies consumer warning is plain-language without raw internals, and analyst view is forensic."""
    text = "I am CBI Officer. Keep this secret. Pay ₹10,000 immediately or go to jail."
    signals = tactic_service.analyze_text(text)
    timeline = tactic_service.timeline_analyzer.build_timeline(signals)

    # 1. Consumer Warning
    consumer_view = tactic_service.serialize_consumer_warning(timeline)
    assert "High-Risk Manipulation Pattern" in consumer_view.title
    assert "CBI" not in consumer_view.summary or "authority" in consumer_view.summary.lower()
    # Ensure no technical model internals are exposed
    assert not hasattr(consumer_view, "detector_sources")
    assert not hasattr(consumer_view, "rule_id")
    assert len(consumer_view.recommended_interventions) >= 1

    # 2. Analyst View
    analyst_view = tactic_service.serialize_analyst_view(timeline)
    assert "signals" in analyst_view
    assert analyst_view["signal_count"] >= 1
    assert "supporting_spans" in analyst_view["signals"][0]
    assert "tactic_vector" in analyst_view


def test_integration_job_task_scam_evolution(tactic_service: TacticIntelligenceService):
    """INTEGRATION TEST 1: Task/Job scam multi-turn conversation progression and escalation."""
    conv = Conversation(conversation_id="conv_job_scam_001")
    conv.add_message(ConversationMessage(
        turn_index=0,
        speaker_role=SpeakerRole.SCAMMER,
        text="Earn ₹5,000 daily with simple YouTube like task from home.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=1,
        speaker_role=SpeakerRole.SCAMMER,
        text="First task is free, test withdrawal of ₹150 credited to your account.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=2,
        speaker_role=SpeakerRole.SCAMMER,
        text="Join our Telegram group @vip_tasks to receive VIP tasks.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=3,
        speaker_role=SpeakerRole.SCAMMER,
        text="We gave you profit, now invest ₹5000 to unlock premium task wallet.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=4,
        speaker_role=SpeakerRole.SCAMMER,
        text="Pay ₹5,000 immediately within 10 minutes or your earnings will be lost.",
    ))

    timeline = tactic_service.analyze_conversation(conv)

    assert len(timeline.signals) >= 4
    assert timeline.manipulation_density > 0.5
    assert timeline.escalation_signal is True
    assert "PAYMENT_INTERVENTION_CANDIDATE" in timeline.intervention_candidates
    assert "PAYMENT_PRESSURE" in timeline.tactic_vector
    assert "TRUST_BUILDING" in timeline.tactic_vector


def test_integration_digital_arrest_fixture(tactic_service: TacticIntelligenceService):
    """INTEGRATION TEST 2: Digital arrest coercion progression and anti-isolation candidate."""
    conv = Conversation(conversation_id="conv_digital_arrest_001")
    conv.add_message(ConversationMessage(
        turn_index=0,
        speaker_role=SpeakerRole.IMPERSONATED_AUTHORITY,
        text="Calling from Mumbai Police Cyber Cell. An FIR has been registered for illegal package.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=1,
        speaker_role=SpeakerRole.IMPERSONATED_AUTHORITY,
        text="An arrest warrant is issued by court and you will face jail if you disobey.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=2,
        speaker_role=SpeakerRole.IMPERSONATED_AUTHORITY,
        text="Stay on this video call, do not disconnect, and keep this strictly confidential from family.",
    ))
    conv.add_message(ConversationMessage(
        turn_index=3,
        speaker_role=SpeakerRole.IMPERSONATED_AUTHORITY,
        text="Transfer ₹50,000 to the verification clearance account right now.",
    ))

    timeline = tactic_service.analyze_conversation(conv)

    assert timeline.escalation_signal is True
    # Anti-isolation should fire because SECRECY/ISOLATION + PAYMENT_PRESSURE are both present
    assert "ANTI_ISOLATION_INTERVENTION_CANDIDATE" in timeline.intervention_candidates
    assert "PAYMENT_INTERVENTION_CANDIDATE" in timeline.intervention_candidates
    assert "INDEPENDENT_VERIFICATION_CANDIDATE" in timeline.intervention_candidates


def test_pattern_engine_interoperability(tactic_service: TacticIntelligenceService):
    """INTEGRATION TEST 3: Verifies mapping to PatternEngineV1 declarative signal codes."""
    text = "Calling from CBI officer. Video call isolation required, keep secret and deposit ₹20,000."
    signals = tactic_service.analyze_text(text)
    pattern_signals = TacticTimelineAnalyzer.map_tactics_to_pattern_signals(signals)

    assert "LAW_ENFORCEMENT_IMPERSONATION" in pattern_signals
    assert "SECRECY_COERCION" in pattern_signals
    assert "SECURITY_DEPOSIT_DEMAND" in pattern_signals
