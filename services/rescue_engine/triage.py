"""Rescue Triage Engine for ScamGraph AI (Prompt 16 / Phase 5B).

Determines:
- What happened (financial, credential, device, identity damage)
- What is still at immediate risk
- Contextual Emergency Action Plan (DO NOW, DO NEXT, PRESERVE, REPORT, MONITOR)
- Priority level without generic static checklists
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from packages.schemas.rescue import (
    ActionCategory,
    ActionStatus,
    EmergencyActionPlan,
    ExposureAssessment,
    ExposureCategory,
    ExposureSeverity,
    LossEvent,
    LossStatus,
    LossType,
    RecoveryScamProtection,
    ReportingResourceType,
    RescueActionItem,
    RescueTriage,
)
from services.rescue_engine.resources import official_resources_registry


class RescueTriageEngine:
    """Evaluates post-loss/exposure context and generates emergency mitigation plans."""

    def __init__(self):
        self.policy_version = "2026.10-v1"
        self.engine_version = "RescueTriageEngine-v1.0"

    def evaluate_triage(
        self,
        incident_id: str,
        loss_events: List[LossEvent],
        exposures: List[ExposureAssessment],
        ongoing_contact: bool = False,
        scam_family: Optional[str] = None,
        additional_demands_present: bool = False,
        recovery_offer_received: bool = False,
    ) -> RescueTriage:
        """Computes comprehensive RescueTriage state for an incident."""
        loss_types: List[LossType] = []
        total_reported_loss = 0.0

        for le in loss_events:
            total_reported_loss += le.amount
            if le.payment_method.upper() == "UPI":
                loss_types.append(LossType.UPI_PAYMENT)
            elif le.payment_method.upper() in ("IMPS", "NEFT", "RTGS", "BANK"):
                loss_types.append(LossType.BANK_TRANSFER)
            elif le.payment_method.upper() == "CARD":
                loss_types.append(LossType.CARD_PAYMENT)
            elif le.payment_method.upper() == "CRYPTO":
                loss_types.append(LossType.CRYPTO_TRANSFER)
            else:
                loss_types.append(LossType.MONEY_TRANSFER)

        has_financial = total_reported_loss > 0 or len(loss_events) > 0
        has_credential = False
        has_device = False
        has_identity = False
        has_active_remote = False

        for exp in exposures:
            if exp.category in (ExposureCategory.BANK_ACCOUNT, ExposureCategory.EMAIL_ACCOUNT):
                has_credential = True
                loss_types.append(LossType.CREDENTIAL_DISCLOSURE)
            elif exp.category == ExposureCategory.DEVICE:
                has_device = True
                loss_types.append(LossType.REMOTE_ACCESS)
                if exp.active_now or (exp.remote_tool_name and exp.remote_tool_name.strip()):
                    has_active_remote = True
            elif exp.category == ExposureCategory.IDENTITY:
                has_identity = True
                loss_types.append(LossType.IDENTITY_DOCUMENT_DISCLOSURE)

        # Deduplicate loss_types
        unique_loss_types = list(dict.fromkeys(loss_types))
        if not unique_loss_types:
            unique_loss_types = [LossType.UNKNOWN]
        elif len(unique_loss_types) > 1:
            unique_loss_types.insert(0, LossType.MULTIPLE)

        # Determine LossStatus
        if has_financial:
            loss_status = LossStatus.PAYMENT_COMPLETED
        elif has_credential:
            loss_status = LossStatus.CREDENTIALS_EXPOSED
        elif has_device or has_identity:
            loss_status = LossStatus.ACCOUNT_COMPROMISE_SUSPECTED
        else:
            loss_status = LossStatus.NO_CONFIRMED_LOSS

        # Determine Priority
        if has_active_remote:
            priority = "EMERGENCY_CRITICAL"
        elif has_financial:
            # Check if any payment occurred within the last 48 hours (Golden Hour / Window)
            now = datetime.now(timezone.utc)
            recent = any(
                (now - le.occurred_at).total_seconds() < 172800 for le in loss_events
            )
            priority = "EMERGENCY_CRITICAL" if recent else "URGENT"
        elif has_credential:
            priority = "URGENT"
        elif has_identity:
            priority = "ELEVATED"
        else:
            priority = "STANDARD"

        return RescueTriage(
            incident_id=incident_id,
            loss_types=unique_loss_types,
            loss_status=loss_status,
            financial_exposure=has_financial,
            credential_exposure=has_credential,
            account_exposure=has_credential or has_device,
            device_exposure=has_device,
            identity_exposure=has_identity,
            total_reported_loss=round(total_reported_loss, 2),
            currency="INR",
            ongoing_contact=ongoing_contact,
            remote_access_active_or_possible=has_active_remote,
            additional_payment_risk=additional_demands_present,
            recovery_scam_risk=recovery_offer_received or has_financial,
            priority=priority,
            policy_version=self.policy_version,
            engine_version=self.engine_version,
        )

    def generate_action_plan(
        self,
        triage: RescueTriage,
        loss_events: List[LossEvent],
        exposures: List[ExposureAssessment],
        bank_hint: Optional[str] = None,
    ) -> EmergencyActionPlan:
        """Constructs a context-grounded Emergency Action Plan."""
        do_now: List[RescueActionItem] = []
        do_next: List[RescueActionItem] = []
        preserve: List[RescueActionItem] = []
        report: List[RescueActionItem] = []
        monitor: List[RescueActionItem] = []

        helpline_1930 = official_resources_registry.get_national_helpline("IN")
        ncrp_portal = official_resources_registry.get_cybercrime_portal("IN")
        bank_resource = official_resources_registry.find_bank_resource(bank_hint or "") if bank_hint else None
        p_order = 1

        # -------------------------------------------------------------
        # 1. DO NOW (Immediate Safety & Stop-Payment)
        # -------------------------------------------------------------
        if triage.remote_access_active_or_possible:
            do_now.append(
                RescueActionItem(
                    category=ActionCategory.DO_NOW,
                    priority_order=p_order,
                    title="Terminate Remote Access & Enable Airplane Mode",
                    description=(
                        "Immediately uninstall or force-close any remote screen sharing software "
                        "(e.g., AnyDesk, TeamViewer, RustDesk). Switch your device to Airplane Mode or "
                        "disconnect Wi-Fi/data to block the attacker's active session."
                    ),
                    action_type="DEVICE_SETTING",
                    is_immediate_lifeline=True,
                )
            )
            p_order += 1

        if triage.financial_exposure:
            # Check timing: is this within emergency window or historical?
            now = datetime.now(timezone.utc)
            is_recent = not loss_events or any(
                (now - le.occurred_at).total_seconds() < 2592000 for le in loss_events  # < 30 days
            )
            is_golden_hour = not loss_events or any(
                (now - le.occurred_at).total_seconds() < 172800 for le in loss_events  # < 48 hours
            )

            if is_golden_hour:
                do_now.append(
                    RescueActionItem(
                        category=ActionCategory.DO_NOW,
                        priority_order=p_order,
                        title="Call 1930 National Cyber Financial Fraud Helpline Immediately",
                        description=(
                            "Report the fraudulent transfer to 1930 right now. Have your bank name, "
                            "account number, and 12-digit UTR/transaction reference number ready. "
                            "1930 triggers inter-bank hold alerts along the mule account trail."
                        ),
                        official_resource=helpline_1930,
                        action_type="DIRECT_CALL",
                        link_or_dial="1930",
                        is_immediate_lifeline=True,
                    )
                )
                p_order += 1
            elif is_recent:
                do_now.append(
                    RescueActionItem(
                        category=ActionCategory.DO_NOW,
                        priority_order=p_order,
                        title="Report Fraudulent Debit to 1930 Helpline",
                        description=(
                            "Dial 1930 or submit details to cybercrime.gov.in. Note: While immediate "
                            "transaction freeze operates most effectively in the first 48 hours, "
                            "official reporting is required for bank disputes and legal redress."
                        ),
                        official_resource=helpline_1930,
                        action_type="DIRECT_CALL",
                        link_or_dial="1930",
                        is_immediate_lifeline=False,
                    )
                )
                p_order += 1
            else:
                # Historical incident (> 3 months ago)
                do_now.append(
                    RescueActionItem(
                        category=ActionCategory.DO_NOW,
                        priority_order=p_order,
                        title="File Historical Financial Dispute with Bank & NCRP",
                        description=(
                            "Because this incident occurred in the past, an emergency stop-payment freeze is no longer available. "
                            "Proceed with formal bank dispute documentation and cybercrime portal reporting."
                        ),
                        action_type="BROWSER_LINK",
                        link_or_dial="https://cybercrime.gov.in",
                    )
                )
                p_order += 1

            # Bank fraud desk notification
            bank_target = bank_resource or official_resources_registry.get_by_id("res_in_bank_sbi")
            do_now.append(
                RescueActionItem(
                    category=ActionCategory.DO_NOW,
                    priority_order=p_order,
                    title=f"Notify {bank_target.organization if bank_target else 'Your Bank'} 24x7 Fraud Desk",
                    description=(
                        "Call your bank's dedicated fraud hotline immediately. Request an emergency "
                        "hotlisting of your compromised account/card and an immediate fraudulent transaction alert."
                    ),
                    official_resource=bank_target,
                    action_type="DIRECT_CALL" if bank_target and bank_target.official_phone else "BROWSER_LINK",
                    link_or_dial=bank_target.official_phone if bank_target else "https://cybercrime.gov.in",
                    is_immediate_lifeline=True,
                )
            )
            p_order += 1

        if triage.credential_exposure:
            do_now.append(
                RescueActionItem(
                    category=ActionCategory.DO_NOW,
                    priority_order=p_order,
                    title="Change Account Credentials from a Clean Device",
                    description=(
                        "Secure the account whose password or credentials were shared. Do NOT perform "
                        "this from the compromised device if remote software was installed. "
                        "Log out of all other active sessions and enable two-factor authentication (2FA)."
                    ),
                    action_type="DEVICE_SETTING",
                    is_immediate_lifeline=True,
                )
            )
            p_order += 1

        if triage.ongoing_contact:
            do_now.append(
                RescueActionItem(
                    category=ActionCategory.DO_NOW,
                    priority_order=p_order,
                    title="Cease Communication with the Scammer",
                    description=(
                        "Do not confront, alert, or send further money to the fraudster. "
                        "Preserve the chat evidence first before blocking their number or handle."
                    ),
                    action_type="COPY_TEXT",
                )
            )
            p_order += 1

        # -------------------------------------------------------------
        # 2. DO NEXT (Secondary Containment & Account Hardening)
        # -------------------------------------------------------------
        if triage.identity_exposure:
            uidai_resource = official_resources_registry.get_by_id("res_in_uidai_lock")
            do_next.append(
                RescueActionItem(
                    category=ActionCategory.DO_NEXT,
                    priority_order=1,
                    title="Lock Aadhaar Biometrics on UIDAI Portal",
                    description=(
                        "If you shared your Aadhaar card or number, visit myaadhaar.uidai.gov.in and "
                        "lock your biometric authentication to prevent unauthorized AePS cash withdrawals."
                    ),
                    official_resource=uidai_resource,
                    action_type="BROWSER_LINK",
                    link_or_dial="https://myaadhaar.uidai.gov.in",
                )
            )

        if triage.financial_exposure:
            npci_resource = official_resources_registry.get_by_id("res_in_upi_npci")
            do_next.append(
                RescueActionItem(
                    category=ActionCategory.DO_NEXT,
                    priority_order=2,
                    title="Lodge UPI Dispute with NPCI",
                    description=(
                        "File a formal dispute on NPCI's Dispute Redressal Mechanism using your 12-digit UTR "
                        "for any fraudulent UPI payments."
                    ),
                    official_resource=npci_resource,
                    action_type="BROWSER_LINK",
                    link_or_dial="https://www.npci.org.in/what-we-do/upi/dispute-redressal-mechanism",
                )
            )

        do_next.append(
            RescueActionItem(
                category=ActionCategory.DO_NEXT,
                priority_order=3,
                title="Inform a Trusted Family Member or Colleague",
                description=(
                    "Scammers often rely on psychological isolation, shame, and urgency. "
                    "Sharing the situation with a trusted person brings immediate emotional clarity "
                    "and protects you from continued manipulation."
                ),
                action_type="COPY_TEXT",
            )
        )

        # -------------------------------------------------------------
        # 3. PRESERVE (Evidence Manifest)
        # -------------------------------------------------------------
        preserve.append(
            RescueActionItem(
                category=ActionCategory.PRESERVE,
                priority_order=1,
                title="Preserve Transaction Receipts & UTR Numbers",
                description="Save unedited PDF/screenshot statements showing exact timestamps, debited amount, and 12-digit UTR.",
                action_type="COPY_TEXT",
            )
        )
        preserve.append(
            RescueActionItem(
                category=ActionCategory.PRESERVE,
                priority_order=2,
                title="Capture Full Chat and Call Screenshots",
                description="Keep full uncropped screenshots of chat messages, sender profile information, and phone call logs.",
                action_type="COPY_TEXT",
            )
        )
        preserve.append(
            RescueActionItem(
                category=ActionCategory.PRESERVE,
                priority_order=3,
                title="Record Suspect Identifiers (VPA, Links, Accounts)",
                description="Record the beneficiary UPI ID (VPA), bank account number, IFSC, APK filename, or website links.",
                action_type="COPY_TEXT",
            )
        )

        # -------------------------------------------------------------
        # 4. REPORT (Formal Cybercrime Documentation)
        # -------------------------------------------------------------
        report.append(
            RescueActionItem(
                category=ActionCategory.REPORT,
                priority_order=1,
                title="File Complaint on National Cyber Crime Reporting Portal (NCRP)",
                description=(
                    "Submit a comprehensive complaint on cybercrime.gov.in under 'Financial Fraud'. "
                    "Upload preserved screenshots, transaction statements, and your ScamGraph Case Package."
                ),
                official_resource=ncrp_portal,
                action_type="BROWSER_LINK",
                link_or_dial="https://cybercrime.gov.in",
            )
        )
        report.append(
            RescueActionItem(
                category=ActionCategory.REPORT,
                priority_order=2,
                title="Record the NCRP Acknowledgement Number",
                description="Note down the official complaint acknowledgement number. Provide it to your bank's nodal officer for dispute escalation.",
                action_type="COPY_TEXT",
            )
        )

        # -------------------------------------------------------------
        # 5. MONITOR (Recovery-Scam Defense & Account Alerts)
        # -------------------------------------------------------------
        monitor.append(
            RescueActionItem(
                category=ActionCategory.MONITOR,
                priority_order=1,
                title="CRITICAL WARNING: Beware of Fake Recovery Scams",
                description=(
                    "Fraudsters, fake 'ethical hackers', or unverified agents may approach you claiming they can "
                    "'recover' or 'hack back' your lost money for an advance fee, tax, or commission. "
                    "THIS IS A SECOND SCAM. Never pay money to anyone claiming they can retrieve lost funds."
                ),
                action_type="COPY_TEXT",
                is_immediate_lifeline=True,
            )
        )
        monitor.append(
            RescueActionItem(
                category=ActionCategory.MONITOR,
                priority_order=2,
                title="Monitor Bank Statements & SMS for Mandates",
                description="Check your accounts daily for unexpected auto-debits, recurring UPI mandates, or SIM-swap indicators.",
                action_type="COPY_TEXT",
            )
        )

        total_actions = len(do_now) + len(do_next) + len(preserve) + len(report) + len(monitor)

        return EmergencyActionPlan(
            incident_id=triage.incident_id,
            do_now=do_now,
            do_next=do_next,
            preserve=preserve,
            report=report,
            monitor=monitor,
            total_actions=total_actions,
            completed_actions=0,
        )


rescue_triage_engine = RescueTriageEngine()
