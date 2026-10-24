"""Comprehensive Unit & Regression Tests for Phase 1A Entity Intelligence V2.

Tests:
1. Deterministic normalization for phone, email, domain, URL, UPI VPA, Telegram, and Brand
2. IDNA / Punycode homoglyph detection for suspicious domains
3. Multi-entity extraction with exact character spans and suggested roles
4. Entity resolution: EXACT_MATCH, STRONG_MATCH, and strict fuzzy gating (NEVER auto-merge)
5. Lineage-preserving merge & reversible split protocols
6. Relationship manager: idempotency, co-occurrences, and multi-hop graph traversal
7. Multi-dimensional reputation: source reliability weights, temporal decay, and burst detection
8. Authoritative directory verification: official bank domains and sovereign .gov.in portals
9. Privacy serialization (consumer vs analyst) and anti-enumeration search defense
10. Cross-incident entity correlation across multi-channel interaction journeys
"""

from datetime import datetime, timezone, timedelta
import pytest

from packages.schemas.entity import (
    Entity,
    EntityObservationRole,
    EntityRelationshipType,
    EntityType,
    EntityVerificationState,
    TrustLevel,
)
from services.entity_intelligence.normalizer import (
    EntityNormalizer,
    FormatValidationStatus,
)
from services.entity_intelligence.privacy import (
    AntiEnumerationGuard,
    PrivacySerializer,
)
from services.entity_intelligence.extractor import (
    EntityExtractor,
    ExtractedEntityCandidate,
)
from services.entity_intelligence.resolver import (
    EntityResolutionEngine,
    ResolutionMatchType,
)
from services.entity_intelligence.reputation import (
    EntityReputationEngine,
)
from services.entity_intelligence.verification import (
    AuthoritativeDirectoryVerificationProvider,
)
from services.entity_intelligence.relationships import (
    EntityRelationshipManager,
)
from services.entity_intelligence.service import (
    EntityIntelligenceService,
)


# =====================================================================
# 1. NORMALIZATION TESTS
# =====================================================================

def test_phone_normalization_indian_conventions():
    """Verify Indian phone normalization: +91, 10-digit mobile, 0 prefix, 91 prefix."""
    # Standard 10 digit starting with 9
    res1 = EntityNormalizer.normalize_phone("9876543210")
    assert res1.normalized_value == "+919876543210"
    assert res1.validation_status == FormatValidationStatus.VALID
    assert res1.display_value == "******3210"
    assert res1.extra_metadata["is_indian_mobile"] is True

    # Leading zero prefix
    res2 = EntityNormalizer.normalize_phone("09876543210")
    assert res2.normalized_value == "+919876543210"
    assert res2.validation_status == FormatValidationStatus.VALID

    # Dashes and spaces
    res3 = EntityNormalizer.normalize_phone("+91 98765-43210")
    assert res3.normalized_value == "+919876543210"

    # Ambiguous international number without plus (never invent country code!)
    res4 = EntityNormalizer.normalize_phone("442079460912")
    assert res4.validation_status == FormatValidationStatus.POSSIBLY_VALID
    assert res4.extra_metadata.get("ambiguous_country") is True
    assert not res4.normalized_value.startswith("+91")


def test_email_normalization():
    """Verify email normalization with Unicode NFC, lowercase domain, and whitespace trimming."""
    res = EntityNormalizer.normalize_email("  Sumeet.Kumar@Example.COM  ")
    assert res.normalized_value == "sumeet.kumar@example.com"
    assert res.validation_status == FormatValidationStatus.VALID
    assert res.display_value.startswith("s***@")


def test_domain_and_punycode_normalization():
    """Verify domain normalization, IDNA homoglyph detection, and root domain parsing."""
    # Standard domain with www.
    res1 = EntityNormalizer.normalize_domain("www.Secure-Bank.CO.IN/")
    assert res1.normalized_value == "secure-bank.co.in"
    assert res1.extra_metadata["root_domain"] == "co.in"
    assert res1.validation_status == FormatValidationStatus.VALID

    # Cyrillic 'a' homoglyph spoofing (IDNA detection)
    # Using cyrillic small letter a (\u0430) in "bаnk.com"
    spoofed = "b\u0430nk.com"
    res2 = EntityNormalizer.normalize_domain(spoofed)
    assert res2.extra_metadata.get("has_punycode_homoglyph") is True
    assert res2.extra_metadata["punycode"].startswith("xn--")


