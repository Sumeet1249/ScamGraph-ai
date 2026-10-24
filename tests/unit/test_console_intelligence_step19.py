"""Unit tests for ScamGraph Intelligence Console V2 (Prompt 19 / Phase 6A)."""

import pytest
from datetime import datetime, timezone

from packages.schemas.console import (
    AlertStatus,
    AlertType,
    CaseStatus,
    ReviewDecisionType,
    ReviewType,
)
from services.console.service import (
    ConsoleIntelligenceService,
    console_intelligence_service,
)
from services.campaign_engine.service import campaign_service


def test_command_center_summary_telemetry():
    """Verifies Command Center aggregate numbers and time window integrity."""
    summary = console_intelligence_service.get_command_center_summary(time_window="24h")
    assert summary.time_window == "24h"
    assert summary.active_alerts_count >= 1
    assert summary.surging_campaigns_count >= 1
    assert summary.pending_reviews_count >= 1
    assert summary.open_cases_count >= 1
    assert summary.health.knowledge_graph == "HEALTHY"
    assert len(summary.recent_network_activity) >= 1


def test_operational_alerts_filtering_and_lifecycle():
    """Tests alert filtering by state and severity, and state transitions."""
    service = ConsoleIntelligenceService()
    all_alerts = service.get_alerts()
    assert len(all_alerts) >= 3

    critical_alerts = service.get_alerts(severity_filter="CRITICAL")
    assert len(critical_alerts) >= 1
    assert all(a.severity == "CRITICAL" for a in critical_alerts)

    # State Transition: NEW -> ACKNOWLEDGED -> INVESTIGATING
    target_alert = critical_alerts[0]
    updated = service.update_alert_status(target_alert.alert_id, AlertStatus.ACKNOWLEDGED)
    assert updated is not None
    assert updated.status == AlertStatus.ACKNOWLEDGED

    updated2 = service.update_alert_status(target_alert.alert_id, AlertStatus.INVESTIGATING)
    assert updated2 is not None
    assert updated2.status == AlertStatus.INVESTIGATING


def test_review_queue_prioritization_and_decision():
    """Verifies that review items are sorted by priority and decisions persist."""
    service = ConsoleIntelligenceService()
    queue = service.get_review_queue()
    assert len(queue) >= 2
    # Check descending priority order
    for i in range(len(queue) - 1):
        assert queue[i].priority_score >= queue[i + 1].priority_score

    # Adjudicate review item
    top_item = queue[0]
    reviewed = service.submit_review_decision(
        review_id=top_item.review_id,
        decision=ReviewDecisionType.CONFIRM,
        reviewer_notes="Confirmed shared infrastructure and 0.94 DNA similarity across 18 incidents.",
        reviewer_id="lead_fraud_analyst_01",
    )
    assert reviewed is not None
    assert reviewed.status == "REVIEWED"
    assert reviewed.decision == ReviewDecisionType.CONFIRM
    assert reviewed.reviewer_id == "lead_fraud_analyst_01"
    assert reviewed.decided_at is not None


def test_review_false_correlation_rejection():
    """Verifies an analyst can reject a candidate correlation without corrupting truth."""
    service = ConsoleIntelligenceService()
    queue = service.get_review_queue()
    split_item = [r for r in queue if r.review_type == ReviewType.ENTITY_SPLIT][0]

    reviewed = service.submit_review_decision(
        review_id=split_item.review_id,
        decision=ReviewDecisionType.REJECT,
        reviewer_notes="SBI helpline 1800112211 is a benign supernode; do not merge scam incidents onto it.",
        reviewer_id="senior_investigator",
    )
    assert reviewed.status == "REVIEWED"
    assert reviewed.decision == ReviewDecisionType.REJECT


def test_investigation_cases_crud():
    """Tests case creation, retrieval, and append-only analyst notes."""
    service = ConsoleIntelligenceService()
    new_case = service.create_case(
        title="Operation TaskBuster: Southern Circle Task Scams",
        priority="HIGH",
        assigned_analyst="Analyst Vikram",
        linked_incident_ids=["inc_01", "inc_02"],
        linked_campaign_ids=["cmp_task_scam_telegram"],
        linked_entities=["task.earn@oksbi"],
        initial_note="Initial case opened following Outbreak Alert in Bengaluru.",
        tags=["TASK_SCAM", "SOUTH_ZONE"],
    )

    assert new_case.case_id.startswith("case_")
    assert new_case.status == CaseStatus.OPEN
    assert len(new_case.notes) == 1
    assert new_case.notes[0]["author"] == "Analyst Vikram"

    # Add note
    updated = service.add_case_note(
        case_id=new_case.case_id,
        text="Subpoena request sent to bank for VPA transaction history.",
        author="Analyst Vikram",
    )
    assert len(updated.notes) == 2
    assert "Subpoena request" in updated.notes[1]["text"]


def test_radar_data_backend_integrity():
    """Proves that Radar telemetry originates from actual Campaign Discovery & Outbreak Radar services."""
    if not campaign_service._campaigns:
        campaign_service.seed_demo_data()

    blips = campaign_service.get_radar_blips(demo_mode=True)
    assert len(blips) >= 1
    first_blip = blips[0]
    assert first_blip.campaign_id is not None
    assert first_blip.ring in ("CRITICAL", "SURGING", "EMERGING", "WATCH")
    assert first_blip.growth_percent >= 0.0

    summary = campaign_service.get_radar_summary(demo_mode=True)
    assert summary.active_campaigns >= 1
    assert summary.surging_count >= 0


def test_degraded_mode_health():
    """Ensures health model reports subsystem degradation gracefully."""
    summary = console_intelligence_service.get_command_center_summary()
    assert summary.health.knowledge_graph in ("HEALTHY", "DEGRADED", "OFFLINE")
    assert isinstance(summary.health.degraded_components, list)
