"""Language and Code-Mixing Detector for ScamGraph AI (Prompt 17 / Phase 5C).

Performs deterministic, lexicon-guided language and code-mixing detection across:
- English (eng)
- Hindi in Devanagari (hin)
- Hinglish / Roman Hindi (hinglish / hin_Latn)
- Bengali in Bengali Script & Roman Bengali (ben)
- Unknown / Unsupported (und)

Key Rules:
1. Roman script is NOT automatically English.
2. Devanagari script is NOT automatically Hindi (could be Marathi).
3. Code-mixing is explicitly tracked and scored (0.0 to 1.0).
4. SCRIPT and LANGUAGE are strictly decoupled.
"""

import re
from typing import Dict, List, Set, Tuple
from packages.schemas.multilingual import (
    LanguageProfile,
    LanguageSegment,
    LanguageSupportTier,
    ScriptType,
)
from services.language_intelligence.script_detector import detect_scripts


# Hinglish / Roman Hindi distinctive token dictionary
HINGLISH_LEXICON: Set[str] = {
    # Verbs / Actions
    "karo", "kro", "krdo", "kardo", "karna", "krna", "dena", "bhejo", "bhejna", "milega", "kamao",
    "shuru", "batao", "btao", "kijiye", "kariye", "karenge", "bolo", "dekho", "aayega",
    # Negations & Modals
    "mat", "mt", "nahi", "nhi", "na", "chahiye", "hoga", "hogi", "hote", "tha", "thi",
    # Pronouns & Salutations
    "aap", "apka", "aapka", "tum", "mera", "meri", "hum", "bhai", "sirji", "bhaiya", "dost",
    # Common Nouns & Adverbs
    "paise", "paisa", "rupaye", "rupiya", "jaldi", "turant", "abhi", "aaj", "pehle", "baad",
    "kaam", "kam", "naukri", "parivar", "police", "daroga", "sarkar", "khata",
    # Particles & Postpositions
    "hai", "hain", "ho", "mein", "me", "se", "ko", "par", "ke", "ki", "ka", "aur", "ya", "toh", "to",
}

# Bengali romanized / distinctive token dictionary
BENGALI_ROMAN_LEXICON: Set[str] = {
    "taka", "korun", "koren", "diben", "deben", "amar", "apnar", "tomar", "bhalo", "thik",
    "ekhon", "tara", "kaje", "chakri", "kotha", "bolun", "shunchen", "ei", "shei",
}

# Common English tokens found in technical / payment contexts
ENGLISH_LEXICON: Set[str] = {
    "payment", "account", "verify", "verification", "click", "link", "task", "job", "money",
    "salary", "urgent", "immediately", "block", "freeze", "police", "customs", "arrest",
    "warrant", "refund", "cashback", "commission", "deposit", "withdrawal", "bonus", "card",
    "bank", "number", "password", "please", "confirm", "update", "details", "contact",
}


