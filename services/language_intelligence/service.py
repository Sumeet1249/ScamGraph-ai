"""Centralized Language Intelligence Service for ScamGraph AI (Prompt 17 / Phase 5C).

Unifies language detection, Indic normalization, protective negation analysis,
transliteration, translation, and canonical behavioral feature synthesis.
"""

from typing import Dict, List, Optional
from packages.schemas.multilingual import (
    BehavioralFeatureSet,
    LanguageProfile,
    LanguageSupportTier,
    MultilingualTextRepresentation,
    NegationSignal,
    ScriptType,
)
from packages.schemas.tactics import ActionRequestedType, TacticType
from services.language_intelligence.detector import language_detector
from services.language_intelligence.negation import protective_negation_engine
from services.language_intelligence.normalizer import indic_normalizer
from services.language_intelligence.translation import translation_adapter
from services.language_intelligence.transliteration import transliteration_adapter


class LanguageIntelligenceService:
    """Master orchestrator for multi-script, code-mixed Indic threat understanding."""

    def __init__(self):
        self.version = "LanguageIntelligenceService-v2.0"
        self._cache: Dict[str, MultilingualTextRepresentation] = {}

    def analyze_text(self, text: str) -> MultilingualTextRepresentation:
        """Processes raw input text into a complete MultilingualTextRepresentation."""
        if not text:
            profile = language_detector.detect("")
            return MultilingualTextRepresentation(
                original_text="",
                language_profile=profile,
                normalized_text="",
                semantic_input_text="",
            )

        if text in self._cache:
            return self._cache[text]

        # 1. Detect Language & Script
        profile = language_detector.detect(text)

        # 2. Normalize Text
        norm_text, norm_steps, urgency_intensity = indic_normalizer.normalize(text)

        # 3. Derive Transliteration (if Indic/Latin mix)
        translit_text = None
        if ScriptType.DEVANAGARI in profile.scripts:
            translit_text, _ = transliteration_adapter.transliterate_to_roman(norm_text)
        elif profile.romanized_indic:
            translit_text, _ = transliteration_adapter.transliterate_to_devanagari(norm_text)

        # 4. Derive Supporting Translation
        translated_text, trans_conf = translation_adapter.translate(norm_text, profile.primary_language)

        # 5. Determine Semantic Input Text
        # For E5/BGE multilingual encoders, the normalized text preserves token semantics best
        semantic_input = norm_text

        rep = MultilingualTextRepresentation(
            original_text=text,
            language_profile=profile,
            normalized_text=norm_text,
            normalized_segments=[norm_text],
            transliterated_text=translit_text,
            translated_text=translated_text,
            translation_confidence=trans_conf,
            semantic_input_text=semantic_input,
            normalization_steps=norm_steps,
            warnings=[] if profile.support_tier != LanguageSupportTier.UNSUPPORTED else ["UNSUPPORTED_LANGUAGE_DEGRADED_ANALYSIS"],
        )

        self._cache[text] = rep
        return rep

    def check_negation(self, text: str) -> NegationSignal:
        """Evaluates protective safety negation."""
        return protective_negation_engine.evaluate(text)

    def extract_behavioral_features(self, text: str) -> BehavioralFeatureSet:
        """
        Synthesizes language-independent behavioral indicators directly from normalized text.
        Works equivalently whether text was submitted in English, Hindi, or Hinglish.
        """
        rep = self.analyze_text(text)
        norm = rep.normalized_text.lower()
        neg = self.check_negation(text)

        tactics: List[TacticType] = []
        actions: List[ActionRequestedType] = []

        # 1. Authority Impersonation (Digital Arrest / Police / CBI)
        authority_detected = any(
            kw in norm
            for kw in [
                "police", "cbi", "customs", "supreme court", "arrest warrant", "money laundering",
                "पुलिस", "सीबीआई", "कस्टम्स", "वारंट", "गिरफ्तारी", "daroga", "thana",
            ]
        )
        if authority_detected:
            tactics.append(TacticType.AUTHORITY)
            tactics.append(TacticType.IMPERSONATION)

        # 2. Secrecy & Isolation
        isolation_detected = any(
            kw in norm
            for kw in [
                "do not disconnect", "call disconnect mat", "stay on call", "lock the door",
                "kisi ko mat batana", "kisi ko mat batao", "किसी को मत बताएं", "गोपनीय", "secret",
            ]
        )
        if isolation_detected:
            tactics.append(TacticType.ISOLATION)
            tactics.append(TacticType.SECRECY)
            actions.append(ActionRequestedType.DO_NOT_DISCONNECT)
            actions.append(ActionRequestedType.KEEP_SECRET)

        # 3. Urgency & Payment Pressure
        urgency_detected = any(
            kw in norm
            for kw in [
                "urgent", "immediately", "within 10 minutes", "abhi", "turant", "jaldi",
                "तुरंत", "जल्दी", "अभी", "block ho jayega", "electricity disconnect",
            ]
        )
        if urgency_detected:
            tactics.append(TacticType.URGENCY)

        payment_pressure = any(
            kw in norm
            for kw in [
                "pay", "deposit", "transfer", "bhejo", "karo", "पेमेंट", "भुगतान", "जमा", "रुपये", "₹",
            ]
        )
        if payment_pressure and urgency_detected:
            tactics.append(TacticType.PAYMENT_PRESSURE)
            actions.append(ActionRequestedType.SEND_PAYMENT)

        # 4. Credential & OTP Demands (WITH NEGATION PROTECTION!)
        has_otp_token = any(
            kw in norm
            for kw in ["otp", "password", "pin", "cvv", "ओटीपी", "पासवर्ड", "पिन"]
        )

        if has_otp_token:
            if neg.is_protective_advisory:
                # PROTECTIVE ADVISORY: Do NOT flag as credential pressure or scam demand!
                pass
            else:
                # Genuine demand: Flag credential pressure and requested action
                tactics.append(TacticType.CREDENTIAL_PRESSURE)
                actions.append(ActionRequestedType.SHARE_OTP)

        # 5. Platform Migration (Job / Task scams)
        platform_migration = any(
            kw in norm
            for kw in ["telegram join", "telegram pe", "whatsapp pe", "टेलीग्राम", "whatsapp message"]
        )
        if platform_migration:
            tactics.append(TacticType.PLATFORM_MIGRATION)
            actions.append(ActionRequestedType.MOVE_PLATFORM)

        # 6. Fake Rewards & Tasks
        reward_detected = any(
            kw in norm
            for kw in ["earn", "commission", "part time job", "kamao", "milega", "इनाम", "कमीशन"]
        )
        if reward_detected:
            tactics.append(TacticType.FAKE_REWARD)
            tactics.append(TacticType.TRUST_BUILDING)

        return BehavioralFeatureSet(
            tactics=list(dict.fromkeys(tactics)),
            requested_actions=list(dict.fromkeys(actions)),
            journey_stage_candidate="INITIAL_PAYMENT" if payment_pressure else None,
            payment_escalation_detected="premium task" in norm or "deposit" in norm,
            platform_migration_detected=platform_migration,
            authority_impersonation_detected=authority_detected,
            secrecy_detected="secret" in norm or "kisi ko mat" in norm,
            isolation_detected=isolation_detected,
            reward_progression_detected=reward_detected,
            withdrawal_blocking_detected="unlock" in norm or "withdrawal" in norm or "tax" in norm,
            credential_request_detected=has_otp_token and not neg.is_protective_advisory,
            protective_negation_present=neg.is_protective_advisory,
        )


language_intelligence_service = LanguageIntelligenceService()
