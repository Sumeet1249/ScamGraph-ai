"""Automated tests for Scenario Runner (Step 15).

Verifies the 6 safe synthetic scenarios execute across the entire pipeline:
1. Normal Utility Payment -> Low risk, No disruptive alert, payment unblocked
2. KYC Bank Scam -> Strong pattern match, High risk, Pre-payment blocker (10s friction)
3. Investment Scam -> High risk, Strong pattern match, Pre-payment blocker
4. Fake Job Scam -> High risk, Strong pattern match, Pre-payment blocker
5. Ambiguous Payment -> Insufficient evidence, Non-disruptive, payment unblocked
6. Emerging Variant (Digital Arrest) -> High risk, Strong pattern match, Pre-payment blocker
"""

import unittest
from pathlib import Path

from services.api.app.domain.enums import InterventionType, MatchLevel, RiskLevel
from services.pattern_engine.matcher.scenario_runner import ScenarioRunner


class TestScenarioRunner(unittest.TestCase):
    def setUp(self):
        self.runner = ScenarioRunner()
        self.scenarios_dir = Path("s:/ScamGraph-AI/data/scenarios")

    def test_scenario_01_normal_payment(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "01_normal_payment.json")
        self.assertEqual(result.scenario_id, "scenario_01_normal_payment")
        self.assertEqual(result.risk_assessment.risk_level, RiskLevel.LOW)
        self.assertLess(result.risk_assessment.risk_score, 35)
        self.assertEqual(result.intervention.action, InterventionType.NONE)
        self.assertFalse(result.intervention.payment_blocked)
        self.assertGreater(len(result.risk_assessment.counter_evidence), 0)

    def test_scenario_02_kyc_scam(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "02_kyc_scam.json")
        self.assertEqual(result.scenario_id, "scenario_02_kyc_scam")
        self.assertIsNotNone(result.pattern_matched)
        self.assertEqual(result.pattern_matched.pattern_id, "KYC_IMPERSONATION")
        self.assertEqual(result.pattern_matched.match_level, MatchLevel.STRONG)
        self.assertEqual(result.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertGreaterEqual(result.risk_assessment.risk_score, 75)
        self.assertEqual(result.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertTrue(result.intervention.payment_blocked)
        self.assertEqual(result.intervention.friction_delay_seconds, 10)

    def test_scenario_03_investment_scam(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "03_investment_scam.json")
        self.assertEqual(result.scenario_id, "scenario_03_investment_scam")
        self.assertIsNotNone(result.pattern_matched)
        self.assertEqual(result.pattern_matched.pattern_id, "INVESTMENT_SCAM")
        self.assertEqual(result.pattern_matched.match_level, MatchLevel.STRONG)
        self.assertEqual(result.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(result.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertTrue(result.intervention.payment_blocked)

    def test_scenario_04_fake_job_scam(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "04_fake_job_scam.json")
        self.assertEqual(result.scenario_id, "scenario_04_fake_job_scam")
        self.assertIsNotNone(result.pattern_matched)
        self.assertEqual(result.pattern_matched.pattern_id, "JOB_TASK_SCAM")
        self.assertEqual(result.pattern_matched.match_level, MatchLevel.STRONG)
        self.assertEqual(result.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(result.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertTrue(result.intervention.payment_blocked)

    def test_scenario_05_ambiguous_payment(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "05_ambiguous_payment.json")
        self.assertEqual(result.scenario_id, "scenario_05_ambiguous_payment")
        self.assertTrue(result.risk_assessment.insufficient_evidence)
        self.assertNotEqual(result.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertNotEqual(result.intervention.action, InterventionType.STRONG_WARNING)
        self.assertFalse(result.intervention.payment_blocked)

    def test_scenario_06_emerging_variant_seed(self):
        result = self.runner.run_scenario_file(self.scenarios_dir / "06_emerging_variant_seed.json")
        self.assertEqual(result.scenario_id, "scenario_06_emerging_variant_seed")
        self.assertIsNotNone(result.pattern_matched)
        self.assertEqual(result.pattern_matched.pattern_id, "DIGITAL_ARREST")
        self.assertEqual(result.pattern_matched.match_level, MatchLevel.STRONG)
        self.assertEqual(result.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(result.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertTrue(result.intervention.payment_blocked)


if __name__ == "__main__":
    unittest.main()
