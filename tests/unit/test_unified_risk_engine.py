"""Unit Tests for Unified ScamGraph Risk Engine (Module D).

Tests multi-signal orchestration, correlation-aware fusion, degraded component handling,
and action recommendation assignment.
"""

import pytest
from datetime import datetime, timezone, timedelta

from packages.schemas.graph_correlation import CorrelationEdgeType, CorrelationNodeType, GraphEdge, GraphNode
from packages.schemas.mule import TransactionDirection, TransactionRecord
from packages.schemas.registry import CreateReportRequest, IdentifierType, TypedIdentifier
from packages.schemas.unified_risk import (
    UnifiedAction,
    UnifiedRiskBand,
    UnifiedRiskRequest,
)
from services.graph_engine.algorithms.risk_propagation import GraphRiskPropagator
from services.graph_engine.correlation.transaction_graph import TransactionGraphEngine
from services.mule_engine.service import MuleIntelligenceService
from services.registry.repository import RegistryRepository
from services.registry.service import SmartRegistryService
from services.risk_engine.unified_engine import UnifiedScamGraphRiskEngine


@pytest.mark.asyncio
class TestUnifiedRiskEngine:
    """Tests the unified multi-signal orchestration engine."""

    async def test_high_risk_multi_signal_synthesis_escalates(self):
        registry_repo = RegistryRepository()
        registry_service = SmartRegistryService(repo=registry_repo)
        mule_service = MuleIntelligenceService()
        graph_engine = TransactionGraphEngine()
        risk_propagator = GraphRiskPropagator(engine=graph_engine)

        engine = UnifiedScamGraphRiskEngine(
            registry_service=registry_service,
            mule_service=mule_service,
            graph_engine=graph_engine,
            risk_propagator=risk_propagator,
        )

        # 1. Ingest confirmed report into Smart Registry
        await registry_service.ingest_report(
            CreateReportRequest(
                reporting_org="BANK_HDFC_01",
                category="ELECTRICITY_IMPERSONATION",
                reason="Confirmed extortion and fraudulent bill collection",
                identifiers=[
                    TypedIdentifier(identifier_type=IdentifierType.UPI_VPA, raw_value="power.collect@oksbi"),
                    TypedIdentifier(identifier_type=IdentifierType.PHONE, raw_value="+919876543210"),
                ],
                confidence=0.95,
            )
        )

        # 2. Add graph node for the phone number
        graph_engine.add_node(GraphNode(
            id="+919876543210",
            node_type=CorrelationNodeType.PHONE,
            label="Suspicious Phone",
            direct_risk=0.90,
            risk_score=0.90,
        ))

        # 3. Create rapid pass-through mule transactions
        t0 = datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id="TX_1",
                timestamp=t0,
                amount=50000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_01",
            ),
            TransactionRecord(
                txn_id="TX_2",
                timestamp=t0 + timedelta(minutes=2),
                amount=49800.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="LAYER_MULE",
                balance_after=200.0,
            ),
        ]

        req = UnifiedRiskRequest(
            message_text="URGENT: Your electricity connection will be DISCONNECTED TODAY at 9:30 PM! Pay now via UPI.",
            vpa="power.collect@oksbi",
            phone="+919876543210",
            url="https://pay-bill-urgent.tk/update",
            transactions=txns,
            account_age_days=10,
            historical_avg_daily_volume=200.0,
        )

        res = await engine.assess(req)

        assert res.overall_risk_score >= 0.85
        assert res.risk_band in (UnifiedRiskBand.HIGH, UnifiedRiskBand.CRITICAL)
        assert res.recommended_action == UnifiedAction.ESCALATE
        assert "REGISTRY_CONFIRMED_ELECTRICITY_IMPERSONATION" in res.reason_codes
        assert "contributing_signals" in res.model_dump()
        assert "registry" in res.contributing_signals
        assert "mule_intelligence" in res.contributing_signals

    async def test_degraded_mode_when_transactions_missing(self):
        engine = UnifiedScamGraphRiskEngine()

        # Query with only message and phone, no transactions
        req = UnifiedRiskRequest(
            message_text="Dear Customer, your electricity bill is due. Please pay.",
            phone="+919123456789",
        )

        res = await engine.assess(req)
        assert res.is_degraded is True
        assert "MULE_INTELLIGENCE_NO_TRANSACTIONS" in res.degraded_components
        assert res.uncertainty_and_data_quality["is_degraded"] is True

    async def test_benign_clean_entity_allows(self):
        engine = UnifiedScamGraphRiskEngine()

        req = UnifiedRiskRequest(
            message_text="Salary of Rs 75,000 credited to your account ending 1234 on 22-Oct-2026.",
            vpa="employer.payroll@icici",
        )

        res = await engine.assess(req)
        assert res.overall_risk_score < 0.30
        assert res.risk_band == UnifiedRiskBand.LOW
        assert res.recommended_action == UnifiedAction.ALLOW
