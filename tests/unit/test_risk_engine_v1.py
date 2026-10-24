"""Unit tests for Step 13: Evidence Fusion and Risk Engine V1.

Verifies:
1. Obvious KYC scam -> HIGH risk
2. Normal payment -> LOW risk
3. Ambiguous payment link -> insufficient_evidence = True
4. Strong pattern with sparse evidence -> elevated risk, lower confidence
5. Multiple independent sources -> higher confidence
6. Contradictory evidence -> counter-evidence retained, risk score discounted
7. Deduplication of multi-source findings -> prevents double-counting
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from services.api.app.domain import (
    Incident,
    Event,
    Evidence,
    PatternMatch,
    GraphCorrelation,
    RiskAssessment,
    RiskLevel,
    ConfidenceLevel,
    EvidenceSource,
    EventType,
    MatchLevel,
)
from services.pattern_engine.matcher.risk_engine_v1 import RiskEngineV1


class TestRiskEngineV1Step13(unittest.TestCase):
    def setUp(self):
        self.engine = RiskEngineV1()
        self.now = datetime.now(timezone.utc)
        self.incident = Incident(
            id=str(uuid4()),
            created_at=self.now,
            updated_at=self.now,
            title="Test Incident",
        )

    def test_case_1_obvious_kyc_scam_produces_high_risk(self):
        evidence = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="OFFICIAL_ENTITY_IMPERSONATION",
                observation="Claims to be SBI Senior Manager",
                confidence=0.95,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="URGENCY_PRESSURE_DETECTED",
                observation="Account block threat within 2 hours",
                confidence=0.90,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.URL_ANALYZER,
                signal="BRAND_TYPOSQUATTING_DETECTED",
                observation="Deceptive domain sbi-kyc-fix.online",
                confidence=0.92,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.TINYFISH,
                signal="OTP_INPUT_FORM_OBSERVED",
                observation="Interactive form actively collects transaction OTP",
                confidence=0.98,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.PAYMENT_MODEL,
                signal="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                observation="Personal VPA scammer.ops@oksbi targeted",
                confidence=0.88,
                timestamp=self.now,
            ),
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED),
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.PAYMENT_REQUEST),
        ]
        pm = [
            PatternMatch(
                pattern_id="KYC_IMPERSONATION",
                pattern_name="KYC / Bank Impersonation Scam",
                match_level=MatchLevel.STRONG,
                confidence=0.94,
            )
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence, pattern_matches=pm)
        self.assertEqual(assessment.risk_level, RiskLevel.HIGH)
        self.assertGreaterEqual(assessment.risk_score, 65)
        self.assertEqual(assessment.evidence_confidence, ConfidenceLevel.HIGH)
        self.assertFalse(assessment.insufficient_evidence)

    def test_case_2_normal_payment_produces_low_risk(self):
        # Normal payment with no threat signals
        evidence = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.USER_INPUT,
                signal="BENIGN_CONVERSATION",
                observation="Dinner split payment request with trusted contact",
                confidence=0.95,
                timestamp=self.now,
            )
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.PAYMENT_INTENT),
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence)
        self.assertEqual(assessment.risk_level, RiskLevel.LOW)
        self.assertTrue(assessment.insufficient_evidence)
        self.assertEqual(assessment.evidence_confidence, ConfidenceLevel.LOW)

    def test_case_3_ambiguous_payment_link_produces_insufficient_evidence(self):
        # Only a payment link without impersonation, without URL evidence, without campaign data
        evidence = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.USER_INPUT,
                signal="PAYMENT_LINK_RECEIVED",
                observation="Received generic payment link",
                confidence=0.80,
                timestamp=self.now,
            )
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED)
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence)
        self.assertTrue(assessment.insufficient_evidence)
        self.assertEqual(assessment.risk_level, RiskLevel.LOW)
        self.assertEqual(assessment.evidence_confidence, ConfidenceLevel.LOW)

    def test_case_4_strong_pattern_with_sparse_evidence_elevates_risk_but_lowers_confidence(self):
        # Only 1 evidence source observed (e.g. user forwarded text alone), but matches pattern
        evidence = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="OFFICIAL_ENTITY_IMPERSONATION",
                observation="Urgent electricity cutoff threat from Bescom",
                confidence=0.92,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="URGENCY_PRESSURE_DETECTED",
                observation="Power will be disconnected tonight",
                confidence=0.90,
                timestamp=self.now,
            ),
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED)
        ]
        pm = [
            PatternMatch(
                pattern_id="ELECTRICITY_DISCONNECTION_FRAUD",
                pattern_name="Electricity Disconnection Fraud",
                match_level=MatchLevel.STRONG,
                confidence=0.88,
            )
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence, pattern_matches=pm)
        # Risk score is elevated due to pattern amplification, but confidence remains LOW due to single source
        self.assertGreaterEqual(assessment.risk_score, 35)
        self.assertEqual(assessment.evidence_confidence, ConfidenceLevel.LOW)

    def test_case_5_multiple_independent_sources_produces_high_confidence(self):
        evidence = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="OFFICIAL_ENTITY_IMPERSONATION",
                observation="Bank impersonation",
                confidence=0.90,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.URL_ANALYZER,
                signal="BRAND_TYPOSQUATTING_DETECTED",
                observation="Deceptive domain",
                confidence=0.92,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.TINYFISH,
                signal="OTP_INPUT_FORM_OBSERVED",
                observation="OTP input form detected",
                confidence=0.95,
                timestamp=self.now,
            ),
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED)
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence)
        self.assertEqual(assessment.evidence_confidence, ConfidenceLevel.HIGH)

    def test_case_6_contradictory_evidence_discounts_risk(self):
        evidence_without_counter = [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="URGENCY_PRESSURE_DETECTED",
                observation="Urgency",
                confidence=0.90,
                timestamp=self.now,
            ),
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.URL_ANALYZER,
                signal="SUSPICIOUS_TLD",
                observation="Unusual TLD",
                confidence=0.85,
                timestamp=self.now,
            ),
        ]
        evidence_with_counter = list(evidence_without_counter) + [
            Evidence(
                id=str(uuid4()),
                incident_id=self.incident.id,
                source=EvidenceSource.RDAP,
                signal="ESTABLISHED_LONG_TERM_DOMAIN",
                observation="Verified official domain active for 14 years",
                confidence=0.99,
                timestamp=self.now,
            )
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED)
        ]

        score_without = self.engine.evaluate(self.incident, events, evidence_without_counter).risk_score
        score_with = self.engine.evaluate(self.incident, events, evidence_with_counter).risk_score

        # Counter-evidence must discount points
        self.assertLess(score_with, score_without)
        assessment = self.engine.evaluate(self.incident, events, evidence_with_counter)
        self.assertIn("ESTABLISHED_LONG_TERM_DOMAIN", assessment.counter_evidence)

    def test_double_counting_prevention(self):
        # Both TinyFish and URL Analyzer report OTP harvesting
        ev_id1 = "ev-otp-url-harvest-001"
        ev_id2 = "ev-otp-dom-tinyfish-002"
        ev_id3 = "ev-imp-message-auth-003"
        evidence = [
            Evidence(
                id=ev_id1,
                incident_id=self.incident.id,
                source=EvidenceSource.URL_ANALYZER,
                signal="OTP_HARVEST_DETECTED",
                observation="URL analyzer detected OTP field",
                confidence=0.85,
                timestamp=self.now,
            ),
            Evidence(
                id=ev_id2,
                incident_id=self.incident.id,
                source=EvidenceSource.TINYFISH,
                signal="OTP_INPUT_FORM_OBSERVED",
                observation="TinyFish DOM detected OTP input element",
                confidence=0.95,
                timestamp=self.now,
            ),
            Evidence(
                id=ev_id3,
                incident_id=self.incident.id,
                source=EvidenceSource.MESSAGE_ANALYZER,
                signal="OFFICIAL_ENTITY_IMPERSONATION",
                observation="Bank impersonation",
                confidence=0.90,
                timestamp=self.now,
            ),
        ]
        events = [
            Event(id=str(uuid4()), incident_id=self.incident.id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED)
        ]

        assessment = self.engine.evaluate(self.incident, events, evidence)
        # Should only have 1 OTP reason code combining ev_id1 and ev_id2, not two separate 35-point penalties!
        otp_codes = [rc for rc in assessment.reason_codes if "RC_OTP_REQUEST" in rc]
        self.assertEqual(len(otp_codes), 1)
        self.assertIn(ev_id1, otp_codes[0])
        self.assertIn(ev_id2, otp_codes[0])


if __name__ == "__main__":
    unittest.main()
