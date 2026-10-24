"""Entity Linking for Tactic Signals in ScamGraph AI V2.

Associates psychological tactics and requested actions with specific entity identifiers
(e.g., impersonated brands, payment recipients, and migrated social handles).
"""

from typing import Dict, List, Optional
from packages.schemas.entity import Entity, EntityType
from packages.schemas.tactics import ActionRequestedType, TacticSignal, TacticType


class TacticEntityLinker:
    """Correlates detected tactics with extracted entities."""

    def link_entities_to_tactics(
        self,
        signals: List[TacticSignal],
        entities: List[Entity],
    ) -> List[TacticSignal]:
        """Enriches tactic signals with relevant entity IDs."""
        if not signals or not entities:
            return signals

        # Index entities by type
        by_type: Dict[EntityType, List[Entity]] = {}
        for ent in entities:
            by_type.setdefault(ent.entity_type, []).append(ent)

        for sig in signals:
            linked_ids: List[str] = list(sig.related_entities)

            # 1. Impersonation & Authority -> Brand / Organization
            if sig.tactic in (TacticType.IMPERSONATION, TacticType.AUTHORITY):
                for ent in by_type.get(EntityType.BRAND, []) + by_type.get(EntityType.ORGANIZATION, []):
                    if ent.entity_id not in linked_ids:
                        linked_ids.append(ent.entity_id)

            # 2. Payment Pressure -> Payment Identifiers
            if sig.tactic == TacticType.PAYMENT_PRESSURE:
                for ent in by_type.get(EntityType.UPI_VPA, []) + by_type.get(EntityType.BANK_ACCOUNT_TOKEN, []) + by_type.get(EntityType.QR_PAYLOAD, []):
                    if ent.entity_id not in linked_ids:
                        linked_ids.append(ent.entity_id)

            # 3. Platform Migration -> Social Handles / WhatsApp
            if sig.tactic == TacticType.PLATFORM_MIGRATION:
                for ent in by_type.get(EntityType.TELEGRAM_HANDLE, []) + by_type.get(EntityType.WHATSAPP_NUMBER, []) + by_type.get(EntityType.SOCIAL_ACCOUNT, []):
                    if ent.entity_id not in linked_ids:
                        linked_ids.append(ent.entity_id)

            # 4. Link Clicks -> URL / Domain
            if ActionRequestedType.CLICK_LINK in sig.requested_actions:
                for ent in by_type.get(EntityType.URL, []) + by_type.get(EntityType.DOMAIN, []):
                    if ent.entity_id not in linked_ids:
                        linked_ids.append(ent.entity_id)

            sig.related_entities = linked_ids

        return signals
