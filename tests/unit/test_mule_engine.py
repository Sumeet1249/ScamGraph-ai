"""Unit Tests for Mule Intelligence Engine (Module B).

Tests transaction validation, 19 behavioral feature extraction, baseline rules engine,
supervised model training & metrics, and risk band mapping.
"""

import pytest
from datetime import datetime, timezone, timedelta
import numpy as np

from packages.schemas.mule import (
    MuleAction,
    MuleEvaluationRequest,
    MuleRiskBand,
    TransactionChannel,
    TransactionDirection,
    TransactionRecord,
)
from services.mule_engine.feature_extractor import MuleFeatureExtractor
from services.mule_engine.model import MuleMLClassifier, vector_to_features
from services.mule_engine.rules_engine import MuleRulesEngine
from services.mule_engine.service import MuleIntelligenceService


class TestTransactionValidation:
    """Tests transaction record validation."""

    def test_positive_amount_required(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError):
            TransactionRecord(
                txn_id="TXN_BAD",
                timestamp=now,
                amount=-100.0,
                direction=TransactionDirection.CREDIT,
            )

    def test_valid_transaction(self):
        now = datetime.now(timezone.utc)
        txn = TransactionRecord(
            txn_id="TXN_001",
            timestamp=now,
            amount=5000.0,
            currency="INR",
            direction=TransactionDirection.CREDIT,
            counterparty_account="ACC_SRC_01",
            channel=TransactionChannel.UPI,
        )
        assert txn.amount == 5000.0
        assert txn.channel == TransactionChannel.UPI


class TestMuleFeatureExtractor:
    """Tests extraction of 19 behavioral patterns."""

    def test_extract_rapid_pass_through_and_churn(self):
        t0 = datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id="TXN_IN_1",
                timestamp=t0,
                amount=50000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_01",
            ),
            TransactionRecord(
                txn_id="TXN_OUT_1",
                timestamp=t0 + timedelta(seconds=120),  # Drained in 2 minutes
                amount=49900.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="LAYER_01",
                balance_after=100.0,
            ),
        ]

        features = MuleFeatureExtractor.extract_features(
            account_id="ACC_MULE_01",
            transactions=txns,
            account_age_days=10,
            historical_avg_daily_volume=200.0,
        )

        assert features.f01_velocity_1h_count == 2
        assert features.f04_dwell_time_seconds_avg == 120.0
        assert features.f05_rapid_churn_ratio == 1.0
        assert features.f03_volume_turnover_ratio == pytest.approx(0.998, 0.01)
        assert features.f14_balance_extraction_ratio == 1.0

    def test_fan_in_and_fan_out_counts(self):
        t0 = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id=f"IN_{i}",
                timestamp=t0 + timedelta(minutes=i * 5),
                amount=10000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account=f"SENDER_{i}",
            )
            for i in range(4)
        ] + [
            TransactionRecord(
                txn_id="OUT_1",
                timestamp=t0 + timedelta(minutes=30),
                amount=39000.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="CASHOUT_01",
            )
        ]

        features = MuleFeatureExtractor.extract_features(
            account_id="ACC_FAN_IN",
            transactions=txns,
        )

        assert features.f07_fan_in_count == 4
        assert features.f08_fan_out_count == 1
        assert features.f09_fan_in_to_out_ratio > 3.0

    def test_round_chunking_and_micro_test(self):
        t0 = datetime(2026, 10, 22, 14, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id="MICRO_TEST",
                timestamp=t0,
                amount=1.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="SENDER_TEST",
            ),
            TransactionRecord(
                txn_id="SPIKE_IN",
                timestamp=t0 + timedelta(minutes=15),
                amount=49999.0,  # Structuring amount
                direction=TransactionDirection.CREDIT,
                counterparty_account="SENDER_TEST",
            ),
        ]

        features = MuleFeatureExtractor.extract_features(
            account_id="ACC_STRUCT",
            transactions=txns,
        )

        assert features.f15_micro_test_followed_by_spike is True
        assert features.f13_round_chunking_detected is True


