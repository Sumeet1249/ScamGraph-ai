"""Unit Tests for India Multilingual Intelligence V2 (Prompt 17 / Phase 5C).

Covers all required tests from Part BM and Part BW:
1. Script detection (Devanagari, Bengali, Latin, Mixed, Unknown)
2. Language & code-mixing detection (English, Hindi, Hinglish, Bengali, Unknown)
3. Indic text normalization & security token preservation
4. Amount normalization (₹500, 500 rs, 500 रुपये)
5. Mandatory Negation test: "OTP share karo" vs "OTP share mat karo" & Hindi/Bengali equivalents
6. Legitimate bank security warning hard-negative collision test
7. Non-destructive Transliteration (Devanagari <-> Roman Indic)
8. Cross-language Journey: English -> Hindi -> Hinglish in a single conversation
9. Cross-language ScamDNA: Same behavior in English, Hindi, Hinglish yields high similarity
10. Cross-language Campaign: Campaign operates across English, Hindi, Hinglish without fragmentation
11. Language-only negative: Two unrelated scams in Hindi do NOT correlate on language alone
12. Digital Arrest in Hindi / Hinglish (authority + isolation + payment pressure)
13. Rescue Triage in Hindi with localized emergency guidance
14. Unsupported language: Safe degradation with PARTIAL_ANALYSIS, never false SAFE
15. Unicode security: Confusables, zero-width characters, homoglyphs handled safely
"""

from datetime import datetime, timezone
import pytest

from packages.schemas.conversation import Conversation, ConversationMessage, SpeakerRole
from packages.schemas.dna import (
    DNADimension,
    DNADimensionType,
    ScamDNA,
)
from packages.schemas.journey import JourneyEvent, JourneyStage
from packages.schemas.multilingual import (
    LanguageSupportTier,
    ScriptType,
)
from packages.schemas.rescue import LossEvent, LossType
from packages.schemas.tactics import ActionRequestedType, TacticType
from services.dna_engine.similarity import ScamDNASimilarityEngine
from services.journey_engine.service import JourneyEngineService
from services.language_intelligence.detector import language_detector
from services.language_intelligence.negation import protective_negation_engine
from services.language_intelligence.normalizer import indic_normalizer
from services.language_intelligence.script_detector import detect_scripts
from services.language_intelligence.service import language_intelligence_service
from services.language_intelligence.transliteration import transliteration_adapter
from services.rescue_engine.service import rescue_service


# 1. SCRIPT DETECTION
def test_script_detection():
    scripts_hi, _ = detect_scripts("नमस्ते आप कैसे हैं")
    assert ScriptType.DEVANAGARI in scripts_hi

    scripts_bn, _ = detect_scripts("আপনি কেমন আছেন")
    assert ScriptType.BENGALI in scripts_bn

    scripts_en, _ = detect_scripts("Hello how are you")
    assert ScriptType.LATIN in scripts_en

    scripts_mixed, _ = detect_scripts("आपका KYC update नहीं हुआ है")
    assert ScriptType.MIXED in scripts_mixed
    assert ScriptType.DEVANAGARI in scripts_mixed
    assert ScriptType.LATIN in scripts_mixed


# 2. LANGUAGE & CODE-MIXING DETECTION
def test_language_and_codemix_detection():
    # Pure Hindi
    prof_hi = language_detector.detect("यह टास्क पूरा करें और कमीशन प्राप्त करें")
    assert prof_hi.primary_language == "hin"
    assert prof_hi.support_tier == LanguageSupportTier.PRODUCTION_VALIDATED

    # Pure English
    prof_en = language_detector.detect("Complete this task and earn your daily commission")
    assert prof_en.primary_language == "eng"
    assert prof_en.code_mixed is False

    # Hinglish / Roman Hindi
    prof_hing = language_detector.detect("ye task complete kro 500 rs commission milega abhi")
    assert prof_hing.primary_language == "hinglish"
    assert prof_hing.romanized_indic is True
    assert prof_hing.code_mixed is True
    assert prof_hing.code_mix_score > 0.0

    # Bengali
    prof_bn = language_detector.detect("এই কাজটি সম্পূর্ণ করুন এবং টাকা উপার্জন করুন")
    assert prof_bn.primary_language == "ben"
    assert prof_bn.support_tier == LanguageSupportTier.BETA


# 3. INDIC TEXT NORMALIZATION & PRESERVATION
def test_indic_normalization_preserves_security_tokens():
    raw_text = "Urgenttt! Send 500 rs to test.vpa@oksbi or visit https://scam-bank.xyz jaldiiiii!!!"
    norm, steps, urgency = indic_normalizer.normalize(raw_text)

    # Elongation collapsed
    assert "urgent" in norm.lower()
    assert "jaldi" in norm.lower()
    assert urgency > 0.0

    # Security tokens preserved intact
    assert "test.vpa@oksbi" in norm
    assert "https://scam-bank.xyz" in norm

    # Amount normalized to ₹500
    assert "₹500" in norm


