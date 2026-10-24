"""Unit tests for Step 10: Canonical Domain Models.

Validates:
1. Valid Incident creation
2. Valid Event creation & temporal ordering
3. Timezone-awareness requirement (rejects naive datetimes)
4. Valid Evidence creation
5. Confidence bounds validation ([0.0, 1.0])
6. Valid RiskAssessment
7. Risk score bounds validation ([0, 100] index rejection)
8. PatternMatch validation
9. InterventionDecision validation (requires non-empty reason)
10. Entity credential protection (rejects sensitive tokens in metadata)
11. Evidence verdict boundary (cannot contain final scam verdict)
"""

import unittest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from pydantic import ValidationError

from services.api.app.domain import (
    Incident,
    Event,
    Entity,
    Evidence,
    Relationship,
    ScamPattern,
    PatternMatch,
    GraphCorrelation,
    RiskAssessment,
    InterventionDecision,
    RiskLevel,
    ConfidenceLevel,
    IncidentStatus,
    EventType,
    EntityType,
    EvidenceSource,
    InterventionType,
    MatchLevel,
)


class TestCanonicalDomainModelsStep10(unittest.TestCase):
    def test_valid_incident(self):
        now = datetime.now(timezone.utc)
        inc = Incident(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            status=IncidentStatus.OPEN,
            title="Suspicious SBI KYC Communication",
            source="USER_REPORT",
            metadata={"channel": "SMS"},
        )
        self.assertEqual(inc.status, IncidentStatus.OPEN)
        self.assertEqual(inc.title, "Suspicious SBI KYC Communication")

    def test_valid_event_and_temporal_ordering(self):
        t1 = datetime.now(timezone.utc)
        t2 = t1 + timedelta(seconds=15)

        ev1 = Event(
            id=str(uuid4()),
            incident_id=str(uuid4()),
            timestamp=t1,
            event_type=EventType.MESSAGE_RECEIVED,
            source=EvidenceSource.MESSAGE_ANALYZER,
            confidence=0.95,
            payload={"text": "KYC update required"},
        )
        ev2 = Event(
            id=str(uuid4()),
            incident_id=str(uuid4()),
            timestamp=t2,
            event_type=EventType.URL_OPENED,
            source=EvidenceSource.URL_ANALYZER,
            confidence=0.90,
            payload={"url": "http://sbi-kyc.online"},
        )

        # Test temporal ordering
        self.assertTrue(ev1 < ev2)
        sorted_events = sorted([ev2, ev1])
        self.assertEqual(sorted_events[0].id, ev1.id)
        self.assertEqual(sorted_events[1].id, ev2.id)

    def test_invalid_naive_timestamp_rejected(self):
        naive_dt = datetime(2026, 10, 21, 1, 0, 0)  # No tzinfo!
        with self.assertRaises(ValidationError) as ctx:
            Incident(
                id=str(uuid4()),
                created_at=naive_dt,
                updated_at=naive_dt,
                title="Test Incident",
            )
        self.assertIn("Timestamp must be timezone-aware", str(ctx.exception))

    def test_valid_evidence(self):
        ev = Evidence(
            id=str(uuid4()),
            incident_id=str(uuid4()),
            source=EvidenceSource.TINYFISH,
            signal="OTP_INPUT_FORM_OBSERVED",
            observation="Form action targets unlisted external IP",
            confidence=0.98,
            timestamp=datetime.now(timezone.utc),
            entity_ids=[str(uuid4())],
            event_ids=[str(uuid4())],
        )
        self.assertEqual(ev.confidence, 0.98)
        self.assertEqual(ev.signal, "OTP_INPUT_FORM_OBSERVED")

    def test_invalid_confidence_bounds(self):
        now = datetime.now(timezone.utc)
        # > 1.0 rejection
        with self.assertRaises(ValidationError):
            Evidence(
                id=str(uuid4()),
                incident_id=str(uuid4()),
                source=EvidenceSource.TINYFISH,
                signal="TEST",
                observation="Observation text",
                confidence=1.05,
                timestamp=now,
            )
        # < 0.0 rejection
        with self.assertRaises(ValidationError):
            Evidence(
                id=str(uuid4()),
                incident_id=str(uuid4()),
                source=EvidenceSource.TINYFISH,
                signal="TEST",
                observation="Observation text",
                confidence=-0.1,
                timestamp=now,
            )

    def test_valid_risk_assessment(self):
        assess = RiskAssessment(
            incident_id=str(uuid4()),
            risk_score=87,
            risk_level=RiskLevel.HIGH,
            evidence_confidence=ConfidenceLevel.HIGH,
            confidence_level=ConfidenceLevel.HIGH,
            reason_codes=["[RC_01] Deceptive bank portal domain"],
            counter_evidence=[],
            pattern_matches=[],
            graph_correlations=[],
            insufficient_evidence=False,
            assessed_at=datetime.now(timezone.utc),
        )
        self.assertEqual(assess.risk_score, 87)
        self.assertEqual(assess.risk_level, RiskLevel.HIGH)

    def test_risk_score_exceeding_100_rejected(self):
        with self.assertRaises(ValidationError):
            RiskAssessment(
                incident_id=str(uuid4()),
                risk_score=105,  # Exceeds 100!
                risk_level=RiskLevel.HIGH,
                evidence_confidence=ConfidenceLevel.HIGH,
                confidence_level=ConfidenceLevel.HIGH,
                assessed_at=datetime.now(timezone.utc),
            )

    def test_pattern_match_validation(self):
        pm = PatternMatch(
            pattern_id="pat_kyc_01",
            pattern_name="KYC_IMPERSONATION",
            matched_events=["MESSAGE_RECEIVED", "URL_OPENED"],
            missing_events=["PAYMENT_REQUEST"],
            supporting_evidence_ids=[str(uuid4())],
            match_level=MatchLevel.STRONG,
            current_stage="SUSPICIOUS_LINK",
            common_next_stage="CREDENTIAL_REQUEST",
            confidence=0.94,
        )
        self.assertEqual(pm.match_level, MatchLevel.STRONG)
        self.assertNotIsInstance(pm.match_level, float)  # Must NOT be a probability

    def test_intervention_decision_requires_non_empty_reason(self):
        # Valid decision
        dec = InterventionDecision(
            incident_id=str(uuid4()),
            intervention_type=InterventionType.PRE_PAYMENT_INTERVENTION,
            reason="Multi-source verified threat directly preceding payment intent.",
            journey_stage="PAYMENT_INTENT",
            payment_proximity=True,
            created_at=datetime.now(timezone.utc),
        )
        self.assertEqual(dec.intervention_type, InterventionType.PRE_PAYMENT_INTERVENTION)

        # Empty reason rejection
        with self.assertRaises(ValidationError):
            InterventionDecision(
                incident_id=str(uuid4()),
                intervention_type=InterventionType.CAUTION,
                reason="",  # Empty reason must fail!
                journey_stage="INITIAL_CONTACT",
                payment_proximity=False,
                created_at=datetime.now(timezone.utc),
            )

    def test_entity_credential_rejection(self):
        # Rejecting passwords or PINs stored in entity metadata
        with self.assertRaises(ValidationError):
            Entity(
                id=str(uuid4()),
                entity_type=EntityType.PHONE,
                normalized_value="+919111111111",
                display_value="+91 91111 11111",
                metadata={"pin": "1234"},  # Prohibited!
            )

    def test_evidence_final_verdict_rejection(self):
        # Evidence represents an observation and must NOT declare a final scam verdict
        with self.assertRaises(ValidationError):
            Evidence(
                id=str(uuid4()),
                incident_id=str(uuid4()),
                source=EvidenceSource.URL_ANALYZER,
                signal="SUSPICIOUS_TLD",
                observation="Conclusive scam verdict: guilty",  # Prohibited!
                confidence=0.9,
                timestamp=datetime.now(timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
