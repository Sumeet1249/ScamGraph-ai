"""Protective Security Negation Engine for ScamGraph AI (Prompt 17 / Phase 5C).

Detects whether a security action (like sharing OTP or clicking a link) is being
explicitly WARNED AGAINST rather than DEMANDED.

Examples:
- English: "Never share your OTP with anyone." -> Protective Negation (NOT a scam demand!)
- Hindi: "अपना OTP किसी के साथ साझा न करें।" -> Protective Negation
- Hinglish: "OTP kisi ko mat dena" / "OTP share mat karo" -> Protective Negation
- Bengali: "OTP কাওকে দেবেন না।" -> Protective Negation

Critical Rule: Legitimate bank security advisories warning users NOT to share credentials
must NEVER be falsely flagged as credential pressure scams merely because the word 'OTP' is present.
"""

import re
from typing import List, Optional
from packages.schemas.multilingual import NegationSignal
from packages.schemas.tactics import ActionRequestedType


# Multilingual protective negation pattern rules
PROTECTIVE_NEGATION_RULES = [
    # English
    (
        re.compile(r"\b(?:never|do\s+not|don'?t|should\s+not)\s+(?:share|disclose|reveal|provide|send)\s+(?:your\s+)?(?:otp|password|pin|cvv|credentials|details)\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "English protective security advisory against credential disclosure",
    ),
    (
        re.compile(r"\b(?:bank|rbi|police|officials)\s+(?:never|will\s+never)\s+ask\s+(?:for\s+)?(?:otp|password|pin|cvv)\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Official authority disclaimer: Bank never asks for credentials",
    ),
    # Hindi (Devanagari)
    (
        re.compile(r"(?:अपना\s+)?(?:ओटीपी|otp|पासवर्ड|पिन)\s+(?:किसी\s+(?:को\s+|के\s+साथ\s+)?(?:भी\s+)?)?(?:साझा\s+न\s+करें|मत\s+बताएं|मत\s+दीजिए|मत\s+दें|नहीं\s+मांगता|न\s+बताएं)", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hindi Devanagari protective warning against OTP sharing",
    ),
    (
        re.compile(r"(?:साझा\s+न\s+करें|मत\s+बताएं|मत\s+दीजिए|मत\s+दें).*(?:ओटीपी|otp|पासवर्ड|पिन)", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hindi Devanagari inverted protective warning against OTP sharing",
    ),
    (
        re.compile(r"(?:बैंक\s+|आरबीआई\s+)?कभी\s+(?:भी\s+)?(?:otp|ओटीपी|पासवर्ड)\s+नहीं\s+मांगता", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hindi authority disclaimer: Bank never asks for OTP",
    ),
    # Hinglish / Roman Hindi
    (
        re.compile(r"\b(?:otp|password|pin)\s+(?:kisi\s+ko\s+)?(?:mat\s+dena|mat\s+batao|mat\s+share\s+karo|mt\s+dena|mt\s+btao|mt\s+batao|nhi\s+dena|share\s+mat\s+karo|share\s+mt\s+karo)\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hinglish protective warning against OTP sharing",
    ),
    (
        re.compile(r"\b(?:kabhi\s+(?:bhi\s+)?)?(?:otp|password)\s+(?:share\s+)?(?:mat\s+karo|mt\s+karo|mat\s+dena)\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hinglish instruction: Never share OTP",
    ),
    (
        re.compile(r"\b(?:kisi\s+ko\s+)?(?:mat\s+dena|mat\s+batao|mt\s+btao|mat\s+share\s+karo).*(?:otp|password|pin)\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hinglish inverted warning: Do not share OTP",
    ),
    (
        re.compile(r"\b(?:bank\s+|police\s+)?kabhi\s+(?:bhi\s+)?(?:otp|password)\s+nahi\s+mangta\b", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Hinglish disclaimer: Bank never asks for OTP",
    ),
    # Bengali
    (
        re.compile(r"(?:otp|ওটিপি)\s+(?:কাওকে\s+|কাউকে\s+)?(?:দেবেন\s+না|শেয়ার\s+করবেন\s+না|বলবেন\s+না)", re.IGNORECASE),
        ActionRequestedType.SHARE_OTP,
        "Bengali protective warning against OTP sharing",
    ),
]


class ProtectiveNegationEngine:
    """Evaluates semantic negation to prevent false positive credential alarms."""

    def evaluate(self, text: str) -> NegationSignal:
        """Determines if the text contains a protective security advisory."""
        if not text:
            return NegationSignal()

        for pattern, action_type, explanation in PROTECTIVE_NEGATION_RULES:
            match = pattern.search(text)
            if match:
                matched_span = match.group(0)
                return NegationSignal(
                    has_negation=True,
                    is_protective_advisory=True,
                    negated_action=action_type,
                    negation_tokens=[matched_span],
                    confidence=0.98,
                    explanation=explanation,
                )

        return NegationSignal(
            has_negation=False,
            is_protective_advisory=False,
            negated_action=None,
            confidence=0.90,
        )


protective_negation_engine = ProtectiveNegationEngine()