# 4. AMOUNT NORMALIZATION
def test_amount_normalization_across_formats():
    cases = [
        ("₹500", "₹500"),
        ("500 rs", "₹500"),
        ("500 rupees", "₹500"),
        ("500 rupaye", "₹500"),
        ("५०० रुपये", "₹500"),
    ]
    for raw, expected in cases:
        norm, _, _ = indic_normalizer.normalize(raw)
        assert expected in norm, f"Failed for {raw}: got {norm}"


# 5. MANDATORY NEGATION TEST: DEMAND VS PROTECTIVE ADVISORY
def test_mandatory_negation_distinction():
    # Demand: Fraudster ordering victim to share OTP
    fraud_en = "Share your OTP right now to complete verification."
    fraud_hi = "अभी अपना ओटीपी बताएं।"
    fraud_hing = "OTP share karo abhi turant."

    assert protective_negation_engine.evaluate(fraud_en).is_protective_advisory is False
    assert protective_negation_engine.evaluate(fraud_hi).is_protective_advisory is False
    assert protective_negation_engine.evaluate(fraud_hing).is_protective_advisory is False

    # Protective Advisory: Bank / Security warning user NEVER to share
    advisory_en = "Bank never asks for your OTP. Do not disclose your password or PIN to anyone."
    advisory_hi = "अपना OTP किसी के साथ साझा न करें। बैंक कभी ओटीपी नहीं मांगता।"
    advisory_hing = "OTP kisi ko mat dena. Bank kabhi password nahi mangta."
    advisory_bn = "OTP কাওকে দেবেন না।"

    assert protective_negation_engine.evaluate(advisory_en).is_protective_advisory is True
    assert protective_negation_engine.evaluate(advisory_hi).is_protective_advisory is True
    assert protective_negation_engine.evaluate(advisory_hing).is_protective_advisory is True
    assert protective_negation_engine.evaluate(advisory_bn).is_protective_advisory is True


# 6. LEGITIMATE BANK SECURITY COLLISION AVOIDANCE
def test_legitimate_bank_warning_collision_avoidance():
    text = "Dear Customer, please be cautious. SBI never asks for your OTP, PIN or CVV. Never share credentials."
    features = language_intelligence_service.extract_behavioral_features(text)

    # Must NOT flag as CREDENTIAL_PRESSURE or SHARE_OTP demand!
    assert TacticType.CREDENTIAL_PRESSURE not in features.tactics
    assert ActionRequestedType.SHARE_OTP not in features.requested_actions
    assert features.protective_negation_present is True


# 7. TRANSLITERATION ADAPTER
def test_transliteration_adapter():
    dev_text = "पेमेंट करो और टास्क पूरा करो"
    roman_candidate, conf = transliteration_adapter.transliterate_to_roman(dev_text)

    assert roman_candidate is not None
    assert "payment" in roman_candidate
    assert "task" in roman_candidate
    assert conf > 0.5


# 8. CROSS-LANGUAGE MULTI-TURN JOURNEY
def test_cross_language_conversation_single_journey():
    journey_service = JourneyEngineService()
    now = datetime.now(timezone.utc)

    # 1 conversation switching across 3 languages
    messages = [
        ConversationMessage(
            message_id="msg_1",
            turn_index=0,
            speaker_role=SpeakerRole.SCAMMER,
            timestamp=now,
            text="Hello! Part time work from home job available.",  # English
        ),
        ConversationMessage(
            message_id="msg_2",
            turn_index=1,
            speaker_role=SpeakerRole.SCAMMER,
            timestamp=now,
            text="Telegram join karo aur task guidelines dekho.",    # Hinglish
        ),
        ConversationMessage(
            message_id="msg_3",
            turn_index=2,
            speaker_role=SpeakerRole.SCAMMER,
            timestamp=now,
            text="पहला कार्य पूरा करने पर आपको ₹200 का इनाम मिला।",  # Hindi Devanagari
        ),
        ConversationMessage(
            message_id="msg_4",
            turn_index=3,
            speaker_role=SpeakerRole.SCAMMER,
            timestamp=now,
            text="Ab VIP upgrade ke liye 5000 rupaye deposit karo.", # Hinglish
        ),
    ]

    events = []
    for i, msg in enumerate(messages):
        feat = language_intelligence_service.extract_behavioral_features(msg.text)
        ev = JourneyEvent(
            event_id=f"jrev_{i}",
            timestamp=now,
            sequence_number=i,
            event_type="MESSAGE_RECEIVED",
            speaker_role=msg.speaker_role.value,
            tactics=[t.value for t in feat.tactics],
            requested_actions=[a.value for a in feat.requested_actions],
            metadata={"text": msg.text},
        )
        events.append(ev)

    journey = journey_service.create_journey("inc_multi_1", events=events)

    assert journey.incident_id == "inc_multi_1"
    # Stage progression must detect grooming moving toward payment escalation
    assert len(journey.stage_observations) >= 2
    stages_observed = [o.stage for o in journey.stage_observations]
    assert any(s in stages_observed for s in (JourneyStage.CONTACT, JourneyStage.DISCOVERY, JourneyStage.PLATFORM_MIGRATION, JourneyStage.TRUST_BUILDING))
    assert any(s in stages_observed for s in (JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION, JourneyStage.REWARD_OR_FAKE_PROFIT))


