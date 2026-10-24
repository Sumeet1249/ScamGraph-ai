"""Unit tests for Step 14: Adaptive Intervention Engine.

Verifies:
1. Benign journey produces no disruptive warning
2. Single suspicious message does not immediately trigger pre-payment warning
3. Risk increases across journey (NONE -> PASSIVE -> CAUTION -> STRONG_WARNING -> PRE_PAYMENT_INTERVENTION)
4. Payment proximity can escalate intervention
5. Low confidence can reduce intervention
6. Strong counter-evidence can reduce intervention
"""

import unittest
from services.api.app.domain.enums import ConfidenceLevel, InterventionType, MatchLevel
from services.api.app.domain.models import PatternMatch
from services.pattern_engine.matcher.intervention_engine import AdaptiveInterventionEngine


class TestAdaptiveInterventionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AdaptiveInterventionEngine()
        self.sample_pattern = PatternMatch(
            pattern_id="KYC_IMPERSONATION",
            pattern_name="KYC / Bank Impersonation Scam",
            matched_events=["MESSAGE_RECEIVED", "URL_OPENED"],
            missing_events=["PAYMENT_REQUEST"],
            supporting_evidence_ids=["ev-1"],
            match_level=MatchLevel.MODERATE,
            current_stage="SUSPICIOUS_LINK",
            common_next_stage="PAYMENT_REQUEST",
            confidence=0.75,
        )

    def test_benign_journey_produces_no_disruptive_warning(self):
        decision = self.engine.decide_intervention(
            risk_score=8,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="INITIAL_CONTACT",
            payment_proximity=False,
            num_events=2,
        )
        self.assertEqual(decision.action, InterventionType.NONE)
        self.assertEqual(decision.friction_delay_seconds, 0)
        self.assertFalse(decision.payment_blocked)

    def test_single_suspicious_message_does_not_trigger_pre_payment(self):
        # Even if a single message has a high Threat Risk Index (e.g. 85),
        # alert fatigue protection must cap it from triggering pre-payment blocking.
        decision = self.engine.decide_intervention(
            risk_score=85,
            evidence_confidence=ConfidenceLevel.HIGH,
            journey_stage="INITIAL_CONTACT",
            payment_proximity=False,
            num_events=1,
        )
        self.assertNotEqual(decision.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertIn(decision.action, [InterventionType.CAUTION, InterventionType.STRONG_WARNING])
        self.assertFalse(decision.payment_blocked)

    def test_risk_increases_across_journey(self):
        # 1. Unknown message: risk 15 -> NONE
        d1 = self.engine.decide_intervention(
            risk_score=15,
            evidence_confidence=ConfidenceLevel.LOW,
            journey_stage="INITIAL_CONTACT",
            num_events=1,
        )
        self.assertEqual(d1.action, InterventionType.NONE)

        # 2. Impersonation: risk 28 -> PASSIVE
        d2 = self.engine.decide_intervention(
            risk_score=28,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="IMPERSONATION",
            num_events=2,
        )
        self.assertEqual(d2.action, InterventionType.PASSIVE)

        # 3. Urgency + suspicious URL: risk 48 -> CAUTION
        d3 = self.engine.decide_intervention(
            risk_score=48,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="SUSPICIOUS_LINK",
            num_events=3,
        )
        self.assertEqual(d3.action, InterventionType.CAUTION)

        # 4. OTP request: risk 68 -> STRONG_WARNING
        d4 = self.engine.decide_intervention(
            risk_score=68,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="CREDENTIAL_OTP_HARVEST",
            num_events=4,
        )
        self.assertEqual(d4.action, InterventionType.STRONG_WARNING)

        # 5. Payment request + converging evidence: risk 86 -> PRE_PAYMENT_INTERVENTION
        d5 = self.engine.decide_intervention(
            risk_score=86,
            evidence_confidence=ConfidenceLevel.HIGH,
            journey_stage="PAYMENT_REQUEST",
            payment_proximity=True,
            pattern_match=self.sample_pattern,
            num_events=5,
        )
        self.assertEqual(d5.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertEqual(d5.friction_delay_seconds, 10)
        self.assertTrue(d5.payment_blocked)

    def test_payment_proximity_can_escalate_intervention(self):
        # Base risk 50 without payment proximity -> CAUTION
        d_normal = self.engine.decide_intervention(
            risk_score=50,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="SUSPICIOUS_LINK",
            payment_proximity=False,
            num_events=3,
        )
        self.assertEqual(d_normal.action, InterventionType.CAUTION)

        # Same risk 50 WITH payment proximity -> escalated to STRONG_WARNING
        d_escalated = self.engine.decide_intervention(
            risk_score=50,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="PAYMENT_REQUEST",
            payment_proximity=True,
            num_events=3,
        )
        self.assertEqual(d_escalated.action, InterventionType.STRONG_WARNING)

        # Risk 76 with payment proximity -> escalated to PRE_PAYMENT_INTERVENTION
        d_pre_pay = self.engine.decide_intervention(
            risk_score=76,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="PAYMENT_INTENT",
            payment_proximity=True,
            num_events=3,
        )
        self.assertEqual(d_pre_pay.action, InterventionType.PRE_PAYMENT_INTERVENTION)

    def test_low_confidence_can_reduce_intervention(self):
        # Risk 85 with HIGH confidence -> PRE_PAYMENT_INTERVENTION
        d_high_conf = self.engine.decide_intervention(
            risk_score=85,
            evidence_confidence=ConfidenceLevel.HIGH,
            journey_stage="PAYMENT_REQUEST",
            num_events=3,
        )
        self.assertEqual(d_high_conf.action, InterventionType.PRE_PAYMENT_INTERVENTION)

        # Risk 85 with LOW confidence -> de-escalated to STRONG_WARNING
        d_low_conf = self.engine.decide_intervention(
            risk_score=85,
            evidence_confidence=ConfidenceLevel.LOW,
            journey_stage="PAYMENT_REQUEST",
            num_events=3,
        )
        self.assertEqual(d_low_conf.action, InterventionType.STRONG_WARNING)

    def test_strong_counter_evidence_can_reduce_intervention(self):
        # Base risk 70 -> STRONG_WARNING
        d_without_counter = self.engine.decide_intervention(
            risk_score=70,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="SUSPICIOUS_LINK",
            num_events=3,
        )
        self.assertEqual(d_without_counter.action, InterventionType.STRONG_WARNING)

        # Same risk with verified official domain counter-evidence -> capped at CAUTION
        d_with_counter = self.engine.decide_intervention(
            risk_score=70,
            evidence_confidence=ConfidenceLevel.MEDIUM,
            journey_stage="SUSPICIOUS_LINK",
            counter_evidence=["ESTABLISHED_LONG_TERM_DOMAIN", "OFFICIAL_MERCHANT_VPA_VERIFIED"],
            num_events=3,
        )
        self.assertEqual(d_with_counter.action, InterventionType.CAUTION)


if __name__ == "__main__":
    unittest.main()
