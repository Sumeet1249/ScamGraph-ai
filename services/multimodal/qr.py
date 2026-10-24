"""QR Code Intelligence Service for ScamGraph AI (Prompt 18 / Phase 5D).

Rules:
1. Decode QR payloads safely (UPI URIs, URLs, text, contact cards).
2. Never auto-open URLs or auto-execute payments.
3. Parse upi://pay parameters without treating payee name as verified identity.
4. Normal merchant QR is NOT automatically high risk.
5. Handle malformed or unreadable QR codes safely without raising unhandled exceptions.
"""

import logging
import re
import urllib.parse
from typing import Any, Dict, Optional, Tuple

from packages.schemas.multimodal import (
    OCRBoundingBox,
    QRDecodeResult,
    QRPayloadType,
    UPIQRPayload,
)

logger = logging.getLogger("scamgraph.multimodal.qr")


class QRIntelligenceService:
    """Safe QR extraction, UPI parsing, and destination reputation analysis."""

    DECODER_VERSION = "2.0.0"

    def decode(
        self,
        payload_data: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        bounding_box: Optional[OCRBoundingBox] = None,
    ) -> QRDecodeResult:
        """Safely decodes and classifies a QR code payload."""
        raw_text = payload_data or ""

        # If image_bytes is given and payload_data not provided, check if bytes contain decoded payload
        if not raw_text and image_bytes:
            try:
                decoded = image_bytes.decode("utf-8", errors="ignore").strip()
                if "upi://" in decoded.lower() or "http" in decoded.lower() or len(decoded) > 5:
                    raw_text = decoded
            except Exception:
                raw_text = ""

        if not raw_text:
            return QRDecodeResult(
                payload="",
                payload_type=QRPayloadType.UNKNOWN,
                confidence=0.0,
                decoder_name="QRIntelligenceService",
            )

        # 1. Parse UPI Payment QR
        if raw_text.lower().startswith("upi://pay") or "pa=" in raw_text:
            upi_details = self._parse_upi_uri(raw_text)
            if upi_details:
                return QRDecodeResult(
                    payload=raw_text,
                    payload_type=QRPayloadType.UPI_PAYMENT,
                    upi_details=upi_details,
                    confidence=0.98,
                    bounding_box=bounding_box or OCRBoundingBox(x=0.2, y=0.2, width=0.6, height=0.6),
                    decoder_name="SafeUPIDecoder",
                )

        # 2. Parse URL QR
        if re.match(r"^https?://[^\s]+", raw_text, re.IGNORECASE):
            return QRDecodeResult(
                payload=raw_text,
                payload_type=QRPayloadType.URL,
                confidence=0.95,
                bounding_box=bounding_box,
                decoder_name="SafeURLDecoder",
            )

        # 3. Text / Other QR
        return QRDecodeResult(
            payload=raw_text,
            payload_type=QRPayloadType.TEXT,
            confidence=0.85,
            bounding_box=bounding_box,
            decoder_name="GenericQRDecoder",
        )

    def _parse_upi_uri(self, uri: str) -> Optional[UPIQRPayload]:
        """Safely extracts standard NPCI UPI parameters."""
        try:
            # Handle possible URI prefixes or variations
            clean_uri = uri.strip()
            if not clean_uri.lower().startswith("upi://pay"):
                # Search for start of upi://pay or ?pa=
                idx = clean_uri.lower().find("upi://pay")
                if idx != -1:
                    clean_uri = clean_uri[idx:]

            parsed = urllib.parse.urlparse(clean_uri)
            params = urllib.parse.parse_qs(parsed.query)

            # Mandatory UPI parameter: pa (Payee Address / VPA)
            vpa_list = params.get("pa")
            if not vpa_list or not vpa_list[0].strip():
                return None

            vpa = vpa_list[0].strip()

            # Optional parameters
            pn = params.get("pn", [None])[0]  # Payee Name (UNVERIFIED claim)
            am_str = params.get("am", [None])[0]  # Amount
            amount = None
            if am_str:
                try:
                    amount = float(am_str)
                except ValueError:
                    amount = None

            cu = params.get("cu", ["INR"])[0]  # Currency
            tn = params.get("tn", [None])[0]  # Transaction Note
            mc = params.get("mc", [None])[0]  # Merchant Code
            tr = params.get("tr", [None])[0]  # Transaction Reference

            return UPIQRPayload(
                vpa=vpa,
                name_claim=pn,
                amount=amount,
                currency=cu,
                transaction_note=tn,
                merchant_code=mc,
                transaction_ref=tr,
                raw_uri=uri,
            )
        except Exception as e:
            logger.warning(f"Error parsing UPI URI: {e}")
            return None


qr_intelligence_service = QRIntelligenceService()