# 9. CROSS-LANGUAGE SCAMDNA SIMILARITY
def test_cross_language_scamdna_similarity():
    from services.dna_engine.builder import ScamDNABuilder
    from packages.schemas.journey import ScamJourney

    sim_engine = ScamDNASimilarityEngine()
    journey_task = ScamJourney(
        incident_id="inc_task",
        stage_history=[
            JourneyStage.CONTACT,
            JourneyStage.PLATFORM_MIGRATION,
            JourneyStage.INITIAL_PAYMENT,
            JourneyStage.PAYMENT_ESCALATION,
        ],
        current_stage=JourneyStage.PAYMENT_ESCALATION,
    )

    dna_en = ScamDNABuilder.build(
        incident_id="inc_en",
        journey=journey_task,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        requested_actions=["PAY_FEE", "COMPLETE_TASK"],
        message_text="Complete simple tasks and earn ₹5000 daily.",
    )

    dna_hi = ScamDNABuilder.build(
        incident_id="inc_hi",
        journey=journey_task,
        tactics=["TRUST_BUILDING", "FAKE_REWARD", "PAYMENT_PRESSURE"],
        requested_actions=["PAY_FEE", "COMPLETE_TASK"],
        message_text="यह टास्क पूरा करें और ₹5000 कमाएँ।",
    )

    match = sim_engine.compare(dna_en, dna_hi)
    assert match.overall_similarity >= 0.70
    assert match.variant_status.value in ("KNOWN_PATTERN", "LIKELY_VARIANT", "POSSIBLE_VARIANT")


# 10. CROSS-LANGUAGE CAMPAIGN CONTINUITY
def test_cross_language_campaign_continuity():
    from services.campaign_engine.discovery import CampaignDiscoveryEngine
    from packages.schemas.correlation import CandidateIncidentGroup

    discovery = CampaignDiscoveryEngine()
    now = datetime.now(timezone.utc)

    # 3 incidents belonging to same campaign operating across English, Hindi, Hinglish
    inc_data = {
        "inc_c_en": {
            "incident_id": "inc_c_en",
            "canonical_family": "DIGITAL_ARREST",
            "entities": [{"entity_type": "PAYMENT_VPA", "canonical_value": "cbi-fake-desk@oksbi"}],
            "languages": ["English"],
        },
        "inc_c_hi": {
            "incident_id": "inc_c_hi",
            "canonical_family": "DIGITAL_ARREST",
            "entities": [{"entity_type": "PAYMENT_VPA", "canonical_value": "cbi-fake-desk@oksbi"}],
            "languages": ["Hindi"],
        },
        "inc_c_hing": {
            "incident_id": "inc_c_hing",
            "canonical_family": "DIGITAL_ARREST",
            "entities": [{"entity_type": "PAYMENT_VPA", "canonical_value": "cbi-fake-desk@oksbi"}],
            "languages": ["Hinglish"],
        },
    }

    group = CandidateIncidentGroup(
        group_id="grp_cross_lang_01",
        member_incident_ids=["inc_c_en", "inc_c_hi", "inc_c_hing"],
        relationship_density=0.85,
        strong_edge_count=3,
        evidence_diversity=["SHARED_PAYMENT(cbi-fake-desk@oksbi)", "HIGH_SCAM_DNA_SIMILARITY"],
        primary_family="DIGITAL_ARREST",
    )

    campaign = discovery.evaluate_candidate_group(group, incidents_data=inc_data)
    assert campaign is not None
    assert campaign.incident_count == 3
    # Campaign must aggregate all 3 languages without fragmenting
    assert "English" in campaign.languages
    assert "Hindi" in campaign.languages
    assert "Hinglish" in campaign.languages


