"""High-precision, multi-lingual contextual rule engine for ScamGraph Tactic Intelligence.

Implements versioned rules across English, Hindi, and Hinglish with contextual negation,
protective advisory filtering, quoted-text detection, and evidence span extraction.
"""

from dataclasses import dataclass, field
import hashlib
import re
from typing import Dict, List, Optional, Pattern, Set, Tuple

from packages.schemas.tactics import (
    ActionRequestedType,
    EvidenceSpan,
    TacticSignal,
    TacticType,
)
from ml.tactics.ontology import TACTIC_SEVERITY, TACTIC_DEFAULT_ACTIONS


@dataclass
class TacticRule:
    """Individual rule definition targeting a specific psychological manipulation tactic."""
    rule_id: str
    tactic: TacticType
    language: str  # en, hi, hinglish, multilingual
    positive_patterns: List[Pattern[str]]
    negative_patterns: List[Pattern[str]] = field(default_factory=list)
    requested_actions: List[ActionRequestedType] = field(default_factory=list)
    severity: str = "MEDIUM"
    base_confidence: float = 0.85
    weight: float = 1.0


# ---------------------------------------------------------------------------
# Global Negation, Advisory, and Quoted-Content Guards
# ---------------------------------------------------------------------------

GLOBAL_ADVISORY_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\b(never\s+share|do\s+not\s+share|don'?t\s+share|never\s+disclose|never\s+reveal)\b", re.IGNORECASE),
    re.compile(r"\b(bank\s+never\s+asks|rbi\s+never\s+asks|officials\s+never\s+ask)\b", re.IGNORECASE),
    re.compile(r"\b(police\s+(have\s+)?warn(s|ed|ing)?|cyber\s*cell\s+advisory|scam\s+alert|fraud\s+awareness)\b", re.IGNORECASE),
    re.compile(r"\b(kabhi\s+(bhi\s+)?share\s+mat\s+karna|kisi\s+ko\s+mat\s+dena|bank\s+kabhi\s+nahi\s+mangta)\b", re.IGNORECASE),
    re.compile(r"\b(beware\s+of\s+fraudsters|public\s+advisory|caution\s+notice)\b", re.IGNORECASE),
]

ROUTINE_TRANSACTION_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\b(successfully\s+(paid|received|debited|credited))\b", re.IGNORECASE),
    re.compile(r"\b(available\s+bal(ance)?|txn\s+ref\s+no|ref\s+no:?\s*\w+)\b", re.IGNORECASE),
    re.compile(r"\b(interview\s+(is\s+)?(scheduled|tomorrow|at))\b", re.IGNORECASE),
]

QUOTED_INQUIRY_PATTERNS: List[Pattern[str]] = [
    re.compile(r"\b(someone\s+told\s+me|got\s+this\s+message|is\s+this\s+(a\s+)?scam|is\s+this\s+(real|legit|genuine))\b", re.IGNORECASE),
    re.compile(r"['\"].*['\"]\s*(\?|is\s+this)", re.IGNORECASE),
]


def is_quoted_inquiry(text: str) -> bool:
    """Checks whether the user is asking about or quoting suspicious text."""
    for p in QUOTED_INQUIRY_PATTERNS:
        if p.search(text):
            return True
    return False


def is_global_advisory(text: str) -> bool:
    """Checks whether the text is an educational advisory or protective warning."""
    for p in GLOBAL_ADVISORY_PATTERNS:
        if p.search(text):
            return True
    return False


def is_routine_notification(text: str) -> bool:
    """Checks whether text is a legitimate receipt or routine schedule notification."""
    for p in ROUTINE_TRANSACTION_PATTERNS:
        if p.search(text):
            # If it's a routine transaction and doesn't contain explicit coercive threat words, treat as routine
            if not re.search(r"\b(arrest|block(ed)?|disconnect|urgent|jail|police)\b", text, re.IGNORECASE):
                return True
    return False


# ---------------------------------------------------------------------------
# Rule Catalog Across All 20 Tactics
# ---------------------------------------------------------------------------

