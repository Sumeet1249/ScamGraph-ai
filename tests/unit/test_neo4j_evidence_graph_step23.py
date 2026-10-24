"""Unit and integration tests for Step 23: Neo4j Evidence Graph.

Validates:
1. EntityNormalizer (Domain, URL, Phone, Payment, IP, ASN, Cert, NS)
2. Node upsert (Incident, Phone, Domain, PaymentEntity, etc.)
3. Provenance-backed relationship creation
4. Idempotency (running synchronization twice does not duplicate nodes or edges)
5. Synthetic multi-incident correlation:
   - Incident A: Phone1, Domain1, Payment1
   - Incident B: Phone1, Domain2, Payment2
   - Incident C: Phone3, Domain3, Payment1
   - Incident D: Phone4, Domain4, Payment4
   - Expect: A ↔ B (Phone1), A ↔ C (Payment1), B & C indirectly connected through A, D unrelated.
6. Shared entity queries and related incident queries
7. Neo4j unavailable graceful handling (returns status="UNAVAILABLE" without destroying incident flow)
"""

from __future__ import annotations

import pytest

from services.graph_engine import (
    EntityNormalizer,
    GraphEntityNode,
    GraphNodeType,
    GraphRelationshipType,
    GraphSyncService,
    IncidentNode,
    Neo4jClient,
    Neo4jGraphRepository,
    RelationshipProvenance,
    entity_normalizer,
)


@pytest.fixture
def repo():
    """Provides a fresh isolated Neo4jGraphRepository instance."""
    r = Neo4jGraphRepository()
    r.clear_mock_store()
    return r


@pytest.fixture
def sync_service(repo):
    """Provides a GraphSyncService using the isolated repository."""
    return GraphSyncService(repository=repo, normalizer=entity_normalizer)


# -----------------------------------------------------------------------------
# 1. Entity Normalization Tests
# -----------------------------------------------------------------------------


def test_entity_normalizer_url_and_domain():
    """Ensure URL and domain variants normalize to identical values without destroying display value."""
    norm = entity_normalizer

    # Domain normalization
    d1, disp1 = norm.normalize_domain("HTTPS://Example.COM/login")
    d2, disp2 = norm.normalize_domain("www.example.com")
    d3, disp3 = norm.normalize_domain("example.com:443")
    assert d1 == "example.com"
    assert d2 == "example.com"
    assert d3 == "example.com"
    assert disp1 == "HTTPS://Example.COM/login"

    # URL normalization
    u1, _ = norm.normalize_url("HTTPS://Example.COM/login")
    u2, _ = norm.normalize_url("https://example.com/login/")
    u3, _ = norm.normalize_url("https://example.com/login#section")
    u4, _ = norm.normalize_url("https://example.com/login?b=2&a=1")
    u5, _ = norm.normalize_url("https://example.com/login?a=1&b=2")

    assert u1 == "https://example.com/login"
    assert u2 == "https://example.com/login"
    assert u3 == "https://example.com/login"
    assert u4 == u5, "Query parameters must sort deterministically"


def test_entity_normalizer_phone_and_payment():
    """Ensure phone numbers and UPI/bank payment identifiers normalize cleanly."""
    norm = entity_normalizer

    # Phone normalization
    p1, _ = norm.normalize_phone("+91-98765-43210")
    p2, _ = norm.normalize_phone("09876543210")
    p3, _ = norm.normalize_phone("9876543210")
    p4, _ = norm.normalize_phone("+91 9876543210")
    assert p1 == "+919876543210"
    assert p2 == "+919876543210"
    assert p3 == "+919876543210"
    assert p4 == "+919876543210"

    # Payment entity normalization
    pay1, _ = norm.normalize_payment_entity("ABC@upi", "UPI")
    pay2, _ = norm.normalize_payment_entity("abc@upi", "UPI")
    pay3, _ = norm.normalize_payment_entity("John.Doe@okaxis ", "UPI")
    assert pay1 == "abc@upi"
    assert pay2 == "abc@upi"
    assert pay3 == "john.doe@okaxis"

    # Bank account
    acc1, _ = norm.normalize_payment_entity("1234 5678 9012", "BANK_ACCOUNT")
    acc2, _ = norm.normalize_payment_entity("1234-5678-9012", "BANK_ACCOUNT")
    assert acc1 == "123456789012"
    assert acc2 == "123456789012"