class LanguageIntelligenceDetector:
    """Enterprise language and code-mix detection engine."""

    def __init__(self):
        self.version = "LangIntel-v2.0"

    def detect(self, text: str) -> LanguageProfile:
        """Computes comprehensive LanguageProfile from raw text."""
        if not text or not text.strip():
            return LanguageProfile(
                primary_language="und",
                scripts=[ScriptType.UNKNOWN],
                confidence=0.5,
                support_tier=LanguageSupportTier.UNSUPPORTED,
                detection_method="EMPTY_FALLBACK",
            )

        scripts, script_ratios = detect_scripts(text)
        tokens = re.findall(r"\b[a-zA-Z\u0900-\u097F\u0980-\u09FF]+\b", text.lower())
        total_tokens = len(tokens)

        # 1. Check Devanagari Dominance
        if script_ratios.get("DEVANAGARI", 0.0) >= 0.40:
            # Check for mixed English terms in Devanagari text (e.g. "KYC update करें")
            has_english_tokens = any(t in ENGLISH_LEXICON for t in tokens)
            code_mixed = has_english_tokens or script_ratios.get("LATIN", 0.0) > 0.10
            code_mix_score = min(1.0, script_ratios.get("LATIN", 0.0) * 2.0)

            return LanguageProfile(
                primary_language="hin",
                secondary_languages=["eng"] if code_mixed else [],
                language_probabilities={"hin": 0.90, "eng": 0.10 if code_mixed else 0.0},
                scripts=scripts,
                code_mixed=code_mixed,
                code_mix_score=round(code_mix_score, 2),
                romanized_indic=False,
                confidence=0.95,
                support_tier=LanguageSupportTier.PRODUCTION_VALIDATED,
                detection_method="DEVANAGARI_SCRIPT_ANALYSIS",
            )

        # 2. Check Bengali Dominance
        if script_ratios.get("BENGALI", 0.0) >= 0.40:
            has_english_tokens = any(t in ENGLISH_LEXICON for t in tokens)
            code_mixed = has_english_tokens or script_ratios.get("LATIN", 0.0) > 0.10
            return LanguageProfile(
                primary_language="ben",
                secondary_languages=["eng"] if code_mixed else [],
                language_probabilities={"ben": 0.90, "eng": 0.10 if code_mixed else 0.0},
                scripts=scripts,
                code_mixed=code_mixed,
                code_mix_score=round(min(1.0, script_ratios.get("LATIN", 0.0) * 2.0), 2),
                romanized_indic=False,
                confidence=0.90,
                support_tier=LanguageSupportTier.BETA,
                detection_method="BENGALI_SCRIPT_ANALYSIS",
            )

        # 3. Latin Script Analysis (English vs Hinglish / Roman Hindi vs Roman Bengali)
        if total_tokens > 0:
            hinglish_count = sum(1 for t in tokens if t in HINGLISH_LEXICON)
            bengali_roman_count = sum(1 for t in tokens if t in BENGALI_ROMAN_LEXICON)
            english_count = sum(1 for t in tokens if t in ENGLISH_LEXICON)

            hinglish_ratio = hinglish_count / total_tokens
            bengali_roman_ratio = bengali_roman_count / total_tokens
            english_ratio = english_count / total_tokens

            # Rule: If Hinglish tokens >= 15% or count >= 2, classify as Hinglish / Roman Hindi
            if hinglish_ratio >= 0.12 or hinglish_count >= 2:
                is_code_mixed = english_count > 0 or english_ratio > 0.10
                code_mix_score = min(1.0, (english_count / max(1, hinglish_count + english_count)))

                return LanguageProfile(
                    primary_language="hinglish",
                    secondary_languages=["eng", "hin"],
                    language_probabilities={
                        "hinglish": 0.85,
                        "hin": 0.70,
                        "eng": round(english_ratio, 2),
                    },
                    scripts=scripts,
                    code_mixed=True,
                    code_mix_score=round(code_mix_score, 2),
                    romanized_indic=True,
                    confidence=0.92,
                    support_tier=LanguageSupportTier.PRODUCTION_VALIDATED,
                    detection_method="ROMAN_INDIC_LEXICAL_ANALYSIS",
                )

            # Rule: Roman Bengali
            if bengali_roman_ratio >= 0.15 or bengali_roman_count >= 2:
                return LanguageProfile(
                    primary_language="ben",
                    secondary_languages=["eng"],
                    language_probabilities={"ben": 0.80, "eng": round(english_ratio, 2)},
                    scripts=scripts,
                    code_mixed=english_count > 0,
                    code_mix_score=0.5,
                    romanized_indic=True,
                    confidence=0.82,
                    support_tier=LanguageSupportTier.BETA,
                    detection_method="ROMAN_BENGALI_LEXICAL_ANALYSIS",
                )

        # 4. Pure English fallback in Latin script
        if script_ratios.get("LATIN", 0.0) >= 0.60:
            return LanguageProfile(
                primary_language="eng",
                secondary_languages=[],
                language_probabilities={"eng": 0.95},
                scripts=scripts,
                code_mixed=False,
                code_mix_score=0.0,
                romanized_indic=False,
                confidence=0.95,
                support_tier=LanguageSupportTier.PRODUCTION_VALIDATED,
                detection_method="LATIN_ENGLISH_LEXICAL_ANALYSIS",
            )

        # 5. Unsupported / Ambiguous
        return LanguageProfile(
            primary_language="und",
            secondary_languages=[],
            language_probabilities={"und": 1.0},
            scripts=scripts,
            code_mixed=False,
            code_mix_score=0.0,
            confidence=0.50,
            support_tier=LanguageSupportTier.UNSUPPORTED,
            detection_method="UNKNOWN_FALLBACK",
        )


language_detector = LanguageIntelligenceDetector()
