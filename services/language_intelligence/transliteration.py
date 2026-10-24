"""Transliteration Adapter for ScamGraph AI (Prompt 17 / Phase 5C).

Provides non-destructive, bidirectional transliteration candidates between
Devanagari and Roman script to assist downstream semantic representation and search.

Key Principle: Transliteration is NOT authoritative truth.
Original text is preserved immutable; transliterated text is a derived feature.
"""

from typing import Dict, Optional, Tuple
from packages.schemas.multilingual import ScriptType


# Domain-specific phonetic mappings for common Indian scam keywords
PHONETIC_DEVANAGARI_TO_ROMAN: Dict[str, str] = {
    "पेमेंट": "payment",
    "टास्क": "task",
    "कमीशन": "commission",
    "अकाउंट": "account",
    "ब्लॉक": "block",
    "रुपये": "rupaye",
    "ओटीपी": "otp",
    "तुरंत": "turant",
    "जल्दी": "jaldi",
    "करो": "karo",
    "भेजो": "bhejo",
    "पुलिस": "police",
    "सीबीआई": "cbi",
    "गिरफ्तारी": "giriftari",
    "डिजिटल": "digital",
    "अरेस्ट": "arrest",
    "लिंक": "link",
    "क्लिक": "click",
    "डाउनलोड": "download",
}

PHONETIC_ROMAN_TO_DEVANAGARI: Dict[str, str] = {
    "payment": "पेमेंट",
    "task": "टास्क",
    "commission": "कमीशन",
    "account": "अकाउंट",
    "block": "ब्लॉक",
    "rupaye": "रुपये",
    "otp": "ओटीपी",
    "turant": "तुरंत",
    "jaldi": "जल्दी",
    "karo": "करो",
    "bhejo": "भेजो",
    "police": "पुलिस",
    "cbi": "सीबीआई",
    "digital": "डिजिटल",
    "arrest": "अरेस्ट",
    "link": "लिंक",
}


class TransliterationAdapter:
    """Non-destructive transliteration candidate generator."""

    def __init__(self):
        self.version = "Translit-v2.0"

    def transliterate_to_roman(self, text: str) -> Tuple[Optional[str], float]:
        """
        Derives Roman phonetic candidate from Devanagari text.
        Returns: (candidate_text, confidence)
        """
        if not text:
            return None, 0.0

        words = text.split()
        converted_words = []
        replaced_count = 0

        for w in words:
            clean_w = w.strip(".,!?\"'()")
            if clean_w in PHONETIC_DEVANAGARI_TO_ROMAN:
                converted_words.append(PHONETIC_DEVANAGARI_TO_ROMAN[clean_w])
                replaced_count += 1
            else:
                converted_words.append(w)

        if replaced_count > 0:
            confidence = min(0.95, replaced_count / max(1, len(words)) + 0.4)
            return " ".join(converted_words), round(confidence, 2)

        return None, 0.0

    def transliterate_to_devanagari(self, text: str) -> Tuple[Optional[str], float]:
        """
        Derives Devanagari phonetic candidate from Roman text.
        Returns: (candidate_text, confidence)
        """
        if not text:
            return None, 0.0

        words = text.split()
        converted_words = []
        replaced_count = 0

        for w in words:
            clean_w = w.lower().strip(".,!?\"'()")
            if clean_w in PHONETIC_ROMAN_TO_DEVANAGARI:
                converted_words.append(PHONETIC_ROMAN_TO_DEVANAGARI[clean_w])
                replaced_count += 1
            else:
                converted_words.append(w)

        if replaced_count > 0:
            confidence = min(0.90, replaced_count / max(1, len(words)) + 0.3)
            return " ".join(converted_words), round(confidence, 2)

        return None, 0.0


transliteration_adapter = TransliterationAdapter()
