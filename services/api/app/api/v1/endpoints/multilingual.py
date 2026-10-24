"""FastAPI Endpoints for India Multilingual Intelligence V2 (Prompt 17 / Phase 5C)."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from packages.schemas.multilingual import (
    BehavioralFeatureSet,
    LanguageProfile,
    MultilingualTextRepresentation,
    NegationSignal,
    ScriptType,
)
from services.intervention_engine.catalog import MESSAGE_CATALOG
from services.language_intelligence.detector import language_detector
from services.language_intelligence.negation import protective_negation_engine
from services.language_intelligence.normalizer import indic_normalizer
from services.language_intelligence.script_detector import detect_scripts
from services.language_intelligence.service import language_intelligence_service

router = APIRouter()


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., description="Raw message text to analyze")


class NormalizationResponse(BaseModel):
    original_text: str
    normalized_text: str
    steps_applied: List[str]
    urgency_intensity_score: float


@router.post("/detect", response_model=LanguageProfile)
def detect_language_profile(req: TextAnalysisRequest):
    """Detects scripts, language probabilities, code-mixing score, and support tier."""
    return language_detector.detect(req.text)


@router.post("/normalize", response_model=NormalizationResponse)
def normalize_indic_text(req: TextAnalysisRequest):
    """Normalizes Indic/code-mixed text preserving security tokens (UPI, URLs, phones, amounts)."""
    norm, steps, score = indic_normalizer.normalize(req.text)
    return NormalizationResponse(
        original_text=req.text,
        normalized_text=norm,
        steps_applied=steps,
        urgency_intensity_score=score,
    )


@router.post("/represent", response_model=MultilingualTextRepresentation)
def generate_text_representation(req: TextAnalysisRequest):
    """Produces unified MultilingualTextRepresentation (original, normalized, transliterated, translated)."""
    return language_intelligence_service.analyze_text(req.text)


@router.post("/negation-check", response_model=NegationSignal)
def check_protective_negation(req: TextAnalysisRequest):
    """Evaluates whether text contains protective safety negation (e.g. 'Never share OTP')."""
    return protective_negation_engine.evaluate(req.text)


@router.post("/behavioral-features", response_model=BehavioralFeatureSet)
def extract_behavioral_features(req: TextAnalysisRequest):
    """Extracts language-independent behavioral indicators directly from normalized text."""
    return language_intelligence_service.extract_behavioral_features(req.text)


@router.get("/locales")
def list_locales():
    """Lists supported user interface and safety guidance locales."""
    return {
        "supported_locales": [
            {"code": "en", "name": "English", "tier": "PRODUCTION_VALIDATED"},
            {"code": "hi", "name": "हिन्दी (Hindi)", "tier": "PRODUCTION_VALIDATED"},
            {"code": "hinglish", "name": "Hinglish (Roman Hindi)", "tier": "PRODUCTION_VALIDATED"},
            {"code": "bn", "name": "বাংলা (Bengali)", "tier": "BETA"},
        ],
        "message_catalog_keys": list(MESSAGE_CATALOG.keys()),
    }
