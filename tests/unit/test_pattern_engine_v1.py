"""Unit tests for Step 12: Scam Pattern Engine V1 (Deterministic & Explainable).

Verifies:
1. Complete KYC journey -> STRONG match
2. Partial KYC journey -> MODERATE match
3. Investment journey -> STRONG match
4. Fake job journey -> STRONG match
5. Benign journey -> must NOT produce a STRONG match
6. Events in wrong order -> lower score than in-order events
7. Missing stages -> handled gracefully
8. Ambiguous journey -> low match level
"""

import unittest
from services.pattern_engine.matcher.pattern_engine_v1 import PatternEngineV1
from services.api.app.domain import MatchLevel


class TestPatternEngineV1Step12(unittest.TestCase):
    def setUp(self):
        self.engine = PatternEngineV1()

    def test_complete_kyc_journey_produces_strong_match(self):
        signals = [
            "OFFICIAL_ENTITY_IMPERSONATION",
            "FINANCIAL_CONTEXT",
            "URGENCY_PRESSURE_DETECTED",
            "SUSPICIOUS_URL_PRESENT",
            "OTP_INPUT_FORM_OBSERVED",
            "INDIVIDUAL_VPA_PAYMENT_TARGETED",
        ]
        events = [
            "MESSAGE_RECEIVED",
            "URL_OPENED",
            "CREDENTIAL_REQUEST",
            "OTP_REQUEST",
            "PAYMENT_REQUEST",
        ]
        match = self.engine.evaluate_pattern("KYC_IMPERSONATION", signals, events)
        self.assertIsNotNone(match)
        self.assertEqual(match.match_level, MatchLevel.STRONG)
        self.assertGreaterEqual(match.confidence, 0.70)
        self.assertEqual(match.current_stage, "PAYMENT_REQUEST")

    def test_partial_kyc_journey_produces_moderate_match(self):
        # Missing URL and OTP, but has required impersonation & financial context
        signals = [
            "OFFICIAL_ENTITY_IMPERSONATION",
            "FINANCIAL_CONTEXT",
            "URGENCY_PRESSURE_DETECTED",
        ]
        events = [
            "MESSAGE_RECEIVED",
        ]
        match = self.engine.evaluate_pattern("KYC_IMPERSONATION", signals, events)
        self.assertIsNotNone(match)
        self.assertIn(match.match_level, [MatchLevel.MODERATE, MatchLevel.WEAK])
        self.assertNotEqual(match.match_level, MatchLevel.STRONG)

    def test_investment_scam_journey_produces_strong_match(self):
        signals = [
            "FINANCIAL_CONTEXT",
            "HIGH_RETURN_PROMISE",
            "TELEGRAM_COMMUNICATION_CHANNEL",
            "CRYPTO_OR_UPI_DEPOSIT_REQUEST",
        ]
        events = [
            "MESSAGE_RECEIVED",
            "URL_OPENED",
            "PAYMENT_REQUEST",
        ]
        match = self.engine.evaluate_pattern("INVESTMENT_SCAM", signals, events)
        self.assertIsNotNone(match)
        self.assertEqual(match.match_level, MatchLevel.STRONG)

    def test_fake_job_journey_produces_strong_match(self):
        signals = [
            "EMPLOYMENT_OFFER_CONTEXT",
            "REGISTRATION_OR_BADGE_FEE",
            "TELEGRAM_COMMUNICATION_CHANNEL",
            "PERSONAL_VPA_PAYMENT_TARGETED",
        ]
        events = [
            "MESSAGE_RECEIVED",
            "URL_OPENED",
            "PAYMENT_REQUEST",
        ]
        match = self.engine.evaluate_pattern("JOB_TASK_SCAM", signals, events)
        self.assertIsNotNone(match)
        self.assertEqual(match.match_level, MatchLevel.STRONG)

    def test_benign_journey_must_not_produce_strong_match(self):
        # Normal dinner bill split or personal greeting
        signals = ["CASUAL_CONVERSATION"]
        events = ["MESSAGE_RECEIVED", "PAYMENT_INTENT"]
        match = self.engine.match_best_pattern(signals, events)
        # Must either be None or MatchLevel.NONE / WEAK
        if match:
            self.assertNotEqual(match.match_level, MatchLevel.STRONG)
            self.assertLess(match.confidence, 0.40)

    def test_events_in_wrong_order_scores_lower_than_in_order(self):
        signals = [
            "OFFICIAL_ENTITY_IMPERSONATION",
            "FINANCIAL_CONTEXT",
            "URGENCY_PRESSURE_DETECTED",
        ]
        in_order_events = ["MESSAGE_RECEIVED", "URL_OPENED", "OTP_REQUEST", "PAYMENT_REQUEST"]
        wrong_order_events = ["PAYMENT_REQUEST", "OTP_REQUEST", "URL_OPENED", "MESSAGE_RECEIVED"]

        match_in_order = self.engine.evaluate_pattern("KYC_IMPERSONATION", signals, in_order_events)
        match_wrong_order = self.engine.evaluate_pattern("KYC_IMPERSONATION", signals, wrong_order_events)

        self.assertGreater(match_in_order.confidence, match_wrong_order.confidence)

    def test_ambiguous_case(self):
        signals = ["UNSOLICITED_MESSAGE"]
        events = ["MESSAGE_RECEIVED"]
        match = self.engine.evaluate_pattern("KYC_IMPERSONATION", signals, events)
        self.assertIn(match.match_level, [MatchLevel.NONE, MatchLevel.WEAK])


if __name__ == "__main__":
    unittest.main()
