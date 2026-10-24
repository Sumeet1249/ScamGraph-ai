"""Ontology and taxonomy definitions for ScamGraph Tactic Intelligence Engine V2."""

from typing import Dict, List, Set
from packages.schemas.tactics import TacticType, ActionRequestedType

# Severity Mapping per Tactic
TACTIC_SEVERITY: Dict[TacticType, str] = {
    TacticType.AUTHORITY: "HIGH",
    TacticType.URGENCY: "MEDIUM",
    TacticType.FEAR: "HIGH",
    TacticType.GREED: "MEDIUM",
    TacticType.SCARCITY: "LOW",
    TacticType.SOCIAL_PROOF: "LOW",
    TacticType.ROMANCE: "MEDIUM",
    TacticType.TRUST_BUILDING: "LOW",
    TacticType.SECRECY: "HIGH",
    TacticType.ISOLATION: "CRITICAL",
    TacticType.RECIPROCITY: "MEDIUM",
    TacticType.LOSS_AVERSION: "HIGH",
    TacticType.FAKE_REWARD: "MEDIUM",
    TacticType.THREAT: "CRITICAL",
    TacticType.IMPERSONATION: "HIGH",
    TacticType.PAYMENT_PRESSURE: "CRITICAL",
    TacticType.CREDENTIAL_PRESSURE: "CRITICAL",
    TacticType.REMOTE_ACCESS_PRESSURE: "CRITICAL",
    TacticType.PLATFORM_MIGRATION: "MEDIUM",
    TacticType.COMPLIANCE_PRESSURE: "HIGH",
}

# Critical Safety Tactics (directly require urgent protective interventions)
CRITICAL_SAFETY_TACTICS: Set[TacticType] = {
    TacticType.ISOLATION,
    TacticType.SECRECY,
    TacticType.PAYMENT_PRESSURE,
    TacticType.CREDENTIAL_PRESSURE,
    TacticType.REMOTE_ACCESS_PRESSURE,
    TacticType.THREAT,
}

# Natural requested actions associated with each tactic
TACTIC_DEFAULT_ACTIONS: Dict[TacticType, List[ActionRequestedType]] = {
    TacticType.CREDENTIAL_PRESSURE: [ActionRequestedType.SHARE_OTP, ActionRequestedType.SHARE_CREDENTIAL],
    TacticType.REMOTE_ACCESS_PRESSURE: [ActionRequestedType.INSTALL_APP, ActionRequestedType.SHARE_SCREEN, ActionRequestedType.DOWNLOAD_FILE],
    TacticType.PAYMENT_PRESSURE: [ActionRequestedType.SEND_PAYMENT, ActionRequestedType.APPROVE_UPI_REQUEST, ActionRequestedType.PAY_FEE],
    TacticType.SECRECY: [ActionRequestedType.KEEP_SECRET],
    TacticType.ISOLATION: [ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.KEEP_SECRET],
    TacticType.PLATFORM_MIGRATION: [ActionRequestedType.MOVE_PLATFORM, ActionRequestedType.ADD_CONTACT],
    TacticType.FAKE_REWARD: [ActionRequestedType.CLICK_LINK, ActionRequestedType.SCAN_QR],
    TacticType.AUTHORITY: [ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
    TacticType.URGENCY: [ActionRequestedType.CLICK_LINK, ActionRequestedType.SEND_PAYMENT, ActionRequestedType.REPLY],
    TacticType.FEAR: [ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.SEND_PAYMENT],
    TacticType.GREED: [ActionRequestedType.CLICK_LINK, ActionRequestedType.MOVE_PLATFORM],
    TacticType.SCARCITY: [ActionRequestedType.CLICK_LINK, ActionRequestedType.REPLY],
    TacticType.SOCIAL_PROOF: [ActionRequestedType.MOVE_PLATFORM],
    TacticType.ROMANCE: [ActionRequestedType.SEND_PAYMENT, ActionRequestedType.PAY_FEE],
    TacticType.TRUST_BUILDING: [ActionRequestedType.REPLY, ActionRequestedType.INVEST_MORE],
    TacticType.RECIPROCITY: [ActionRequestedType.SEND_PAYMENT, ActionRequestedType.INVEST_MORE],
    TacticType.LOSS_AVERSION: [ActionRequestedType.SEND_PAYMENT, ActionRequestedType.PAY_FEE],
    TacticType.THREAT: [ActionRequestedType.SEND_PAYMENT, ActionRequestedType.DO_NOT_DISCONNECT],
    TacticType.IMPERSONATION: [ActionRequestedType.CALL_NUMBER, ActionRequestedType.CLICK_LINK, ActionRequestedType.REPLY],
    TacticType.COMPLIANCE_PRESSURE: [ActionRequestedType.DO_NOT_DISCONNECT, ActionRequestedType.REPLY],
}

# Consumer Plain-Language Tactic Labels
CONSUMER_TACTIC_NAMES: Dict[TacticType, str] = {
    TacticType.AUTHORITY: "Claiming official authority or law enforcement status",
    TacticType.URGENCY: "Creating artificial urgency or strict time deadlines",
    TacticType.FEAR: "Threatening legal arrest, account closure, or penalties",
    TacticType.GREED: "Promising unrealistic high returns or guaranteed profits",
    TacticType.SCARCITY: "Claiming limited opportunity or scarce slots",
    TacticType.SOCIAL_PROOF: "Showing fake member earnings or group testimonials",
    TacticType.ROMANCE: "Building fake emotional or matrimonial intimacy",
    TacticType.TRUST_BUILDING: "Offering small initial profits or grooming trust",
    TacticType.SECRECY: "Demanding that you keep this conversation secret from family or bank",
    TacticType.ISOLATION: "Insisting you stay on call and avoid speaking with anyone",
    TacticType.RECIPROCITY: "Using small favors or rewards to demand larger deposits",
    TacticType.LOSS_AVERSION: "Threatening total loss of your money unless fees are paid",
    TacticType.FAKE_REWARD: "Claiming unverified prizes, lottery wins, or gift vouchers",
    TacticType.THREAT: "Making direct threats of blackmail, raids, or exposure",
    TacticType.IMPERSONATION: "Impersonating reputable organizations, couriers, or banks",
    TacticType.PAYMENT_PRESSURE: "Pressuring you to make an immediate money transfer or UPI deposit",
    TacticType.CREDENTIAL_PRESSURE: "Demanding your secret OTP, passwords, or ATM PIN",
    TacticType.REMOTE_ACCESS_PRESSURE: "Asking you to install remote support apps or share your screen",
    TacticType.PLATFORM_MIGRATION: "Attempting to move you to private channels like Telegram or WhatsApp",
    TacticType.COMPLIANCE_PRESSURE: "Demanding strict obedience without asking questions",
}
