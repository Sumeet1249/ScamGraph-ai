"""Normalized Semantic Representations for ScamGraph AI (Step 20).

Translates multi-dimensional entities, raw messages, incident timelines, and patterns
into canonical normalized text before vector embedding.

Rules:
- Never embed raw, messy JSON dumps directly.
- Normalize psychological lure, identity, tactics, and expected victim action.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SemanticRepresentation:
    """Structured, normalized semantic representation ready for vector encoding."""
    claimed_identity: Optional[str] = None
    intent: Optional[str] = None
    tactics: List[str] = field(default_factory=list)
    requested_action: Optional[str] = None
    financial_context: bool = False
    journey_stage: Optional[str] = None
    context_snippet: Optional[str] = None

    def to_normalized_text(self) -> str:
        """Renders canonical key-value text formatted for multilingual dense embedding."""
        lines = []
        if self.claimed_identity:
            lines.append(f"claimed_identity: {self.claimed_identity.strip()}")
        if self.intent:
            lines.append(f"intent: {self.intent.strip()}")
        if self.tactics:
            clean_tactics = ", ".join(sorted({t.strip().lower() for t in self.tactics}))
            lines.append(f"tactics: {clean_tactics}")
        if self.requested_action:
            lines.append(f"requested_action: {self.requested_action.strip()}")
        lines.append(f"financial_context: {'true' if self.financial_context else 'false'}")
        if self.journey_stage:
            lines.append(f"journey_stage: {self.journey_stage.strip().lower()}")
        if self.context_snippet:
            lines.append(f"context: {self.context_snippet.strip()}")
        return "\n".join(lines)


class SemanticRepresentationBuilder:
    """Builder methods producing consistent semantic representations."""

    @staticmethod
    def build_from_message(
        text: str,
        claimed_identity: Optional[str] = None,
        intent: Optional[str] = None,
        tactics: Optional[List[str]] = None,
        requested_action: Optional[str] = None,
        financial_context: bool = False,
        journey_stage: Optional[str] = None,
    ) -> SemanticRepresentation:
        """Builds a semantic representation from an incoming user or victim message."""
        extracted_tactics = list(tactics or [])
        lower_text = text.lower()

        # Heuristic hints if not provided
        if not claimed_identity:
            if any(b in lower_text for b in ["sbi", "hdfc", "icici", "axis", "bank"]):
                claimed_identity = "bank"
            elif any(e in lower_text for e in ["electricity", "power", "light", "bijli"]):
                claimed_identity = "electricity utility"
            elif any(c in lower_text for c in ["police", "cbi", "cyber crime", "court"]):
                claimed_identity = "law enforcement"
            elif any(j in lower_text for j in ["job", "rating", "part time", "task"]):
                claimed_identity = "employer / recruiter"

        if not intent:
            if any(k in lower_text for k in ["kyc", "pan", "aadhaar", "verify", "verification"]):
                intent = "account verification"
            elif any(d in lower_text for d in ["cutoff", "disconnect", "suspend", "block"]):
                intent = "threatened service disconnection"
            elif any(p in lower_text for p in ["pay", "deposit", "fee", "transfer"]):
                intent = "payment demand"

        if not requested_action:
            if "http" in lower_text or "www." in lower_text or ".com" in lower_text:
                requested_action = "open URL"
            elif any(o in lower_text for o in ["otp", "code", "pin"]):
                requested_action = "submit OTP or credentials"
            elif any(p in lower_text for p in ["upi", "pay", "deposit", "transfer"]):
                requested_action = "execute money transfer"

        is_fin = financial_context or any(
            f in lower_text for f in ["inr", "rs", "rupees", "bank", "account", "payment", "upi", "deposit", "bonus"]
        )

        return SemanticRepresentation(
            claimed_identity=claimed_identity,
            intent=intent,
            tactics=extracted_tactics,
            requested_action=requested_action,
            financial_context=is_fin,
            journey_stage=journey_stage,
            context_snippet=text[:250],
        )

    @staticmethod
    def build_from_incident(
        incident_id: str,
        title: str,
        events: List[Any],
        evidence: List[Any],
    ) -> SemanticRepresentation:
        """Builds a composite incident summary representation from chronological timeline."""
        tactics = []
        claimed_identity = None
        has_fin = False
        journey_stage = None
        requested_actions = []

        for ev in evidence:
            sig = getattr(ev, "signal", "")
            if "IMPERSONAT" in sig or "OFFICIAL" in sig:
                claimed_identity = getattr(ev, "observation", "impersonated entity")
            if any(t in sig for t in ["URGENCY", "FEAR", "THREAT", "LURE"]):
                tactics.append(sig.lower())
            if any(f in sig for f in ["PAYMENT", "FEE", "DEPOSIT", "VPA"]):
                has_fin = True

        for event in events:
            etype = getattr(event, "event_type", None)
            val = etype.value if hasattr(etype, "value") else str(etype)
            if "PAYMENT" in val:
                has_fin = True
                requested_actions.append("execute payment")
                journey_stage = "PAYMENT_REQUEST"
            elif "URL" in val:
                requested_actions.append("open URL")
                journey_stage = "SUSPICIOUS_LINK"
            elif "OTP" in val or "CREDENTIAL" in val:
                requested_actions.append("provide credentials / OTP")
                journey_stage = "CREDENTIAL_HARVEST"

        return SemanticRepresentation(
            claimed_identity=claimed_identity or "unspecified",
            intent=title,
            tactics=tactics or ["social engineering"],
            requested_action=", ".join(requested_actions) if requested_actions else "user interaction",
            financial_context=has_fin,
            journey_stage=journey_stage or "INITIAL_CONTACT",
            context_snippet=f"Incident {incident_id}: {title}",
        )

    @staticmethod
    def build_from_pattern(
        pattern_id: str,
        pattern_name: str,
        tactics: List[str],
        expected_stages: List[str],
        description: str = "",
    ) -> SemanticRepresentation:
        """Builds normalized semantic text for known scam pattern taxonomy."""
        return SemanticRepresentation(
            claimed_identity=pattern_name,
            intent=f"Scam Pattern: {pattern_id}",
            tactics=tactics,
            requested_action="coerced action / payment",
            financial_context=True,
            journey_stage=expected_stages[-1] if expected_stages else None,
            context_snippet=description or pattern_name,
        )

    @staticmethod
    def build_from_campaign(
        campaign_id: str,
        name: str,
        pattern_type: str,
        tactics: List[str],
        description: str = "",
    ) -> SemanticRepresentation:
        """Builds normalized semantic text for syndicated campaign clusters."""
        return SemanticRepresentation(
            claimed_identity=name,
            intent=f"Attack Campaign: {pattern_type}",
            tactics=tactics,
            requested_action="financial transfer / credential harvest",
            financial_context=True,
            journey_stage="CAMPAIGN_CLUSTER",
            context_snippet=description or f"Campaign cluster: {name} ({campaign_id})",
        )
