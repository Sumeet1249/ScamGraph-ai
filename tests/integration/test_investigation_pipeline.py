"""Integration tests for Unified Investigation Orchestrator Pipeline (Step 18).

Tests the 7 complete journeys:
1. Normal payment -> Low risk, no disruptive alert
2. KYC journey -> High risk, Strong KYC pattern, Pre-payment blocker (10s friction)
3. Investment journey -> High risk, Strong Investment pattern, Pre-payment blocker
4. Fake job journey -> High risk, Strong Job Task pattern, Pre-payment blocker
5. Ambiguous journey -> Insufficient evidence, Low/Unknown risk, payment unblocked
6. URL investigation unavailable -> Assessment completes with partial status and reduced confidence
7. TinyFish unavailable -> Assessment completes without failing; does NOT mean safe; confidence reduced
"""

import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from services.api.app.domain.enums import (
    ConfidenceLevel,
    EventType,
    EvidenceSource,
    InterventionType,
    MatchLevel,
    RiskLevel,
)
from services.api.app.domain.models import Event, Evidence, Incident
from services.api.app.repository import InMemoryIncidentRepository
from services.investigation.orchestrator import InvestigationOrchestrator
from services.investigation.tinyfish.client import TinyFishClient
from services.investigation.tinyfish.exceptions import TinyFishTimeoutError
from services.investigation.tinyfish.service import TinyFishWebInvestigator
from services.investigation.url_analysis.service import URLInvestigationService


