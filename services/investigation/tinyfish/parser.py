"""TinyFish Observation Parser (Step 17).

Translates structured observables into canonical ScamGraph Evidence and Entity objects.
All generated Evidence objects have source = EvidenceSource.TINYFISH.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse
from uuid import uuid4

from services.api.app.domain.enums import EntityType, EvidenceSource
from services.api.app.domain.models import Entity, Evidence
from services.investigation.tinyfish.models import TinyFishObservationData

logger = logging.getLogger("investigation.tinyfish.parser")


class TinyFishParser:
    """Parses raw TinyFish JSON observables into canonical Evidence and Entity objects."""

    @classmethod
    def parse(
        cls,
        incident_id: str,
        inspected_url: str,
        raw_data: Dict[str, Any],
    ) -> Tuple[TinyFishObservationData, List[Evidence], List[Entity]]:
        """Parses observables dictionary and returns structured data, evidence, and entities."""
        if not isinstance(raw_data, dict):
            logger.warning("Malformed TinyFish payload: expected dict, got %s", type(raw_data))
            return TinyFishObservationData(), [], []

        # Validate with Pydantic model
        try:
            obs = TinyFishObservationData(**raw_data)
        except Exception:
            # Fallback to permissive extraction if schema contains unexpected fields
            obs = TinyFishObservationData(
                page_title=raw_data.get("page_title"),
                claimed_brands=raw_data.get("claimed_brands") or [],
                login_fields=raw_data.get("login_fields") or [],
                credential_fields=raw_data.get("credential_fields") or [],
                otp_fields=raw_data.get("otp_fields") or [],
                payment_fields=raw_data.get("payment_fields") or [],
                personal_information_fields=raw_data.get("personal_information_fields") or [],
                phone_numbers=raw_data.get("phone_numbers") or [],
                email_addresses=raw_data.get("email_addresses") or [],
                payment_identifiers=raw_data.get("payment_identifiers") or [],
                linked_domains=raw_data.get("linked_domains") or [],
                redirects=raw_data.get("redirects") or [],
                urgency_claims=raw_data.get("urgency_claims") or [],
                financial_claims=raw_data.get("financial_claims") or [],
                brand_impersonation_observations=raw_data.get("brand_impersonation_observations") or [],
                observable_actions=raw_data.get("observable_actions") or [],
                evidence=raw_data.get("evidence") or [],
            )

        evidence_items: List[Evidence] = []
        entities: List[Entity] = []
        now = datetime.now(timezone.utc)

        # ── 1. OTP Fields Observed ──
        if obs.otp_fields:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-otp-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="OTP_FIELD_PRESENT",
                    observation=f"DOM contains one-time password input field(s): {', '.join(obs.otp_fields[:3])}",
                    confidence=0.98,
                    timestamp=now,
                )
            )

        # ── 2. Credential Fields Observed ──
        if obs.credential_fields:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-cred-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="CREDENTIAL_COLLECTION",
                    observation=f"DOM contains password/credential harvesting field(s): {', '.join(obs.credential_fields[:3])}",
                    confidence=0.95,
                    timestamp=now,
                )
            )

        # ── 3. Login Form Present ──
        if obs.login_fields:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-login-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="LOGIN_FORM_PRESENT",
                    observation=f"Login authentication interface detected with fields: {', '.join(obs.login_fields[:3])}",
                    confidence=0.90,
                    timestamp=now,
                )
            )

        # ── 4. Payment Fields Observed ──
        if obs.payment_fields:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-payf-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="PAYMENT_FIELD_PRESENT",
                    observation=f"Payment/card/PIN entry input elements detected: {', '.join(obs.payment_fields[:3])}",
                    confidence=0.92,
                    timestamp=now,
                )
            )

        # ── 5. Payment Identifiers Observed ──
        if obs.payment_identifiers:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-payid-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="PAYMENT_IDENTIFIER_OBSERVED",
                    observation=f"Payment destination handles / wallets observed on page: {', '.join(obs.payment_identifiers[:3])}",
                    confidence=0.94,
                    timestamp=now,
                )
            )
            for pid in obs.payment_identifiers:
                entities.append(
                    Entity(
                        id=f"ent-pay-{uuid4().hex[:8]}",
                        entity_type=EntityType.PAYMENT_ENTITY,
                        normalized_value=pid.lower().strip(),
                        display_value=pid.strip(),
                    )
                )

        # ── 6. Claimed Brands ──
        if obs.claimed_brands:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-brand-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="CLAIMED_BRAND",
                    observation=f"Website layout claims association with brand(s): {', '.join(obs.claimed_brands[:3])}",
                    confidence=0.90,
                    timestamp=now,
                )
            )
            for brand in obs.claimed_brands:
                entities.append(
                    Entity(
                        id=f"ent-brd-{uuid4().hex[:8]}",
                        entity_type=EntityType.BRAND,
                        normalized_value=brand.lower().strip(),
                        display_value=brand.strip(),
                    )
                )

        # ── 7. Phone Numbers ──
        if obs.phone_numbers:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-phone-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="PHONE_OBSERVED",
                    observation=f"Contact telephone number(s) observed: {', '.join(obs.phone_numbers[:3])}",
                    confidence=0.92,
                    timestamp=now,
                )
            )
            for phone in obs.phone_numbers:
                clean_phone = phone.replace(" ", "").replace("-", "")
                entities.append(
                    Entity(
                        id=f"ent-ph-{uuid4().hex[:8]}",
                        entity_type=EntityType.PHONE,
                        normalized_value=clean_phone,
                        display_value=phone.strip(),
                    )
                )

        # ── 8. Email Addresses ──
        if obs.email_addresses:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-email-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="EMAIL_OBSERVED",
                    observation=f"Contact email address(es) observed: {', '.join(obs.email_addresses[:3])}",
                    confidence=0.92,
                    timestamp=now,
                )
            )
            for email in obs.email_addresses:
                entities.append(
                    Entity(
                        id=f"ent-em-{uuid4().hex[:8]}",
                        entity_type=EntityType.EMAIL,
                        normalized_value=email.lower().strip(),
                        display_value=email.strip(),
                    )
                )

        # ── 9. Urgency Language ──
        if obs.urgency_claims:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-urg-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="URGENCY_LANGUAGE",
                    observation=f"Urgent pressure claims observed on page: '{obs.urgency_claims[0]}'",
                    confidence=0.88,
                    timestamp=now,
                )
            )

        # ── 10. Financial Claims ──
        if obs.financial_claims:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-fin-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="FINANCIAL_CLAIM",
                    observation=f"Financial promise or fee claim observed on page: '{obs.financial_claims[0]}'",
                    confidence=0.88,
                    timestamp=now,
                )
            )

        # ── 11. Redirects ──
        if obs.redirects:
            evidence_items.append(
                Evidence(
                    id=f"evi-tf-redir-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.TINYFISH,
                    signal="REDIRECT_OBSERVED",
                    observation=f"TinyFish browser observed {len(obs.redirects)} redirection step(s)",
                    confidence=0.85,
                    timestamp=now,
                )
            )

        # ── Add Domain and URL Entities ──
        try:
            parsed = urlparse(inspected_url)
            if parsed.hostname:
                entities.append(
                    Entity(
                        id=f"ent-dom-{uuid4().hex[:8]}",
                        entity_type=EntityType.DOMAIN,
                        normalized_value=parsed.hostname.lower(),
                        display_value=parsed.hostname,
                    )
                )
            entities.append(
                Entity(
                    id=f"ent-url-{uuid4().hex[:8]}",
                    entity_type=EntityType.URL,
                    normalized_value=inspected_url.lower(),
                    display_value=inspected_url,
                )
            )
        except Exception:
            pass

        return obs, evidence_items, entities
