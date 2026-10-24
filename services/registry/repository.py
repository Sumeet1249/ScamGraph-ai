"""Smart Registry Repository Layer.

Defines persistence interface and in-memory implementation for entities, reports,
identifiers, disputes, revocations, and audit logs.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from uuid import uuid4

from packages.schemas.registry import (
    AuditAction,
    AuditEvent,
    CanonicalFingerprint,
    DisputeRecord,
    IdentifierType,
    RegistryEntity,
    RegistryReport,
    RegistryStatistics,
    ReportStatus,
    RevocationRecord,
)
from services.registry.fingerprint import (
    ACTIVE_KEY_VERSION,
    RegistryFingerprinter,
)


class RegistryRepository:
    """In-memory, thread-safe repository for Smart Registry."""

    def __init__(self):
        self._reports: Dict[str, RegistryReport] = {}
        self._entities: Dict[str, RegistryEntity] = {}
        self._entities_by_fingerprint: Dict[str, str] = {}
        self._fingerprint_index: Dict[str, Set[str]] = {}
        self._disputes: Dict[str, DisputeRecord] = {}
        self._revocations: Dict[str, RevocationRecord] = {}
        self._audit_log: List[AuditEvent] = []
        self._screening_count: int = 0
        self._lock = asyncio.Lock()
        self._seeded = False

    async def ensure_seeded(self):
        """Seed initial synthetic benchmark records if empty."""
        async with self._lock:
            if self._seeded or len(self._reports) > 0:
                return
            self._seeded = True
            now = datetime.now(timezone.utc)

            # Synthetic suspect 1: Electricity Bill Phishing UPI
            upi_raw = "electricity.desk@oksbi"
            fp_upi = RegistryFingerprinter.generate_fingerprint(IdentifierType.UPI_VPA, upi_raw)
            ent_id_1 = "ent_upi_elec01"
            rep_id_1 = "rep_elec_phish01"

            entity_1 = RegistryEntity(
                entity_id=ent_id_1,
                entity_type=IdentifierType.UPI_VPA,
                fingerprint=fp_upi.fingerprint,
                normalization_version="v1",
                protection_key_version="v1",
                status=ReportStatus.CONFIRMED,
                category="UTILITY_PHISHING",
                report_count=1,
                associated_report_ids=[rep_id_1],
                highest_risk_score=0.95,
                masked_preview=fp_upi.normalized_preview,
                created_at=now,
                updated_at=now,
                metadata={"synthetic_seed": True, "label": "Electricity Disconnection Phishing"},
            )
            report_1 = RegistryReport(
                report_id=rep_id_1,
                reporting_org="BANK_SBI_01",
                entity_id=ent_id_1,
                entity_name="Power Disconnection Impersonator",
                category="UTILITY_PHISHING",
                reason="SMS impersonation targeting senior citizens warning power cut at 9:30 PM",
                status=ReportStatus.CONFIRMED,
                confidence=0.95,
                created_at=now,
                updated_at=now,
                fingerprints=[fp_upi],
                evidence_references=["I4C-COMPLAINT-1930-2026-X99", "FIR-DEL-CYBER-2026-081"],
                review_history=[{
                    "timestamp": now.isoformat(),
                    "action": "SEED_CONFIRMED",
                    "actor": "BANK_SBI_01",
                    "status": ReportStatus.CONFIRMED.value,
                    "notes": "Verified fraud report with 14 victim complaints on 1930 portal.",
                }],
            )

            # Synthetic suspect 2: Telegram Part-time Job Mule Phone
            phone_raw = "+919876543210"
            fp_phone = RegistryFingerprinter.generate_fingerprint(IdentifierType.PHONE, phone_raw)
            ent_id_2 = "ent_phone_mule02"
            rep_id_2 = "rep_tg_mule02"

            entity_2 = RegistryEntity(
                entity_id=ent_id_2,
                entity_type=IdentifierType.PHONE,
                fingerprint=fp_phone.fingerprint,
                normalization_version="v1",
                protection_key_version="v1",
                status=ReportStatus.CONFIRMED,
                category="MULE_ACCOUNT",
                report_count=1,
                associated_report_ids=[rep_id_2],
                highest_risk_score=0.92,
                masked_preview=fp_phone.normalized_preview,
                created_at=now,
                updated_at=now,
                metadata={"synthetic_seed": True, "label": "Telegram Task Scam Recruiter"},
            )
            report_2 = RegistryReport(
                report_id=rep_id_2,
                reporting_org="BANK_HDFC_01",
                entity_id=ent_id_2,
                entity_name="Task Scam Mule Account",
                category="MULE_ACCOUNT",
                reason="Rapid pass-through cash-out following reported Telegram investment task scam",
                status=ReportStatus.CONFIRMED,
                confidence=0.92,
                created_at=now,
                updated_at=now,
                fingerprints=[fp_phone],
                evidence_references=["I4C-TASK-2026-M442"],
                review_history=[{
                    "timestamp": now.isoformat(),
                    "action": "SEED_CONFIRMED",
                    "actor": "BANK_HDFC_01",
                    "status": ReportStatus.CONFIRMED.value,
                    "notes": "Automated alert triggered on 12 instant outward IMPS withdrawals.",
                }],
            )

            # Synthetic suspect 3: Disputed Agricultural Merchant Account
            acc_raw = "SBIN0001234:009876543210"
            fp_acc = RegistryFingerprinter.generate_fingerprint(IdentifierType.BANK_ACCOUNT, acc_raw)
            ent_id_3 = "ent_acc_mule03"
            rep_id_3 = "rep_acc_disp03"
            dsp_id_3 = "dsp_mandi_01"

            entity_3 = RegistryEntity(
                entity_id=ent_id_3,
                entity_type=IdentifierType.BANK_ACCOUNT,
                fingerprint=fp_acc.fingerprint,
                normalization_version="v1",
                protection_key_version="v1",
                status=ReportStatus.DISPUTED,
                category="MULE_ACCOUNT",
                report_count=1,
                associated_report_ids=[rep_id_3],
                highest_risk_score=0.44,
                masked_preview=fp_acc.normalized_preview,
                created_at=now,
                updated_at=now,
                metadata={"synthetic_seed": True, "label": "Contested Grain Merchant"},
            )
            report_3 = RegistryReport(
                report_id=rep_id_3,
                reporting_org="BANK_AXIS_01",
                entity_id=ent_id_3,
                entity_name="Grain Trader Account",
                category="MULE_ACCOUNT",
                reason="High-velocity inward UPI credits followed by cash withdrawal",
                status=ReportStatus.DISPUTED,
                confidence=0.88,
                created_at=now,
                updated_at=now,
                fingerprints=[fp_acc],
                active_dispute_id=dsp_id_3,
                evidence_references=["AXIS-ALERT-2026-901"],
                review_history=[
                    {
                        "timestamp": now.isoformat(),
                        "action": "INITIAL_REPORT",
                        "actor": "BANK_AXIS_01",
                        "status": ReportStatus.CONFIRMED.value,
                        "notes": "Unusual volume spike outside normal profile.",
                    },
                    {
                        "timestamp": now.isoformat(),
                        "action": "DISPUTE_FILED",
                        "actor": "BANK_ICICI_01",
                        "status": ReportStatus.DISPUTED.value,
                        "notes": "Beneficiary proved legitimate agricultural mandi sales with certified APMC receipts.",
                    },
                ],
            )
            dispute_3 = DisputeRecord(
                dispute_id=dsp_id_3,
                report_id=rep_id_3,
                entity_id=ent_id_3,
                disputing_org="BANK_ICICI_01",
                reason="Beneficiary operates registered grain trading stall; spike corresponds to seasonal soybean harvest harvest auction.",
                status="OPEN",
                created_at=now,
                evidence_documents=["apmc_mandi_receipt_oct2026.pdf", "gstin_certificate.pdf"],
            )

            # Insert into in-memory indices
            for ent in (entity_1, entity_2, entity_3):
                self._entities[ent.entity_id] = ent
                self._entities_by_fingerprint[ent.fingerprint] = ent.entity_id

            for rep in (report_1, report_2, report_3):
                self._reports[rep.report_id] = rep
                for fp in rep.fingerprints:
                    if fp.fingerprint not in self._fingerprint_index:
                        self._fingerprint_index[fp.fingerprint] = set()
                    self._fingerprint_index[fp.fingerprint].add(rep.report_id)

            self._disputes[dsp_id_3] = dispute_3

            # Add initial audit events
            for rep in (report_1, report_2, report_3):
                self._audit_log.append(
                    AuditEvent(
                        audit_id=f"aud_seed_{rep.report_id}",
                        timestamp=now,
                        entity_type="REGISTRY_REPORT",
                        entity_id=rep.report_id,
                        action=AuditAction.REPORT_CREATED,
                        actor_org=rep.reporting_org,
                        actor_user="SYSTEM_BOOTSTRAP",
                        previous_state=None,
                        new_state=rep.status.value,
                        reason=rep.reason,
                        integrity_hash="sha256_seed_integrity_verified_token",
                    )
                )

    # -------------------------------------------------------------------------
    # Entity Operations
    # -------------------------------------------------------------------------

    async def save_entity(self, entity: RegistryEntity) -> RegistryEntity:
        """Store or update a core RegistryEntity."""
        async with self._lock:
            self._entities[entity.entity_id] = entity
            self._entities_by_fingerprint[entity.fingerprint] = entity.entity_id
            return entity

    async def get_entity(self, entity_id: str) -> Optional[RegistryEntity]:
        """Fetch entity by ID."""
        await self.ensure_seeded()
        async with self._lock:
            return self._entities.get(entity_id)

    async def get_entity_by_fingerprint(self, fingerprint: str) -> Optional[RegistryEntity]:
        """Lookup entity by protected fingerprint."""
        await self.ensure_seeded()
        async with self._lock:
            ent_id = self._entities_by_fingerprint.get(fingerprint)
            if ent_id:
                return self._entities.get(ent_id)
            return None

    async def list_entities(
        self,
        status: Optional[ReportStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RegistryEntity]:
        """List entities with optional status filter."""
        await self.ensure_seeded()
        async with self._lock:
            results = list(self._entities.values())
            if status:
                results = [e for e in results if e.status == status]
            results.sort(key=lambda x: x.updated_at, reverse=True)
            return results[offset : offset + limit]

    # -------------------------------------------------------------------------
    # Report Operations
    # -------------------------------------------------------------------------

    async def save_report(self, report: RegistryReport) -> RegistryReport:
        """Store or update a report and update fingerprint index."""
        async with self._lock:
            self._reports[report.report_id] = report
            for fp in report.fingerprints:
                if fp.fingerprint not in self._fingerprint_index:
                    self._fingerprint_index[fp.fingerprint] = set()
                self._fingerprint_index[fp.fingerprint].add(report.report_id)
            return report

    async def get_report(self, report_id: str) -> Optional[RegistryReport]:
        """Fetch report by ID."""
        await self.ensure_seeded()
        async with self._lock:
            return self._reports.get(report_id)

    async def list_reports(
        self,
        status: Optional[ReportStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RegistryReport]:
        """List reports with optional status filter."""
        await self.ensure_seeded()
        async with self._lock:
            results = list(self._reports.values())
            if status:
                results = [r for r in results if r.status == status]
            results.sort(key=lambda x: x.created_at, reverse=True)
            return results[offset : offset + limit]

    async def find_reports_by_fingerprint(self, fingerprint: str) -> List[RegistryReport]:
        """Lookup reports containing an exact fingerprint."""
        await self.ensure_seeded()
        async with self._lock:
            report_ids = self._fingerprint_index.get(fingerprint, set())
            return [self._reports[rid] for rid in report_ids if rid in self._reports]

    # -------------------------------------------------------------------------
    # Dispute Operations
    # -------------------------------------------------------------------------

    async def save_dispute(self, dispute: DisputeRecord) -> DisputeRecord:
        """Store dispute record."""
        async with self._lock:
            self._disputes[dispute.dispute_id] = dispute
            return dispute

    async def get_dispute(self, dispute_id: str) -> Optional[DisputeRecord]:
        """Fetch dispute by ID."""
        await self.ensure_seeded()
        async with self._lock:
            return self._disputes.get(dispute_id)

    async def list_disputes(self, limit: int = 50, offset: int = 0) -> List[DisputeRecord]:
        """List all disputes."""
        await self.ensure_seeded()
        async with self._lock:
            results = list(self._disputes.values())
            results.sort(key=lambda x: x.created_at, reverse=True)
            return results[offset : offset + limit]

    async def list_disputes_for_report(self, report_id: str) -> List[DisputeRecord]:
        """Fetch all disputes for a given report."""
        await self.ensure_seeded()
        async with self._lock:
            return [d for d in self._disputes.values() if d.report_id == report_id]

    # -------------------------------------------------------------------------
    # Revocation Operations
    # -------------------------------------------------------------------------

    async def save_revocation(self, revocation: RevocationRecord) -> RevocationRecord:
        """Store revocation record."""
        async with self._lock:
            self._revocations[revocation.revocation_id] = revocation
            return revocation

    async def get_revocation(self, revocation_id: str) -> Optional[RevocationRecord]:
        """Fetch revocation by ID."""
        await self.ensure_seeded()
        async with self._lock:
            return self._revocations.get(revocation_id)

    async def list_revocations(self, limit: int = 50, offset: int = 0) -> List[RevocationRecord]:
        """List all revocations."""
        await self.ensure_seeded()
        async with self._lock:
            results = list(self._revocations.values())
            results.sort(key=lambda x: x.revoked_at, reverse=True)
            return results[offset : offset + limit]

    # -------------------------------------------------------------------------
    # Audit & Statistics Operations
    # -------------------------------------------------------------------------

    async def append_audit_event(self, event: AuditEvent) -> AuditEvent:
        """Append an immutable audit event."""
        async with self._lock:
            self._audit_log.append(event)
            return event

    async def get_audit_trail(self, entity_id: str) -> List[AuditEvent]:
        """Retrieve audit events for an entity or report."""
        await self.ensure_seeded()
        async with self._lock:
            events = [e for e in self._audit_log if e.entity_id == entity_id]
            events.sort(key=lambda x: x.timestamp)
            return events

    async def list_all_audit_events(self, limit: int = 100) -> List[AuditEvent]:
        """Retrieve latest system-wide audit events."""
        await self.ensure_seeded()
        async with self._lock:
            events = list(self._audit_log)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events[:limit]

    async def record_screening_call(self):
        """Track screening metrics."""
        async with self._lock:
            self._screening_count += 1

    async def get_statistics(self) -> RegistryStatistics:
        """Calculate live aggregate metrics."""
        await self.ensure_seeded()
        async with self._lock:
            confirmed = sum(1 for e in self._entities.values() if e.status == ReportStatus.CONFIRMED)
            under_review = sum(1 for e in self._entities.values() if e.status == ReportStatus.UNDER_REVIEW)
            disputed = sum(1 for e in self._entities.values() if e.status == ReportStatus.DISPUTED)
            revoked = sum(1 for e in self._entities.values() if e.status == ReportStatus.REVOKED)

            return RegistryStatistics(
                total_entities=len(self._entities),
                total_reports=len(self._reports),
                confirmed_count=confirmed,
                under_review_count=under_review,
                disputed_count=disputed,
                revoked_count=revoked,
                screening_count=self._screening_count,
                audit_event_count=len(self._audit_log),
                active_key_version=ACTIVE_KEY_VERSION,
                supported_identifier_types=[t.value for t in IdentifierType],
                system_status="HEALTHY",
            )


# Global singleton repository
registry_repository = RegistryRepository()


def get_registry_repository() -> RegistryRepository:
    """Dependency provider for FastAPI."""
    return registry_repository