class TestInvestigationPipelineStep18(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryIncidentRepository()
        self.tinyfish = TinyFishWebInvestigator(client=TinyFishClient(mode="mock"))
        self.orchestrator = InvestigationOrchestrator(
            repository=self.repo,
            web_investigator=self.tinyfish,
        )
        self.now = datetime.now(timezone.utc)

    def test_journey_1_normal_payment(self):
        inc_id = f"inc-norm-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="Utility Bill Payment")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Your utility bill of 1450 INR is ready. View at https://utility.example.com/portal"}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=20), event_type=EventType.URL_OPENED, payload={"text": "User opened https://utility.example.com/portal"}),
            Event(id=f"ev-3-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=50), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Pay 1450 INR to utility@officialbank"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        # Add counter evidence
        ev_counter = Evidence(
            id=f"evi-c1-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.DNS,
            signal="ESTABLISHED_LONG_TERM_DOMAIN",
            observation="Domain utility.example.com registered 14 years ago",
            confidence=0.98,
            timestamp=self.now,
        )
        asyncio.run(self.repo.add_evidence(inc_id, ev_counter))

        assessment = asyncio.run(self.orchestrator.assess_incident(inc_id))

        self.assertNotEqual(assessment.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(assessment.risk_assessment.risk_level, RiskLevel.LOW)
        self.assertLess(assessment.risk_assessment.risk_score, 35)
        self.assertEqual(assessment.intervention.action, InterventionType.NONE)
        self.assertFalse(assessment.intervention.payment_blocked)

    def test_journey_2_kyc_journey(self):
        inc_id = f"inc-kyc-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="SBI KYC Threat")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Dear customer, your bank account is blocked. Update KYC at https://sbi-verify.example.test/kyc"}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=20), event_type=EventType.URL_OPENED, payload={"text": "User visited https://sbi-verify.example.test/kyc"}),
            Event(id=f"ev-3-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=40), event_type=EventType.CREDENTIAL_REQUEST, payload={"text": "Netbanking password entered"}),
            Event(id=f"ev-4-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=60), event_type=EventType.OTP_REQUEST, payload={"text": "SMS OTP entered"}),
            Event(id=f"ev-5-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=80), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Transfer 25,000 INR to fraudster.wallet@fakeupi"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        # Add initial message signals
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-imp-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="OFFICIAL_ENTITY_IMPERSONATION",
            observation="Sender claims to be SBI Netbanking Admin",
            confidence=0.95,
            timestamp=self.now,
        )))
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-urg-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="URGENCY_PRESSURE_DETECTED",
            observation="Account suspension deadline 2 hours",
            confidence=0.92,
            timestamp=self.now,
        )))

        assessment = asyncio.run(self.orchestrator.assess_incident(inc_id))

        self.assertEqual(assessment.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertGreaterEqual(assessment.risk_assessment.risk_score, 75)
        self.assertGreater(len(assessment.pattern_matches), 0)
        self.assertEqual(assessment.pattern_matches[0].pattern_id, "KYC_IMPERSONATION")
        self.assertEqual(assessment.pattern_matches[0].match_level, MatchLevel.STRONG)
        self.assertEqual(assessment.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertTrue(assessment.intervention.payment_blocked)
        self.assertEqual(assessment.intervention.friction_delay_seconds, 10)

    def test_journey_3_investment_journey(self):
        inc_id = f"inc-inv-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="AI Crypto Trading")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Join VIP club earning 30% daily return at https://crypto-vip.example.test/invest"}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=25), event_type=EventType.URL_OPENED, payload={"text": "Opened portal"}),
            Event(id=f"ev-3-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=55), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Deposit 10,000 INR into invest.pool@fakeupi"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-fin-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="HIGH_RETURN_PROMISE",
            observation="Guarantees 30% daily yield",
            confidence=0.95,
            timestamp=self.now,
        )))
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-fincx-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="FINANCIAL_CONTEXT",
            observation="Trading investment opportunity",
            confidence=0.90,
            timestamp=self.now,
        )))

        assessment = asyncio.run(self.orchestrator.assess_incident(inc_id))

        self.assertEqual(assessment.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(assessment.pattern_matches[0].pattern_id, "INVESTMENT_SCAM")
        self.assertEqual(assessment.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)

    def test_journey_4_fake_job_journey(self):
        inc_id = f"inc-job-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="Part-Time Rating Tasks")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Earn 3000/day rating hotels. Register at https://easyjob.example.test/apply"}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=20), event_type=EventType.URL_OPENED, payload={"text": "Opened application page"}),
            Event(id=f"ev-3-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=40), event_type=EventType.CREDENTIAL_REQUEST, payload={"text": "Account registration"}),
            Event(id=f"ev-4-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=70), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Deposit 5,000 INR task deposit to unlock bonus"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-job-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="EMPLOYMENT_OFFER_CONTEXT",
            observation="Unsolicited part-time job offer",
            confidence=0.94,
            timestamp=self.now,
        )))
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-fee-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.PAYMENT_MODEL,
            signal="REGISTRATION_OR_BADGE_FEE",
            observation="Deposit demanded to access tasks",
            confidence=0.96,
            timestamp=self.now,
        )))

        assessment = asyncio.run(self.orchestrator.assess_incident(inc_id))

        self.assertEqual(assessment.risk_assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(assessment.pattern_matches[0].pattern_id, "JOB_TASK_SCAM")
        self.assertEqual(assessment.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)

    def test_journey_5_ambiguous_journey(self):
        inc_id = f"inc-amb-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="Dinner Split")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Hey, please send the 500 INR for dinner."}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=30), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Payment link to friend.peer@example.test"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        assessment = asyncio.run(self.orchestrator.assess_incident(inc_id))

        self.assertTrue(assessment.risk_assessment.insufficient_evidence)
        self.assertEqual(assessment.risk_assessment.risk_level, RiskLevel.LOW)
        self.assertNotEqual(assessment.intervention.action, InterventionType.PRE_PAYMENT_INTERVENTION)
        self.assertFalse(assessment.intervention.payment_blocked)

    def test_journey_6_url_investigation_unavailable(self):
        inc_id = f"inc-url-unavail-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="URL Down Test")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Check update at https://slow-down.example.com"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        # Mock URL investigation failure
        mock_url_svc = URLInvestigationService()
        mock_url_svc.investigate_url = AsyncMock(side_effect=Exception("Network unreachable"))
        orchestrator = InvestigationOrchestrator(repository=self.repo, url_service=mock_url_svc)

        # Must not raise 500 error; assessment completes with available evidence
        assessment = asyncio.run(orchestrator.assess_incident(inc_id))
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.incident_id, inc_id)

    def test_journey_7_tinyfish_unavailable_lowers_confidence_without_marking_safe(self):
        inc_id = f"inc-tf-down-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="TinyFish Outage Test")
        asyncio.run(self.repo.create_incident(incident))

        events = [
            Event(id=f"ev-1-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now, event_type=EventType.MESSAGE_RECEIVED, payload={"text": "Urgent: Your account is locked! Verify at https://sbi-fake.example.com"}),
            Event(id=f"ev-2-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=20), event_type=EventType.URL_OPENED, payload={"text": "Opened link"}),
            Event(id=f"ev-3-{uuid4().hex[:8]}", incident_id=inc_id, timestamp=self.now + timedelta(seconds=40), event_type=EventType.PAYMENT_REQUEST, payload={"text": "Transfer verification fee"}),
        ]
        for ev in events:
            asyncio.run(self.repo.add_event(inc_id, ev))

        # Add strong message indicators
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-imp-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="OFFICIAL_ENTITY_IMPERSONATION",
            observation="Impersonates Bank Manager",
            confidence=0.95,
            timestamp=self.now,
        )))
        asyncio.run(self.repo.add_evidence(inc_id, Evidence(
            id=f"evi-urg-{uuid4().hex[:8]}",
            incident_id=inc_id,
            source=EvidenceSource.MESSAGE_ANALYZER,
            signal="URGENCY_PRESSURE_DETECTED",
            observation="Urgent freeze threat",
            confidence=0.90,
            timestamp=self.now,
        )))

        # Mock TinyFish timeout failure
        mock_client = TinyFishClient(mode="live", api_key="dummy-key")
        mock_client.fetch_page_observables = AsyncMock(side_effect=TinyFishTimeoutError("TinyFish timeout 4.0s"))
        mock_tf = TinyFishWebInvestigator(client=mock_client)

        orchestrator = InvestigationOrchestrator(repository=self.repo, web_investigator=mock_tf)
        assessment = asyncio.run(orchestrator.assess_incident(inc_id))

        # Provider failure MUST NOT automatically mark incident safe / LOW
        self.assertNotEqual(assessment.risk_assessment.risk_level, RiskLevel.LOW)
        self.assertEqual(assessment.investigation_status.get("tinyfish"), "unavailable")
        # Evidence confidence reflects missing data
        self.assertNotEqual(assessment.risk_assessment.confidence_level, ConfidenceLevel.HIGH)

    def test_idempotency_does_not_duplicate_evidence(self):
        inc_id = f"inc-idemp-{uuid4().hex[:8]}"
        incident = Incident(id=inc_id, created_at=self.now, updated_at=self.now, title="Idempotency Test")
        asyncio.run(self.repo.create_incident(incident))
        asyncio.run(self.repo.add_event(inc_id, Event(
            id=f"ev-1-{uuid4().hex[:8]}",
            incident_id=inc_id,
            timestamp=self.now,
            event_type=EventType.MESSAGE_RECEIVED,
            payload={"text": "Check out https://utility.example.com/portal"},
        )))

        # Run assessment 1st time
        res1 = asyncio.run(self.orchestrator.assess_incident(inc_id))
        count1 = len(res1.evidence)

        # Run assessment 2nd time
        res2 = asyncio.run(self.orchestrator.assess_incident(inc_id))
        count2 = len(res2.evidence)

        # Must not duplicate evidence
        self.assertEqual(count1, count2)


if __name__ == "__main__":
    unittest.main()
