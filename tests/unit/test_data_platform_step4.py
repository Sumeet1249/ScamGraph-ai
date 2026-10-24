"""Comprehensive test suite for Phase 0D: India Data Platform & Product Schemas."""

import pytest
from datetime import datetime, timezone

from packages.schemas.conversation import Conversation, ConversationMessage, SpeakerRole
from packages.schemas.tactics import ActionRequestedType, ManipulationSignal, TacticType
from packages.schemas.payment_context import ClaimedPaymentReason, PaymentContextRecord
from packages.schemas.journey_corpus import JourneyOutcome, ScamJourneyRecord
from packages.schemas.evidence_record import ClaimEvidenceRecord, EvidencePolarity
from packages.schemas.campaign_foundation import CampaignRecord, CampaignVelocity
from packages.schemas.review_queue import ReviewItem, ReviewReason, ReviewStatus, UserFeedbackRecord, UserFeedbackType
from packages.schemas.product_events import ProductEvent, ProductEventType
from packages.data_platform.adapters import HinglishScamAdapter, ICFD31kAdapter, ScamHamIndiaAdapter
from packages.data_platform.auditor import DatasetQualityAuditor


def test_conversation_ordering():
    """Verify multi-turn conversation maintains chronological turn order."""
    conv = Conversation(
        channel="WHATSAPP",
        scam_family="job_task",
        primary_language="hinglish",
    )
    m1 = ConversationMessage(turn_index=1, speaker_role=SpeakerRole.SCAMMER, text="Like 3 YouTube videos to earn Rs 500")
    m0 = ConversationMessage(turn_index=0, speaker_role=SpeakerRole.SCAMMER, text="Hello, part time work available")
    m2 = ConversationMessage(turn_index=2, speaker_role=SpeakerRole.VICTIM, text="Okay completed, send payment")

    conv.add_message(m1)
    conv.add_message(m0)
    conv.add_message(m2)

    assert len(conv.messages) == 3
    assert [m.turn_index for m in conv.messages] == [0, 1, 2]
    assert conv.messages[0].text == "Hello, part time work available"


def test_tactics_and_actions():
    """Verify manipulation signals capture psychological tactics and calls to action."""
    signal = ManipulationSignal(
        tactics_present=[TacticType.AUTHORITY, TacticType.SECRECY, TacticType.FEAR],
        actions_requested=[ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.SEND_PAYMENT],
        primary_tactic=TacticType.AUTHORITY,
        manipulation_severity="CRITICAL",
        explanation="Digital arrest pattern: impersonating CBI with demands for secrecy and payment.",
    )
    assert len(signal.tactics_present) == 3
    assert TacticType.AUTHORITY in signal.tactics_present
    assert ActionRequestedType.DO_NOT_DISCONNECT in signal.actions_requested


def test_payment_context_record():
    """Verify PaymentContextRecord evaluates pre-payment context and cooling-off duration."""
    ctx = PaymentContextRecord(
        incident_id="inc_test_123",
        claimed_reason=ClaimedPaymentReason.TASK_DEPOSIT,
        inferred_reason=ClaimedPaymentReason.TASK_DEPOSIT,
        amount_inr=15000.0,
        amount_bucket="HIGH",
        recipient_vpa="taskpay@okhdfcbank",
        pressure_present=True,
        prior_small_reward_received=True,
        recommended_delay_minutes=30,
        consumer_warning="Stop. You are being asked to send ₹15,000 for a prepaid task.",
    )
    assert ctx.claimed_reason == ClaimedPaymentReason.TASK_DEPOSIT
    assert ctx.recommended_delay_minutes == 30
    assert ctx.prior_small_reward_received is True


def test_evidence_corroboration_and_contradiction():
    """Verify evidence schema supports both fraud indicators and legitimacy counter-evidence."""
    sup = ClaimEvidenceRecord(
        claim="SENDER_IS_FRAUD",
        polarity=EvidencePolarity.SUPPORTS,
        source_service="ml/url",
        rationale="Domain registered 2 days ago on .tk TLD",
    )
    contra = ClaimEvidenceRecord(
        claim="SENDER_IS_FRAUD",
        polarity=EvidencePolarity.CONTRADICTS,
        source_service="reputation/dns",
        rationale="Sender domain matches official SBI domain cert",
    )
    assert sup.polarity == EvidencePolarity.SUPPORTS
    assert contra.polarity == EvidencePolarity.CONTRADICTS


def test_dataset_adapters():
    """Verify external adapters correctly map raw inputs to ScamGraphRecordV2."""
    shi_adapter = ScamHamIndiaAdapter()
    rec_shi = shi_adapter.map_record({"text": "Update your KYC at http://sbi.tk", "label": "spam"})
    assert rec_shi.provenance.source_name == "anmolshrivastav/scam-ham-india"
    assert rec_shi.provenance.source_type.value == "PUBLIC_MIXED"
    assert rec_shi.labels["is_scam"] == 1

    icfd_adapter = ICFD31kAdapter()
    rec_icfd = icfd_adapter.map_record({"conversation": "Hello officer speaking", "label": "fraud"})
    assert rec_icfd.provenance.source_type.value == "SYNTHETIC_LLM"
    assert rec_icfd.provenance.license == "cc-by-nc-4.0"

    hng_adapter = HinglishScamAdapter()
    rec_hng = hng_adapter.map_record({"text": "Turant apna bijli bill bharein nahi to line cut hogi", "label": "spam"})
    assert rec_hng.language.primary_language == "hi"
    assert rec_hng.language.code_mixed is True


def test_cross_dataset_contamination_detection():
    """Verify DatasetQualityAuditor detects cross-dataset exact duplicates and template overlap."""
    adapter = ScamHamIndiaAdapter()
    ds_a = [
        adapter.map_record({"text": "Your SBI account 9876543210 is blocked", "label": "spam"}),
        adapter.map_record({"text": "Normal salary credit", "label": "ham"}),
    ]
    ds_b = [
        adapter.map_record({"text": "Your SBI account 9876543210 is blocked", "label": "spam"}), # exact dupe
        adapter.map_record({"text": "Your HDFC account 9123456789 is blocked", "label": "spam"}), # template dupe
    ]

    res = DatasetQualityAuditor.audit_cross_dataset_contamination(ds_a, "A", ds_b, "B")
    assert res["exact_cross_duplicates"] == 1
    assert res["cross_template_overlaps"] == 2
    assert res["contamination_risk"] == "HIGH"
