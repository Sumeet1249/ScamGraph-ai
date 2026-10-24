"""Contextual Intervention Policy Engine (Phase 4B / Prompt 14).

Fuses Tripartite Decision (Risk, Confidence, Urgency) with situational context
(Payment Proximity, Payment Reason, Social Engineering Tactics, Journey Progression)
to determine WHAT protective action ScamGraph should take at this exact moment.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from packages.schemas.contextual_intervention import (
    FrictionLevel,
    InterventionDecision,
    InterventionTiming,
    InterventionType,
    PaymentProximity,
    PaymentReason,
    PrePaymentContext,
    VerificationPlan,
)
from services.intervention_engine.catalog import get_localized_message
from services.intervention_engine.verification import verification_recommendation_engine
from services.intervention_engine.memory import intervention_memory_manager


class InterventionPolicyEngine:
    """Evaluates context and policy rules to decide user-interrupting interventions."""

    POLICY_VERSION = "4.2.0"
    ENGINE_VERSION = "contextual_intervention_v2"

    def evaluate(
        self,
        subject_id: str,
        risk: float,
        confidence: float,
        urgency: float,
        journey_stage: str = "INITIAL_CONTACT",
        payment_proximity: PaymentProximity = PaymentProximity.NONE,
        payment_reason: PaymentReason = PaymentReason.UNKNOWN,
        tactics: Optional[List[str]] = None,
        claimed_org: Optional[str] = None,
        suspect_url: Optional[str] = None,
        suspect_phone: Optional[str] = None,
        campaign_context: Optional[Dict[str, Any]] = None,
        already_paid: bool = False,
        lang: str = "en",
    ) -> InterventionDecision:
        """Determines the appropriate contextual intervention."""
        tactics_list = [t.upper() for t in (tactics or [])]
        reason_codes: List[str] = []
        is_outbreak = bool(campaign_context and campaign_context.get("lifecycle_state") == "OUTBREAK")

        # ── Rule 1: Post-Loss Emergency Handoff ──
        if already_paid or journey_stage in ("LOSS_CONFIRMED", "POST_PAYMENT", "RECOVERY_EXTRACTION"):
            primary_action = InterventionType.EMERGENCY_RESPONSE
            secondary = [InterventionType.VERIFY_INDEPENDENTLY]
            friction = FrictionLevel.EMERGENCY
            timing = InterventionTiming.NOW
            msg_key = "emergency.already_paid"
            reason_codes.append("RC_INTV_ALREADY_PAID: Financial loss reported or confirmed; emergency response initiated")
            cooling_minutes = 0
            priority = "EMERGENCY"
            severity = "CRITICAL"

        # ── Rule 2: Remote Access Software / Malicious APK ──
        elif any(
            t in ("REMOTE_ACCESS_PRESSURE", "SCREEN_SHARE", "ANYDESK", "TEAMVIEWER", "RUSTDESK", "APK")
            or "REMOTE" in t
            or "SCREEN" in t
            for t in tactics_list
        ):
            primary_action = InterventionType.DO_NOT_INSTALL_REMOTE_ACCESS
            secondary = [InterventionType.BREAK_CONTACT_AND_VERIFY, InterventionType.VERIFY_INDEPENDENTLY]
            friction = FrictionLevel.STRONG
            timing = InterventionTiming.BEFORE_NEXT_ACTION
            msg_key = "remote_access.do_not_install"
            reason_codes.append("RC_INTV_REMOTE_ACCESS: Device control / screen-share pressure detected")
            cooling_minutes = 60
            priority = "CRITICAL"
            severity = "CRITICAL"

        # ── Rule 3: Direct OTP or Credential Intercept ──
        elif any(t in ("CREDENTIAL_PRESSURE", "OTP_REQUEST", "PIN_REQUEST", "CVV_REQUEST") or "OTP" in t for t in tactics_list):
            is_otp = any("OTP" in t for t in tactics_list)
            primary_action = InterventionType.DO_NOT_SHARE_OTP if is_otp else InterventionType.DO_NOT_SHARE_CREDENTIALS
            secondary = [InterventionType.BREAK_CONTACT_AND_VERIFY]
            friction = FrictionLevel.STRONG
            timing = InterventionTiming.BEFORE_CREDENTIAL_SHARE
            msg_key = "otp.do_not_share" if is_otp else "credentials.do_not_share"
            reason_codes.append("RC_INTV_CREDENTIAL_CAPTURE: Direct request for confidential authentication credential")
            cooling_minutes = 60
            priority = "CRITICAL"
            severity = "CRITICAL"

        # ── Rule 4: Digital Arrest & Anti-Isolation Protection ──
        elif (
            any(t in ("ISOLATION", "ISOLATION_TACTIC", "SECRECY", "SECRECY_TACTIC") for t in tactics_list)
            and any(t in ("AUTHORITY", "AUTHORITY_TACTIC", "FEAR", "FEAR_TACTIC", "PAT_DIGITAL_ARREST") for t in tactics_list)
        ):
            primary_action = InterventionType.TALK_TO_TRUSTED_PERSON
            secondary = [
                InterventionType.BREAK_CONTACT_AND_VERIFY,
                InterventionType.VERIFY_INDEPENDENTLY,
                InterventionType.DELAY_PAYMENT,
            ]
            friction = FrictionLevel.STRONG
            timing = InterventionTiming.NOW
            msg_key = "isolation.talk_to_trusted_person"
            reason_codes.append("RC_INTV_ANTI_ISOLATION: Coercive isolation combined with authority/arrest threats")
            cooling_minutes = 120
            priority = "CRITICAL"
            severity = "CRITICAL"

        # ── Rule 5: Task Scam Pre-Loss Intercept (Small reward -> Deposit request) ──
        elif (
            (payment_reason == PaymentReason.JOB_OR_TASK or any(t in ("FAKE_REWARD", "PAT_TASK_SCAM") for t in tactics_list))
            and (risk >= 0.55 or payment_proximity in (PaymentProximity.REQUESTED, PaymentProximity.IMMINENT))
        ):
            primary_action = InterventionType.DELAY_PAYMENT
            secondary = [InterventionType.VERIFY_INDEPENDENTLY, InterventionType.BREAK_CONTACT_AND_VERIFY]
            friction = FrictionLevel.DELAY_PAYMENT
            timing = InterventionTiming.BEFORE_PAYMENT
            msg_key = "payment.delay.task_scam"
            reason_codes.append("RC_INTV_TASK_SCAM: Monetization deposit request following prepaid/task manipulation")
            cooling_minutes = 120
            priority = "HIGH"
            severity = "HIGH"

        # ── Rule 6: Active Campaign Outbreak Override ──
        elif is_outbreak and risk >= 0.50:
            primary_action = (
                InterventionType.DELAY_PAYMENT
                if payment_proximity in (PaymentProximity.REQUESTED, PaymentProximity.IMMINENT, PaymentProximity.APPROACHING)
                else InterventionType.STRONG_WARNING
            )
            secondary = [InterventionType.VERIFY_INDEPENDENTLY]
            friction = (
                FrictionLevel.DELAY_PAYMENT
                if payment_proximity in (PaymentProximity.REQUESTED, PaymentProximity.IMMINENT)
                else FrictionLevel.STRONG
            )
            timing = InterventionTiming.BEFORE_PAYMENT if payment_proximity != PaymentProximity.NONE else InterventionTiming.NOW
            msg_key = "payment.pause.high_risk"
            reason_codes.append("RC_INTV_CAMPAIGN_OUTBREAK: Incident matches active circulating syndicate outbreak cluster")
            cooling_minutes = 120
            priority = "CRITICAL"
            severity = "CRITICAL"

        # ── Rule 7: Authority Threat Without Immediate Isolation ──
        elif any(t in ("AUTHORITY", "AUTHORITY_TACTIC", "FEAR", "FEAR_TACTIC") for t in tactics_list) and risk >= 0.50:
            primary_action = (
                InterventionType.BREAK_CONTACT_AND_VERIFY
                if risk >= 0.65
                else InterventionType.VERIFY_INDEPENDENTLY
            )
            secondary = [InterventionType.TALK_TO_TRUSTED_PERSON]
            friction = FrictionLevel.STRONG if risk >= 0.65 else FrictionLevel.MODERATE
            timing = InterventionTiming.BEFORE_NEXT_ACTION
            msg_key = "authority.verify_independently"
            reason_codes.append("RC_INTV_AUTHORITY_PRESSURE: Institutional impersonation or legal threat detected")
            cooling_minutes = 60 if risk >= 0.65 else 0
            priority = "HIGH"
            severity = "HIGH"

        # ── Rule 8: High Risk Pre-Loss Payment Intercept ──
        elif (
            risk >= 0.65
            and (
                payment_proximity in (PaymentProximity.REQUESTED, PaymentProximity.IMMINENT, PaymentProximity.APPROACHING)
                or urgency >= 0.60
            )
        ):
            primary_action = InterventionType.DELAY_PAYMENT
            secondary = [InterventionType.PAUSE_AND_VERIFY, InterventionType.VERIFY_INDEPENDENTLY]
            friction = FrictionLevel.DELAY_PAYMENT
            timing = InterventionTiming.BEFORE_PAYMENT
            msg_key = "payment.pause.high_risk"
            reason_codes.append("RC_INTV_HIGH_RISK_PAYMENT: Imminent payment transfer requested under high fraud likelihood")
            cooling_minutes = 120
            priority = "HIGH"
            severity = "HIGH"

        # ── Rule 9: Legitimate Payment Protection (Hard Negatives) ──
        elif (
            payment_reason in (PaymentReason.RENT, PaymentReason.FAMILY_OR_FRIEND, PaymentReason.BILL, PaymentReason.PURCHASE)
            and risk < 0.35
            and len(tactics_list) == 0
        ):
            primary_action = InterventionType.NO_ACTION
            secondary = []
            friction = FrictionLevel.NONE
            timing = InterventionTiming.BACKGROUND_EDUCATION
            msg_key = "payment.safe.legitimate"
            reason_codes.append("RC_INTV_LEGITIMATE_CONTEXT: Verified routine payment category with zero manipulation markers")
            cooling_minutes = 0
            priority = "LOW"
            severity = "LOW"

        # ── Rule 10: Zero-Day / Behavioral Manipulation Intercept ──
        elif (risk >= 0.45 or urgency >= 0.70 or len(tactics_list) >= 1) and risk >= 0.35:
            if payment_proximity in (PaymentProximity.REQUESTED, PaymentProximity.IMMINENT):
                primary_action = InterventionType.PAUSE_AND_VERIFY
                secondary = [InterventionType.VERIFY_INDEPENDENTLY]
                friction = FrictionLevel.MODERATE
                timing = InterventionTiming.BEFORE_PAYMENT
                cooling_minutes = 30
            else:
                primary_action = InterventionType.VERIFY_INDEPENDENTLY
                secondary = [InterventionType.CAUTION]
                friction = FrictionLevel.LIGHT
                timing = InterventionTiming.NOW
                cooling_minutes = 0
            msg_key = "general.verify_independently"
            reason_codes.append("RC_INTV_BEHAVIORAL_ANOMALY: Behavioral manipulation detected without verified historical campaign match")
            priority = "MEDIUM"
            severity = "MEDIUM"

        # ── Rule 11: Low Risk Educational Advisory ──
        elif risk >= 0.15:
            primary_action = InterventionType.EDUCATE
            secondary = []
            friction = FrictionLevel.LIGHT
            timing = InterventionTiming.BACKGROUND_EDUCATION
            msg_key = "general.educate"
            reason_codes.append("RC_INTV_GENERAL_AWARENESS: Minor indicators observed; baseline educational guidance issued")
            cooling_minutes = 0
            priority = "LOW"
            severity = "LOW"

        # ── Rule 12: Default Benign ──
        else:
            primary_action = InterventionType.NO_ACTION
            secondary = []
            friction = FrictionLevel.NONE
            timing = InterventionTiming.BACKGROUND_EDUCATION
            msg_key = "payment.safe.legitimate"
            reason_codes.append("RC_INTV_NO_ACTION: Benign communication with no suspicious markers")
            cooling_minutes = 0
            priority = "LOW"
            severity = "LOW"

        # Retrieve localized content
        loc = get_localized_message(msg_key, lang=lang)

        # Generate independent verification plan
        ver_type = claimed_org
        if not ver_type:
            if payment_reason and payment_reason != PaymentReason.UNKNOWN:
                ver_type = payment_reason.value
            elif tactics_list:
                ver_type = tactics_list[0]
            else:
                ver_type = "GENERAL"
        plan = verification_recommendation_engine.generate_plan(
            claimed_type=ver_type,
            claimed_entity_name=claimed_org,
            suspect_url=suspect_url,
            suspect_phone=suspect_phone,
        )

        decision = InterventionDecision(
            subject_id=subject_id,
            intervention_type=primary_action,
            secondary_interventions=secondary,
            priority=priority,
            severity=severity,
            trigger_reason_codes=reason_codes,
            risk=risk,
            confidence=confidence,
            urgency=urgency,
            journey_stage=journey_stage,
            payment_proximity=payment_proximity,
            requested_action="PAYMENT" if payment_proximity != PaymentProximity.NONE else None,
            campaign_context=campaign_context,
            message_key=msg_key,
            consumer_headline=loc.headline,
            consumer_message=loc.message,
            recommended_steps=loc.steps,
            verification_plan=plan,
            friction_level=friction,
            timing=timing,
            suggested_cooling_off_minutes=cooling_minutes,
            policy_version=self.POLICY_VERSION,
            engine_version=self.ENGINE_VERSION,
        )

        return decision


intervention_policy_engine = InterventionPolicyEngine()
