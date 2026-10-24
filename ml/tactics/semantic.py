"""Semantic Prototype-Based Tactic Matcher for ScamGraph AI V2.

Compares incoming text against calibrated positive and negative prototypes
using token-vector projection and calibrated similarity thresholds.
"""

import math
import re
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.tactics import (
    ActionRequestedType,
    EvidenceSpan,
    TacticSignal,
    TacticType,
)
from ml.tactics.ontology import TACTIC_SEVERITY, TACTIC_DEFAULT_ACTIONS


# Calibrated prototypes across high-impact tactics
TACTIC_PROTOTYPES: Dict[TacticType, Dict[str, List[str]]] = {
    TacticType.AUTHORITY: {
        "positive": [
            "calling from Mumbai police cyber crime department",
            "this is an official arrest order from the Supreme Court and CBI",
            "TRAI notice regarding illegal telecom activity on your Aadhaar card",
            "Customs officer speaking from international airport terminal",
        ],
        "negative": [
            "police advisory warning citizens against online fraud",
            "cyber crime cell advises people never to share personal data",
            "police warning regarding digital arrest scams in your area",
        ],
    },
    TacticType.FEAR: {
        "positive": [
            "an arrest warrant has been registered against you and you will go to jail",
            "your bank accounts and assets will be frozen immediately for money laundering",
            "electricity connection will be disconnected tonight due to unpaid bill",
        ],
        "negative": [
            "beware of fake electricity disconnection alerts",
            "do not panic if someone calls claiming an arrest warrant",
        ],
    },
    TacticType.SECRECY: {
        "positive": [
            "keep this secret and do not tell your family members or bank staff",
            "this investigation is strictly confidential and must not be disclosed",
            "kisi ko mat batana ghar walo ko bhi nahi",
        ],
        "negative": [
            "read our confidentiality policy and privacy terms",
            "bank respects the confidentiality of user account records",
        ],
    },
    TacticType.ISOLATION: {
        "positive": [
            "remain on the video call and lock yourself in a closed room",
            "do not disconnect this call or you will face immediate arrest",
            "stay on line and do not speak with anyone in the house",
        ],
        "negative": [
            "please hold the line while our support executive assists you",
            "stay connected to high speed wifi for better call quality",
        ],
    },
    TacticType.PAYMENT_PRESSURE: {
        "positive": [
            "transfer ₹15,000 immediately to verify your account or pay security deposit",
            "approve the UPI collect request right now to release your funds",
            "deposit money urgently into the clearing account",
        ],
        "negative": [
            "your bill of 450 rupees was paid successfully",
            "reminder that the monthly bill is due on the 28th",
        ],
    },
    TacticType.CREDENTIAL_PRESSURE: {
        "positive": [
            "tell me the 6 digit OTP you just received on your mobile phone",
            "enter your ATM PIN and netbanking password to update KYC",
            "share the verification code sent to your SMS",
        ],
        "negative": [
            "never share your OTP or PIN with anyone including bank staff",
            "bank never calls to ask for OTP or internet banking passwords",
        ],
    },
    TacticType.REMOTE_ACCESS_PRESSURE: {
        "positive": [
            "install AnyDesk or QuickSupport application on your mobile device",
            "share your mobile screen with the technical executive to complete verification",
            "download and run this APK file to receive the security patch",
        ],
        "negative": [
            "beware of fraudsters asking to install AnyDesk or screen sharing apps",
        ],
    },
    TacticType.PLATFORM_MIGRATION: {
        "positive": [
            "message our hiring manager on Telegram at username to get job details",
            "move to WhatsApp chat for faster task processing and daily income",
            "join our private Telegram group for investment instructions",
        ],
        "negative": [
            "official support is only provided via our registered helpdesk email",
        ],
    },
    TacticType.TRUST_BUILDING: {
        "positive": [
            "complete this small test task and we will immediately credit ₹150",
            "you can withdraw small profits first to build your confidence in our platform",
            "we are a legitimate government registered ISO enterprise",
        ],
        "negative": [
            "welcome to your new savings account thank you for banking with us",
        ],
    },
    TacticType.RECIPROCITY: {
        "positive": [
            "we gave you free profits now deposit ₹3,000 for VIP tasks",
            "we recovered your lost investment so pay our 10% legal fee",
        ],
        "negative": [
            "refer a colleague to get a ₹100 discount coupon on your next order",
        ],
    },
    TacticType.LOSS_AVERSION: {
        "positive": [
            "pay ₹5,000 tax clearance now or your ₹60,000 balance will be permanently lost",
            "your accumulated wallet profits will lapse unless you pay the unlock fee",
        ],
        "negative": [
            "purchase insurance coverage to mitigate against potential market loss",
        ],
    },
    TacticType.FAKE_REWARD: {
        "positive": [
            "congratulations you have won a lottery prize of 25 lakhs in the lucky draw",
            "scan this QR code to claim your 2,000 rupees cashback gift voucher",
        ],
        "negative": [
            "credit card statement: 120 reward points credited on grocery purchase",
        ],
    },
}


