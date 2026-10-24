"""Unit tests for Pattern Engine (Semantic NLP & Multi-Signal Fusion)."""

import unittest
from services.pattern_engine.semantic.nlp import SemanticSignalExtractor
from services.pattern_engine.matcher.fusion import EvidenceFusionEngine
from packages.schemas import (
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    RiskLevel,
    EvidenceConfidence,
    InterventionAction,
)


class TestPatternEngine(unittest.TestCase):
    def test_semantic_extraction_english_and_hinglish(self):
        text_en = "Your electricity power will be disconnected immediately at 9:30 PM. Call officer."
        signals_en = SemanticSignalExtractor.extract_signals("inc_201", text_en)
        self.assertGreaterEqual(len(signals_en), 2)
        types_en = [s.signal_type for s in signals_en]
        self.assertIn("URGENCY_PRESSURE_DETECTED", types_en)
        self.assertIn("OFFICIAL_ENTITY_IMPERSONATION", types_en)

        text_hi = "Turant bijli bill bhare nahi to light kat di jayegi."
        signals_hi = SemanticSignalExtractor.extract_signals("inc_202", text_hi)
        self.assertGreaterEqual(len(signals_hi), 1)
        self.assertEqual(signals_hi[0].signal_type, "URGENCY_PRESSURE_DETECTED")

    def test_evidence_fusion_single_signal_returns_insufficient_evidence(self):
        single_sig = [
            EvidenceSignal(
                incident_id="inc_203",
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.85,
                description="Urgency keyword found",
                provenance=ProvenanceRecord(
                    source_service="services/pattern-engine",
                    detector_name="SemanticSignalExtractor",
                    target_artifact="text",
                ),
            )
        ]
        assessment = EvidenceFusionEngine.evaluate("inc_203", single_sig, payment_proximate=False)
        self.assertEqual(assessment.risk_level, RiskLevel.INSUFFICIENT_EVIDENCE)
        self.assertEqual(assessment.evidence_confidence, EvidenceConfidence.LOW)
        self.assertTrue(assessment.is_insufficient_evidence)
        self.assertEqual(assessment.intervention.action, InterventionAction.NONE)

    def test_multi_dimensional_fusion_triggers_high_risk_and_prepayment_friction(self):
        multi_signals = [
            # Dimension 1: SEMANTIC
            EvidenceSignal(
                incident_id="inc_204",
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.90,
                weight=1.5,
                description="Immediate disconnection threat",
                provenance=ProvenanceRecord(
                    source_service="services/pattern-engine",
                    detector_name="NLP",
                    target_artifact="sms",
                ),
            ),
            # Dimension 2: URL
            EvidenceSignal(
                incident_id="inc_204",
                dimension=SignalDimension.URL,
                signal_type="BRAND_TYPOSQUATTING_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.92,
                weight=1.8,
                description="Hyphenated brand impersonation URL",
                provenance=ProvenanceRecord(
                    source_service="services/investigation",
                    detector_name="URLAnalyzer",
                    target_artifact="http://mahavitaran-bill.info",
                ),
            ),
            # Dimension 3: PAYMENT
            EvidenceSignal(
                incident_id="inc_204",
                dimension=SignalDimension.PAYMENT,
                signal_type="CROSS_INCIDENT_UPI_VPA_REUSE",
                severity=SignalSeverity.CRITICAL,
                confidence=0.98,
                weight=2.0,
                description="VPA previously flagged in fraud incident",
                provenance=ProvenanceRecord(
                    source_service="services/graph-engine",
                    detector_name="Neo4j",
                    target_artifact="fraud@oksbi",
                ),
            ),
        ]

        assessment = EvidenceFusionEngine.evaluate("inc_204", multi_signals, payment_proximate=True)
        self.assertEqual(assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(assessment.evidence_confidence, EvidenceConfidence.HIGH)
        self.assertFalse(assessment.is_insufficient_evidence)
        self.assertEqual(assessment.intervention.action, InterventionAction.PRE_PAYMENT_INTERVENTION)
        self.assertEqual(assessment.intervention.friction_delay_seconds, 10)
        self.assertFalse(assessment.intervention.dismissible)


if __name__ == "__main__":
    unittest.main()
