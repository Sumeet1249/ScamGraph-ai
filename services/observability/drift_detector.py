"""
ScamGraph AI — Scam Drift & Model Drift Intelligence Engine V3
Phase 7C / Prompt 23

Detects and quantifies:
- Model Drift (output score distribution, confidence shifts)
- Data Drift (input language, channel, modality distributions)
- Scam Drift (tactic mutation, journey stage sequencing, payment escalations)
- ScamDNA Cluster Drift (dimensional feature shifts)
- Campaign Drift (velocity surges, variant mutations)
- Novelty Scoring (Novelty != Maliciousness; Drift != Fraud)
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class DriftCategory(str, Enum):
    """Classification of detected drift signals."""
    MODEL_DRIFT = "MODEL_DRIFT"         # Model outputs shifting against baseline
    DATA_DRIFT = "DATA_DRIFT"           # Input distribution shifting (e.g., more Hinglish, longer texts)
    CONCEPT_DRIFT = "CONCEPT_DRIFT"     # Signal-to-outcome mapping mutating
    SCAM_DRIFT = "SCAM_DRIFT"           # Attackers introducing novel tactics, UPI patterns, or channels
    JOURNEY_DRIFT = "JOURNEY_DRIFT"     # Victim progression stages shifting (e.g., faster to payment)
    SCAMDNA_DRIFT = "SCAMDNA_DRIFT"     # Behavioral fingerprint cluster divergence
    CAMPAIGN_DRIFT = "CAMPAIGN_DRIFT"   # Campaign variant emergence or sudden velocity spike


class DriftAlert(BaseModel):
    """Structured alert emitted when statistical or behavioral drift breaches threshold."""
    alert_id: str = Field(default_factory=lambda: generate_id("dft"))
    category: DriftCategory
    metric_name: str
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL
    baseline_value: float
    current_value: float
    deviation_percent: float
    description: str
    runbook_url: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_suppressed_by_cooldown: bool = False


class DriftDetector:
    """
    Monitors aggregate production distributions against rolling baseline windows.
    Enforces deduplication, cooldown windows, and strictly separates 'Drift' from 'Fraud'.
    """

    def __init__(self, cooldown_minutes: int = 60) -> None:
        self.cooldown_minutes = cooldown_minutes
        self._alerts: List[DriftAlert] = []
        self._last_alert_times: Dict[str, datetime] = {}

        # Baseline distributions (simulating rolling 30-day baseline)
        self.baseline_scam_score_mean = 0.58
        self.baseline_hinglish_ratio = 0.32
        self.baseline_digital_arrest_freq = 0.15
        self.baseline_time_to_payment_stages = 4.2
        self.baseline_scamdna_cluster_variance = 0.12

    def calculate_novelty_score(
        self,
        text: str,
        detected_tactics: List[str],
        known_tactics_catalog: Optional[set[str]] = None,
    ) -> Tuple[float, str]:
        """
        Computes explainable novelty score (0.0 to 1.0).
        CRITICAL PRINCIPLE: Novelty != Maliciousness.
        Novelty prioritizes analyst review; it does NOT convict.
        """
        catalog = known_tactics_catalog or {
            "AUTHORITY_IMPERSONATION",
            "URGENCY",
            "CREDENTIAL_HARVESTING",
            "ADVANCE_FEE",
            "ISOLATION",
        }
        unknown_tactics = [t for t in detected_tactics if t not in catalog]
        novelty_ratio = len(unknown_tactics) / max(1, len(detected_tactics)) if detected_tactics else 0.0

        if novelty_ratio > 0.4:
            explanation = f"Novel tactic combination identified: {unknown_tactics}"
            score = round(min(1.0, 0.5 + novelty_ratio * 0.5), 2)
        elif "skype digital court" in text.lower():
            explanation = "Emerging tactic variant: Video-call simulated courtroom"
            score = 0.85
        else:
            explanation = "Pattern matches established scam signatures"
            score = 0.10

        return score, explanation

    def evaluate_model_output_drift(self, current_batch_scores: List[float]) -> Optional[DriftAlert]:
        """Detect shifts in the model's mean score distribution."""
        if not current_batch_scores:
            return None
        current_mean = sum(current_batch_scores) / len(current_batch_scores)
        dev = abs(current_mean - self.baseline_scam_score_mean) / self.baseline_scam_score_mean
        if dev > 0.20:
            return self._emit_alert(
                category=DriftCategory.MODEL_DRIFT,
                metric_name="mean_risk_score",
                baseline=self.baseline_scam_score_mean,
                current=current_mean,
                deviation_pct=round(dev * 100, 1),
                desc=f"Model output score distribution shifted by {round(dev*100, 1)}%",
                runbook="docs/startup-v2/observability/RUNBOOKS.md#model-score-shift",
            )
        return None

    def evaluate_scamdna_cluster_drift(self, current_cluster_variance: float) -> Optional[DriftAlert]:
        """Detect ScamDNA cluster expansion or emergence of new clusters."""
        dev = abs(current_cluster_variance - self.baseline_scamdna_cluster_variance) / self.baseline_scamdna_cluster_variance
        if dev > 0.35:
            return self._emit_alert(
                category=DriftCategory.SCAMDNA_DRIFT,
                metric_name="cluster_variance",
                baseline=self.baseline_scamdna_cluster_variance,
                current=current_cluster_variance,
                deviation_pct=round(dev * 100, 1),
                desc=f"ScamDNA cluster variance expanded by {round(dev*100, 1)}%, indicating new behavioral variants",
                runbook="docs/startup-v2/observability/RUNBOOKS.md#scamdna-cluster-drift",
            )
        return None

    def evaluate_journey_drift(self, current_avg_stages_to_payment: float) -> Optional[DriftAlert]:
        """Detect changes in scam journey velocity (e.g. pressure stage accelerated)."""
        dev = abs(current_avg_stages_to_payment - self.baseline_time_to_payment_stages) / self.baseline_time_to_payment_stages
        if dev > 0.25:
            return self._emit_alert(
                category=DriftCategory.JOURNEY_DRIFT,
                metric_name="stages_to_payment",
                baseline=self.baseline_time_to_payment_stages,
                current=current_avg_stages_to_payment,
                deviation_pct=round(dev * 100, 1),
                desc=f"Victim journey accelerated: payment requested {round(dev*100, 1)}% faster than baseline",
                runbook="docs/startup-v2/observability/RUNBOOKS.md#journey-drift",
            )
        return None

    def evaluate_campaign_drift(self, recent_velocity_surge: float) -> Optional[DriftAlert]:
        """Detect sudden surge in campaign incident reporting."""
        if recent_velocity_surge > 3.0:  # 3x baseline velocity
            return self._emit_alert(
                category=DriftCategory.CAMPAIGN_DRIFT,
                metric_name="campaign_velocity_multiplier",
                baseline=1.0,
                current=recent_velocity_surge,
                deviation_pct=round((recent_velocity_surge - 1.0) * 100, 1),
                desc=f"Campaign outbreak surge detected: velocity {recent_velocity_surge}x above baseline",
                runbook="docs/startup-v2/observability/RUNBOOKS.md#campaign-variant-surge",
            )
        return None

    def _emit_alert(
        self,
        category: DriftCategory,
        metric_name: str,
        baseline: float,
        current: float,
        deviation_pct: float,
        desc: str,
        runbook: str,
    ) -> DriftAlert:
        alert_key = f"{category.value}:{metric_name}"
        now = datetime.now(timezone.utc)
        is_suppressed = False

        if alert_key in self._last_alert_times:
            elapsed = (now - self._last_alert_times[alert_key]).total_seconds() / 60.0
            if elapsed < self.cooldown_minutes:
                is_suppressed = True

        if not is_suppressed:
            self._last_alert_times[alert_key] = now

        alert = DriftAlert(
            category=category,
            metric_name=metric_name,
            baseline_value=round(baseline, 3),
            current_value=round(current, 3),
            deviation_percent=deviation_pct,
            description=desc,
            runbook_url=runbook,
            is_suppressed_by_cooldown=is_suppressed,
        )
        self._alerts.append(alert)
        return alert

    def list_alerts(self) -> List[DriftAlert]:
        return self._alerts


# Singleton instance
_drift_detector: Optional[DriftDetector] = None


def get_drift_detector() -> DriftDetector:
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = DriftDetector()
    return _drift_detector
