"""Unit tests for Step 18: Explainable RiskEngine.

Tests:
1. obvious scam
2. legitimate payment
3. ambiguous case
4. missing TinyFish
5. missing graph data
6. contradictory evidence
7. reason codes linking back to Evidence IDs
"""

import unittest
from services.pattern_engine.matcher.risk_engine import RiskEngine
from services.pattern_engine.patterns.scam_patterns import PatternMatcher
from packages.schemas import (
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    RiskLevel,
    EvidenceConfidence,
    InterventionAction,
)


class TestRiskEngineStep18(unittest.TestCase):
    def test_obvious_scam_evaluates_high_risk_and_prepayment_intervention(self):
        signals = [
            EvidenceSignal(
                signal_id="sig_urg_1",
                incident_id="inc_scam",
                dimension=SignalDimension.SEMANTIC,
                signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                severity=SignalSeverity.HIGH,
                confidence=0.92,
                weight=1.8,
                description="Impersonates State Electricity Board",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="NLP", target_artifact="msg"),
            ),
            EvidenceSignal(
                signal_id="sig_url_1",
                incident_id="inc_scam",
                dimension=SignalDimension.URL,
                signal_type="BRAND_TYPOSQUATTING_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.90,
                weight=1.8,
                description="Deceptive domain",
                provenance=ProvenanceRecord(source_service="URL", detector_name="URL", target_artifact="url"),
            ),
            EvidenceSignal(
                signal_id="sig_pay_1",
                incident_id="inc_scam",
                dimension=SignalDimension.PAYMENT,
                signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.88,
                weight=1.5,
                description="Personal VPA handle",
                provenance=ProvenanceRecord(source_service="PAY", detector_name="PAY", target_artifact="vpa"),
            ),
        ]
        match = PatternMatcher.match(signals)
        assess = RiskEngine.evaluate("inc_scam", signals, pattern_match=match, payment_proximate=True)

        self.assertGreaterEqual(assess.risk_score, 65)  # Index >= 65
        self.assertEqual(assess.risk_level, RiskLevel.HIGH)
        self.assertEqual(assess.evidence_confidence, EvidenceConfidence.HIGH)
        self.assertEqual(assess.recommended_intervention.action, InterventionAction.PRE_PAYMENT_INTERVENTION)
        self.assertEqual(assess.recommended_intervention.friction_delay_seconds, 10)

        # Verify reason codes link back to Evidence IDs
        self.assertTrue(any("sig_urg_1" in rc for rc in assess.reason_codes))
        self.assertTrue(any("sig_url_1" in rc for rc in assess.reason_codes))
        self.assertTrue(any("sig_pay_1" in rc for rc in assess.reason_codes))

    def test_ambiguous_case_returns_insufficient_evidence(self):
        signals = [
            EvidenceSignal(
                signal_id="sig_ambig_1",
                incident_id="inc_ambig",
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.80,
                description="Slight urgency marker",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="NLP", target_artifact="msg"),
            )
        ]
        assess = RiskEngine.evaluate("inc_ambig", signals)
        self.assertEqual(assess.risk_level, RiskLevel.INSUFFICIENT_EVIDENCE)
        self.assertEqual(assess.evidence_confidence, EvidenceConfidence.LOW)
        self.assertTrue(assess.is_insufficient_evidence)
        self.assertEqual(assess.recommended_intervention.action, InterventionAction.NONE)

    def test_legitimate_payment_with_counter_evidence(self):
        signals = [
            EvidenceSignal(
                signal_id="sig_trusted_1",
                incident_id="inc_legit",
                dimension=SignalDimension.URL,
                signal_type="ESTABLISHED_LONG_TERM_DOMAIN",
                severity=SignalSeverity.INFO,
                confidence=0.99,
                weight=1.5,
                is_counter_evidence=True,
                description="Domain is 15 years old",
                provenance=ProvenanceRecord(source_service="RDAP", detector_name="RDAP", target_artifact="onlinesbi.sbi"),
            )
        ]
        assess = RiskEngine.evaluate("inc_legit", signals)
        # Uncorroborated single benign signal triggers safe INSUFFICIENT_EVIDENCE / LOW
        self.assertEqual(assess.recommended_intervention.action, InterventionAction.NONE)
        self.assertTrue(assess.is_insufficient_evidence)

    def test_contradictory_evidence_discounts_risk_score(self):
        # 1 suspicious urgency + 1 suspicious domain + 1 established counter-evidence
        signals_without_counter = [
            EvidenceSignal(
                signal_id="s1",
                incident_id="inc_contra",
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.90,
                description="Urgency",
                provenance=ProvenanceRecord(source_service="A", detector_name="A", target_artifact="A"),
            ),
            EvidenceSignal(
                signal_id="s2",
                incident_id="inc_contra",
                dimension=SignalDimension.URL,
                signal_type="SUSPICIOUS_TLD_USED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.85,
                description="TLD",
                provenance=ProvenanceRecord(source_service="B", detector_name="B", target_artifact="B"),
            ),
        ]
        signals_with_counter = list(signals_without_counter) + [
            EvidenceSignal(
                signal_id="s_counter",
                incident_id="inc_contra",
                dimension=SignalDimension.URL,
                signal_type="ESTABLISHED_LONG_TERM_DOMAIN",
                severity=SignalSeverity.INFO,
                confidence=0.95,
                is_counter_evidence=True,
                description="Official domain",
                provenance=ProvenanceRecord(source_service="C", detector_name="C", target_artifact="C"),
            )
        ]

        score_without = RiskEngine.evaluate("inc_contra", signals_without_counter).risk_score
        score_with = RiskEngine.evaluate("inc_contra", signals_with_counter).risk_score

        # Counter-evidence MUST meaningfully discount risk score
        self.assertLess(score_with, score_without)

    def test_missing_tinyfish_or_missing_graph_data_evaluates_gracefully(self):
        signals = [
            EvidenceSignal(
                signal_id="s_nlp",
                incident_id="inc_missing_deps",
                dimension=SignalDimension.SEMANTIC,
                signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                severity=SignalSeverity.HIGH,
                confidence=0.90,
                description="Impersonation",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="NLP", target_artifact="msg"),
            ),
            EvidenceSignal(
                signal_id="s_pay",
                incident_id="inc_missing_deps",
                dimension=SignalDimension.PAYMENT,
                signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.85,
                description="VPA",
                provenance=ProvenanceRecord(source_service="PAY", detector_name="PAY", target_artifact="vpa"),
            ),
        ]
        # graph_correlation is None, TinyFish signals are absent
        assess = RiskEngine.evaluate("inc_missing_deps", signals, graph_correlation=None)
        self.assertFalse(assess.is_insufficient_evidence)
        self.assertIn(assess.risk_level, [RiskLevel.MEDIUM, RiskLevel.HIGH])
        self.assertEqual(assess.evidence_confidence, EvidenceConfidence.MEDIUM)


if __name__ == "__main__":
    unittest.main()