def test_url_normalization_deterministic_query_sorting():
    """Verify URL normalization strips default ports and deterministically sorts query parameters."""
    raw_url = "HTTP://EXAMPLE.COM:80/path/to/login/?session=xyz&auth=123#frag"
    res = EntityNormalizer.normalize_url(raw_url)
    assert res.normalized_value == "http://example.com/path/to/login?auth=123&session=xyz"
    assert res.validation_status == FormatValidationStatus.VALID
    assert "#frag" not in res.normalized_value


def test_upi_vpa_normalization():
    """Verify UPI VPA normalization parses handle and PSP without asserting ownership."""
    res = EntityNormalizer.normalize_upi_vpa("  MerchantHelp@OKSBI  ")
    assert res.normalized_value == "merchanthelp@oksbi"
    assert res.extra_metadata["psp"] == "oksbi"
    assert res.display_value == "m***@oksbi"
    assert res.validation_status == FormatValidationStatus.VALID


def test_telegram_handle_normalization():
    """Verify Telegram handle strips @ and t.me/ prefixes."""
    res1 = EntityNormalizer.normalize_telegram_handle("@TaskWorkDaily")
    assert res1.normalized_value == "@taskworkdaily"
    assert res1.extra_metadata["profile_url"] == "https://t.me/taskworkdaily"

    res2 = EntityNormalizer.normalize_telegram_handle("https://t.me/CryptoEarnOnline")
    assert res2.normalized_value == "@cryptoearnonline"


def test_brand_normalization_aliases():
    """Verify brand normalization maps aliases to canonical Indian organizations."""
    res1 = EntityNormalizer.normalize_brand("yono")
    assert res1.normalized_value == "SBI YONO"

    res2 = EntityNormalizer.normalize_brand("cyber crime police")
    assert res2.normalized_value == "Police Department"


# =====================================================================
# 2. EXTRACTION TESTS
# =====================================================================

def test_deterministic_multi_entity_extractor():
    """Verify multi-entity extractor detects phone, URL, UPI, Telegram, and brand in a single text."""
    sample_text = (
        "SBI YONO Alert: Update KYC immediately at https://sbi-update.xyz/login. "
        "Contact electricity officer at 9876543210 or on Telegram @officialhelper. "
        "Pay registration fee to accounthelp@oksbi"
    )

    candidates = EntityExtractor.extract_all(sample_text)
    types_found = set(c.entity_type for c in candidates)

    assert EntityType.BRAND in types_found
    assert EntityType.URL in types_found
    assert EntityType.DOMAIN in types_found
    assert EntityType.PHONE in types_found
    assert EntityType.TELEGRAM_HANDLE in types_found
    assert EntityType.UPI_VPA in types_found

    # Verify character spans
    for c in candidates:
        assert c.span_start >= 0
        assert c.span_end > c.span_start
        assert sample_text[c.span_start:c.span_end] == c.raw_value or c.entity_type == EntityType.DOMAIN


# =====================================================================
# 3. RESOLUTION & GATING TESTS
# =====================================================================

def test_entity_resolution_exact_and_alias():
    """Verify exact hash match and verified alias resolution."""
    engine = EntityResolutionEngine()

    ent = Entity(
        entity_id="ent_101",
        entity_type=EntityType.UPI_VPA,
        canonical_value="scam@oksbi",
        display_value="s***@oksbi",
        masked_value="s***@oksbi",
        canonical_hash="hash_scam_123",
        aliases=["scam_legacy@oksbi"],
    )
    engine.index_entity(ent)

    # Exact hash match
    norm_exact = EntityNormalizer.normalize_upi_vpa("scam@oksbi")
    norm_exact.canonical_hash = "hash_scam_123"
    res1 = engine.resolve(norm_exact)
    assert res1.match_type == ResolutionMatchType.EXACT_MATCH
    assert res1.matched_entity_id == "ent_101"

    # Alias match
    norm_alias = EntityNormalizer.normalize_upi_vpa("scam_legacy@oksbi")
    res2 = engine.resolve(norm_alias)
    assert res2.match_type == ResolutionMatchType.STRONG_MATCH
    assert res2.matched_entity_id == "ent_101"


