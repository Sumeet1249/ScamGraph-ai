"""Smart Registry Business Logic Service.

Implements report ingestion, identifier screening, lifecycle state machine,
entity linkage, dispute resolution, revocation handling, and immutable audit event generation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from packages.schemas.registry import (
    AuditAction,
    AuditEvent,
    CanonicalFingerprint,
    CreateReportRequest,
    DisputeDecisionRequest,
    DisputeRecord,
    IdentifierType,
    MatchType,
    RegistryEntity,
    RegistryEntityDetail,
    RegistryFeedbackRequest,
    RegistryReport,
    RegistryStatistics,
    ReportStatus,
    ReviewReportRequest,
    RevocationDecisionRequest,
    RevocationRecord,
    ScreeningMatch,
    ScreenRequest,
    ScreenResponse,
    SubmitDisputeRequest,
    SubmitRevocationRequest,
    TypedIdentifier,
)
from services.registry.fingerprint import (
    ACTIVE_KEY_VERSION,
    IdentifierNormalizer,
    RegistryFingerprinter,
)
from services.registry.repository import RegistryRepository, registry_repository


class SmartRegistryService:
    """Core Smart Registry orchestration service."""

    def __init__(self, repo: Optional[RegistryRepository] = None):
        self.repo = repo or registry_repository

    @staticmethod
    def _create_audit_hash(
        action: str,
        entity_id: str,
        actor_org: str,
        timestamp: str,
        previous_state: Optional[str],
        new_state: Optional[str],
    ) -> str:
        """Create SHA-256 cryptographic integrity seal for immutable audit log."""
        canonical = f"{action}:{entity_id}:{actor_org}:{timestamp}:{previous_state}:{new_state}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    async def ingest_report(self, req: CreateReportRequest) -> RegistryReport:
        """Ingest a new suspect entity/identifier report into Smart Registry and link to RegistryEntity."""
        await self.repo.ensure_seeded()
        report_id = f"rep_{uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)

        # 1. Compute HMAC-SHA-256 fingerprints for each identifier
        fingerprints: List[CanonicalFingerprint] = []
        for ident in req.identifiers:
            fp = RegistryFingerprinter.generate_fingerprint(
                ident.identifier_type, ident.raw_value
            )
            fingerprints.append(fp)

        # Initial status: CONFIRMED if reporting confidence is high, else REPORTED
        initial_status = ReportStatus.CONFIRMED if req.confidence >= 0.85 else ReportStatus.REPORTED

        # 2. Check for existing entity via exact fingerprint match (Entity Deduplication / Linking)
        linked_entity_id: Optional[str] = None
        for fp in fingerprints:
            existing_ent = await self.repo.get_entity_by_fingerprint(fp.fingerprint)
            if existing_ent:
                linked_entity_id = existing_ent.entity_id
                # Update existing entity
                existing_ent.report_count += 1
                if report_id not in existing_ent.associated_report_ids:
                    existing_ent.associated_report_ids.append(report_id)
                existing_ent.highest_risk_score = max(existing_ent.highest_risk_score, req.confidence)
                existing_ent.updated_at = now
                if initial_status == ReportStatus.CONFIRMED and existing_ent.status != ReportStatus.DISPUTED:
                    existing_ent.status = ReportStatus.CONFIRMED
                await self.repo.save_entity(existing_ent)
                break

        # If no existing entity found, create a new RegistryEntity for primary identifier
        if not linked_entity_id and fingerprints:
            primary_fp = fingerprints[0]
            new_ent_id = f"ent_{uuid4().hex[:10]}"
            new_entity = RegistryEntity(
                entity_id=new_ent_id,
                entity_type=primary_fp.identifier_type,
                fingerprint=primary_fp.fingerprint,
                normalization_version="v1",
                protection_key_version=primary_fp.key_version,
                status=initial_status,
                category=req.category,
                report_count=1,
                associated_report_ids=[report_id],
                highest_risk_score=req.confidence,
                masked_preview=primary_fp.normalized_preview,
                created_at=now,
                updated_at=now,
                metadata={"reporting_org": req.reporting_org, "entity_name": req.entity_name},
            )
            await self.repo.save_entity(new_entity)
            linked_entity_id = new_ent_id

        # 3. Create full report
        report = RegistryReport(
            report_id=report_id,
            reporting_org=req.reporting_org,
            entity_id=linked_entity_id,
            entity_name=req.entity_name,
            category=req.category,
            reason=req.reason,
            status=initial_status,
            confidence=req.confidence,
            created_at=now,
            updated_at=now,
            fingerprints=fingerprints,
            evidence_references=req.evidence_references,
            review_history=[{
                "timestamp": now.isoformat(),
                "action": "INGESTED",
                "actor": req.reporting_org,
                "status": initial_status.value,
                "notes": f"Initial report filed with {len(fingerprints)} identifiers.",
                "linked_entity_id": linked_entity_id,
            }],
            metadata=req.metadata,
        )

        saved = await self.repo.save_report(report)

        # 4. Append immutable audit event
        audit_id = f"aud_{uuid4().hex[:10]}"
        audit_hash = self._create_audit_hash(
            action=AuditAction.REPORT_CREATED.value,
            entity_id=report_id,
            actor_org=req.reporting_org,
            timestamp=now.isoformat(),
            previous_state=None,
            new_state=initial_status.value,
        )
        audit_event = AuditEvent(
            audit_id=audit_id,
            timestamp=now,
            entity_type="REGISTRY_REPORT",
            entity_id=report_id,
            action=AuditAction.REPORT_CREATED,
            actor_org=req.reporting_org,
            actor_user=req.reporting_org,
            previous_state=None,
            new_state=initial_status.value,
            reason=req.reason,
            integrity_hash=audit_hash,
        )
        await self.repo.append_audit_event(audit_event)

        return saved

    async def screen_identifiers(self, req: ScreenRequest) -> ScreenResponse:
        """Screen one or more typed identifiers against confirmed registry reports."""
        await self.repo.ensure_seeded()
        await self.repo.record_screening_call()

        screening_id = f"scr_{uuid4().hex[:10]}"
        correlation_id = req.correlation_id or f"corr_{uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        matches: List[ScreeningMatch] = []
        has_confirmed = False
        has_disputed = False
        has_revoked = False
        highest_risk = 0.0
        warnings: List[str] = []

        for ident in req.identifiers:
            try:
                # Generate primary fingerprint and candidate fingerprints (for version rotation lookup)
                candidates = RegistryFingerprinter.generate_all_version_fingerprints(
                    ident.identifier_type, ident.raw_value
                )
            except ValueError as ve:
                warnings.append(f"Invalid identifier skipped ({ident.identifier_type.value}): {str(ve)}")
                continue

            reports: List[RegistryReport] = []
            matched_fp_str = candidates[0] if candidates else ""

            for cand_fp in candidates:
                reps = await self.repo.find_reports_by_fingerprint(cand_fp)
                if reps:
                    reports = reps
                    matched_fp_str = cand_fp
                    break

            for rep in reports:
                is_disputed = rep.status == ReportStatus.DISPUTED
                is_revoked = rep.status == ReportStatus.REVOKED

                if is_disputed:
                    has_disputed = True
                if is_revoked:
                    has_revoked = True

                rep_warnings: List[str] = []
                # Calculate screening risk score
                if rep.status == ReportStatus.CONFIRMED:
                    has_confirmed = True
                    match_risk = round(rep.confidence, 2)
                    reason_code = f"REGISTRY_CONFIRMED_{rep.category.upper()}"
                elif rep.status == ReportStatus.DISPUTED:
                    match_risk = round(rep.confidence * 0.5, 2)
                    reason_code = f"REGISTRY_DISPUTED_{rep.category.upper()}"
                    rep_warnings.append("Active dispute pending resolution; risk score discounted by 50%.")
                elif rep.status == ReportStatus.REVOKED:
                    match_risk = 0.0
                    reason_code = f"REGISTRY_REVOKED_{rep.category.upper()}"
                    rep_warnings.append("Historic fraud report has been formally revoked; active risk suppressed.")
                else:
                    match_risk = round(rep.confidence * 0.7, 2)
                    reason_code = f"REGISTRY_{rep.status.value}_{rep.category.upper()}"

                highest_risk = max(highest_risk, match_risk)

                matches.append(
                    ScreeningMatch(
                        identifier_type=ident.identifier_type,
                        match_type=MatchType.EXACT_FINGERPRINT,
                        matched_fingerprint=matched_fp_str,
                        entity_id=rep.entity_id,
                        report_id=rep.report_id,
                        report_status=rep.status,
                        category=rep.category,
                        reporting_source=rep.reporting_org,
                        reported_at=rep.created_at,
                        is_disputed=is_disputed,
                        is_revoked=is_revoked,
                        risk_score=match_risk,
                        reason_code=reason_code,
                        confidence=rep.confidence,
                        warnings=rep_warnings,
                        data_freshness="REALTIME",
                    )
                )

        response = ScreenResponse(
            screening_id=screening_id,
            screened_at=now,
            caller_org=req.caller_org,
            total_queried=len(req.identifiers),
            total_hits=len(matches),
            has_confirmed_hit=has_confirmed,
            has_disputed_hit=has_disputed,
            has_revoked_hit=has_revoked,
            highest_risk_score=highest_risk,
            matches=matches,
            correlation_id=correlation_id,
            warnings=warnings,
        )

        # Log screening audit event
        audit_hash = self._create_audit_hash(
            action=AuditAction.SCREENING_PERFORMED.value,
            entity_id=screening_id,
            actor_org=req.caller_org,
            timestamp=now.isoformat(),
            previous_state=None,
            new_state=f"HITS_{len(matches)}",
        )
        audit_event = AuditEvent(
            audit_id=f"aud_{uuid4().hex[:10]}",
            timestamp=now,
            entity_type="SCREENING_EVENT",
            entity_id=screening_id,
            action=AuditAction.SCREENING_PERFORMED,
            actor_org=req.caller_org,
            actor_user=req.caller_org,
            previous_state=None,
            new_state=f"HITS_{len(matches)}",
            reason=f"Queried {len(req.identifiers)} identifiers; matched {len(matches)} hits.",
            integrity_hash=audit_hash,
        )
        await self.repo.append_audit_event(audit_event)

        return response

    async def review_report(self, report_id: str, req: ReviewReportRequest) -> RegistryReport:
        """Review and transition the status of a report (e.g. to CONFIRMED, REJECTED, or UNDER_REVIEW)."""
        report = await self.repo.get_report(report_id)
        if not report:
            raise ValueError(f"Report '{report_id}' not found.")

        now = datetime.now(timezone.utc)
        prev_status = report.status.value
        report.status = req.new_status
        report.updated_at = now
        report.review_history.append({
            "timestamp": now.isoformat(),
            "action": "STATUS_REVIEW",
            "actor": req.reviewer,
            "status": req.new_status.value,
            "notes": req.notes,
        })
        saved = await self.repo.save_report(report)

        # If linked to an entity, update entity status
        if report.entity_id:
            entity = await self.repo.get_entity(report.entity_id)
            if entity:
                entity.status = req.new_status
                entity.updated_at = now
                await self.repo.save_entity(entity)

        # Append audit event
        audit_hash = self._create_audit_hash(
            action=AuditAction.REPORT_REVIEWED.value,
            entity_id=report_id,
            actor_org="REGISTRY_COMPLIANCE",
            timestamp=now.isoformat(),
            previous_state=prev_status,
            new_state=req.new_status.value,
        )
        await self.repo.append_audit_event(
            AuditEvent(
                audit_id=f"aud_{uuid4().hex[:10]}",
                timestamp=now,
                entity_type="REGISTRY_REPORT",
                entity_id=report_id,
                action=AuditAction.REPORT_REVIEWED,
                actor_org="REGISTRY_COMPLIANCE",
                actor_user=req.reviewer,
                previous_state=prev_status,
                new_state=req.new_status.value,
                reason=req.notes,
                integrity_hash=audit_hash,
            )
        )
        return saved

    async def submit_dispute(self, req: SubmitDisputeRequest) -> DisputeRecord:
        """Submit a formal dispute against a registry report."""
        report = await self.repo.get_report(req.report_id)
        if not report:
            raise ValueError(f"Report '{req.report_id}' not found.")

        dispute_id = f"dsp_{uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        prev_status = report.status.value

        dispute = DisputeRecord(
            dispute_id=dispute_id,
            report_id=req.report_id,
            entity_id=report.entity_id,
            disputing_org=req.disputing_org,
            reason=req.reason,
            status="OPEN",
            created_at=now,
            evidence_documents=req.evidence_documents,
        )
        await self.repo.save_dispute(dispute)

        # Transition report state machine to DISPUTED
        report.status = ReportStatus.DISPUTED
        report.active_dispute_id = dispute_id
        report.updated_at = now
        report.review_history.append({
            "timestamp": now.isoformat(),
            "action": "DISPUTE_FILED",
            "actor": req.disputing_org,
            "status": ReportStatus.DISPUTED.value,
            "notes": req.reason,
            "dispute_id": dispute_id,
        })
        await self.repo.save_report(report)

        # Update entity status to DISPUTED
        if report.entity_id:
            entity = await self.repo.get_entity(report.entity_id)
            if entity:
                entity.status = ReportStatus.DISPUTED
                entity.updated_at = now
                await self.repo.save_entity(entity)

        # Immutable audit trail
        audit_hash = self._create_audit_hash(
            action=AuditAction.DISPUTE_FILED.value,
            entity_id=req.report_id,
            actor_org=req.disputing_org,
            timestamp=now.isoformat(),
            previous_state=prev_status,
            new_state=ReportStatus.DISPUTED.value,
        )
        audit_event = AuditEvent(
            audit_id=f"aud_{uuid4().hex[:10]}",
            timestamp=now,
            entity_type="REGISTRY_REPORT",
            entity_id=req.report_id,
            action=AuditAction.DISPUTE_FILED,
            actor_org=req.disputing_org,
            actor_user=req.disputing_org,
            previous_state=prev_status,
            new_state=ReportStatus.DISPUTED.value,
            reason=req.reason,
            integrity_hash=audit_hash,
        )
        await self.repo.append_audit_event(audit_event)

        return dispute

    async def resolve_dispute(self, dispute_id: str, req: DisputeDecisionRequest) -> DisputeRecord:
        """Resolve an open dispute with UPHELD (confirm report) or DISMISSED (reject report)."""
        dispute = await self.repo.get_dispute(dispute_id)
        if not dispute:
            raise ValueError(f"Dispute '{dispute_id}' not found.")

        report = await self.repo.get_report(dispute.report_id)
        now = datetime.now(timezone.utc)

        if req.decision.upper() in ("UPHELD", "RESOLVED_UPHELD"):
            dispute.status = "RESOLVED_UPHELD"
            target_report_status = ReportStatus.CONFIRMED
        else:
            dispute.status = "RESOLVED_DISMISSED"
            target_report_status = ReportStatus.REJECTED

        dispute.resolved_at = now
        dispute.resolution_notes = req.notes
        dispute.reviewed_by = req.reviewer
        await self.repo.save_dispute(dispute)

        if report:
            prev_status = report.status.value
            report.status = target_report_status
            report.active_dispute_id = None
            report.updated_at = now
            report.review_history.append({
                "timestamp": now.isoformat(),
                "action": "DISPUTE_RESOLVED",
                "actor": req.reviewer,
                "status": target_report_status.value,
                "notes": f"Dispute {dispute_id} decided: {dispute.status}. Notes: {req.notes}",
            })
            await self.repo.save_report(report)

            if report.entity_id:
                entity = await self.repo.get_entity(report.entity_id)
                if entity:
                    entity.status = target_report_status
                    entity.updated_at = now
                    await self.repo.save_entity(entity)

        # Audit event
        audit_hash = self._create_audit_hash(
            action=AuditAction.DISPUTE_RESOLVED.value,
            entity_id=dispute.report_id,
            actor_org="REGISTRY_ARBITRATION",
            timestamp=now.isoformat(),
            previous_state="DISPUTED",
            new_state=dispute.status,
        )
        await self.repo.append_audit_event(
            AuditEvent(
                audit_id=f"aud_{uuid4().hex[:10]}",
                timestamp=now,
                entity_type="REGISTRY_DISPUTE",
                entity_id=dispute_id,
                action=AuditAction.DISPUTE_RESOLVED,
                actor_org="REGISTRY_ARBITRATION",
                actor_user=req.reviewer,
                previous_state="OPEN",
                new_state=dispute.status,
                reason=req.notes,
                integrity_hash=audit_hash,
            )
        )
        return dispute

    async def submit_revocation(self, req: SubmitRevocationRequest) -> RevocationRecord:
        """Revoke a previously filed report upon authorization."""
        report = await self.repo.get_report(req.report_id)
        if not report:
            raise ValueError(f"Report '{req.report_id}' not found.")

        # Role authorization check: only the reporting org or an authorized admin can revoke
        if req.authorizing_org != report.reporting_org and req.authorizing_org != "ADMIN":
            raise PermissionError(
                f"Organization '{req.authorizing_org}' is not authorized to revoke report submitted by '{report.reporting_org}'."
            )

        revocation_id = f"rev_{uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        prev_status = report.status.value

        revocation = RevocationRecord(
            revocation_id=revocation_id,
            report_id=req.report_id,
            entity_id=report.entity_id,
            authorizing_org=req.authorizing_org,
            revocation_reason=req.revocation_reason,
            authorized_by=req.authorized_by,
            revoked_at=now,
            status="APPROVED",
        )
        await self.repo.save_revocation(revocation)

        # Transition state machine to REVOKED
        report.status = ReportStatus.REVOKED
        report.revocation_id = revocation_id
        report.updated_at = now
        report.review_history.append({
            "timestamp": now.isoformat(),
            "action": "REVOCATION_APPROVED",
            "actor": req.authorizing_org,
            "status": ReportStatus.REVOKED.value,
            "notes": req.revocation_reason,
            "revocation_id": revocation_id,
        })
        await self.repo.save_report(report)

        # Update entity status to REVOKED
        if report.entity_id:
            entity = await self.repo.get_entity(report.entity_id)
            if entity:
                entity.status = ReportStatus.REVOKED
                entity.updated_at = now
                await self.repo.save_entity(entity)

        # Audit trail
        audit_hash = self._create_audit_hash(
            action=AuditAction.REVOCATION_APPROVED.value,
            entity_id=req.report_id,
            actor_org=req.authorizing_org,
            timestamp=now.isoformat(),
            previous_state=prev_status,
            new_state=ReportStatus.REVOKED.value,
        )
        audit_event = AuditEvent(
            audit_id=f"aud_{uuid4().hex[:10]}",
            timestamp=now,
            entity_type="REGISTRY_REPORT",
            entity_id=req.report_id,
            action=AuditAction.REVOCATION_APPROVED,
            actor_org=req.authorizing_org,
            actor_user=req.authorized_by,
            previous_state=prev_status,
            new_state=ReportStatus.REVOKED.value,
            reason=req.revocation_reason,
            integrity_hash=audit_hash,
        )
        await self.repo.append_audit_event(audit_event)

        return revocation

    async def get_entity_detail(self, entity_id: str) -> RegistryEntityDetail:
        """Fetch detailed entity with linked reports and audit trail."""
        entity = await self.repo.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity '{entity_id}' not found.")

        reports: List[RegistryReport] = []
        for rep_id in entity.associated_report_ids:
            rep = await self.repo.get_report(rep_id)
            if rep:
                reports.append(rep)

        audit_trail = await self.repo.get_audit_trail(entity_id)
        return RegistryEntityDetail(
            entity=entity,
            reports=reports,
            audit_trail=audit_trail,
        )

    async def log_feedback(self, req: RegistryFeedbackRequest) -> Dict[str, Any]:
        """Record screening outcome feedback."""
        now = datetime.now(timezone.utc)
        audit_hash = self._create_audit_hash(
            action=AuditAction.FEEDBACK_LOGGED.value,
            entity_id=req.report_id,
            actor_org=req.reporting_org,
            timestamp=now.isoformat(),
            previous_state=None,
            new_state=req.outcome,
        )
        audit_event = AuditEvent(
            audit_id=f"aud_{uuid4().hex[:10]}",
            timestamp=now,
            entity_type="SCREENING_FEEDBACK",
            entity_id=req.report_id,
            action=AuditAction.FEEDBACK_LOGGED,
            actor_org=req.reporting_org,
            actor_user=req.reporting_org,
            previous_state=None,
            new_state=req.outcome,
            reason=req.feedback_notes or req.outcome,
            integrity_hash=audit_hash,
        )
        await self.repo.append_audit_event(audit_event)

        return {
            "status": "FEEDBACK_RECORDED",
            "screening_id": req.screening_id,
            "report_id": req.report_id,
            "recorded_at": now.isoformat(),
        }


# Global singleton service
smart_registry_service = SmartRegistryService()


def get_smart_registry_service() -> SmartRegistryService:
    """FastAPI Dependency Provider."""
    return smart_registry_service