def _tokenize(text: str) -> List[str]:
    """Lightweight whitespace and punctuation-stripped tokenization."""
    return [w for w in re.split(r"\W+", text.lower()) if len(w) > 2]


def _bow_vector(tokens: List[str]) -> Dict[str, float]:
    """Computes normalized term frequency vector."""
    tf: Dict[str, float] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0
    norm = math.sqrt(sum(v * v for v in tf.values()))
    if norm > 0:
        for k in tf:
            tf[k] /= norm
    return tf


def _cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Computes cosine similarity between two term frequency vectors."""
    score = 0.0
    for k, val in v1.items():
        if k in v2:
            score += val * v2[k]
    return score


class SemanticTacticMatcher:
    """Performs prototype-based semantic matching with threshold calibration."""

    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold
        # Pre-compute prototype vectors
        self.positive_vectors: Dict[TacticType, List[Dict[str, float]]] = {}
        self.negative_vectors: Dict[TacticType, List[Dict[str, float]]] = {}

        for tactic, exemplars in TACTIC_PROTOTYPES.items():
            self.positive_vectors[tactic] = [_bow_vector(_tokenize(t)) for t in exemplars.get("positive", [])]
            self.negative_vectors[tactic] = [_bow_vector(_tokenize(t)) for t in exemplars.get("negative", [])]

    def match(
        self,
        text: str,
        artifact_id: Optional[str] = None,
        event_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        turn_index: Optional[int] = None,
    ) -> List[TacticSignal]:
        """Matches text against positive and negative prototypes."""
        tokens = _tokenize(text)
        if not tokens:
            return []
        query_vec = _bow_vector(tokens)

        signals: List[TacticSignal] = []

        for tactic, pos_vecs in self.positive_vectors.items():
            max_pos_sim = max((_cosine_similarity(query_vec, pv) for pv in pos_vecs), default=0.0)
            neg_vecs = self.negative_vectors.get(tactic, [])
            max_neg_sim = max((_cosine_similarity(query_vec, nv) for nv in neg_vecs), default=0.0)

            # Requires positive similarity above threshold AND higher than negative prototypes
            if max_pos_sim >= self.threshold and max_pos_sim > (max_neg_sim + 0.10):
                # Build supporting span preview
                span = EvidenceSpan(
                    start=0,
                    end=min(len(text), 100),
                    text=text[:100],
                    confidence=round(max_pos_sim, 3),
                )

                signal = TacticSignal(
                    tactic=tactic,
                    confidence=round(min(max_pos_sim + 0.2, 0.95), 2),
                    severity=TACTIC_SEVERITY.get(tactic, "MEDIUM"),
                    artifact_id=artifact_id,
                    event_id=event_id,
                    incident_id=incident_id,
                    conversation_id=conversation_id,
                    turn_index=turn_index,
                    supporting_spans=[span],
                    requested_actions=list(TACTIC_DEFAULT_ACTIONS.get(tactic, [])),
                    detector_sources=["SEMANTIC"],
                    metadata={"semantic_score": round(max_pos_sim, 3)},
                )
                signals.append(signal)

        return signals
