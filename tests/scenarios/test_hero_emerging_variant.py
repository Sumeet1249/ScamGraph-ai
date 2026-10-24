"""Step 21 — The Hero Test: Emerging Scam Variant Detection.

Scenario:
Historical incident:
- Brand: SBI
- Tactic: KYC suspension
- Phone: +919111111111 (Phone A)
- Domain: sbi-kyc-fix.online (Domain A)
- UPI VPA: sbi.officer@oksbi (UPI A)

New variant incident:
- Brand: HDFC
- Tactic: Security verification
- Phone: +919222222222 (Phone B)
- Domain: hdfc-security-check.xyz (Domain B)
- UPI VPA: hdfc.desk@paytm (UPI B)

Result:
- IDENTIFIER MATCH: Phone NO, Domain NO, Payment NO
- WORKFLOW MATCH: Semantic HIGH, Temporal HIGH, Pattern HIGH
- RESULT: POSSIBLE EMERGING CAMPAIGN / VARIANT
"""

import unittest
from services.pattern_engine.semantic.fingerprint_builder import ScamFingerprintBuilder
from services.pattern_engine.patterns.scam_patterns import PatternMatcher, SCAM_PATTERNS, PatternMatch
from services.pattern_engine.matcher.variant_detector import EmergingVariantDetector
from packages.schemas import (
    EmergingStatus,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
)


class TestHeroEmergingVariantStep21(unittest.TestCase):
    def test_hero_emerging_variant_detection(self):
        # 1. Historical Known Scam Database
        historical_phones = ["+919111111111"]
        historical_domains = ["sbi-kyc-fix.online"]
        historical_vpas = ["sbi.officer@oksbi"]

        # 2. Incoming New Incident (Brand B, Phone B, Domain B, UPI B)
        new_incident_id = "inc_hero_emerging_variant_001"
        new_phone = "+919222222222"
        new_domain = "hdfc-security-check.xyz"
        new_vpa = "hdfc.desk@paytm"

        # Multi-stage grooming signals observed for the new incident:
        # impersonation -> account threat -> urgency -> credential page -> OTP -> payment
        new_incident_signals = [
            EvidenceSignal(
                incident_id=new_incident_id,
                dimension=SignalDimension.SEMANTIC,
                signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                severity=SignalSeverity.HIGH,
                confidence=0.94,
                description="Sender purports to represent HDFC Security Team",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="NLP", target_artifact="msg"),
            ),
            EvidenceSignal(
                incident_id=new_incident_id,
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.90,
                description="Urgent account threat: verify within 2 hours to avoid freeze",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="NLP", target_artifact="msg"),
            ),
            EvidenceSignal(
                incident_id=new_incident_id,
                dimension=SignalDimension.URL,
                signal_type="BRAND_TYPOSQUATTING_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.92,
                description="Unofficial domain hosting security check form",
                provenance=ProvenanceRecord(source_service="URL", detector_name="URL", target_artifact=new_domain),
            ),
            EvidenceSignal(
                incident_id=new_incident_id,
                dimension=SignalDimension.URL,
                signal_type="OTP_INPUT_FORM_OBSERVED",
                severity=SignalSeverity.CRITICAL,
                confidence=0.98,
                description="Web page actively contains an OTP harvest input",
                provenance=ProvenanceRecord(source_service="TinyFish", detector_name="TinyFish", target_artifact=new_domain),
            ),
            EvidenceSignal(
                incident_id=new_incident_id,
                dimension=SignalDimension.PAYMENT,
                signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.88,
                description="Payment requested to individual handle",
                provenance=ProvenanceRecord(source_service="PAY", detector_name="PAY", target_artifact=new_vpa),
            ),
        ]

        # 3. Build Fingerprint
        fingerprint = ScamFingerprintBuilder.build(
            incident_id=new_incident_id,
            message_summary="HDFC account security verification needed immediately",
            claimed_identity="HDFC Bank Security Desk",
            tactics=["ACCOUNT_BLOCK_THREAT", "IMMEDIATE_URGENCY", "IMPERSONATION"],
            requested_action="VERIFY_NETBANKING_AND_SUBMIT_OTP",
            stage_sequence=[
                "INITIAL_CONTACT",
                "IMPERSONATION",
                "URGENCY_PRESSURE",
                "SUSPICIOUS_LINK",
                "CREDENTIAL_OTP_HARVEST",
                "PAYMENT_REQUEST",
            ],
            temporal_pace_seconds=145,  # Grooming took ~2.5 minutes
            infrastructure_hash={
                "phone": new_phone,
                "domain": new_domain,
            },
            payment_profile={
                "vpa": new_vpa,
            },
        )

        # 4. Pattern Matching
        pattern_match = PatternMatcher.match(new_incident_signals)
        self.assertIsNotNone(pattern_match)
        self.assertTrue(pattern_match.is_strong_match)

        # 5. Evaluate with EmergingVariantDetector
        eval_result = EmergingVariantDetector.evaluate(
            incident_id=new_incident_id,
            fingerprint=fingerprint,
            historical_phones=historical_phones,
            historical_domains=historical_domains,
            historical_vpas=historical_vpas,
            pattern_match=pattern_match,
            semantic_similarity_score=0.82,  # Strong semantic match to banking impersonation
            temporal_pace_seconds=145,
        )

        # ─────────────────────────────────────────────────────────────
        # HERO ASSERTIONS
        # ─────────────────────────────────────────────────────────────
        # 1. KNOWN IDENTIFIER MATCH: All NO
        self.assertFalse(eval_result.identifier_match.phone_matched, "Phone should be brand-new (NO match)")
        self.assertFalse(eval_result.identifier_match.domain_matched, "Domain should be brand-new (NO match)")
        self.assertFalse(eval_result.identifier_match.payment_matched, "Payment VPA should be brand-new (NO match)")
        self.assertFalse(eval_result.identifier_match.has_any_match)

        # 2. WORKFLOW MATCH: All HIGH
        self.assertEqual(eval_result.workflow_match.semantic_level, "HIGH")
        self.assertEqual(eval_result.workflow_match.temporal_level, "HIGH")
        self.assertEqual(eval_result.workflow_match.pattern_level, "HIGH")

        # 3. FINAL VERDICT: POSSIBLE_EMERGING_CAMPAIGN
        self.assertEqual(eval_result.status, EmergingStatus.POSSIBLE_EMERGING_CAMPAIGN)
        self.assertIn("HERO MATCH", eval_result.verdict_explanation)


if __name__ == "__main__":
    unittest.main()