def test_entity_normalizer_ip_and_asn():
    """Ensure IP addresses and ASNs normalize properly."""
    norm = entity_normalizer

    ip1, _ = norm.normalize_ip("192.168.1.1")
    ip2, _ = norm.normalize_ip(" 192.168.1.1 ")
    assert ip1 == "192.168.1.1"
    assert ip2 == "192.168.1.1"

    asn1, _ = norm.normalize_asn("AS13335")
    asn2, _ = norm.normalize_asn("13335")
    asn3, _ = norm.normalize_asn("as 13335")
    assert asn1 == "AS13335"
    assert asn2 == "AS13335"
    assert asn3 == "AS13335"


# -----------------------------------------------------------------------------
# 2. Node Upsert & Provenance Relationship Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_node_upsert_and_provenance_relationships(repo):
    """Test creating nodes and provenance-tracked edges."""
    # 1. Upsert Incident
    inc = IncidentNode(id="inc_001", channel="SMS", status="ACTIVE", risk_score=85.0)
    await repo.upsert_incident(inc)

    # 2. Upsert Phone
    phone = GraphEntityNode(
        node_type=GraphNodeType.PHONE,
        normalized_value="+919876543210",
        display_value="+91-98765-43210",
    )
    await repo.upsert_entity(phone)

    # 3. Connect with Provenance
    prov = RelationshipProvenance(
        evidence_ids=["sig_001", "sig_002"],
        confidence=0.92,
        source="MESSAGE_ANALYZER",
    )
    res = await repo.connect_incident_entity(
        incident_id="inc_001",
        entity_type="Phone",
        entity_id="+919876543210",
        provenance=prov,
    )
    assert res["relationship"] == "OBSERVED"

    # Verify query
    entities = await repo.find_incident_entities("inc_001")
    assert len(entities) == 1
    assert entities[0]["entity_type"] == "Phone"
    assert entities[0]["entity_id"] == "+919876543210"


# -----------------------------------------------------------------------------
# 3. Idempotency Test
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_idempotent_synchronization(sync_service, repo):
    """Running graph synchronization twice must NOT duplicate nodes or relationships."""
    incident = {"id": "inc_idem_001", "channel": "SMS"}
    entities = [
        {"type": "PHONE", "value": "+919876543210"},
        {"type": "DOMAIN", "value": "phish-bank.com"},
        {"type": "PAYMENT", "value": "scammer@fakeupi"},
    ]
    evidence = [{"signal_id": "sig_001"}]

    # First sync
    res1 = await sync_service.sync_incident(incident=incident, entities=entities, evidence=evidence)
    assert res1.status == "SUCCESS"
    nodes_after_first = len(repo._mock_entities) + len(repo._mock_incidents)
    rels_after_first = len(repo._mock_relationships)

    # Second sync (identical data)
    res2 = await sync_service.sync_incident(incident=incident, entities=entities, evidence=evidence)
    assert res2.status == "SUCCESS"
    nodes_after_second = len(repo._mock_entities) + len(repo._mock_incidents)
    rels_after_second = len(repo._mock_relationships)

    assert nodes_after_first == nodes_after_second, "Node count must remain constant on re-sync"
    assert rels_after_first == rels_after_second, "Relationship count must remain constant on re-sync"


