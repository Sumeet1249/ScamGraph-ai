"""Payment Screenshot Intelligence & Loss Extraction (Prompt 18 / Phase 5D).

Rules:
1. Extract financial amounts, payee claims, VPAs, transaction reference numbers, and payment status claims.
2. Maintain verification_state: screenshot text "Successful" is user-provided evidence, NOT bank-verified settlement.
3. Feed Rescue Engine (LossEvent, RescueTimeline, EvidencePreservation, CasePackage).
4. Deduplicate multiple uploads of the same transaction receipt using reference ID or content hash.
"""

import hashlib
import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.multimodal import PaymentScreenshotExtraction
from packages.schemas.rescue import LossEvent, LossType
from services.language_intelligence.normalizer import indic_normalizer

logger = logging.getLogger("scamgraph.multimodal.payment")


# Common UPI transaction reference patterns (12-digit UTR or alphanumeric)
REF_PATTERNS = [
    re.compile(r"\b(?:utr|ref|rrn|txn\s*id|transaction\s*id)[:\s#]*([a-zA-Z0-9]{8,22})\b", re.IGNORECASE),
    re.compile(r"\b([0-9]{12})\b"),  # Standard 12-digit UPI reference
]

STATUS_PATTERNS = {
    "SUCCESSFUL": re.compile(r"\b(?:paid\s+successfully|payment\s+successful|successful|completed|sent)\b", re.IGNORECASE),
    "PENDING": re.compile(r"\b(?:pending|processing|in\s+progress)\b", re.IGNORECASE),
    "FAILED": re.compile(r"\b(?:failed|declined|cancelled)\b", re.IGNORECASE),
}


class PaymentScreenshotExtractor:
    """Extracts transaction attributes from payment receipts and wallet screenshots."""

    def __init__(self):
        self._processed_refs: Set[str] = set()

    def extract(
        self,
        text: str,
        artifact_hash: Optional[str] = None,
    ) -> Tuple[PaymentScreenshotExtraction, bool]:
        """Extracts financial parameters from screenshot text.
        
        Returns:
            Tuple of (PaymentScreenshotExtraction, is_duplicate)
        """
        if not text:
            return PaymentScreenshotExtraction(raw_text=""), False

        norm_text, _, _ = indic_normalizer.normalize(text)

        # 1. Extract Amount
        amount = None
        amt_match = re.search(r"₹\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)", norm_text)
        if amt_match:
            try:
                amount = float(amt_match.group(1).replace(",", ""))
            except ValueError:
                amount = None

        if amount is None:
            # Fallback pattern for numbers following 'paid' or 'amount'
            num_match = re.search(r"\b(?:paid|sent|amount|transfer)\s*(?:rs\.?|inr)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)\b", norm_text, re.IGNORECASE)
            if num_match:
                try:
                    amount = float(num_match.group(1).replace(",", ""))
                except ValueError:
                    amount = None

        # 2. Extract VPA / Payee
        vpa = None
        vpa_match = re.search(r"\b([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})\b", text)
        if vpa_match:
            vpa = vpa_match.group(1).lower()

        # 3. Extract Payee Name Claim
        name_claim = None
        to_match = re.search(r"\b(?:to|paid\s+to|sent\s+to)\s+([A-Za-z\s]{3,30})\b", text, re.IGNORECASE)
        if to_match:
            name_claim = to_match.group(1).strip()

        # 4. Extract Transaction / UTR Reference
        ref_id = None
        for pat in REF_PATTERNS:
            m = pat.search(text)
            if m:
                candidate = m.group(1)
                # Ensure candidate is not a phone number or the extracted amount
                if candidate != str(amount) and len(candidate) >= 8:
                    ref_id = candidate
                    break

        # 5. Extract Payment Status Claim
        status_claim = "UNKNOWN"
        for st_name, pat in STATUS_PATTERNS.items():
            if pat.search(text):
                status_claim = st_name
                break

        # 6. Duplicate check (Section 28)
        dedup_key = ref_id or (f"{amount}_{vpa}" if (amount and vpa) else artifact_hash)
        is_duplicate = False
        if dedup_key:
            if dedup_key in self._processed_refs:
                is_duplicate = True
            else:
                self._processed_refs.add(dedup_key)

        extraction = PaymentScreenshotExtraction(
            amount=amount,
            currency="INR",
            recipient_claim=name_claim,
            vpa=vpa,
            reference_id=ref_id,
            payment_status_claim=status_claim,
            confidence=0.92 if (amount and ref_id) else (0.75 if amount else 0.50),
            raw_text=text[:500],
        )

        return extraction, is_duplicate

    def to_rescue_loss_event(
        self,
        extraction: PaymentScreenshotExtraction,
        incident_id: str,
        source_artifact_id: str,
    ) -> Optional[LossEvent]:
        """Converts valid payment extraction into a Rescue LossEvent."""
        if not extraction.amount or extraction.amount <= 0:
            return None

        return LossEvent(
            loss_id=f"loss_multi_{extraction.reference_id or source_artifact_id[:8]}",
            incident_id=incident_id,
            loss_type=LossType.UPI_PAYMENT if extraction.vpa else LossType.MONEY_TRANSFER,
            amount=extraction.amount,
            currency=extraction.currency,
            recipient_entity_id=extraction.vpa,
            recipient_name_claim=extraction.recipient_claim,
            payment_reference=extraction.reference_id,
            payment_method="UPI" if extraction.vpa else "BANK_TRANSFER",
            user_verified=False,  # Unverified screenshot text
            notes=f"Extracted from payment receipt artifact {source_artifact_id}. Status: {extraction.payment_status_claim}",
        )


payment_screenshot_extractor = PaymentScreenshotExtractor()
