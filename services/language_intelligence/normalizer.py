"""Indic Text Normalizer for ScamGraph AI (Prompt 17 / Phase 5C).

Performs robust text cleaning for Indian multilingual and code-mixed messaging noise
without destroying meaning or corrupting security-significant tokens.

Features:
- Unicode NFKC normalization
- Zero-width space/joiner removal where safe
- Elongation / character repetition reduction (e.g. 'jaldiiiii' -> 'jaldi')
- Roman Hindi phonetic spelling standardization (e.g. 'kro' -> 'karo', 'mt' -> 'mat')
- Currency and amount normalization (e.g. '500 rs', '५०० रुपये' -> '₹500')
- Absolute preservation of security tokens: UPI IDs, phone numbers, URLs, OTPs, handles
"""

import re
from typing import Dict, List, Tuple
import unicodedata

# Security token preservation regex patterns
URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)
UPI_VPA_PATTERN = re.compile(r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b")
PHONE_PATTERN = re.compile(r"(?:\+91[\-\s]?)?[6-9]\d{9}\b")
HANDLE_PATTERN = re.compile(r"@[a-zA-Z0-9_]{3,32}")

# Devanagari numerals to ASCII digits
DEVANAGARI_DIGITS = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

# Common Roman-Hindi spelling normalizations
SPELLING_NORMALIZATIONS = {
    r"\bkro\b": "karo",
    r"\bkrdo\b": "kar do",
    r"\bkardo\b": "kar do",
    r"\bkr\s+dena\b": "kar dena",
    r"\bkrdena\b": "kar dena",
    r"\bmt\b": "mat",               # Critical for negation: "share mt karo" -> "share mat karo"
    r"\bmat\s+kro\b": "mat karo",
    r"\bbtao\b": "batao",
    r"\bbtaiye\b": "bataiye",
    r"\bplz\b": "please",
    r"\bpls\b": "please",
    r"\burgnt\b": "urgent",
    r"\bjldi\b": "jaldi",
    r"\bmsg\b": "message",
    r"\btxn\b": "transaction",
    r"\bacct?\b": "account",
}


class IndicTextNormalizer:
    """Enterprise text normalizer preserving security entities and emotional urgency."""

    def __init__(self):
        self.version = "IndicNorm-v2.0"

    def normalize(self, text: str) -> Tuple[str, List[str], float]:
        """
        Normalizes Indic/code-mixed text.
        Returns: (normalized_text, normalization_steps_applied, urgency_intensity_score)
        """
        if not text:
            return "", [], 0.0

        steps: List[str] = []
        urgency_score = 0.0

        # 1. Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", text)
        steps.append("UNICODE_NFKC")

        # 2. Strip dangerous zero-width and invisible characters
        zero_width_chars = ["\u200B", "\u200C", "\u200D", "\u200E", "\u200F", "\uFEFF", "\u2060"]
        has_zw = any(c in norm for c in zero_width_chars)
        if has_zw:
            for c in zero_width_chars:
                norm = norm.replace(c, "")
            steps.append("ZERO_WIDTH_REMOVAL")

        # 3. Protect security tokens before modifying words
        preserved_tokens: Dict[str, str] = {}
        token_counter = 0

        def protect(match):
            nonlocal token_counter
            placeholder = f"__SG_SEC_TOKEN_{token_counter}__"
            preserved_tokens[placeholder] = match.group(0)
            token_counter += 1
            return placeholder

        # Protect URLs, UPI IDs, Phones, Handles
        norm = URL_PATTERN.sub(protect, norm)
        norm = UPI_VPA_PATTERN.sub(protect, norm)
        norm = PHONE_PATTERN.sub(protect, norm)
        norm = HANDLE_PATTERN.sub(protect, norm)

        # 4. Convert Devanagari numerals to ASCII digits
        has_dev_digit = any(d in norm for d in DEVANAGARI_DIGITS)
        if has_dev_digit:
            for d, a in DEVANAGARI_DIGITS.items():
                norm = norm.replace(d, a)
            steps.append("DEVANAGARI_DIGITS_CONVERTED")

        # 5. Handle character repetition / elongation (e.g., 'jaldiiiii' -> 'jaldi', 'urgentttt' -> 'urgent')
        # Detect and calculate urgency intensity boost
        elongation_matches = list(re.finditer(r"([a-zA-Z!?.])\1{2,}", norm))
        if elongation_matches:
            urgency_score = min(1.0, len(elongation_matches) * 0.25)
            # Collapse to max 1 for letters (except vowels/punctuation max 1 or 2)
            norm = re.sub(r"([a-zA-Z])\1{2,}", r"\1", norm)
            # Collapse multiple punctuation (e.g. '!!!!' -> '!')
            norm = re.sub(r"([!?])\1+", r"\1", norm)
            steps.append("ELONGATION_COLLAPSED")

        # 6. Normalize currency and payment amount expressions (₹500, Rs 500, 500 rs, 500 rupaye, ५०० रुपये)
        amt_pattern_1 = re.compile(r"(?:^|\b|\s)(?:rs\.?|inr|rupees?|rupaye?|रुपये|रुपया|টাকা)\s*(\d+(?:,\d+)*(?:\.\d+)?)(?:\b|\s|$)", re.IGNORECASE)
        amt_pattern_2 = re.compile(r"(?:^|\b|\s)(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rs\.?|inr|rupees?|rupaye?|रुपये|रुपया|টাকা|/-)(?:\b|\s|$)", re.IGNORECASE)

        if amt_pattern_1.search(norm) or amt_pattern_2.search(norm):
            norm = amt_pattern_1.sub(r" ₹\1 ", norm)
            norm = amt_pattern_2.sub(r" ₹\1 ", norm)
            steps.append("AMOUNT_NORMALIZED")

        # 7. Apply Roman-Hindi spelling normalizations
        for pat, repl in SPELLING_NORMALIZATIONS.items():
            if re.search(pat, norm, re.IGNORECASE):
                norm = re.sub(pat, repl, norm, flags=re.IGNORECASE)
                steps.append(f"SPELLING_NORMALIZED_{repl.upper()}")

        # 8. Restore preserved security tokens
        for placeholder, original_token in preserved_tokens.items():
            norm = norm.replace(placeholder, original_token)

        # 9. Normalize multiple whitespaces
        norm = re.sub(r"\s+", " ", norm).strip()

        return norm, list(dict.fromkeys(steps)), urgency_score


indic_normalizer = IndicTextNormalizer()
