"""Rescue Case Package Generator for ScamGraph AI (Phase 5B).

Organizes post-loss incident details into a structured, privacy-safe case package
ready for submission or reference when contacting:
- 1930 National Cyber Financial Fraud Helpline
- National Cyber Crime Reporting Portal (NCRP)
- Bank 24x7 Emergency Fraud Desks

Strictly enforces:
- Non-accusatory language: "User reported that identifier X was involved in the suspected incident"
- Clear distinction between USER-PROVIDED FACTS and SCAMGRAPH ANALYSIS
- Tokenized / masked sensitive credentials
- Standard legal disclaimers (not an official FIR or police document)
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from packages.schemas.rescue import (
    EvidencePreservationItem,
    LossEvent,
    OfficialReportingResource,
    RescueCasePackage,
    RescueTimelineEvent,
    RescueTriage,
)


class RescueCasePackageGenerator:
    """Generates structured JSON and human-readable reporting packages."""

    def generate_package(
        self,
        incident_id: str,
        triage: RescueTriage,
        loss_events: List[LossEvent],
        timeline_events: List[RescueTimelineEvent],
        evidence_items: List[EvidencePreservationItem],
        reporting_resources: List[OfficialReportingResource],
        contact_entities: Optional[List[Dict[str, Any]]] = None,
        urls_and_domains: Optional[List[str]] = None,
        social_handles: Optional[List[str]] = None,
        claimed_organizations: Optional[List[str]] = None,
        inferred_scam_family: Optional[str] = None,
        manipulation_tactics: Optional[List[str]] = None,
        campaign_id: Optional[str] = None,
        actions_taken: Optional[List[str]] = None,
        recommended_actions: Optional[List[str]] = None,
    ) -> RescueCasePackage:
        """Assembles a complete, privacy-safe RescueCasePackage."""
        now = datetime.now(timezone.utc)

        total_loss = sum(le.amount for le in loss_events)
        currency = loss_events[0].currency if loss_events else "INR"

        user_facts = {
            "incident_reported_at": now.isoformat(),
            "loss_status": triage.loss_status.value,
            "financial_exposure": triage.financial_exposure,
            "credential_exposure": triage.credential_exposure,
            "device_exposure": triage.device_exposure,
            "identity_exposure": triage.identity_exposure,
            "ongoing_contact_reported": triage.ongoing_contact,
        }

        # Build clean copyable text summary for victim to paste into 1930 / NCRP form
        summary_lines = [
            f"INCIDENT SUMMARY (FOR 1930 / POLICE CYBER CELL / BANK FRAUD DESK):",
            f"Case Reference (ScamGraph): {incident_id}",
            f"Reported Loss: {currency} {total_loss:,.2f} across {len(loss_events)} payment(s).",
        ]
        if inferred_scam_family:
            summary_lines.append(f"Incident Typology: Suspected {inferred_scam_family.replace('_', ' ').title()}")

        if loss_events:
            summary_lines.append("\nPayment Details (User-Reported):")
            for idx, le in enumerate(loss_events, 1):
                ref_str = f", Ref: {le.transaction_reference_tokenized}" if le.transaction_reference_tokenized else ""
                recip_str = f", Recipient: {le.recipient_identifier}" if le.recipient_identifier else ""
                time_str = le.occurred_at.strftime("%Y-%m-%d %H:%M UTC")
                summary_lines.append(
                    f"  {idx}. {le.currency} {le.amount:,.2f} via {le.payment_method} at {time_str}{recip_str}{ref_str}"
                )

        if contact_entities or urls_and_domains or social_handles:
            summary_lines.append("\nSuspect Identifiers Provided:")
            if contact_entities:
                for ce in contact_entities:
                    summary_lines.append(f"  - Contact: {ce.get('type')}: {ce.get('value')}")
            if urls_and_domains:
                for u in urls_and_domains:
                    summary_lines.append(f"  - Website/URL: {u}")
            if social_handles:
                for sh in social_handles:
                    summary_lines.append(f"  - Profile/Channel: {sh}")

        summary_lines.append(
            "\nImmediate Actions Taken: "
            + (", ".join(actions_taken) if actions_taken else "Reporting initiated via ScamGraph AI.")
        )
        copyable_summary = "\n".join(summary_lines)

        return RescueCasePackage(
            incident_id=incident_id,
            generated_at=now,
            package_version="1.0.0",
            assessment_version="UnifiedAssessment-v2.0",
            user_reported_facts=user_facts,
            reported_total_loss=round(total_loss, 2),
            confirmed_verified_loss=None,  # Never falsely claim bank verification without bank feed
            currency=currency,
            payment_events_count=len(loss_events),
            payment_events=loss_events,
            timeline_events=timeline_events,
            contact_entities=contact_entities or [],
            urls_and_domains=urls_and_domains or [],
            social_handles=social_handles or [],
            claimed_organizations=claimed_organizations or [],
            inferred_scam_family=inferred_scam_family,
            scam_journey_summary=(
                f"Incident progressed through {len(timeline_events)} recorded stages. "
                f"Initial loss of {currency} {total_loss:,.2f} reported."
            ),
            manipulation_tactics=manipulation_tactics or [],
            network_campaign_id=campaign_id,
            evidence_manifest=evidence_items,
            actions_already_taken=actions_taken or [],
            recommended_official_actions=recommended_actions
            or [
                "Call 1930 immediately to freeze bank accounts along the money trail",
                "Notify sending bank fraud desk to report unauthorized/disputed debit",
                "File formal complaint at https://cybercrime.gov.in (NCRP)",
            ],
            official_reporting_resources=reporting_resources,
            copyable_incident_summary=copyable_summary,
            legal_disclaimer=(
                "This document is a technical Incident Information Package prepared based on user-provided "
                "statements and ScamGraph AI automated analysis. It does NOT constitute an official Police "
                "FIR, Government Cybercrime Registration, or guarantee of fund recovery. It is designed to assist "
                "victims in filing accurate, structured reports with verified authorities and banking institutions."
            ),
        )

    def render_markdown(self, package: RescueCasePackage) -> str:
        """Formats the case package as a clean, human-readable markdown document."""
        md = []
        md.append("# SCAMGRAPH RESCUE — INCIDENT INFORMATION PACKAGE")
        md.append(f"**Case Reference:** `{package.incident_id}` | **Generated:** {package.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        md.append(f"**Package Version:** {package.package_version} | **Assessment Engine:** {package.assessment_version}")
        md.append("\n---\n")

        # Legal notice
        md.append("> [!IMPORTANT]")
        md.append(f"> **OFFICIAL NOTICE & DISCLAIMER:**\n> {package.legal_disclaimer}\n")

        # Section 1: User Reported Facts
        md.append("## 1. USER-REPORTED FACTS & LOSS SUMMARY")
        md.append(f"- **Total Reported Loss:** **{package.currency} {package.reported_total_loss:,.2f}**")
        md.append(f"- **Payments Recorded:** {package.payment_events_count}")
        md.append(f"- **Verification State:** User-Reported (Unverified by Banking Core)")
        md.append("")
        if package.payment_events:
            md.append("| # | Amount | Method | Recipient / VPA | Transaction Ref | Occurred At (UTC) |")
            md.append("|---|---|---|---|---|---|")
            for idx, pe in enumerate(package.payment_events, 1):
                recip = pe.recipient_identifier or "N/A"
                ref = pe.transaction_reference_tokenized or "N/A"
                md.append(
                    f"| {idx} | {pe.currency} {pe.amount:,.2f} | {pe.payment_method} | {recip} | {ref} | {pe.occurred_at.strftime('%Y-%m-%d %H:%M')} |"
                )
        md.append("\n")

        # Section 2: Timeline
        md.append("## 2. INCIDENT & RESPONSE TIMELINE")
        if package.timeline_events:
            for te in package.timeline_events:
                t_str = te.occurred_at.strftime("%Y-%m-%d %H:%M UTC")
                md.append(f"- **`{t_str}`** — **{te.title}** ({te.source})")
                md.append(f"  *{te.description}*")
        else:
            md.append("*No timeline events recorded yet.*")
        md.append("\n")

        # Section 3: Suspect Identifiers
        md.append("## 3. SUSPECT IDENTIFIERS (USER-REPORTED)")
        if package.contact_entities:
            md.append("**Suspect Contacts:**")
            for c in package.contact_entities:
                md.append(f"- {c.get('type')}: `{c.get('value')}` ({c.get('role', 'Suspect')})")
        if package.urls_and_domains:
            md.append("**Websites & Links:**")
            for u in package.urls_and_domains:
                md.append(f"- `{u}`")
        if package.social_handles:
            md.append("**Social Handles / Channels:**")
            for sh in package.social_handles:
                md.append(f"- `{sh}`")
        if package.claimed_organizations:
            md.append("**Claimed Organizations:**")
            for o in package.claimed_organizations:
                md.append(f"- Impersonated Entity: **{o}**")
        md.append("\n")

        # Section 4: ScamGraph Analysis
        md.append("## 4. SCAMGRAPH AUTOMATED ANALYSIS")
        md.append(f"- **Typology / Inferred Family:** `{package.inferred_scam_family or 'UNCLASSIFIED'}`")
        md.append(f"- **Manipulation Tactics Detected:** {', '.join(package.manipulation_tactics) if package.manipulation_tactics else 'None identified'}")
        if package.network_campaign_id:
            md.append(f"- **Correlated Campaign Pattern:** `{package.network_campaign_id}`")
        md.append("\n")

        # Section 5: Evidence Manifest
        md.append("## 5. EVIDENCE PRESERVATION MANIFEST")
        if package.evidence_manifest:
            md.append("| Evidence ID | Type | Title | SHA-256 Hash | Redaction |")
            md.append("|---|---|---|---|---|")
            for item in package.evidence_manifest:
                md.append(f"| `{item.evidence_id}` | {item.evidence_type} | {item.display_title} | `{item.sha256_hash[:16]}...` | {item.redaction_state} |")
        else:
            md.append("*No evidentiary artifacts attached to this case package.*")
        md.append("\n")

        # Section 6: Official Resources
        md.append("## 6. VERIFIED OFFICIAL REPORTING CHANNELS")
        for res in package.official_reporting_resources:
            phone_str = f" | Phone: **{res.official_phone}**" if res.official_phone else ""
            url_str = f" | [Official Portal]({res.official_url})" if res.official_url else ""
            md.append(f"- **{res.display_name}** ({res.organization}){phone_str}{url_str}")
            for inst in res.instructions[:2]:
                md.append(f"  - {inst}")
        md.append("\n")

        # Section 7: Copyable Incident Summary
        md.append("## 7. COPYABLE INCIDENT STATEMENT")
        md.append("```text")
        md.append(package.copyable_incident_summary)
        md.append("```\n")

        return "\n".join(md)


case_package_generator = RescueCasePackageGenerator()