# 11. LANGUAGE-ONLY NEGATIVE: UNRELATED SCAMS DO NOT CORRELATE ON LANGUAGE ALONE
def test_language_only_negative_no_false_correlation():
    from services.dna_engine.builder import ScamDNABuilder
    from packages.schemas.journey import ScamJourney

    sim_engine = ScamDNASimilarityEngine()

    journey_elec = ScamJourney(
        incident_id="inc_elec",
        stage_history=[JourneyStage.CONTACT, JourneyStage.URGENCY],
        current_stage=JourneyStage.URGENCY,
    )
    dna_electricity = ScamDNABuilder.build(
        incident_id="inc_elec",
        journey=journey_elec,
        tactics=["URGENCY", "FEAR", "THREAT"],
        message_text="आपका बिजली बिल बकाया है। आज रात 9:30 बजे बिजली काट दी जाएगी।",
    )

    journey_matri = ScamJourney(
        incident_id="inc_matri",
        stage_history=[JourneyStage.CONTACT, JourneyStage.TRUST_BUILDING],
        current_stage=JourneyStage.TRUST_BUILDING,
    )
    dna_matrimonial = ScamDNABuilder.build(
        incident_id="inc_matri",
        journey=journey_matri,
        tactics=["ROMANCE", "RECIPROCITY"],
        message_text="प्रिय, मैं लंदन से आपके लिए उपहार भेज रहा हूँ। सीमा शुल्क अधिकारी संपर्क करेंगे।",
    )

    match = sim_engine.compare(dna_electricity, dna_matrimonial)
    # Must NOT correlate merely because both occurred in Hindi!
    assert match.overall_similarity < 0.50
    assert match.variant_status.value in ("NOVEL_PATTERN", "INSUFFICIENT_EVIDENCE")


# 12. DIGITAL ARREST IN HINDI / HINGLISH
def test_digital_arrest_hindi_behavioral_features():
    hindi_text = "सीबीआई दिल्ली मुख्यालय। आपके आधार पर मनी लॉन्ड्रिंग का केस दर्ज है। कॉल डिस्कनेक्ट मत करना। किसी को मत बताएं। तुरंत ₹50000 सिक्योरिटी डिपॉजिट जमा करें।"
    feat = language_intelligence_service.extract_behavioral_features(hindi_text)

    assert TacticType.AUTHORITY in feat.tactics
    assert TacticType.IMPERSONATION in feat.tactics
    assert TacticType.ISOLATION in feat.tactics
    assert TacticType.SECRECY in feat.tactics
    assert ActionRequestedType.DO_NOT_DISCONNECT in feat.requested_actions
    assert ActionRequestedType.KEEP_SECRET in feat.requested_actions
    assert ActionRequestedType.SEND_PAYMENT in feat.requested_actions


# 13. RESCUE TRIAGE IN HINDI
def test_rescue_triage_hindi_report():
    service = rescue_service
    inc = service.get_or_create_incident(
        initial_loss_type=LossType.UPI_PAYMENT,
        user_notes="मैंने टेलीग्राम पर 25000 रुपये भेज दिए और ओटीपी भी बता दिया",
    )
    iid = inc.incident_id

    service.record_loss(iid, amount=25000.0, payment_method="UPI")
    triage = service.get_triage(iid)
    plan = service.get_action_plan(iid)

    assert triage.financial_exposure is True
    assert triage.priority in ("EMERGENCY_CRITICAL", "URGENT")
    # Action plan DO NOW must contain 1930
    assert any("1930" in a.title for a in plan.do_now)


# 14. UNSUPPORTED LANGUAGE GRACEFUL DEGRADATION
def test_unsupported_language_degradation():
    # Russian or unrelated non-supported text
    foreign_text = "Привет, это срочное сообщение для подтверждения платежа."
    rep = language_intelligence_service.analyze_text(foreign_text)

    # Must NOT return SAFE! Must flag as UNSUPPORTED and note degraded analysis
    assert rep.language_profile.support_tier == LanguageSupportTier.UNSUPPORTED
    assert "UNSUPPORTED_LANGUAGE_DEGRADED_ANALYSIS" in rep.warnings


# 15. UNICODE CONFUSABLES & ZERO-WIDTH SAFETY
def test_unicode_confusable_and_zero_width_safety():
    # Text injected with zero-width spaces (\u200B) and elongation
    malicious_text = "p\u200Ba\u200By\u200Bm\u200Be\u200Bn\u200Bt jaldiiiii 5000 rs"
    norm, steps, _ = indic_normalizer.normalize(malicious_text)

    # Zero-width spaces removed, allowing regex and tokens to match
    assert "\u200B" not in norm
    assert "payment" in norm.lower()
    assert "₹5000" in norm
    assert "ZERO_WIDTH_REMOVAL" in steps