TACTIC_RULES: List[TacticRule] = [
    # 1. CREDENTIAL_PRESSURE
    TacticRule(
        rule_id="TACTIC-CREDENTIAL-EN-001",
        tactic=TacticType.CREDENTIAL_PRESSURE,
        language="en",
        positive_patterns=[
            re.compile(r"\b(share|provide|tell\s+me|send|enter)\s+(your\s+)?(6[- ]digit\s+)?(otp|one[- ]time[- ]password|pin|atm\s+pin|netbanking\s+password|cvv)\b", re.IGNORECASE),
            re.compile(r"\b(read\s+out|forward)\s+(the\s+)?(otp|code|sms)\b", re.IGNORECASE),
            re.compile(r"\b(otp\s+is\s+required\s+to\s+(verify|unblock|cancel))\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(never\s+share|do\s+not\s+share|don'?t\s+share|never\s+disclose)\s+(your\s+)?(otp|pin|password|cvv)\b", re.IGNORECASE),
            re.compile(r"\b(bank\s+never\s+asks\s+for\s+(otp|pin))\b", re.IGNORECASE),
            re.compile(r"\b(do\s+not\s+share\s+this\s+(otp|code)\s+with\s+anyone)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SHARE_OTP, ActionRequestedType.SHARE_CREDENTIAL],
        severity="CRITICAL",
        base_confidence=0.96,
    ),
    TacticRule(
        rule_id="TACTIC-CREDENTIAL-HI-001",
        tactic=TacticType.CREDENTIAL_PRESSURE,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(otp\s+(batao|share\s*karo|send\s*karo|forward\s*karo|de\s*do|bt@o))\b", re.IGNORECASE),
            re.compile(r"\b(pin\s+number\s+(do|batao)|cvv\s+batao|code\s+batao)\b", re.IGNORECASE),
            re.compile(r"\b(verification\s+ke\s+liye\s+otp\s+(chahiye|batao|do))\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(kabhi\s+(bhi\s+)?otp\s+share\s+mat\s+karna|kisi\s+ko\s+otp\s+mat\s+dena)\b", re.IGNORECASE),
            re.compile(r"\b(otp\s+kisi\s+ke\s+saath\s+share\s+na\s+kare)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SHARE_OTP, ActionRequestedType.SHARE_CREDENTIAL],
        severity="CRITICAL",
        base_confidence=0.96,
    ),

    # 2. REMOTE_ACCESS_PRESSURE
    TacticRule(
        rule_id="TACTIC-REMOTE-EN-001",
        tactic=TacticType.REMOTE_ACCESS_PRESSURE,
        language="en",
        positive_patterns=[
            re.compile(r"\b(install|download)\s+(anydesk|quicksupport|teamviewer|rustdesk|zoho\s+assist)\b", re.IGNORECASE),
            re.compile(r"\b(share\s+(your\s+)?(mobile\s+)?screen|start\s+screen\s+sharing|allow\s+remote\s+access)\b", re.IGNORECASE),
            re.compile(r"\b(install|download)\s+(this\s+)?(\.apk|support\s+app|security\s+update\s+app)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(beware\s+of\s+fraudulent\s+screen\s+sharing\s+apps)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.INSTALL_APP, ActionRequestedType.SHARE_SCREEN, ActionRequestedType.DOWNLOAD_FILE],
        severity="CRITICAL",
        base_confidence=0.95,
    ),
    TacticRule(
        rule_id="TACTIC-REMOTE-HI-001",
        tactic=TacticType.REMOTE_ACCESS_PRESSURE,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(anydesk|quicksupport|teamviewer)\s+(download|install)\s*(karo|kijiye)\b", re.IGNORECASE),
            re.compile(r"\b(screen\s+share\s*(karo|kijiye)|screen\s+dikhao)\b", re.IGNORECASE),
            re.compile(r"\b(apk\s+file\s+install\s*karo)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.INSTALL_APP, ActionRequestedType.SHARE_SCREEN],
        severity="CRITICAL",
        base_confidence=0.95,
    ),

    # 3. SECRECY
    TacticRule(
        rule_id="TACTIC-SECRECY-EN-001",
        tactic=TacticType.SECRECY,
        language="en",
        positive_patterns=[
            re.compile(r"\b(do\s+not\s+tell|don'?t\s+tell)\s+(anyone|your\s+family|your\s+bank|the\s+police)\b", re.IGNORECASE),
            re.compile(r"\b(keep\s+(this\s+)?(strictly\s+)?(confidential|secret|between\s+us))\b", re.IGNORECASE),
            re.compile(r"\b(this\s+is\s+a\s+(secret|confidential)\s+(investigation|matter|operation))\b", re.IGNORECASE),
            re.compile(r"\b(do\s+not\s+disclose\s+this\s+to\s+anyone)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(our\s+confidentiality\s+agreement|privacy\s+policy)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.KEEP_SECRET],
        severity="HIGH",
        base_confidence=0.94,
    ),
    TacticRule(
        rule_id="TACTIC-SECRECY-HI-001",
        tactic=TacticType.SECRECY,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(kisi\s+ko\s+(bhi\s+)?(mat\s+batana|mat\s+batao|mt\s+btana))\b", re.IGNORECASE),
            re.compile(r"\b(ghar\s+walo(n)?\s+ko\s+mat\s+batana|family\s+ko\s+mat\s+batana)\b", re.IGNORECASE),
            re.compile(r"\b(bank\s+walo(n)?\s+ko\s+kuch\s+mat\s+bolna|secret\s+rakhna)\b", re.IGNORECASE),
            re.compile(r"\b(gupt\s+(janch|mamla)\s+hai)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.KEEP_SECRET],
        severity="HIGH",
        base_confidence=0.95,
    ),

    # 4. ISOLATION
    TacticRule(
        rule_id="TACTIC-ISOLATION-EN-001",
        tactic=TacticType.ISOLATION,
        language="en",
        positive_patterns=[
            re.compile(r"\b(stay\s+on\s+(the\s+)?(call|line|video\s+call|skype))\b", re.IGNORECASE),
            re.compile(r"\b(do\s+not\s+disconnect|don'?t\s+hang\s+up|do\s+not\s+cut\s+the\s+call)\b", re.IGNORECASE),
            re.compile(r"\b(lock\s+the\s+door|remain\s+in\s+your\s+room|isolate\s+yourself)\b", re.IGNORECASE),
            re.compile(r"\b(keep\s+your\s+camera\s+(turned\s+)?on|do\s+not\s+leave\s+the\s+frame)\b", re.IGNORECASE),
            re.compile(r"\b(video\s+call\s+isolation\s+required)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(please\s+hold\s+the\s+line\s+while\s+we\s+transfer)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.KEEP_SECRET],
        severity="CRITICAL",
        base_confidence=0.95,
    ),
    TacticRule(
        rule_id="TACTIC-ISOLATION-HI-001",
        tactic=TacticType.ISOLATION,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(call\s+(cut|disconnect)\s+mat\s+karna|line\s+pe\s+bane\s+raho)\b", re.IGNORECASE),
            re.compile(r"\b(kamra\s+band\s+kar\s+lo|gate\s+lock\s+kar\s+lo|room\s+me\s+akele\s+raho)\b", re.IGNORECASE),
            re.compile(r"\b(camera\s+on\s+rakhna|screen\s+se\s+mat\s+hatna)\b", re.IGNORECASE),
            re.compile(r"\b(kisi\s+se\s+baat\s+mat\s+karo)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT],
        severity="CRITICAL",
        base_confidence=0.96,
    ),

    # 5. PAYMENT_PRESSURE
    TacticRule(
        rule_id="TACTIC-PAYMENT-EN-001",
        tactic=TacticType.PAYMENT_PRESSURE,
        language="en",
        positive_patterns=[
            re.compile(r"\b(pay\s+now|pay\s+immediately|send\s+payment|transfer\s+money\s+now)\b", re.IGNORECASE),
            re.compile(r"\b(deposit\s+(₹|rs\.?|inr)?\s*[\d,]+([,\.]\d+)?\s*(immediately|now|to\s+unlock)?)\b", re.IGNORECASE),
            re.compile(r"\b(transfer\s+(₹|rs\.?|inr)?\s*[\d,]+([,\.]\d+)?)\b", re.IGNORECASE),
            re.compile(r"\b(pay\s+(₹|rs\.?|inr)?\s*[\d,]+([,\.]\d+)?)\b", re.IGNORECASE),
            re.compile(r"\b(approve\s+(the\s+)?(upi\s+)?collect\s+request|accept\s+request\s+on\s+(gpay|phonepe|paytm))\b", re.IGNORECASE),
            re.compile(r"\b(pay\s+(security\s+deposit|customs\s+fee|processing\s+fee|clearance\s+charge|tax))\b", re.IGNORECASE),
            re.compile(r"\b(recharge\s+(your\s+)?(task\s+wallet|vip\s+account))\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(payment\s+(was\s+)?(successful|received|completed))\b", re.IGNORECASE),
            re.compile(r"\b(bill\s+due\s+(date|on))\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.APPROVE_UPI_REQUEST, ActionRequestedType.PAY_FEE],
        severity="CRITICAL",
        base_confidence=0.93,
    ),
    TacticRule(
        rule_id="TACTIC-PAYMENT-HI-001",
        tactic=TacticType.PAYMENT_PRESSURE,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(abhi\s+payment\s*(karo|kijiye)|turant\s+paise\s*(bhejo|transfer\s*karo))\b", re.IGNORECASE),
            re.compile(r"\b(upi\s+(pe\s+)?(bhej\s+do|transfer\s+karo)|collect\s+request\s+accept\s+karo)\b", re.IGNORECASE),
            re.compile(r"\b(deposit\s+jama\s*karo|recharge\s*karo|paise\s+dalo)\b", re.IGNORECASE),
            re.compile(r"\b((p@y|paise)\s+(n0w|kro))\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(aapka\s+bill\s+bhugtan\s+safal\s+raha)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.APPROVE_UPI_REQUEST],
        severity="CRITICAL",
        base_confidence=0.94,
    ),

    # 6. AUTHORITY
    TacticRule(
        rule_id="TACTIC-AUTHORITY-EN-001",
        tactic=TacticType.AUTHORITY,
        language="en",
        positive_patterns=[
            re.compile(r"\b(calling\s+from|officer\s+from|official\s+from)\s+(cbi|ed|mumbai\s+police|delhi\s+police|cyber\s*crime|trai|supreme\s+court|high\s+court|rbi|income\s+tax)\b", re.IGNORECASE),
            re.compile(r"\b(calling\s+from\s+cbi\s+officer)\b", re.IGNORECASE),
            re.compile(r"\b(under\s+section\s+\d+\w*|warrant\s+issued\s+by|official\s+notice\s+from\s+(trai|cbi|police))\b", re.IGNORECASE),
            re.compile(r"\b(i\s+am\s+(inspector|officer|deputy\s+commissioner))\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(police\s+(has|have)?\s+warn(ed|ing)?|advisory\s+issued\s+by\s+police)\b", re.IGNORECASE),
            re.compile(r"\b(cbi\s+warns|rbi\s+says)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.92,
    ),
    TacticRule(
        rule_id="TACTIC-AUTHORITY-HI-001",
        tactic=TacticType.AUTHORITY,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b((police|cbi|thana|cyber\s*cell)\s+se\s+(bol\s+raha\s+hu|baat\s+kar\s+rahe\s+hai))\b", re.IGNORECASE),
            re.compile(r"\b(trai\s+se\s+notice\s+hai|police\s+enquiry\s+hai)\b", re.IGNORECASE),
            re.compile(r"\b(adhikari\s+bol\s+raha\s+hu)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(police\s+ne\s+chetavni\s+di\s+hai|police\s+advisory)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.92,
    ),

    # 7. URGENCY
    TacticRule(
        rule_id="TACTIC-URGENCY-EN-001",
        tactic=TacticType.URGENCY,
        language="en",
        positive_patterns=[
            re.compile(r"\b(within\s+\d+\s+(hours?|minutes?|mins?))\b", re.IGNORECASE),
            re.compile(r"\b(immediate\s+action\s+required|act\s+immediately|do\s+not\s+delay)\b", re.IGNORECASE),
            re.compile(r"\b(will\s+be\s+(blocked|disconnected|suspended)\s+(today|tonight|at\s+\d+:\d+))\b", re.IGNORECASE),
            re.compile(r"\b(last\s+(chance|reminder)|before\s+midnight)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(interview\s+(is\s+)?tomorrow|scheduled\s+for|working\s+days)\b", re.IGNORECASE),
            re.compile(r"\b(bill\s+due\s+on\s+\d+)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK, ActionRequestedType.REPLY],
        severity="MEDIUM",
        base_confidence=0.88,
    ),
    TacticRule(
        rule_id="TACTIC-URGENCY-HI-001",
        tactic=TacticType.URGENCY,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(turant\s*karo|aaj\s*hi\s*karo|abhi\s*ke\s*abhi)\b", re.IGNORECASE),
            re.compile(r"\b(\d+\s*ghante\s*ke\s*andar|2\s*ghante\s*me)\b", re.IGNORECASE),
            re.compile(r"\b(aaj\s*raat\s*tak\s*band\s*ho\s*jayega|der\s*mat\s*karo)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(kal\s+interview\s+hai)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK, ActionRequestedType.REPLY],
        severity="MEDIUM",
        base_confidence=0.89,
    ),

    # 8. FEAR
    TacticRule(
        rule_id="TACTIC-FEAR-EN-001",
        tactic=TacticType.FEAR,
        language="en",
        positive_patterns=[
            re.compile(r"\b(arrest\s+warrant|fir\s+registered|non[- ]bailable\s+warrant)\b", re.IGNORECASE),
            re.compile(r"\b(face\s+jail|sent\s+to\s+prison|criminal\s+charges)\b", re.IGNORECASE),
            re.compile(r"\b(digital\s+arrest|account\s+frozen\s+for\s+money\s+laundering)\b", re.IGNORECASE),
            re.compile(r"\b(electricity\s+will\s+be\s+disconnected\s+tonight)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(protect\s+yourself\s+from\s+digital\s+arrest|beware\s+of\s+fake\s+arrest)\b", re.IGNORECASE),
            re.compile(r"\b(police\s+(have\s+)?warn(s|ed)?\s+people\s+about\s+digital\s+arrest)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.93,
    ),
    TacticRule(
        rule_id="TACTIC-FEAR-HI-001",
        tactic=TacticType.FEAR,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(police\s+case\s+ho\s+jayega|giraftari\s+hogi|jail\s+jana\s+padega)\b", re.IGNORECASE),
            re.compile(r"\b(fir\s+darj\s+ho\s+gayi|account\s+freeze\s+kar\s+diya\s+jayega)\b", re.IGNORECASE),
            re.compile(r"\b(bijli\s+cut\s+ho\s+jayegi|light\s+kat\s+(di\s+)?jayegi)\b", re.IGNORECASE),
            re.compile(r"\b(police\s+ghar\s+aayegi)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(digital\s+arrest\s+se\s+bache)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.SEND_PAYMENT],
        severity="HIGH",
        base_confidence=0.93,
    ),

    # 9. GREED / FINANCIAL LURE
    TacticRule(
        rule_id="TACTIC-GREED-EN-001",
        tactic=TacticType.GREED,
        language="en",
        positive_patterns=[
            re.compile(r"\b(earn\s+(₹|rs\.?|inr)?\s*[\d,]+\s*(daily|per\s+day))\b", re.IGNORECASE),
            re.compile(r"\b(guaranteed\s+(returns?|profit|income)|double\s+your\s+money)\b", re.IGNORECASE),
            re.compile(r"\b(part[- ]time\s+job\s+earn\s+money\s+from\s+home)\b", re.IGNORECASE),
            re.compile(r"\b(simple\s+(youtube\s+like|google\s+review)\s+task\s+to\s+earn)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(subject\s+to\s+market\s+risk|terms\s+and\s+conditions\s+apply)\b", re.IGNORECASE),
            re.compile(r"\b(competitive\s+salary\s+based\s+on\s+experience)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM, ActionRequestedType.CLICK_LINK],
        severity="MEDIUM",
        base_confidence=0.88,
    ),
    TacticRule(
        rule_id="TACTIC-GREED-HI-001",
        tactic=TacticType.GREED,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(ghar\s+baithe\s+(paise\s+kamaye|kamai\s+karo))\b", re.IGNORECASE),
            re.compile(r"\b(roj\s+[\d,]+\s*(rupaye|kamao))\b", re.IGNORECASE),
            re.compile(r"\b(paisa\s+double|guaranteed\s+munafa)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM, ActionRequestedType.CLICK_LINK],
        severity="MEDIUM",
        base_confidence=0.89,
    ),

    # 10. SCARCITY
    TacticRule(
        rule_id="TACTIC-SCARCITY-EN-001",
        tactic=TacticType.SCARCITY,
        language="en",
        positive_patterns=[
            re.compile(r"\b(only\s+\d+\s+(slots?|seats?|vacanc(y|ies))\s+(left|remaining))\b", re.IGNORECASE),
            re.compile(r"\b(limited\s+period\s+offer|first\s+\d+\s+people\s+only)\b", re.IGNORECASE),
            re.compile(r"\b(offer\s+expires\s+in\s+\d+\s+minutes)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(sale\s+ends\s+sunday|routine\s+clearance)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK, ActionRequestedType.REPLY],
        severity="LOW",
        base_confidence=0.82,
    ),
    TacticRule(
        rule_id="TACTIC-SCARCITY-HI-001",
        tactic=TacticType.SCARCITY,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(sirf\s+\d+\s+(seat|slot)\s+bache?\s+hai)\b", re.IGNORECASE),
            re.compile(r"\b(aakhri\s+mauka\s+hai|kuch\s+hi\s+seats)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK],
        severity="LOW",
        base_confidence=0.84,
    ),

    # 11. SOCIAL_PROOF
    TacticRule(
        rule_id="TACTIC-SOCPROOF-EN-001",
        tactic=TacticType.SOCIAL_PROOF,
        language="en",
        positive_patterns=[
            re.compile(r"\b(see\s+withdrawal\s+proofs|check\s+group\s+member\s+earnings)\b", re.IGNORECASE),
            re.compile(r"\b(thousands\s+of\s+members\s+already\s+withdrew|all\s+members\s+made\s+profit)\b", re.IGNORECASE),
            re.compile(r"\b(look\s+at\s+the\s+payment\s+screenshots\s+in\s+group)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM],
        severity="LOW",
        base_confidence=0.85,
    ),
    TacticRule(
        rule_id="TACTIC-SOCPROOF-HI-001",
        tactic=TacticType.SOCIAL_PROOF,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(sabko\s+withdrawal\s+mil\s+gaya|group\s+me\s+proof\s+dekho)\b", re.IGNORECASE),
            re.compile(r"\b(members\s+ne\s+paise\s+kamaye|dekho\s+sab\s+kama\s+rahe\s+hai)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM],
        severity="LOW",
        base_confidence=0.86,
    ),

    # 12. ROMANCE
    TacticRule(
        rule_id="TACTIC-ROMANCE-EN-001",
        tactic=TacticType.ROMANCE,
        language="en",
        positive_patterns=[
            re.compile(r"\b(sent\s+a\s+costly\s+gift\s+for\s+you|customs\s+held\s+parcel\s+darling)\b", re.IGNORECASE),
            re.compile(r"\b(want\s+to\s+marry\s+you|financial\s+help\s+for\s+our\s+marriage)\b", re.IGNORECASE),
            re.compile(r"\b(my\s+love,\s+please\s+clear\s+the\s+airport\s+customs)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.PAY_FEE],
        severity="MEDIUM",
        base_confidence=0.90,
    ),

    # 13. TRUST_BUILDING
    TacticRule(
        rule_id="TACTIC-TRUST-EN-001",
        tactic=TacticType.TRUST_BUILDING,
        language="en",
        positive_patterns=[
            re.compile(r"\b(first\s+task\s+is\s+free|test\s+withdrawal\s+of\s+(₹|rs\.?|inr)?\s*[\d,]+\s+credited)\b", re.IGNORECASE),
            re.compile(r"\b(try\s+with\s+small\s+amount\s+first|you\s+can\s+withdraw\s+anytime)\b", re.IGNORECASE),
            re.compile(r"\b(we\s+are\s+a\s+registered\s+iso\s+company|trust\s+us,\s+see\s+our\s+certificate)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.REPLY, ActionRequestedType.INVEST_MORE],
        severity="LOW",
        base_confidence=0.86,
    ),
    TacticRule(
        rule_id="TACTIC-TRUST-HI-001",
        tactic=TacticType.TRUST_BUILDING,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(pehle\s+chota\s+task\s+karo|chota\s+deposit\s+karke\s+dekh\s+lo)\b", re.IGNORECASE),
            re.compile(r"\b(150\s+rupaye\s+mil\s+gaye\s+na|vishwas\s+karo\s+pehle)\b", re.IGNORECASE),
            re.compile(r"\b(kabhi\s+bhi\s+withdraw\s+kar\s+sakte\s+ho)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.REPLY, ActionRequestedType.INVEST_MORE],
        severity="LOW",
        base_confidence=0.88,
    ),

    # 14. RECIPROCITY
    TacticRule(
        rule_id="TACTIC-RECIPROCITY-EN-001",
        tactic=TacticType.RECIPROCITY,
        language="en",
        positive_patterns=[
            re.compile(r"\b(we\s+helped\s+you\s+earn\s+profit,\s+now\s+(invest|deposit))\b", re.IGNORECASE),
            re.compile(r"\b(we\s+gave\s+you\s+profit,\s+now\s+invest)\b", re.IGNORECASE),
            re.compile(r"\b(we\s+recovered\s+your\s+lost\s+money,\s+pay\s+our\s+(fee|commission))\b", re.IGNORECASE),
            re.compile(r"\b(you\s+received\s+the\s+bonus,\s+now\s+complete\s+the\s+recharge)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.INVEST_MORE],
        severity="MEDIUM",
        base_confidence=0.87,
    ),
    TacticRule(
        rule_id="TACTIC-RECIPROCITY-HI-001",
        tactic=TacticType.RECIPROCITY,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(humne\s+profit\s+diya\s+ab\s+(recharge|deposit)\s+karo)\b", re.IGNORECASE),
            re.compile(r"\b(bonus\s+mil\s+gaya\s+ab\s+next\s+task\s+karo)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.INVEST_MORE],
        severity="MEDIUM",
        base_confidence=0.88,
    ),

    # 15. LOSS_AVERSION
    TacticRule(
        rule_id="TACTIC-LOSSAVERSION-EN-001",
        tactic=TacticType.LOSS_AVERSION,
        language="en",
        positive_patterns=[
            re.compile(r"\b(pay\s+(₹|rs\.?|inr)?\s*[\d,]+\s+or\s+lose\s+(your\s+entire|your\s+balance|your\s+earnings))\b", re.IGNORECASE),
            re.compile(r"\b(funds\s+will\s+be\s+(forfeited|frozen\s+permanently|lapsed)\s+if\s+tax\s+not\s+paid)\b", re.IGNORECASE),
            re.compile(r"\b(all\s+your\s+earnings\s+will\s+be\s+lost\s+unless\s+you\s+upgrade)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.PAY_FEE],
        severity="HIGH",
        base_confidence=0.91,
    ),
    TacticRule(
        rule_id="TACTIC-LOSSAVERSION-HI-001",
        tactic=TacticType.LOSS_AVERSION,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(paise\s+do\s+varna\s+sara\s+balance\s+(doob|chala)\s+jayega)\b", re.IGNORECASE),
            re.compile(r"\b(tax\s+nahi\s+bhara\s+to\s+account\s+lapse\s+ho\s+jayega)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.PAY_FEE],
        severity="HIGH",
        base_confidence=0.92,
    ),

    # 16. FAKE_REWARD
    TacticRule(
        rule_id="TACTIC-FAKEREWARD-EN-001",
        tactic=TacticType.FAKE_REWARD,
        language="en",
        positive_patterns=[
            re.compile(r"\b(you\s+(have\s+)?won\s+(a\s+)?(lottery|lucky\s+draw|cashback|prize)\s+of\s+(₹|rs\.?|inr)?\s*[\d,]+)\b", re.IGNORECASE),
            re.compile(r"\b(congratulations!?\s+claim\s+your\s+(gift\s+card|reward|iphone))\b", re.IGNORECASE),
            re.compile(r"\b(scan\s+qr\s+code\s+to\s+receive\s+cashback)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(reward\s+points\s+statement|points\s+earned\s+on\s+purchase)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK, ActionRequestedType.SCAN_QR],
        severity="MEDIUM",
        base_confidence=0.90,
    ),
    TacticRule(
        rule_id="TACTIC-FAKEREWARD-HI-001",
        tactic=TacticType.FAKE_REWARD,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(aapne\s+[\d,]+\s*(lakh|crore)\s+ki\s+lottery\s+jeeti)\b", re.IGNORECASE),
            re.compile(r"\b(inaam\s+nikla\s+hai|lucky\s+draw\s+me\s+naam\s+aaya\s+hai)\b", re.IGNORECASE),
            re.compile(r"\b(cashback\s+paane\s+ke\s+liye\s+scan\s+karo)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CLICK_LINK, ActionRequestedType.SCAN_QR],
        severity="MEDIUM",
        base_confidence=0.91,
    ),

    # 17. THREAT
    TacticRule(
        rule_id="TACTIC-THREAT-EN-001",
        tactic=TacticType.THREAT,
        language="en",
        positive_patterns=[
            re.compile(r"\b(we\s+will\s+leak\s+(your\s+)?(private\s+photos|video|contacts))\b", re.IGNORECASE),
            re.compile(r"\b(police\s+will\s+raid\s+your\s+(house|home)\s+in\s+\d+\s+hour)\b", re.IGNORECASE),
            re.compile(r"\b(we\s+will\s+(defame|ruin)\s+your\s+reputation)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.DO_NOT_DISCONNECT],
        severity="CRITICAL",
        base_confidence=0.95,
    ),
    TacticRule(
        rule_id="TACTIC-THREAT-HI-001",
        tactic=TacticType.THREAT,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(video\s+leak\s+kar\s+denge|photos\s+viral\s+kar\s+denge)\b", re.IGNORECASE),
            re.compile(r"\b(barbaad\s+kar\s+denge|sabko\s+bhej\s+denge)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.SEND_PAYMENT, ActionRequestedType.DO_NOT_DISCONNECT],
        severity="CRITICAL",
        base_confidence=0.95,
    ),

    # 18. IMPERSONATION
    TacticRule(
        rule_id="TACTIC-IMPERSONATION-EN-001",
        tactic=TacticType.IMPERSONATION,
        language="en",
        positive_patterns=[
            re.compile(r"\b(calling\s+from\s+(fedex|bluedart|dhl)\s+customs\s+department)\b", re.IGNORECASE),
            re.compile(r"\b(i\s+am\s+the\s+ceo\s+of|this\s+is\s+state\s+electricity\s+board\s+head\s+office)\b", re.IGNORECASE),
            re.compile(r"\b(sbi\s+security\s+division\s+alert\s+desk|sbi\s+security\s+division)\b", re.IGNORECASE),
        ],
        negative_patterns=[
            re.compile(r"\b(tracking\s+alert:\s+package\s+delivered|fedex\s+tracking)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CALL_NUMBER, ActionRequestedType.CLICK_LINK],
        severity="HIGH",
        base_confidence=0.90,
    ),
    TacticRule(
        rule_id="TACTIC-IMPERSONATION-HI-001",
        tactic=TacticType.IMPERSONATION,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(fedex\s+parcel\s+department\s+se\s+bol\s+raha\s+hu)\b", re.IGNORECASE),
            re.compile(r"\b(bijli\s+vibhag\s+head\s+office\s+se)\b", re.IGNORECASE),
            re.compile(r"\b(sbi\s+branch\s+manager\s+bol\s+raha\s+hu)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.CALL_NUMBER, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.91,
    ),

    # 19. PLATFORM_MIGRATION
    TacticRule(
        rule_id="TACTIC-MIGRATION-EN-001",
        tactic=TacticType.PLATFORM_MIGRATION,
        language="en",
        positive_patterns=[
            re.compile(r"\b(message\s+me\s+on\s+whatsapp\s+(at|for\s+details)?)\b", re.IGNORECASE),
            re.compile(r"\b(join\s+(our\s+)?telegram\s+(@\w+|channel|group)?)\b", re.IGNORECASE),
            re.compile(r"\b(telegram\s+@\w+)\b", re.IGNORECASE),
            re.compile(r"\b(contact\s+(our\s+)?(receptionist|manager)\s+on\s+telegram\s*@\w+)\b", re.IGNORECASE),
            re.compile(r"\b(let\s+us\s+continue\s+on\s+(telegram|whatsapp))\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM, ActionRequestedType.ADD_CONTACT],
        severity="MEDIUM",
        base_confidence=0.92,
    ),
    TacticRule(
        rule_id="TACTIC-MIGRATION-HI-001",
        tactic=TacticType.PLATFORM_MIGRATION,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(whatsapp\s+pe\s+(aao|message\s*karo))\b", re.IGNORECASE),
            re.compile(r"\b(telegram\s+pe\s+(msg\s*karo|contact\s*karo|aao))\b", re.IGNORECASE),
            re.compile(r"\b(telegram\s+group\s+join\s*karo)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.MOVE_PLATFORM, ActionRequestedType.ADD_CONTACT],
        severity="MEDIUM",
        base_confidence=0.92,
    ),

    # 20. COMPLIANCE_PRESSURE
    TacticRule(
        rule_id="TACTIC-COMPLIANCE-EN-001",
        tactic=TacticType.COMPLIANCE_PRESSURE,
        language="en",
        positive_patterns=[
            re.compile(r"\b(answer\s+only\s+(yes\s+or\s+no|with\s+yes|with\s+no))\b", re.IGNORECASE),
            re.compile(r"\b(follow\s+instructions\s+without\s+(argument|interruption|question))\b", re.IGNORECASE),
            re.compile(r"\b(do\s+exactly\s+as\s+you\s+are\s+told\s+by\s+the\s+officer)\b", re.IGNORECASE),
            re.compile(r"\b(do\s+not\s+argue\s+with\s+law\s+enforcement)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.91,
    ),
    TacticRule(
        rule_id="TACTIC-COMPLIANCE-HI-001",
        tactic=TacticType.COMPLIANCE_PRESSURE,
        language="hinglish",
        positive_patterns=[
            re.compile(r"\b(sirf\s+(ha|na|haan|nahi)\s+me\s+(jawab\s+do|bolo))\b", re.IGNORECASE),
            re.compile(r"\b(jaisa\s+bola\s+hai\s+waisa\s+karo|bahas\s+mat\s+karo)\b", re.IGNORECASE),
            re.compile(r"\b(order\s+follow\s+karo|chupchap\s+suno)\b", re.IGNORECASE),
        ],
        requested_actions=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
        severity="HIGH",
        base_confidence=0.92,
    ),
]


class RuleBasedTacticEngine:
    """Evaluates rules against input text to extract evidence-backed tactic signals."""

    def __init__(self, rules: Optional[List[TacticRule]] = None):
        self.rules = rules or TACTIC_RULES

    def match(
        self,
        text: str,
        artifact_id: Optional[str] = None,
        event_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        turn_index: Optional[int] = None,
    ) -> List[TacticSignal]:
        """Runs the rule set against text, resolving negations and evidence spans."""
        if not text or not text.strip():
            return []

        # Check global inquiry / quote context
        quoted = is_quoted_inquiry(text)

        # Check global routine notification (e.g. routine bill receipt without threats)
        if is_routine_notification(text):
            return []

        # Check global advisory (e.g. "Police advisory: never share OTP with anyone")
        global_advisory = is_global_advisory(text)

        signals: List[TacticSignal] = []
        matched_tactics: Set[TacticType] = set()

        for rule in self.rules:
            # Check negative patterns first for this rule
            rule_negated = False
            for neg in rule.negative_patterns:
                if neg.search(text):
                    rule_negated = True
                    break

            if rule_negated or (global_advisory and rule.tactic in (TacticType.CREDENTIAL_PRESSURE, TacticType.AUTHORITY, TacticType.FEAR, TacticType.IMPERSONATION)):
                continue

            # Evaluate positive patterns
            for pos in rule.positive_patterns:
                match = pos.search(text)
                if match:
                    span_text = match.group(0)
                    start_idx = match.start()
                    end_idx = match.end()

                    span = EvidenceSpan(
                        start=start_idx,
                        end=end_idx,
                        text=span_text,
                        confidence=rule.base_confidence,
                    )

                    # Determine requested actions
                    actions = list(rule.requested_actions) or list(TACTIC_DEFAULT_ACTIONS.get(rule.tactic, []))

                    signal = TacticSignal(
                        tactic=rule.tactic,
                        confidence=rule.base_confidence,
                        severity=rule.severity,
                        artifact_id=artifact_id,
                        event_id=event_id,
                        incident_id=incident_id,
                        conversation_id=conversation_id,
                        turn_index=turn_index,
                        supporting_spans=[span],
                        requested_actions=actions,
                        detector_sources=["RULE"],
                        is_negated=False,
                        is_quoted=quoted,
                        metadata={"rule_id": rule.rule_id, "language": rule.language},
                    )

                    # Deduplicate by tactic type across patterns
                    if rule.tactic not in matched_tactics:
                        matched_tactics.add(rule.tactic)
                        signals.append(signal)
                    else:
                        # Append span to existing signal
                        for s in signals:
                            if s.tactic == rule.tactic:
                                s.supporting_spans.append(span)
                    break

        return signals
