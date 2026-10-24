"""Translation Adapter for ScamGraph AI (Prompt 17 / Phase 5C).

Provides supporting English translations for Indic/code-mixed messages while strictly
preserving critical security domain terminology (OTP, UPI, KYC, PAN, Aadhaar, etc.).

Key Principle: Translation is a SUPPORTING signal, NEVER the sole basis of classification.
"""

import re
from typing import Dict, Optional, Tuple


# Lexicon-guided translation mappings for common Indic scam expressions
INDIC_PHRASE_TRANSLATIONS: Dict[str, str] = {
    # Tasks & Job Scams
    r"\bpart\s*time\s*job\s*hai\b": "part time job is available",
    r"\btelegram\s*join\s*karo\b": "join telegram",
    r"\bfirst\s*task\s*complete\s*karo\b": "complete the first task",
    r"\bpremium\s*task\s*ke\s*liye\b": "for premium task",
    r"\bdeposit\s*karo\b": "deposit money",
    r"\bcommission\s*milega\b": "you will receive commission",
    r"\bpaise\s*kamao\b": "earn money",
    r"\bbonus\s*milega\b": "you will get bonus",
    # Urgency & Pressure
    r"\babhi\s*payment\s*karo\b": "pay right now",
    r"\bturant\s*karo\b": "do it immediately",
    r"\bjaldi\s*bhejo\b": "send quickly",
    r"\baccount\s*block\s*ho\s*jayega\b": "account will be blocked",
    r"\bkyc\s*update\s*karo\b": "update KYC",
    # Authority & Digital Arrest
    r"\bpolice\s*case\s*hoga\b": "police case will be filed",
    r"\barrest\s*warrant\s*jari\s*hua\b": "arrest warrant has been issued",
    r"\bcall\s*disconnect\s*mat\s*karna\b": "do not disconnect the call",
    r"\bkisi\s*ko\s*mat\s*batao\b": "do not tell anyone",
    # Bengali phrases
    r"\btaka\s*pathan\b": "send money",
    r"\bekhon\s*koren\b": "do it now",
    r"\baccount\s*bondho\s*hobe\b": "account will be closed",
}


class TranslationAdapter:
    """Translates Indic messages to supporting English representations."""

    def __init__(self):
        self.version = "TransAdapter-v2.0"

    def translate(self, text: str, source_language: str = "hin") -> Tuple[Optional[str], float]:
        """
        Translates Indic text into supporting English text.
        Returns: (translated_text, confidence)
        """
        if not text or source_language == "eng":
            return None, 1.0

        translated = text.lower()
        matched = False

        for pattern, english_replacement in INDIC_PHRASE_TRANSLATIONS.items():
            if re.search(pattern, translated, re.IGNORECASE):
                translated = re.sub(pattern, english_replacement, translated, flags=re.IGNORECASE)
                matched = True

        if matched:
            return translated, 0.85

        return None, 0.0


translation_adapter = TranslationAdapter()
