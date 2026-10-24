"""Language Intelligence Service Package for ScamGraph AI (Prompt 17 / Phase 5C)."""

from services.language_intelligence.script_detector import detect_scripts
from services.language_intelligence.normalizer import IndicTextNormalizer, indic_normalizer
from services.language_intelligence.detector import LanguageIntelligenceDetector, language_detector
from services.language_intelligence.negation import ProtectiveNegationEngine, protective_negation_engine
from services.language_intelligence.transliteration import TransliterationAdapter, transliteration_adapter
from services.language_intelligence.translation import TranslationAdapter, translation_adapter
from services.language_intelligence.service import LanguageIntelligenceService, language_intelligence_service

__all__ = [
    "detect_scripts",
    "IndicTextNormalizer",
    "indic_normalizer",
    "LanguageIntelligenceDetector",
    "language_detector",
    "ProtectiveNegationEngine",
    "protective_negation_engine",
    "TransliterationAdapter",
    "transliteration_adapter",
    "TranslationAdapter",
    "translation_adapter",
    "LanguageIntelligenceService",
    "language_intelligence_service",
]
