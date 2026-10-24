"""FastAPI Router for Multimodal Intelligence V2 (Prompt 18 / Phase 5D).

Endpoints:
- POST /screenshot: Ingest and analyze chat or document screenshots.
- POST /qr: Safely decode QR images and parse UPI payment URIs.
- POST /payment-receipt: Extract transaction attributes and create Rescue LossEvents.
- POST /audio: Transcribe audio calls, generate tactic timelines, and check negation.
- POST /fuse: Fuse multimodal evidence while preventing double-counting.
- POST /cross-modal-journey: Reconstruct multi-channel scam journeys.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from packages.schemas.multimodal import (
    DerivedObservation,
    EvidenceFusionResult,
    OCRResult,
    PaymentScreenshotExtraction,
    QRDecodeResult,
    SyntheticMediaSignal,
    TranscriptArtifact,
)
from packages.schemas.rescue import LossEvent
from services.multimodal.service import multimodal_service

router = APIRouter(prefix="/multimodal", tags=["Multimodal Intelligence V2"])


class ScreenshotAnalysisRequest(BaseModel):
    incident_id: str
    artifact_id: str = "art_scr_01"
    raw_text_hint: Optional[str] = None
    confidence_override: Optional[float] = None


class ScreenshotAnalysisResponse(BaseModel):
    ocr_result: OCRResult
    observations: List[DerivedObservation]


class QRAnalysisRequest(BaseModel):
    incident_id: str
    artifact_id: str = "art_qr_01"
    payload_data: Optional[str] = None


class QRAnalysisResponse(BaseModel):
    qr_result: QRDecodeResult
    observations: List[DerivedObservation]


class PaymentReceiptRequest(BaseModel):
    incident_id: str
    artifact_id: str = "art_pay_01"
    text: str


class PaymentReceiptResponse(BaseModel):
    extraction: PaymentScreenshotExtraction
    is_duplicate: bool
    loss_event: Optional[LossEvent] = None
    observations: List[DerivedObservation]


class AudioAnalysisRequest(BaseModel):
    incident_id: str
    artifact_id: str = "art_aud_01"
    raw_transcript_hint: Optional[str] = None
    confidence_override: Optional[float] = None


class AudioAnalysisResponse(BaseModel):
    transcript: TranscriptArtifact
    behavioral_data: Dict[str, Any]
    synthetic_signal: SyntheticMediaSignal
    observations: List[DerivedObservation]


class FusionRequest(BaseModel):
    incident_id: str
    observations: List[DerivedObservation]


class CrossModalJourneyRequest(BaseModel):
    incident_id: str
    events: List[Dict[str, Any]]


@router.post("/screenshot", response_model=ScreenshotAnalysisResponse)
async def analyze_screenshot(req: ScreenshotAnalysisRequest):
    """Processes a screenshot into OCR text, Indic normalization, entities, and observations."""
    ocr_res, obs = multimodal_service.process_screenshot(
        incident_id=req.incident_id,
        artifact_id=req.artifact_id,
        raw_text_hint=req.raw_text_hint,
        confidence_override=req.confidence_override,
    )
    return ScreenshotAnalysisResponse(ocr_result=ocr_res, observations=obs)


@router.post("/qr", response_model=QRAnalysisResponse)
async def analyze_qr(req: QRAnalysisRequest):
    """Decodes QR code and safely extracts UPI payment parameters without triggering payment."""
    qr_res, obs = multimodal_service.process_qr(
        incident_id=req.incident_id,
        artifact_id=req.artifact_id,
        payload_data=req.payload_data,
    )
    return QRAnalysisResponse(qr_result=qr_res, observations=obs)


@router.post("/payment-receipt", response_model=PaymentReceiptResponse)
async def analyze_payment_receipt(req: PaymentReceiptRequest):
    """Extracts payment evidence, checks for duplicates, and creates Rescue LossEvents."""
    ext, is_dup, loss_ev, obs = multimodal_service.process_payment_screenshot(
        incident_id=req.incident_id,
        artifact_id=req.artifact_id,
        text=req.text,
    )
    return PaymentReceiptResponse(
        extraction=ext,
        is_duplicate=is_dup,
        loss_event=loss_ev,
        observations=obs,
    )


@router.post("/audio", response_model=AudioAnalysisResponse)
async def analyze_audio(req: AudioAnalysisRequest):
    """Transcribes audio, extracts call tactic timeline, and provides safe synthetic media guidance."""
    trans, beh, synth, obs = multimodal_service.process_audio(
        incident_id=req.incident_id,
        artifact_id=req.artifact_id,
        raw_transcript_hint=req.raw_transcript_hint,
        confidence_override=req.confidence_override,
    )
    return AudioAnalysisResponse(
        transcript=trans,
        behavioral_data=beh,
        synthetic_signal=synth,
        observations=obs,
    )


@router.post("/fuse", response_model=EvidenceFusionResult)
async def fuse_multimodal_evidence(req: FusionRequest):
    """Fuses observations while preventing double-counting of derived artifacts."""
    return multimodal_service.fuse_evidence(
        incident_id=req.incident_id,
        observations=req.observations,
    )


@router.post("/cross-modal-journey")
async def reconstruct_cross_modal_journey(req: CrossModalJourneyRequest):
    """Reconstructs a single canonical ScamJourney across SMS, calls, screenshots, and payments."""
    journey = multimodal_service.reconstruct_cross_modal_journey(
        incident_id=req.incident_id,
        events_spec=req.events,
    )
    return journey.model_dump()