class TestMuleRulesEngine:
    """Tests deterministic baseline heuristic rules."""

    def test_high_risk_mule_triggers_critical_rules(self):
        t0 = datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id="IN_1",
                timestamp=t0,
                amount=95000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_A",
            ),
            TransactionRecord(
                txn_id="IN_2",
                timestamp=t0 + timedelta(minutes=5),
                amount=95000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_B",
            ),
            TransactionRecord(
                txn_id="IN_3",
                timestamp=t0 + timedelta(minutes=10),
                amount=95000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_C",
            ),
            TransactionRecord(
                txn_id="OUT_1",
                timestamp=t0 + timedelta(minutes=12),
                amount=284000.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="LAYER_X",
                balance_after=50.0,
            ),
        ]

        features = MuleFeatureExtractor.extract_features(
            account_id="ACC_CRITICAL",
            transactions=txns,
            account_age_days=5,
            historical_avg_daily_volume=100.0,
        )

        score, hits = MuleRulesEngine.evaluate(features)
        assert score >= 0.70
        rule_ids = [h.rule_id for h in hits]
        assert "RULE_FULL_VOLUME_TURNOVER" in rule_ids
        assert "RULE_RAPID_PASS_THROUGH" in rule_ids
        assert "RULE_FAN_IN_CONVERGENCE" in rule_ids


class TestMuleMLClassifierPipeline:
    """Tests ML training and evaluation on synthetic time-aware distributions."""

    def test_training_and_metrics_calculation(self):
        # Generate synthetic feature vectors (50 benign, 50 mules)
        np.random.seed(42)
        X_benign = np.random.normal(loc=1.0, scale=0.5, size=(50, 19))
        X_mule = np.random.normal(loc=5.0, scale=1.0, size=(50, 19))

        X = np.vstack([X_benign, X_mule])
        y = np.array([0] * 50 + [1] * 50)

        # Time-aware split: first 70 for train, last 30 for test
        indices = np.arange(100)
        np.random.shuffle(indices)
        train_idx, test_idx = indices[:70], indices[70:]

        report = MuleMLClassifier.train_and_evaluate(
            X_train=X[train_idx],
            y_train=y[train_idx],
            X_test=X[test_idx],
            y_test=y[test_idx],
            save_artifact=True,
        )

        assert "metrics" in report
        assert "precision" in report["metrics"]
        assert "recall" in report["metrics"]
        assert "f1_score" in report["metrics"]
        assert "pr_auc" in report["metrics"]
        assert report["metrics"]["precision"] >= 0.70
        assert report["metrics"]["recall"] >= 0.70


@pytest.mark.asyncio
class TestMuleIntelligenceService:
    """Tests end-to-end account evaluation and disposition."""

    async def test_evaluate_mule_account_returns_freeze_suspend(self):
        service = MuleIntelligenceService()
        t0 = datetime(2026, 10, 22, 9, 0, 0, tzinfo=timezone.utc)
        txns = [
            TransactionRecord(
                txn_id="TXN_M1",
                timestamp=t0,
                amount=50000.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_01",
            ),
            TransactionRecord(
                txn_id="TXN_M2",
                timestamp=t0 + timedelta(minutes=2),
                amount=25000.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="MULE_HOP_1",
            ),
            TransactionRecord(
                txn_id="TXN_M3",
                timestamp=t0 + timedelta(minutes=3),
                amount=24900.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="MULE_HOP_2",
                balance_after=50.0,
            ),
            TransactionRecord(
                txn_id="TXN_M4",
                timestamp=t0 + timedelta(minutes=10),
                amount=49999.0,
                direction=TransactionDirection.CREDIT,
                counterparty_account="VICTIM_02",
            ),
            TransactionRecord(
                txn_id="TXN_M5",
                timestamp=t0 + timedelta(minutes=12),
                amount=49900.0,
                direction=TransactionDirection.DEBIT,
                counterparty_account="CASHOUT_CRYPTO",
            ),
        ]

        req = MuleEvaluationRequest(
            account_id="ACC_MULE_HIGH",
            transactions=txns,
            account_age_days=8,
            historical_avg_daily_volume=500.0,
            has_registry_match=True,
        )

        res = await service.evaluate_account(req)
        assert res.risk_band in (MuleRiskBand.HIGH, MuleRiskBand.CRITICAL)
        assert res.recommended_action in (MuleAction.STEP_UP_KYC, MuleAction.FREEZE_SUSPEND)
        assert len(res.top_contributing_rules) > 0
        assert res.extracted_features.f01_velocity_1h_count == 5
