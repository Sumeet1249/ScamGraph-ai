"""Versioned Scam Journey Templates & Transition Graph for ScamGraph AI V2.

Encodes family-specific stage progressions, expected transitions, heuristic priors,
and allowed next-stage possibilities for task scams, investment frauds, digital arrest,
KYC impersonation, and fake customer support scams.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.journey import JourneyStage


@dataclass
class StageTransition:
    """Directed edge in the journey transition graph."""
    from_stage: JourneyStage
    to_stage: JourneyStage
    weight: float = 1.0  # Heuristic prior / rule weight
    is_common: bool = True
    description: str = ""


@dataclass
class JourneyTemplate:
    """Declarative specification for a known scam family progression."""
    family_id: str
    name: str
    description: str
    expected_sequence: List[JourneyStage]
    required_stages: Set[JourneyStage]
    optional_stages: Set[JourneyStage]
    allowed_transitions: Dict[JourneyStage, List[JourneyStage]]
    monetization_entry_stages: Set[JourneyStage]
    next_stage_hints: Dict[JourneyStage, str]


# ---------------------------------------------------------------------------
# Family Templates Specification
# ---------------------------------------------------------------------------

JOB_TASK_TEMPLATE = JourneyTemplate(
    family_id="JOB_TASK",
    name="Part-Time Job & Task Scam",
    description="Lures victim with YouTube like/rating tasks, credits small initial profits, migrates to Telegram, then traps victim in VIP deposit recharges and fake withdrawal taxes.",
    expected_sequence=[
        JourneyStage.DISCOVERY,
        JourneyStage.CONTACT,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.REWARD_OR_FAKE_PROFIT,
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.PAYMENT_ESCALATION,
        JourneyStage.WITHDRAWAL_BLOCK,
        JourneyStage.RECOVERY_FEE,
        JourneyStage.EXIT,
    ],
    required_stages={
        JourneyStage.CONTACT,
        JourneyStage.INITIAL_PAYMENT,
    },
    optional_stages={
        JourneyStage.DISCOVERY,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.REWARD_OR_FAKE_PROFIT,
        JourneyStage.PAYMENT_ESCALATION,
        JourneyStage.WITHDRAWAL_BLOCK,
        JourneyStage.RECOVERY_FEE,
        JourneyStage.EXIT,
    },
    allowed_transitions={
        JourneyStage.DISCOVERY: [JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION],
        JourneyStage.CONTACT: [JourneyStage.PLATFORM_MIGRATION, JourneyStage.TRUST_BUILDING, JourneyStage.REWARD_OR_FAKE_PROFIT],
        JourneyStage.PLATFORM_MIGRATION: [JourneyStage.TRUST_BUILDING, JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.TRUST_BUILDING: [JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.REWARD_OR_FAKE_PROFIT: [JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION],
        JourneyStage.INITIAL_PAYMENT: [JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.PAYMENT_ESCALATION, JourneyStage.WITHDRAWAL_BLOCK],
        JourneyStage.PAYMENT_ESCALATION: [JourneyStage.WITHDRAWAL_BLOCK, JourneyStage.RECOVERY_FEE, JourneyStage.EXIT],
        JourneyStage.WITHDRAWAL_BLOCK: [JourneyStage.RECOVERY_FEE, JourneyStage.THREAT_OR_PRESSURE, JourneyStage.EXIT],
        JourneyStage.RECOVERY_FEE: [JourneyStage.RECOVERY_FEE, JourneyStage.EXIT],
        JourneyStage.EXIT: [],
    },
    monetization_entry_stages={JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION},
    next_stage_hints={
        JourneyStage.CONTACT: "Scammers often offer a small legitimate test payout to gain trust.",
        JourneyStage.TRUST_BUILDING: "Next, scammers typically offer fake rewards or invite you to deposit small funds.",
        JourneyStage.INITIAL_PAYMENT: "Once initial funds are deposited, scammers commonly escalate demands for larger VIP task deposits.",
        JourneyStage.WITHDRAWAL_BLOCK: "Scammers usually invent fake 'tax' or 'channel clearance fees' when you attempt to withdraw.",
    },
)

INVESTMENT_TEMPLATE = JourneyTemplate(
    family_id="INVESTMENT",
    name="High-Return Trading & Investment Fraud",
    description="Promises guaranteed 300% trading returns on fake portal, displays fabricated profit dashboards, and locks funds under regulatory clearance pretexts.",
    expected_sequence=[
        JourneyStage.DISCOVERY,
        JourneyStage.CONTACT,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.REWARD_OR_FAKE_PROFIT,
        JourneyStage.PAYMENT_ESCALATION,
        JourneyStage.WITHDRAWAL_BLOCK,
        JourneyStage.RECOVERY_FEE,
    ],
    required_stages={
        JourneyStage.CONTACT,
        JourneyStage.INITIAL_PAYMENT,
    },
    optional_stages={
        JourneyStage.DISCOVERY,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.REWARD_OR_FAKE_PROFIT,
        JourneyStage.PAYMENT_ESCALATION,
        JourneyStage.WITHDRAWAL_BLOCK,
        JourneyStage.RECOVERY_FEE,
    },
    allowed_transitions={
        JourneyStage.DISCOVERY: [JourneyStage.CONTACT, JourneyStage.PLATFORM_MIGRATION],
        JourneyStage.CONTACT: [JourneyStage.TRUST_BUILDING, JourneyStage.PLATFORM_MIGRATION, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.PLATFORM_MIGRATION: [JourneyStage.INITIAL_PAYMENT, JourneyStage.REWARD_OR_FAKE_PROFIT],
        JourneyStage.INITIAL_PAYMENT: [JourneyStage.REWARD_OR_FAKE_PROFIT, JourneyStage.PAYMENT_ESCALATION],
        JourneyStage.REWARD_OR_FAKE_PROFIT: [JourneyStage.PAYMENT_ESCALATION, JourneyStage.WITHDRAWAL_BLOCK],
        JourneyStage.PAYMENT_ESCALATION: [JourneyStage.WITHDRAWAL_BLOCK, JourneyStage.RECOVERY_FEE],
        JourneyStage.WITHDRAWAL_BLOCK: [JourneyStage.RECOVERY_FEE, JourneyStage.EXIT],
        JourneyStage.RECOVERY_FEE: [JourneyStage.EXIT],
        JourneyStage.EXIT: [],
    },
    monetization_entry_stages={JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION},
    next_stage_hints={
        JourneyStage.INITIAL_PAYMENT: "The platform will likely show fake inflated profits to lure you into investing larger sums.",
        JourneyStage.REWARD_OR_FAKE_PROFIT: "Attempts to withdraw funds will likely be blocked citing security audits or capital gains tax.",
    },
)

DIGITAL_ARREST_TEMPLATE = JourneyTemplate(
    family_id="DIGITAL_ARREST",
    name="Digital Arrest & Law Enforcement Impersonation",
    description="Impersonates CBI, Police, Customs, or TRAI claiming an illegal narcotics package, enforces secret video-call isolation, and extorts verification deposits.",
    expected_sequence=[
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.URGENCY,
        JourneyStage.THREAT_OR_PRESSURE,
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.PAYMENT_ESCALATION,
    ],
    required_stages={
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.THREAT_OR_PRESSURE,
    },
    optional_stages={
        JourneyStage.URGENCY,
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.PAYMENT_ESCALATION,
    },
    allowed_transitions={
        JourneyStage.CONTACT: [JourneyStage.IMPERSONATION, JourneyStage.URGENCY, JourneyStage.THREAT_OR_PRESSURE],
        JourneyStage.IMPERSONATION: [JourneyStage.URGENCY, JourneyStage.THREAT_OR_PRESSURE, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.URGENCY: [JourneyStage.THREAT_OR_PRESSURE, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.THREAT_OR_PRESSURE: [JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION],
        JourneyStage.INITIAL_PAYMENT: [JourneyStage.PAYMENT_ESCALATION, JourneyStage.EXIT],
        JourneyStage.PAYMENT_ESCALATION: [JourneyStage.EXIT],
    },
    monetization_entry_stages={JourneyStage.INITIAL_PAYMENT, JourneyStage.PAYMENT_ESCALATION},
    next_stage_hints={
        JourneyStage.IMPERSONATION: "Callers claiming official authority often threaten arrest to force victims into secret video calls.",
        JourneyStage.THREAT_OR_PRESSURE: "Scammers typically demand an immediate 'security deposit' or asset verification transfer to drop charges.",
    },
)

KYC_BANK_TEMPLATE = JourneyTemplate(
    family_id="KYC_BANK",
    name="KYC Expiration & Bank Impersonation",
    description="Falsely alerts that bank account, SIM, or electricity will be blocked today, directing victim to fake portals to harvest OTPs or transfer unblock fees.",
    expected_sequence=[
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.URGENCY,
        JourneyStage.CREDENTIAL_REQUEST,
        JourneyStage.INITIAL_PAYMENT,
    ],
    required_stages={
        JourneyStage.CONTACT,
        JourneyStage.URGENCY,
    },
    optional_stages={
        JourneyStage.IMPERSONATION,
        JourneyStage.CREDENTIAL_REQUEST,
        JourneyStage.INITIAL_PAYMENT,
    },
    allowed_transitions={
        JourneyStage.CONTACT: [JourneyStage.IMPERSONATION, JourneyStage.URGENCY, JourneyStage.CREDENTIAL_REQUEST],
        JourneyStage.IMPERSONATION: [JourneyStage.URGENCY, JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.URGENCY: [JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.CREDENTIAL_REQUEST: [JourneyStage.INITIAL_PAYMENT, JourneyStage.EXIT],
        JourneyStage.INITIAL_PAYMENT: [JourneyStage.EXIT],
    },
    monetization_entry_stages={JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT},
    next_stage_hints={
        JourneyStage.URGENCY: "The sender will prompt you to enter netbanking credentials or share an OTP on a malicious link.",
        JourneyStage.CREDENTIAL_REQUEST: "Sharing credentials leads directly to unauthorized fund withdrawal from your bank account.",
    },
)

FAKE_SUPPORT_REFUND_TEMPLATE = JourneyTemplate(
    family_id="FAKE_SUPPORT_REFUND",
    name="Customer Support & Remote Access Refund Scam",
    description="Poses as ecommerce/e-wallet support offering a refund, instructs victim to install AnyDesk or screen-share, and steals credentials or initiates unauthorized debits.",
    expected_sequence=[
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.CREDENTIAL_REQUEST,
        JourneyStage.INITIAL_PAYMENT,
    ],
    required_stages={
        JourneyStage.CONTACT,
        JourneyStage.IMPERSONATION,
    },
    optional_stages={
        JourneyStage.TRUST_BUILDING,
        JourneyStage.CREDENTIAL_REQUEST,
        JourneyStage.INITIAL_PAYMENT,
    },
    allowed_transitions={
        JourneyStage.CONTACT: [JourneyStage.IMPERSONATION, JourneyStage.TRUST_BUILDING],
        JourneyStage.IMPERSONATION: [JourneyStage.TRUST_BUILDING, JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.TRUST_BUILDING: [JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT],
        JourneyStage.CREDENTIAL_REQUEST: [JourneyStage.INITIAL_PAYMENT, JourneyStage.EXIT],
        JourneyStage.INITIAL_PAYMENT: [JourneyStage.EXIT],
    },
    monetization_entry_stages={JourneyStage.CREDENTIAL_REQUEST, JourneyStage.INITIAL_PAYMENT},
    next_stage_hints={
        JourneyStage.IMPERSONATION: "The caller will ask you to install remote support software (AnyDesk, QuickSupport) to 'process your refund'.",
        JourneyStage.CREDENTIAL_REQUEST: "Once remote access is granted, the attacker will attempt to transfer funds from your banking app.",
    },
)

# Registry of all known journey templates
JOURNEY_TEMPLATES: Dict[str, JourneyTemplate] = {
    "JOB_TASK": JOB_TASK_TEMPLATE,
    "INVESTMENT": INVESTMENT_TEMPLATE,
    "DIGITAL_ARREST": DIGITAL_ARREST_TEMPLATE,
    "KYC_BANK": KYC_BANK_TEMPLATE,
    "FAKE_SUPPORT_REFUND": FAKE_SUPPORT_REFUND_TEMPLATE,
}
