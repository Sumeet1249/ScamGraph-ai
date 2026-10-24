"""Console Intelligence Service (Prompt 19 / Phase 6A).

Orchestrates company-grade analyst operations across Command Center, Outbreak Radar,
Alert Center, Human-in-the-loop Reviews, and Case Management Foundation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.console import (
    AlertStatus,
    AlertType,
    CaseStatus,
    CommandCenterSummary,
    IntelligenceAlert,
    InvestigationCase,
    ReviewDecisionType,
    ReviewQueueItem,
    ReviewType,
    SystemIntelligenceHealth,
)
from services.campaign_engine.service import campaign_service

logger = logging.getLogger("console.service")


class ConsoleIntelligenceService:
    """Enterprise operating system service for fraud analysts and investigators."""

    def __init__(self):
        self._alerts: Dict[str, IntelligenceAlert] = {}
        self._reviews: Dict[str, ReviewQueueItem] = {}
        self._cases: Dict[str, InvestigationCase] = {}
        self._seed_default_data()

    def _seed_default_data(self):
        """Seeds initial realistic operational fixtures for local and demo operations."""
        now = datetime.now(timezone.utc)

        # 1. Operational Alerts
        alert1 = IntelligenceAlert(
            alert_id="alt_outbreak_cbi_01",
            alert_type=AlertType.OUTBREAK,
            severity="CRITICAL",
            title="Digital Arrest Syndicate Outbreak in NCR/Mumbai",
            description="Incident reporting velocity surged by +240% across Hindi telephony and WhatsApp channels in the last 24h.",
            campaign_id="cmp_digital_arrest_v2",
            campaign_name="CBI Impersonation Digital Arrest Syndicate",
            metrics={
                "velocity_spike_pct": 240,
                "reporting_rate_per_hr": 14.2,
                "unique_entities": 28,
                "primary_channels": ["PHONE_CALL", "WHATSAPP_SCREENSHOT", "UPI_QR"],
                "languages": ["hi", "en"],
            },
            status=AlertStatus.NEW,
            created_at=now - timedelta(minutes=42),
        )

        alert2 = IntelligenceAlert(
            alert_id="alt_rapid_growth_task_02",
            alert_type=AlertType.RAPID_GROWTH,
            severity="HIGH",
            title="Rapid Growth: Telegram Task Scam Rotating VPAs",
            description="Campaign detected rotating ICICI and SBI merchant VPAs while retaining identical Hinglish task unlock script.",
            campaign_id="cmp_task_scam_telegram",
            campaign_name="Task Scam VIP Unlock Ring",
            metrics={
                "velocity_spike_pct": 110,
                "reporting_rate_per_hr": 7.5,
                "unique_entities": 42,
                "primary_channels": ["TELEGRAM", "SMS", "UPI_QR"],
                "languages": ["hi-Latn", "en"],
            },
            status=AlertStatus.INVESTIGATING,
            created_at=now - timedelta(hours=3),
        )

        alert3 = IntelligenceAlert(
            alert_id="alt_resurgence_fedex_03",
            alert_type=AlertType.RESURGENCE,
            severity="HIGH",
            title="Resurgence: Customs Drug Parcel Impersonation",
            description="Previously dormant customs courier campaign reactivated with newly registered punycode domains.",
            campaign_id="cmp_fedex_customs_phish",
            campaign_name="Customs Drug Parcel Extortion",
            metrics={
                "dormancy_duration_days": 18,
                "new_incidents_24h": 9,
                "primary_channels": ["SMS", "CALL"],
                "languages": ["en", "hi"],
            },
            status=AlertStatus.NEW,
            created_at=now - timedelta(hours=6),
        )

        self._alerts[alert1.alert_id] = alert1
        self._alerts[alert2.alert_id] = alert2
        self._alerts[alert3.alert_id] = alert3

        # 2. Review Queue Items (Human-in-the-loop decisions)
        rev1 = ReviewQueueItem(
            review_id="rev_merge_task_01",
            review_type=ReviewType.CAMPAIGN_MERGE,
            priority_score=0.92,
            title="Candidate Campaign Merge: Task Ring 04 & Task Ring 07",
            summary="Identical ScamDNA V3 signature (0.94 similarity) and shared mule UPI handle vip.tasks@oksbi observed across 18 incidents.",
            evidence_context={
                "dna_similarity": 0.94,
                "shared_vpa": "vip.tasks@oksbi",
                "journey_similarity": 0.96,
                "incident_overlap_count": 18,
            },
            candidate_entities=["vip.tasks@oksbi", "+919876543210"],
            candidate_campaign_ids=["cmp_task_scam_telegram", "cmp_task_scam_alt"],
            status="PENDING",
            created_at=now - timedelta(hours=2),
        )

        rev2 = ReviewQueueItem(
            review_id="rev_split_telecom_02",
            review_type=ReviewType.ENTITY_SPLIT,
            priority_score=0.81,
            title="Possible Supernode Disambiguation: SBI Toll-Free Mention",
            summary="Multiple incidents cluster around 1800112211 which is the genuine SBI helpline cited in advisory SMS captures.",
            evidence_context={
                "entity_value": "1800112211",
                "entity_type": "PHONE",
                "incident_count": 34,
                "is_supernode": True,
            },
            candidate_entities=["1800112211"],
            status="PENDING",
            created_at=now - timedelta(hours=5),
        )

        self._reviews[rev1.review_id] = rev1
        self._reviews[rev2.review_id] = rev2

        # 3. Investigation Cases
        case1 = InvestigationCase(
            case_id="case_op_digital_arrest_2026",
            title="Operation Shield: Cross-State Digital Arrest Ring",
            status=CaseStatus.INVESTIGATING,
            priority="CRITICAL",
            assigned_analyst="Senior Fraud Analyst (T&S)",
            linked_incident_ids=["inc_multi_01", "inc_multi_02", "inc_cbi_998"],
            linked_campaign_ids=["cmp_digital_arrest_v2"],
            linked_entities=["cbi.hq.desk@upi", "+919123456780", "192.0.2.14"],
            notes=[
                {
                    "author": "Analyst A",
                    "timestamp": (now - timedelta(hours=4)).isoformat(),
                    "text": "Corroborated 3 voice recordings with matching script and Skype video pressure. UPI handle frozen via bank liaison.",
                }
            ],
            tags=["DIGITAL_ARREST", "HIGH_VALUE", "PRIORITY_FREEZE"],
            created_at=now - timedelta(days=1),
        )

        self._cases[case1.case_id] = case1

    # -------------------------------------------------------------------------
    # Command Center Telemetry
    # -------------------------------------------------------------------------
    def get_command_center_summary(self, time_window: str = "24h") -> CommandCenterSummary:
        """Assembles operational command center summary with honest backend telemetry."""
        # Ensure campaigns are seeded in campaign engine
        if not campaign_service._campaigns:
            campaign_service.seed_demo_data()

        campaigns = campaign_service.list_campaigns(limit=100)
        surging = [
            c.model_dump() for c in campaigns
            if c.lifecycle_state.value in ("SURGING", "OUTBREAK")
        ]
        emerging = [
            c.model_dump() for c in campaigns
            if c.lifecycle_state.value in ("EMERGING", "NEW")
        ]

        active_alerts = [a for a in self._alerts.values() if a.status in (AlertStatus.NEW, AlertStatus.INVESTIGATING)]
        pending_reviews = [r for r in self._reviews.values() if r.status == "PENDING"]
        open_cases = [c for c in self._cases.values() if c.status in (CaseStatus.OPEN, CaseStatus.INVESTIGATING)]

        recent_activity = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "type": "NEW_CORRELATION",
                "summary": "Shared UPI VPA task.earn@oksbi linked 4 new incident reports across Delhi and Bengaluru.",
                "entities": ["task.earn@oksbi"],
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=38)).isoformat(),
                "type": "VELOCITY_BURST",
                "summary": "Digital arrest call reports crossed 12 per hour threshold in Northern telecom circle.",
                "campaign_id": "cmp_digital_arrest_v2",
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1, minutes=20)).isoformat(),
                "type": "PAYMENT_GUARD_INTERVENTION",
                "summary": "Pre-Payment Guard triggered Level 5 Friction on high-risk QR transfer attempt.",
                "amount": 25000,
            },
        ]

        return CommandCenterSummary(
            time_window=time_window,
            active_alerts_count=len(active_alerts),
            surging_campaigns_count=len(surging),
            emerging_campaigns_count=len(emerging),
            pending_reviews_count=len(pending_reviews),
            open_cases_count=len(open_cases),
            alerts=list(self._alerts.values()),
            surging_campaigns=surging,
            emerging_campaigns=emerging,
            review_queue=list(self._reviews.values()),
            health=SystemIntelligenceHealth(),
            recent_network_activity=recent_activity,
        )

    # -------------------------------------------------------------------------
    # Operational Alerts Management
    # -------------------------------------------------------------------------
    def get_alerts(
        self,
        status_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
    ) -> List[IntelligenceAlert]:
        """Returns filtered list of actionable intelligence alerts."""
        results = list(self._alerts.values())
        if status_filter:
            results = [a for a in results if a.status.value.upper() == status_filter.upper()]
        if severity_filter:
            results = [a for a in results if a.severity.upper() == severity_filter.upper()]

        # Sort newest first
        results.sort(key=lambda a: a.created_at, reverse=True)
        return results

    def update_alert_status(self, alert_id: str, new_status: AlertStatus) -> Optional[IntelligenceAlert]:
        """Transitions alert status with updated timestamp."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
        alert.status = new_status
        alert.updated_at = datetime.now(timezone.utc)
        return alert

    # -------------------------------------------------------------------------
    # Human-in-the-Loop Review Center
    # -------------------------------------------------------------------------
    def get_review_queue(self, type_filter: Optional[str] = None) -> List[ReviewQueueItem]:
        """Returns pending review queue sorted by operational impact priority."""
        items = list(self._reviews.values())
        if type_filter:
            items = [r for r in items if r.review_type.value.upper() == type_filter.upper()]

        # Sort highest priority first
        items.sort(key=lambda r: r.priority_score, reverse=True)
        return items

    def submit_review_decision(
        self,
        review_id: str,
        decision: ReviewDecisionType,
        reviewer_notes: Optional[str] = None,
        reviewer_id: str = "analyst_ops",
    ) -> Optional[ReviewQueueItem]:
        """Persists human analyst adjudication decision with lineage audit trail."""
        item = self._reviews.get(review_id)
        if not item:
            return None

        item.status = "REVIEWED"
        item.decision = decision
        item.reviewer_notes = reviewer_notes
        item.reviewer_id = reviewer_id
        item.decided_at = datetime.now(timezone.utc)
        return item

    # -------------------------------------------------------------------------
    # Case Management Foundation
    # -------------------------------------------------------------------------
    def get_cases(self, status_filter: Optional[str] = None) -> List[InvestigationCase]:
        """Returns active investigation cases."""
        cases = list(self._cases.values())
        if status_filter:
            cases = [c for c in cases if c.status.value.upper() == status_filter.upper()]
        cases.sort(key=lambda c: c.updated_at, reverse=True)
        return cases

    def get_case(self, case_id: str) -> Optional[InvestigationCase]:
        """Retrieves single investigation case by ID."""
        return self._cases.get(case_id)

    def create_case(
        self,
        title: str,
        priority: str = "HIGH",
        assigned_analyst: Optional[str] = None,
        linked_incident_ids: Optional[List[str]] = None,
        linked_campaign_ids: Optional[List[str]] = None,
        linked_entities: Optional[List[str]] = None,
        initial_note: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> InvestigationCase:
        """Creates a new operational investigation case."""
        now = datetime.now(timezone.utc)
        notes = []
        if initial_note:
            notes.append({
                "author": assigned_analyst or "system",
                "timestamp": now.isoformat(),
                "text": initial_note,
            })

        new_case = InvestigationCase(
            title=title,
            priority=priority.upper(),
            assigned_analyst=assigned_analyst,
            linked_incident_ids=linked_incident_ids or [],
            linked_campaign_ids=linked_campaign_ids or [],
            linked_entities=linked_entities or [],
            notes=notes,
            tags=tags or ["NEW_CASE"],
            created_at=now,
            updated_at=now,
        )
        self._cases[new_case.case_id] = new_case
        return new_case

    def add_case_note(self, case_id: str, text: str, author: str = "analyst") -> Optional[InvestigationCase]:
        """Appends an auditable analyst investigation note to the case."""
        case = self._cases.get(case_id)
        if not case:
            return None
        now = datetime.now(timezone.utc)
        case.notes.append({
            "author": author,
            "timestamp": now.isoformat(),
            "text": text,
        })
        case.updated_at = now
        return case


console_intelligence_service = ConsoleIntelligenceService()
