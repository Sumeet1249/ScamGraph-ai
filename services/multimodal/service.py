"""Multimodal Intelligence Central Orchestration Service (Prompt 18 / Phase 5D).

Coordinates:
- Ingestion of screenshots, QR codes, payment receipts, and audio recordings into canonical Artifacts.
- Creation of DerivedObservations with immutable lineage to root artifacts.
- Execution of OCR, QR decoding, Speech-to-Text, Indic normalization, and entity extraction.
- Cross-modal Journey reconstruction with temporal confidence.
- Double-count preventing Evidence Fusion.
- Enrichment of 8-Dimensional ScamDNA V3 behavioral fingerprints.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from packages.schemas.artifact import Artifact, ArtifactType
from packages.schemas.dna import ScamDNA
from packages.schemas.journey import JourneyEvent, JourneyStage, ScamJourney
from packages.schemas.multimodal import (
    DerivedObservation,
    EvidenceFusionResult,
    MultimodalModality,
    ObservationType,
    OCRResult,
    PaymentScreenshotExtraction,
    QRDecodeResult,
    QRPayloadType,
    SyntheticMediaSignal,
    TranscriptArtifact,
)
from packages.schemas.rescue import LossEvent
from services.dna_engine.builder import ScamDNABuilder
from services.journey_engine.service import JourneyEngineService
from services.language_intelligence.detector import language_detector
from services.language_intelligence.normalizer import indic_normalizer
from services.language_intelligence.service import language_intelligence_service
from services.multimodal.audio import audio_intelligence_service
from services.multimodal.fusion import evidence_fusion_engine
from services.multimodal.ocr import ocr_engine
from services.multimodal.payment import payment_screenshot_extractor
from services.multimodal.qr import qr_intelligence_service
from services.multimodal.security import file_security_validator

logger = logging.getLogger("scamgraph.multimodal.service")


class MultimodalIntelligenceService:
    """Enterprise multimodal intelligence coordinator for ScamGraph AI V2."""

    SERVICE_VERSION = "2.0.0"

    def __init__(self):
        self.journey_service = JourneyEngineService()

    # -------------------------------------------------------------------------
    # 1. Screenshot Ingestion & Processing
    # -------------------------------------------------------------------------
    def process_screenshot(
        self,
        incident_id: str,
        artifact_id: str,
        raw_text_hint: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        confidence_override: Optional[float] = None,
    ) -> Tuple[OCRResult, List[DerivedObservation]]:
        """Processes a chat or document screenshot into OCR and derived observations."""
        ocr_res = ocr_engine.extract_text(
            image_bytes=image_bytes,
            raw_text_hint=raw_text_hint,
            confidence_override=confidence_override,
        )

        observations: List[DerivedObservation] = []
        if not ocr_res.full_text:
            return ocr_res, observations

        # Root OCR Text Observation
        root_obs = DerivedObservation(
            source_artifact_id=artifact_id,
            incident_id=incident_id,
            modality=MultimodalModality.SCREENSHOT,
            observation_type=ObservationType.TEXT_SPAN,
            raw_value=ocr_res.full_text,
            normalized_value=indic_normalizer.normalize(ocr_res.full_text)[0],
            confidence=ocr_res.overall_confidence,
            extractor_name="LocalOCR",
        )
        observations.append(root_obs)

        # Extract entities from OCR text (UPI VPAs, URLs, Phone numbers)
        vpas = re.findall(r"\b([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})\b", ocr_res.full_text)
        for vpa in set(vpas):
            observations.append(
                DerivedObservation(
                    source_artifact_id=artifact_id,
                    incident_id=incident_id,
                    modality=MultimodalModality.SCREENSHOT,
                    observation_type=ObservationType.UPI_VPA,
                    raw_value=vpa,
                    normalized_value=vpa.lower(),
                    confidence=ocr_res.overall_confidence,
                    extractor_name="EntityExtractor",
                    lineage_parent_ids=[root_obs.observation_id],  # Derived from root OCR
                )
            )

        urls = re.findall(r"https?://[^\s]+", ocr_res.full_text)
        for u in set(urls):
            observations.append(
                DerivedObservation(
                    source_artifact_id=artifact_id,
                    incident_id=incident_id,
                    modality=MultimodalModality.SCREENSHOT,
                    observation_type=ObservationType.URL,
                    raw_value=u,
                    normalized_value=u.lower(),
                    confidence=ocr_res.overall_confidence,
                    extractor_name="URLExtractor",
                    lineage_parent_ids=[root_obs.observation_id],
                )
            )

        # Extract behavioral tactics & requested actions using Language Intelligence
        feat = language_intelligence_service.extract_behavioral_features(ocr_res.full_text)
        for tac in feat.tactics:
            observations.append(
                DerivedObservation(
                    source_artifact_id=artifact_id,
                    incident_id=incident_id,
                    modality=MultimodalModality.SCREENSHOT,
                    observation_type=ObservationType.TACTIC_EVIDENCE,
                    raw_value=tac.value,
                    normalized_value=tac.value,
                    confidence=ocr_res.overall_confidence,
                    extractor_name="TacticDetector",
                    lineage_parent_ids=[root_obs.observation_id],
                )
            )

        return ocr_res, observations

    # -------------------------------------------------------------------------
    # 2. QR Code Ingestion & Safe Parsing
    # -------------------------------------------------------------------------
    def process_qr(
        self,
        incident_id: str,
        artifact_id: str,
        payload_data: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> Tuple[QRDecodeResult, List[DerivedObservation]]:
        """Processes a QR code image or payload into structured observations."""
        qr_res = qr_intelligence_service.decode(payload_data=payload_data, image_bytes=image_bytes)
        observations: List[DerivedObservation] = []

        if not qr_res.payload or qr_res.payload_type == QRPayloadType.UNKNOWN:
            return qr_res, observations

        # Derived QR Observation
        qr_obs = DerivedObservation(
            source_artifact_id=artifact_id,
            incident_id=incident_id,
            modality=MultimodalModality.QR_IMAGE,
            observation_type=ObservationType.UPI_VPA if qr_res.payload_type == QRPayloadType.UPI_PAYMENT else ObservationType.URL,
            raw_value=qr_res.payload,
            normalized_value=qr_res.upi_details.vpa if qr_res.upi_details else qr_res.payload,
            confidence=qr_res.confidence,
            extractor_name="SafeQRDecoder",
        )
        observations.append(qr_obs)

        # If UPI QR, also extract amount if specified
        if qr_res.upi_details and qr_res.upi_details.amount:
            observations.append(
                DerivedObservation(
                    source_artifact_id=artifact_id,
                    incident_id=incident_id,
                    modality=MultimodalModality.QR_IMAGE,
                    observation_type=ObservationType.PAYMENT_AMOUNT,
                    raw_value=str(qr_res.upi_details.amount),
                    normalized_value=f"₹{int(qr_res.upi_details.amount)}",
                    confidence=qr_res.confidence,
                    extractor_name="SafeQRDecoder",
                    lineage_parent_ids=[qr_obs.observation_id],
                )
            )

        return qr_res, observations

    # -------------------------------------------------------------------------
    # 3. Payment Screenshot Ingestion
    # -------------------------------------------------------------------------
    def process_payment_screenshot(
        self,
        incident_id: str,
        artifact_id: str,
        text: str,
    ) -> Tuple[PaymentScreenshotExtraction, bool, Optional[LossEvent], List[DerivedObservation]]:
        """Extracts payment evidence, checks for duplicates, and creates Rescue LossEvents."""
        extraction, is_dup = payment_screenshot_extractor.extract(text, artifact_hash=artifact_id)
        loss_event = None
        observations: List[DerivedObservation] = []

        if extraction.amount:
            loss_event = payment_screenshot_extractor.to_rescue_loss_event(
                extraction, incident_id=incident_id, source_artifact_id=artifact_id
            )
            # Payment Amount Observation
            obs_amt = DerivedObservation(
                source_artifact_id=artifact_id,
                incident_id=incident_id,
                modality=MultimodalModality.PAYMENT_SCREENSHOT,
                observation_type=ObservationType.PAYMENT_AMOUNT,
                raw_value=str(extraction.amount),
                normalized_value=f"₹{int(extraction.amount)}",
                confidence=extraction.confidence,
                extractor_name="PaymentExtractor",
            )
            observations.append(obs_amt)

            if extraction.vpa:
                observations.append(
                    DerivedObservation(
                        source_artifact_id=artifact_id,
                        incident_id=incident_id,
                        modality=MultimodalModality.PAYMENT_SCREENSHOT,
                        observation_type=ObservationType.UPI_VPA,
                        raw_value=extraction.vpa,
                        normalized_value=extraction.vpa.lower(),
                        confidence=extraction.confidence,
                        extractor_name="PaymentExtractor",
                        lineage_parent_ids=[obs_amt.observation_id],
                    )
                )

            if extraction.reference_id:
                observations.append(
                    DerivedObservation(
                        source_artifact_id=artifact_id,
                        incident_id=incident_id,
                        modality=MultimodalModality.PAYMENT_SCREENSHOT,
                        observation_type=ObservationType.TRANSACTION_REFERENCE,
                        raw_value=extraction.reference_id,
                        normalized_value=extraction.reference_id,
                        confidence=extraction.confidence,
                        extractor_name="PaymentExtractor",
                        lineage_parent_ids=[obs_amt.observation_id],
                    )
                )

        return extraction, is_dup, loss_event, observations

    # -------------------------------------------------------------------------
    # 4. Voice / Audio Call Ingestion
    # -------------------------------------------------------------------------
    def process_audio(
        self,
        incident_id: str,
        artifact_id: str,
        raw_transcript_hint: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        confidence_override: Optional[float] = None,
    ) -> Tuple[TranscriptArtifact, Dict[str, Any], SyntheticMediaSignal, List[DerivedObservation]]:
        """Processes voice note or phone call recording into transcript and tactical observations."""
        transcript, behavioral_data, synth_signal = audio_intelligence_service.analyze_audio(
            audio_bytes=audio_bytes,
            raw_transcript_hint=raw_transcript_hint,
            confidence_override=confidence_override,
        )

        observations: List[DerivedObservation] = []
        if not transcript.full_transcript:
            return transcript, behavioral_data, synth_signal, observations

        # Root Transcript Observation
        root_audio = DerivedObservation(
            source_artifact_id=artifact_id,
            incident_id=incident_id,
            modality=MultimodalModality.AUDIO,
            observation_type=ObservationType.TEXT_SPAN,
            raw_value=transcript.full_transcript,
            normalized_value=indic_normalizer.normalize(transcript.full_transcript)[0],
            confidence=transcript.overall_confidence,
            extractor_name="SpeechToText",
        )
        observations.append(root_audio)

        # Tactics observed in call
        for tac_str in behavioral_data.get("tactics", []):
            observations.append(
                DerivedObservation(
                    source_artifact_id=artifact_id,
                    incident_id=incident_id,
                    modality=MultimodalModality.AUDIO,
                    observation_type=ObservationType.TACTIC_EVIDENCE,
                    raw_value=tac_str,
                    normalized_value=tac_str,
                    confidence=transcript.overall_confidence,
                    extractor_name="CallTacticDetector",
                    lineage_parent_ids=[root_audio.observation_id],
                )
            )

        return transcript, behavioral_data, synth_signal, observations

    # -------------------------------------------------------------------------
    # 5. Cross-Modal Journey Reconstruction (Section 44)
    # -------------------------------------------------------------------------
    def reconstruct_cross_modal_journey(
        self,
        incident_id: str,
        events_spec: List[Dict[str, Any]],
    ) -> ScamJourney:
        """Combines SMS, call recordings, chat screenshots, QR, and payments into one ScamJourney."""
        journey_events: List[JourneyEvent] = []

        for i, spec in enumerate(events_spec):
            channel = spec.get("channel", "UNKNOWN")
            modality = spec.get("modality", "TEXT")
            text = spec.get("text", "")
            tactics = spec.get("tactics", [])
            actions = spec.get("requested_actions", [])
            vpa = spec.get("vpa")

            # Extract tactics and actions automatically from text if not explicitly provided
            if text and not tactics:
                feat = language_intelligence_service.extract_behavioral_features(text)
                tactics = [t.value for t in feat.tactics]
                actions = [a.value for a in feat.requested_actions]

            ev = JourneyEvent(
                event_id=f"jrev_multi_{i}",
                timestamp=spec.get("timestamp") or datetime.now(timezone.utc),
                sequence_number=i,
                event_type=spec.get("event_type", "MESSAGE_RECEIVED"),
                channel=channel,
                speaker_role=spec.get("speaker_role", "SCAMMER"),
                entities=[vpa] if vpa else [],
                tactics=tactics,
                requested_actions=actions,
                timestamp_confidence=spec.get("timestamp_confidence", "EXACT"),
                metadata={"modality": modality, "text": text[:200]},
            )
            journey_events.append(ev)

        journey = self.journey_service.create_journey(incident_id=incident_id, events=journey_events)
        return journey

    # -------------------------------------------------------------------------
    # 6. Evidence Fusion
    # -------------------------------------------------------------------------
    def fuse_evidence(
        self,
        incident_id: str,
        observations: List[DerivedObservation],
    ) -> EvidenceFusionResult:
        """Fuses all derived observations for an incident and prevents double-counting."""
        return evidence_fusion_engine.fuse(incident_id=incident_id, observations=observations)

    # -------------------------------------------------------------------------
    # 7. Multimodal ScamDNA Enrichment (Section 51-53)
    # -------------------------------------------------------------------------
    def build_multimodal_dna(
        self,
        incident_id: str,
        journey: Optional[ScamJourney] = None,
        fusion_result: Optional[EvidenceFusionResult] = None,
        summary_text: Optional[str] = None,
    ) -> ScamDNA:
        """Builds canonical ScamDNA V3 enriched by multimodal behavioral observations."""
        tactics_set = set()
        actions_set = set()
        entities = []

        if fusion_result:
            for obs in fusion_result.observations:
                if obs.observation_type == ObservationType.TACTIC_EVIDENCE:
                    tactics_set.add(obs.normalized_value)
                elif obs.observation_type == ObservationType.REQUESTED_ACTION:
                    actions_set.add(obs.normalized_value)
                elif obs.observation_type == ObservationType.UPI_VPA:
                    entities.append({"entity_type": "PAYMENT_VPA", "canonical_value": obs.normalized_value})

        dna = ScamDNABuilder.build(
            incident_id=incident_id,
            journey=journey,
            tactics=list(tactics_set) if tactics_set else ["TRUST_BUILDING", "PAYMENT_PRESSURE"],
            entities=entities,
            requested_actions=list(actions_set) if actions_set else ["SEND_PAYMENT"],
            message_text=summary_text or "Multimodal incident combining chat, QR, and payment evidence.",
        )
        return dna


multimodal_service = MultimodalIntelligenceService()