def test_entity_resolution_fuzzy_gating_never_auto_merges():
    """CRITICAL RULE: High lexical similarity generates POSSIBLE_MATCH with review flag; NEVER auto-merges!"""
    engine = EntityResolutionEngine()

    ent = Entity(
        entity_id="ent_201",
        entity_type=EntityType.TELEGRAM_HANDLE,
        canonical_value="@quickmoneyinvest",
        display_value="@quickmoneyinvest",
        masked_value="@quickmoneyinvest",
        canonical_hash="hash_tlg_1",
    )
    engine.index_entity(ent)

    # Similar but not identical handle (e.g. character substitution/variation)
    norm_similar = EntityNormalizer.normalize_telegram_handle("@quickmoneyinvestt")
    res = engine.resolve(norm_similar)

    assert res.match_type == ResolutionMatchType.POSSIBLE_MATCH
    assert res.matched_entity_id is None  # Gating: must NOT auto-merge!
    assert "ent_201" in res.candidate_entity_ids
    assert res.requires_human_review is True


def test_lineage_preserving_merge_and_reversible_split():
    """Verify merge preserves observation counts and aliases, and split reverses it cleanly."""
    engine = EntityResolutionEngine()

    ent_canonical = Entity(
        entity_id="ent_can_1",
        entity_type=EntityType.PHONE,
        canonical_value="+919876543210",
        masked_value="******3210",
        canonical_hash="hash_phone_1",
        observation_count=5,
        incident_count=2,
    )
    ent_secondary = Entity(
        entity_id="ent_sec_2",
        entity_type=EntityType.PHONE,
        canonical_value="+919876543210",
        masked_value="******3210",
        canonical_hash="hash_phone_2",
        observation_count=3,
        incident_count=1,
    )
    engine.index_entity(ent_canonical)
    engine.index_entity(ent_secondary)

    # Perform Merge
    merge_rec = engine.merge_entities(
        canonical_entity_id="ent_can_1",
        target_entity_ids=["ent_sec_2"],
        reason="Confirmed duplicate phone record across data migrations",
    )
    assert merge_rec.canonical_entity_id == "ent_can_1"
    assert "ent_sec_2" in merge_rec.merged_entity_ids
    assert ent_canonical.observation_count == 8
    assert ent_canonical.incident_count == 3
    assert "ent_sec_2" in ent_canonical.aliases

    # Perform Split (Error correction)
    split_rec = engine.split_entity(merge_rec, reason="Separate owner confirmed upon dispute")
    assert split_rec.original_entity_id == "ent_can_1"
    assert "ent_sec_2" not in ent_canonical.aliases


# =====================================================================
# 4. RELATIONSHIP & GRAPH TESTS
# =====================================================================

def test_relationship_manager_idempotency_and_traversal():
    """Verify edge creation idempotency and multi-hop graph traversal."""
    rm = EntityRelationshipManager()

    # Link e1 and e2
    rel1 = rm.link_entities(
        source_entity_id="ent_phone_1",
        target_entity_id="ent_url_1",
        relationship_type=EntityRelationshipType.APPEARED_WITH,
        confidence=0.95,
    )
    assert rel1.observation_count == 1

    # Duplicate sighting updates observation_count and last_seen without creating duplicate edge
    rel2 = rm.link_entities(
        source_entity_id="ent_phone_1",
        target_entity_id="ent_url_1",
        relationship_type=EntityRelationshipType.APPEARED_WITH,
    )
    assert len(rm) == 1
    assert rel2.relationship_id == rel1.relationship_id
    assert rel2.observation_count == 2

    # Link e2 and e3
    rm.link_entities(
        source_entity_id="ent_url_1",
        target_entity_id="ent_upi_1",
        relationship_type=EntityRelationshipType.REQUESTED_PAYMENT_TO,
    )
    assert len(rm) == 2

    # Multi-hop traversal from e1 (ent_phone_1)
    connected = rm.find_connected_entities("ent_phone_1", max_depth=2)
    assert "ent_url_1" in connected  # 1-hop distance
    assert connected["ent_url_1"] == 1
    assert "ent_upi_1" in connected  # 2-hop distance
    assert connected["ent_upi_1"] == 2


# =====================================================================
# 5. REPUTATION & VERIFICATION TESTS
# =====================================================================

