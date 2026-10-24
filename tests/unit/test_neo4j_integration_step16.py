"""Unit & integration tests for Step 16: Neo4j integration and Entity Correlation."""

import unittest
import asyncio
from services.graph_engine.neo4j.repository import GraphRepository
from services.graph_engine.correlation.entity_service import EntityCorrelationService
from packages.schemas import SignalDimension, SignalSeverity


class TestNeo4jIntegrationStep16(unittest.TestCase):
    def setUp(self):
        self.repo = GraphRepository()
        self.service = EntityCorrelationService(repo=self.repo)

    async def _setup_and_test_correlation(self):
        # Incident 1 (Victim 1)
        await self.repo.create_incident("inc_v1", channel="SMS")
        await self.repo.create_event("ev_v1_1", "inc_v1", "MESSAGE_RECEIVED", 1)
        await self.repo.create_event("ev_v1_2", "inc_v1", "COLLECT_REQUEST_RECEIVED", 2)
        await self.repo.connect_events_temporally("ev_v1_1", "ev_v1_2", 45)

        # Upsert entities for Incident 1
        await self.repo.upsert_entity("Phone", "+919876543210")
        await self.repo.connect_entity("ev_v1_1", "Phone", "+919876543210", "ORIGINATED_FROM")

        await self.repo.upsert_entity("PaymentEntity", "fraudster@oksbi")
        await self.repo.connect_entity("ev_v1_2", "PaymentEntity", "fraudster@oksbi", "TARGETS")

        # Incident 2 (Victim 2, targeted by the same phone and payment entity)
        await self.repo.create_incident("inc_v2", channel="WhatsApp")
        await self.repo.create_event("ev_v2_1", "inc_v2", "MESSAGE_RECEIVED", 1)
        await self.repo.create_event("ev_v2_2", "inc_v2", "COLLECT_REQUEST_RECEIVED", 2)

        await self.repo.connect_entity("ev_v2_1", "Phone", "+919876543210", "ORIGINATED_FROM")
        await self.repo.connect_entity("ev_v2_2", "PaymentEntity", "fraudster@oksbi", "TARGETS")

        # Run correlation on Incident 2
        report = await self.service.correlate_incident("inc_v2")

        # Assert explainable features
        self.assertEqual(report.shared_phone_count, 1)
        self.assertEqual(report.shared_payment_entity_count, 1)
        self.assertEqual(report.total_shared_entities, 2)

        # Assert explanation paths
        self.assertGreaterEqual(len(report.explanation_paths), 2)
        has_phone_path = any("+919876543210" in p and "inc_v1" in p for p in report.explanation_paths)
        has_payment_path = any("fraudster@oksbi" in p and "inc_v1" in p for p in report.explanation_paths)
        self.assertTrue(has_phone_path)
        self.assertTrue(has_payment_path)

        # Assert canonical EvidenceSignals produced
        self.assertEqual(len(report.signals), 2)
        types = [s.signal_type for s in report.signals]
        self.assertIn("SHARED_PHONE_NUMBER_ACROSS_INCIDENTS", types)
        self.assertIn("SHARED_PAYMENT_ENTITY_ACROSS_INCIDENTS", types)

        pay_sig = next(s for s in report.signals if s.signal_type == "SHARED_PAYMENT_ENTITY_ACROSS_INCIDENTS")
        self.assertEqual(pay_sig.severity, SignalSeverity.CRITICAL)

    def test_entity_correlation_lifecycle(self):
        asyncio.run(self._setup_and_test_correlation())


if __name__ == "__main__":
    unittest.main()
