"""Benchmark tests for ScamGraph AI.

Measures:
1. Event ingestion throughput
2. Pattern matching latency
3. Graph traversal and entity correlation response times
"""

import asyncio
import time
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from packages.schemas import (
    Event,
    EventType,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
)
from services.pattern_engine.patterns.scam_patterns import PatternMatcher
from services.graph_engine.neo4j.repository import GraphRepository
from services.graph_engine.correlation.entity_service import EntityCorrelationService


class TestScamGraphBenchmarks(unittest.TestCase):
    def test_event_ingestion_throughput(self):
        """Measures synthetic event batch creation and parsing throughput."""
        count = 1000
        start = time.perf_counter()
        events = []
        for i in range(count):
            ev = Event(
                event_id=str(uuid4()),
                incident_id="inc_bench_001",
                sequence_number=i + 1,
                event_type=EventType.MESSAGE_RECEIVED,
                timestamp=datetime.now(timezone.utc),
                payload={"text": f"Urgent account suspension message #{i}"},
            )
            events.append(ev)
        duration = time.perf_counter() - start

        self.assertEqual(len(events), count)
        throughput = count / duration
        # Throughput should exceed 1,000 events/sec
        self.assertGreater(throughput, 1000.0)

    def test_pattern_matching_latency(self):
        """Measures PatternMatcher latency across synthetic multi-signal batches."""
        signals = [
            EvidenceSignal(
                incident_id="inc_bench",
                dimension=SignalDimension.SEMANTIC,
                signal_type="OFFICIAL_ENTITY_IMPERSONATION",
                severity=SignalSeverity.HIGH,
                confidence=0.92,
                description="Official bank impersonation",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="Extractor", target_artifact="msg"),
            ),
            EvidenceSignal(
                incident_id="inc_bench",
                dimension=SignalDimension.SEMANTIC,
                signal_type="URGENCY_PRESSURE_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.88,
                description="Urgent account threat",
                provenance=ProvenanceRecord(source_service="NLP", detector_name="Extractor", target_artifact="msg"),
            ),
            EvidenceSignal(
                incident_id="inc_bench",
                dimension=SignalDimension.URL,
                signal_type="BRAND_TYPOSQUATTING_DETECTED",
                severity=SignalSeverity.HIGH,
                confidence=0.95,
                description="Deceptive domain",
                provenance=ProvenanceRecord(source_service="URL", detector_name="Typosquat", target_artifact="url"),
            ),
            EvidenceSignal(
                incident_id="inc_bench",
                dimension=SignalDimension.PAYMENT,
                signal_type="INDIVIDUAL_VPA_PAYMENT_TARGETED",
                severity=SignalSeverity.MEDIUM,
                confidence=0.85,
                description="Personal VPA targeted",
                provenance=ProvenanceRecord(source_service="PAY", detector_name="Validator", target_artifact="vpa"),
            ),
        ]

        iterations = 500
        start = time.perf_counter()
        for _ in range(iterations):
            match = PatternMatcher.match(signals)
            self.assertIsNotNone(match)
        total_time = time.perf_counter() - start

        avg_latency_ms = (total_time / iterations) * 1000
        # Latency should be sub-millisecond (< 2.0 ms)
        self.assertLess(avg_latency_ms, 2.0)

    def test_graph_entity_correlation_latency(self):
        """Measures entity correlation query response times."""
        async def _run():
            repo = GraphRepository()
            for i in range(10):
                await repo.upsert_entity(f"phone_{i % 3}", "Phone", "+919111111111")
                await repo.connect_entity(f"inc_bench_{i}", f"phone_{i % 3}", "USED_PHONE")

            service = EntityCorrelationService(repo=repo)
            iterations = 50
            start = time.perf_counter()
            for _ in range(iterations):
                report = await service.correlate_incident("inc_bench_0")
                self.assertIsNotNone(report)
            total_time = time.perf_counter() - start

            avg_latency_ms = (total_time / iterations) * 1000
            # Average in-memory graph correlation latency should be well under 10 ms
            self.assertLess(avg_latency_ms, 10.0)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