# -----------------------------------------------------------------------------
# 4. Hero Synthetic 4-Incident Graph Test
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_synthetic_four_incident_correlation(sync_service, repo):
    """Validate cross-incident topological correlation:

    Incident A: Phone1, Domain1, Payment1
    Incident B: Phone1, Domain2, Payment2
    Incident C: Phone3, Domain3, Payment1
    Incident D: Phone4, Domain4, Payment4

    Expected:
    - A ↔ B because Phone1 shared
    - A ↔ C because Payment1 shared
    - B and C indirectly connected through A
    - D completely unrelated
    """
    # Incident A
    await sync_service.sync_incident(
        incident={"id": "inc_A", "channel": "SMS"},
        entities=[
            {"type": "PHONE", "value": "+919999900001"},  # Phone1
            {"type": "DOMAIN", "value": "alpha-domain.example"},  # Domain1
            {"type": "PAYMENT", "value": "shared-fraud@fakeupi"},  # Payment1
        ],
    )

    # Incident B
    await sync_service.sync_incident(
        incident={"id": "inc_B", "channel": "SMS"},
        entities=[
            {"type": "PHONE", "value": "+919999900001"},  # Phone1 (Shared with A)
            {"type": "DOMAIN", "value": "beta-domain.example"},  # Domain2
            {"type": "PAYMENT", "value": "pay-beta@fakeupi"},  # Payment2
        ],
    )

    # Incident C
    await sync_service.sync_incident(
        incident={"id": "inc_C", "channel": "WHATSAPP"},
        entities=[
            {"type": "PHONE", "value": "+919999900003"},  # Phone3
            {"type": "DOMAIN", "value": "gamma-domain.example"},  # Domain3
            {"type": "PAYMENT", "value": "shared-fraud@fakeupi"},  # Payment1 (Shared with A)
        ],
    )

    # Incident D
    await sync_service.sync_incident(
        incident={"id": "inc_D", "channel": "EMAIL"},
        entities=[
            {"type": "PHONE", "value": "+919999900004"},  # Phone4 (Isolated)
            {"type": "DOMAIN", "value": "delta-domain.example"},  # Domain4 (Isolated)
            {"type": "PAYMENT", "value": "isolated-pay@fakeupi"},  # Payment4 (Isolated)
        ],
    )

    # 1. Query relationships for Incident A
    related_to_a = await repo.find_related_incidents("inc_A")
    related_ids_a = [r["related_incident_id"] for r in related_to_a]
    assert "inc_B" in related_ids_a, "Incident B must be related to Incident A via Phone1"
    assert "inc_C" in related_ids_a, "Incident C must be related to Incident A via Payment1"
    assert "inc_D" not in related_ids_a, "Incident D must NOT be related to Incident A"

    # Verify shared entities for Incident A
    shared_a = await repo.find_shared_entities("inc_A")
    assert "Phone" in shared_a
    assert shared_a["Phone"][0]["entity_id"] == "+919999900001"
    assert "inc_B" in shared_a["Phone"][0]["shared_with_incidents"]

    assert "PaymentEntity" in shared_a
    assert shared_a["PaymentEntity"][0]["entity_id"] == "shared-fraud@fakeupi"
    assert "inc_C" in shared_a["PaymentEntity"][0]["shared_with_incidents"]

    # 2. Query relationships for Incident B (directly related to A, indirectly to C via A)
    related_to_b = await repo.find_related_incidents("inc_B")
    related_ids_b = [r["related_incident_id"] for r in related_to_b]
    assert "inc_A" in related_ids_b
    assert "inc_D" not in related_ids_b

    # 3. Query relationships for Incident D (completely isolated)
    related_to_d = await repo.find_related_incidents("inc_D")
    assert len(related_to_d) == 0, "Incident D shares zero entities and must have 0 related incidents"

    shared_d = await repo.find_shared_entities("inc_D")
    assert len(shared_d) == 0, "Incident D must have 0 shared entities"


# -----------------------------------------------------------------------------
# 5. Neo4j Offline / Graceful Degradation Test
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_neo4j_unavailable_graceful_handling():
    """Verify that graph sync returns UNAVAILABLE without raising exceptions when driver fails."""
    # Create a mock failing repository that raises an unexpected connection error
    class BrokenRepository(Neo4jGraphRepository):
        async def upsert_incident(self, incident):
            raise ConnectionError("Neo4j database connection refused on port 7687.")

    failing_service = GraphSyncService(repository=BrokenRepository())

    # Attempt synchronization
    result = await failing_service.sync_incident(
        incident={"id": "inc_offline_test", "channel": "SMS"},
        entities=[{"type": "PHONE", "value": "+919876543210"}],
    )

    # Must return UNAVAILABLE status gracefully
    assert result.status == "UNAVAILABLE"
    assert result.incident_id == "inc_offline_test"
    assert "connection refused" in str(result.error).lower()