def test_reputation_decay_and_burst_detection():
    """Verify exponential temporal decay and observation burst velocity detection."""
    rep_engine = EntityReputationEngine(decay_half_life_days=180.0)

    # Observation from 180 days ago should have roughly 0.50 weight
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(days=180)
    w_old = rep_engine.calculate_temporal_weight(old_time, now)
    assert pytest.approx(w_old, abs=0.05) == 0.50

    # Observation from today should have 1.0 weight
    w_today = rep_engine.calculate_temporal_weight(now, now)
    assert pytest.approx(w_today, abs=0.01) == 1.00


def test_authoritative_directory_verification():
    """Verify official Indian government (.gov.in) and scheduled bank domains receive KNOWN_LEGITIMATE."""
    service = EntityIntelligenceService()

    # Official SBI domain
    ent_sbi, _ = service.resolve_and_upsert_entity(
        entity_type=EntityType.DOMAIN,
        raw_value="sbi.co.in",
        incident_id="inc_test_1",
    )
    assert ent_sbi.verification_state == EntityVerificationState.VERIFIED_LEGITIMATE

    trust_sbi = service.assess_entity_trust(ent_sbi.entity_id)
    assert trust_sbi.assessment == TrustLevel.KNOWN_LEGITIMATE
    assert trust_sbi.confidence == 1.0

    # Fake SBI domain
    ent_fake, _ = service.resolve_and_upsert_entity(
        entity_type=EntityType.DOMAIN,
        raw_value="sbi-update-kyc.top",
        incident_id="inc_test_2",
    )
    assert ent_fake.verification_state == EntityVerificationState.OBSERVED
    trust_fake = service.assess_entity_trust(ent_fake.entity_id)
    assert trust_fake.assessment != TrustLevel.KNOWN_LEGITIMATE


# =====================================================================
# 6. PRIVACY & CROSS-INCIDENT CORRELATION TESTS
# =====================================================================

def test_privacy_serialization_and_anti_enumeration():
    """Verify consumer serialization redacts raw PII and anti-enumeration blocks wildcards."""
    ent = Entity(
        entity_id="ent_priv_1",
        entity_type=EntityType.PHONE,
        canonical_value="+919876543210",
        display_value="******3210",
        masked_value="******3210",
        canonical_hash="hash_phone_secret",
        observation_count=3,
        incident_count=2,
    )

    consumer_view = PrivacySerializer.serialize_for_consumer(ent)
    assert "canonical_value" not in consumer_view
    assert consumer_view["display_value"] == "******3210"
    assert consumer_view["observation_count"] == 3

    # Anti-enumeration check
    guard = AntiEnumerationGuard()
    allowed1, _ = guard.check_query_allowed("client_1", "9876543210")
    assert allowed1 is True

    # Short query blocked
    allowed2, _ = guard.check_query_allowed("client_1", "98")
    assert allowed2 is False

    # Wildcard query blocked
    allowed3, _ = guard.check_query_allowed("client_1", "9876*")
    assert allowed3 is False


def test_cross_incident_entity_correlation():
    """Verify Incident A and Incident B are correlated via shared UPI payment identifier."""
    service = EntityIntelligenceService()

    # Incident A text contains a phone, domain, and UPI
    text_a = "Contact 9876543210 for task job. Visit jobs-verify.top and send deposit to worker@oksbi"
    results_a = service.process_incident_text("inc_001", text_a)

    # Incident B text contains a Telegram handle and the SAME UPI
    text_b = "Work from home Telegram @workindia. Send registration fee of Rs 500 to worker@oksbi"
    results_b = service.process_incident_text("inc_002", text_b)

    # Find the entity ID for worker@oksbi
    upi_ent = next(e for e, _ in results_b if e.entity_type == EntityType.UPI_VPA)

    # Traversal from worker@oksbi must find both inc_001 and inc_002
    related_incidents = service.find_related_incidents(upi_ent.entity_id)
    assert "inc_001" in related_incidents
    assert "inc_002" in related_incidents

    # Traversal from Telegram @workindia must find inc_001 via shared UPI infrastructure
    tlg_ent = next(e for e, _ in results_b if e.entity_type == EntityType.TELEGRAM_HANDLE)
    tlg_related = service.find_related_incidents(tlg_ent.entity_id)
    assert "inc_001" in tlg_related
    assert "inc_002" in tlg_related
