"""Message Intelligence Service for ScamGraph AI.

Extracts semantic classification signals, urgency indicators, entity impersonation,
and produces typed EvidenceSignal instances conforming to ScamGraph's multi-signal architecture.

Strict Rule:
Output is structured evidence, NEVER an automated final fraud verdict (Constitutional Rule 10).
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ml.embeddings.encoder import SemanticEncoder, semantic_encoder
from ml.message.baseline import BaselineMessageModel
from packages.schemas.signals import (
    EvidenceSignal,
    ProvenanceRecord,
    SignalDimension,
    SignalSeverity,
)

logger = logging.getLogger(__name__)

# Urgent coercion indicators (English and Hinglish/Hindi Romanized)
URGENCY_PATTERNS = [
    r"\b(urgent|urgently|immediately|immediate|hurry|action required|last chance)\b",
    r"\b(within \d+ (hours?|mins?|minutes?)|24 hours?|today only|expir(es?|ing|ed))\b",
    r"\b(blocked|suspended|deactivated|disconnected|frozen|hold)\b",
    r"\b(turant|jaldi|aaj hi|abhy|rok diya jayega|band kar diya)\b",
]

# Impersonation target entity patterns
IMPERSONATION_ENTITIES = {
    "SBI": r"\b(sbi|state bank|yono)\b",
    "HDFC": r"\b(hdfc|hdfcbank)\b",
    "ICICI": r"\b(icici|imobile)\b",
    "PNB": r"\b(pnb|punjab national)\b",
    "DISCOM_ELECTRICITY": r"\b(electricity|discom|power corp|bijli vibhag|electricity officer)\b",
    "TRAI_TELECOM": r"\b(trai|telecom|airtel|jio|vi-india|vodafone)\b",
    "GOVT_TAX_POLICE": r"\b(income tax|cert-in|cyber crime|police|court notice|cbi|ed notice)\b",
    "COURIER": r"\b(fedex|dhl|india post|courier|customs|parcel)\b",
}

# Credential solicitation patterns
CREDENTIAL_PATTERNS = [
    r"\b(otp|one time password|pin|cvv|password|passcode)\b",
    r"\b(share otp|enter otp|verify otp|bhejo|otp batao)\b",
    r"\b(update kyc|pan card|aadhaar card|link pan|kyc pending)\b",
]

# Lures and lottery claims
LURE_PATTERNS = [
    r"\b(won|winner|lottery|prize|lucky draw|cashback|free gift|gift card)\b",
    r"\b(pre-approved loan|instant loan|zero interest|disbursed without cibil)\b",
    r"\b(work from home|daily salary|part-time job|earn \d+ daily|youtube like)\b",
]

# Legitimate banking notifications (counter-evidence)
BENIGN_TRANSACTION_PATTERNS = [
    r"\b(credited to your a/c|debited from your a/c|txn id|ref no|available bal)\b",
    r"\b(statement generated|salary credited|interest credited)\b",
]


@dataclass
class MessageIntelligenceAnalysis:
    """Consolidated message analysis result."""

    raw_text: str
    classification_signal: Dict[str, Any]
    confidence: float
    semantic_embedding: List[float] = field(default_factory=list)
    extracted_signals: Dict[str, Any] = field(default_factory=dict)
    evidence_signals: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MessageIntelligenceService:
    """Unified service for message classification, signal extraction, and evidence generation."""

    def __init__(
        self,
        baseline_model: Optional[BaselineMessageModel] = None,
        encoder: Optional[SemanticEncoder] = None,
    ):
        # Load or initialize baseline model
        if baseline_model is not None:
            self.model = baseline_model
        else:
            try:
                self.model = BaselineMessageModel.load()
            except Exception as e:
                logger.warning(f"Could not load saved baseline model ({e}), initializing fresh model.")
                self.model = BaselineMessageModel()

        # Semantic encoder for dense embeddings
        self.encoder = encoder or semantic_encoder

    def extract_linguistic_signals(self, text: str) -> Dict[str, Any]:
        """Detect behavioral manipulation markers in text."""
        lower = text.lower()

        urgency_matches = [p for p in URGENCY_PATTERNS if re.search(p, lower)]
        has_urgency = len(urgency_matches) > 0

        impersonated_entities = [
            entity for entity, pattern in IMPERSONATION_ENTITIES.items() if re.search(pattern, lower)
        ]

        credential_matches = [p for p in CREDENTIAL_PATTERNS if re.search(p, lower)]
        has_credential_solicitation = len(credential_matches) > 0

        lure_matches = [p for p in LURE_PATTERNS if re.search(p, lower)]
        has_lure = len(lure_matches) > 0

        benign_matches = [p for p in BENIGN_TRANSACTION_PATTERNS if re.search(p, lower)]
        is_routine_txn = len(benign_matches) > 0 and not has_credential_solicitation

        return {
            "has_urgency": has_urgency,
            "urgency_indicators": urgency_matches,
            "has_impersonation": len(impersonated_entities) > 0,
            "impersonated_entities": impersonated_entities,
            "solicits_credentials": has_credential_solicitation,
            "has_lure": has_lure,
            "is_routine_transaction": is_routine_txn,
        }

    def analyze_message(
        self,
        text: str,
        incident_id: str,
        event_id: Optional[str] = None,
        include_embedding: bool = True,
    ) -> MessageIntelligenceAnalysis:
        """Analyze message text and generate EvidenceSignal instances for the incident."""
        text_clean = text.strip()

        # 1. Classification prediction
        if self.model.is_trained:
            pred = self.model.predict_single(text_clean)
        else:
            # Fallback heuristic if untrained
            pred = {
                "label": "unknown",
                "is_scam": False,
                "scam_probability": 0.5,
                "ham_probability": 0.5,
                "confidence": 0.0,
            }

        scam_prob = pred["scam_probability"]
        confidence = pred["confidence"]

        # 2. Extract linguistic cues
        signals = self.extract_linguistic_signals(text_clean)

        # 3. Dense semantic embedding
        embedding: List[float] = []
        if include_embedding and self.encoder is not None:
            try:
                emb = self.encoder.encode([text_clean])[0]
                embedding = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            except Exception as e:
                logger.warning(f"Semantic embedding generation failed: {e}")

        # 4. Synthesize EvidenceSignals
        evidence_signals: List[EvidenceSignal] = []
        provenance = ProvenanceRecord(
            source_service="services/investigation/message_ai",
            detector_name="BaselineMessageModel (TF-IDF + Logistic Regression)",
            target_artifact=text_clean[:120],
            source_category="ML_MODEL",
            provider="ScamGraph Team",
            model_id="scamgraph-message-baseline",
            model_version="v1.0.0",
            raw_evidence={
                "scam_probability": scam_prob,
                "confidence": confidence,
                "extracted_signals": signals,
            },
        )

        # High/Medium scam model match (suppressed if cleanly verified routine transaction)
        if scam_prob >= 0.70 and not (signals["is_routine_transaction"] and not signals["has_urgency"]):
            evidence_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=event_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="SCAM_MESSAGE_SEMANTIC_MATCH",
                    severity=SignalSeverity.HIGH if scam_prob >= 0.85 else SignalSeverity.MEDIUM,
                    confidence=min(1.0, scam_prob),
                    weight=1.2,
                    is_counter_evidence=False,
                    description=f"Message classified as scam with {round(scam_prob * 100, 1)}% probability.",
                    provenance=provenance,
                )
            )

        # Urgency pressure signal
        if signals["has_urgency"]:
            evidence_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=event_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="URGENCY_PRESSURE_DETECTED",
                    severity=SignalSeverity.MEDIUM,
                    confidence=0.88,
                    weight=1.1,
                    is_counter_evidence=False,
                    description="Coercive urgency language detected (account block or tight deadline).",
                    provenance=provenance,
                )
            )

        # Official entity impersonation
        if signals["has_impersonation"]:
            entities_str = ", ".join(signals["impersonated_entities"])
            evidence_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=event_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                    severity=SignalSeverity.HIGH,
                    confidence=0.92,
                    weight=1.3,
                    is_counter_evidence=False,
                    description=f"Claims representation of recognized institution: {entities_str}.",
                    provenance=provenance,
                )
            )

        # Credential or OTP solicitation
        if signals["solicits_credentials"]:
            evidence_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=event_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="SENSITIVE_CREDENTIAL_SOLICITATION",
                    severity=SignalSeverity.CRITICAL if scam_prob >= 0.6 else SignalSeverity.HIGH,
                    confidence=0.95,
                    weight=1.4,
                    is_counter_evidence=False,
                    description="Solicitation of OTP, PAN, PIN, or confidential credentials detected.",
                    provenance=provenance,
                )
            )

        # Counter-evidence: routine transaction without suspicious indicators
        if signals["is_routine_transaction"] and not signals["solicits_credentials"] and not signals["has_urgency"]:
            evidence_signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    event_id=event_id,
                    dimension=SignalDimension.SEMANTIC,
                    signal_type="LEGITIMATE_TRANSACTION_NOTIFICATION",
                    severity=SignalSeverity.INFO,
                    confidence=0.88,
                    weight=1.0,
                    is_counter_evidence=True,
                    description="Message exhibits characteristics of standard transactional confirmation.",
                    provenance=provenance,
                )
            )

        return MessageIntelligenceAnalysis(
            raw_text=text_clean,
            classification_signal={
                "label": pred.get("label", "unknown"),
                "is_scam": pred.get("is_scam", False),
                "scam_probability": scam_prob,
                "confidence": confidence,
            },
            confidence=confidence,
            semantic_embedding=embedding,
            extracted_signals=signals,
            evidence_signals=[s.model_dump() for s in evidence_signals],
        )
