"""Unit and integration tests for Step 24: Neo4j Graph Analytics.

Validates:
1. Weakly Connected Components (WCC)
2. Bipartite Node Neighborhood Similarity (Jaccard, Overlap, Cosine)
3. Candidate Campaign Community Detection
4. High-Value Hub Entity Discovery (degree centrality)
5. Explainable relationship path traversal
6. Verification on synthetic 13-incident graph (Campaign Alpha, Campaign Beta, Unrelated Benign)
"""

from __future__ import annotations

import pytest

from services.graph_engine import (
    GraphAnalyticsService,
    GraphSyncService,
    Neo4jGraphRepository,
    entity_normalizer,
)


@pytest.fixture
def repo():
    r = Neo4jGraphRepository()
    r.clear_mock_store()
    return r


@pytest.fixture
def sync_service(repo):
    return GraphSyncService(repository=repo, normalizer=entity_normalizer)


@pytest.fixture
def analytics_service(repo):
    return GraphAnalyticsService(repo=repo)


async def seed_synthetic_dataset(sync_service, analytics_service):
    """Seed synthetic 13-incident graph:

    - Campaign Alpha (5 incidents)
    - Campaign Beta (4 incidents)
    - Unrelated Benign Group (4 incidents)
    """
    # Campaign Alpha (5 incidents) - KYC Impersonation Ring
    for i in range(1, 6):
        phone = "+919811100001" if i != 4 else "+919811100002"
        domain = "alpha-kyc.example" if i in (1, 3, 4) else f"alpha-variant-{i}.example"
        payment = "mule.alpha@fakeupi" if i != 3 else "mule.alpha2@fakeupi"
        await sync_service.sync_incident(
            incident={"id": f"alpha_{i}", "channel": "SMS"},
            entities=[
                {"type": "PHONE", "value": phone},
                {"type": "DOMAIN", "value": domain},
                {"type": "PAYMENT", "value": payment},
            ],
        )

    # Campaign Beta (4 incidents) - Fake Job Ring
    for i in range(1, 5):
        phone = "+919822200001" if i != 3 else "+919822200002"
        domain = "beta-job.example" if i in (1, 2, 3) else "beta-work.example"
        payment = "job.hr@fakeupi" if i != 2 else "job.pay@fakeupi"
        await sync_service.sync_incident(
            incident={"id": f"beta_{i}", "channel": "WHATSAPP"},
            entities=[
                {"type": "PHONE", "value": phone},
                {"type": "DOMAIN", "value": domain},
                {"type": "PAYMENT", "value": payment},
            ],
        )

    # Unrelated Benign Group (4 isolated incidents)
    for i in range(1, 5):
        await sync_service.sync_incident(
            incident={"id": f"benign_{i}", "channel": "SMS"},
            entities=[
                {"type": "PHONE", "value": f"+91983330000{i}"},
                {"type": "DOMAIN", "value": f"utility-official-{i}.example"},
                {"type": "PAYMENT", "value": f"merchant{i}@officialbank"},
            ],
        )

    return analytics_service


# -----------------------------------------------------------------------------
# 1. Connected Components (WCC) Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_connected_components_wcc(sync_service, analytics_service):
    """Verify WCC clusters Alpha (size 5) and Beta (size 4), while benign incidents are isolated."""
    await seed_synthetic_dataset(sync_service, analytics_service)
    components = await analytics_service.find_connected_components()
    assert len(components) >= 2

    # Verify largest component is Campaign Alpha
    comp_sizes = [c["size"] for c in components]
    assert 5 in comp_sizes, "Campaign Alpha (5 incidents) must form a connected component"
    assert 4 in comp_sizes, "Campaign Beta (4 incidents) must form a connected component"

    alpha_comp = next(c for c in components if "alpha_1" in c["incident_ids"])
    assert len(alpha_comp["incident_ids"]) == 5
    for i in range(1, 6):
        assert f"alpha_{i}" in alpha_comp["incident_ids"]

    beta_comp = next(c for c in components if "beta_1" in c["incident_ids"])
    assert len(beta_comp["incident_ids"]) == 4
    for i in range(1, 5):
        assert f"beta_{i}" in beta_comp["incident_ids"]

    # Benign incidents should be in components of size 1
    benign_comp = next(c for c in components if "benign_1" in c["incident_ids"])
    assert benign_comp["size"] == 1


# -----------------------------------------------------------------------------
# 2. Node Similarity Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_similar_incidents_neighborhood(sync_service, analytics_service):
    """Test incident neighborhood similarity."""
    await seed_synthetic_dataset(sync_service, analytics_service)

    # Compare within Campaign Alpha
    similar_to_alpha1 = await analytics_service.find_similar_incidents("alpha_1", top_k=5, metric="jaccard")
    assert len(similar_to_alpha1) > 0

    # Top similar should be other Alpha incidents
    top_match = similar_to_alpha1[0]
    assert top_match["incident_b"].startswith("alpha_")
    assert top_match["similarity_score"] >= 0.33
    assert len(top_match["shared_neighbors"]) >= 1

    # Alpha 1 should NOT be similar to any Beta or Benign incident
    beta_and_benign = [s for s in similar_to_alpha1 if s["incident_b"].startswith(("beta_", "benign_"))]
    assert len(beta_and_benign) == 0

    # Test Overlap metric
    overlap_matches = await analytics_service.find_similar_incidents("alpha_1", top_k=5, metric="overlap")
    assert overlap_matches[0]["similarity_score"] >= top_match["similarity_score"]


# -----------------------------------------------------------------------------
# 3. Community Detection Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_candidate_campaign_communities(sync_service, analytics_service):
    """Test discovery of candidate campaign communities."""
    await seed_synthetic_dataset(sync_service, analytics_service)
    communities = await analytics_service.find_communities()
    assert len(communities) == 2, "Must discover exactly 2 candidate campaign communities (Alpha and Beta)"

    comm_sizes = sorted([c["size"] for c in communities])
    assert comm_sizes == [4, 5]

    for comm in communities:
        assert "candidate campaign community" in comm["explanation"].lower()
        assert len(comm["important_entities"]) >= 1


# -----------------------------------------------------------------------------
# 4. High-Value Hub Entities Discovery Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_high_value_entities(sync_service, analytics_service):
    """Test degree centrality and discovery of hub infrastructure/payment entities."""
    await seed_synthetic_dataset(sync_service, analytics_service)
    high_value = await analytics_service.find_high_value_entities(top_k=5)
    assert len(high_value) >= 2

    # Check top entities
    top_entity = high_value[0]
    assert top_entity["incident_count"] >= 3
    assert top_entity["degree"] >= 3

    # Primary Alpha phone (+919811100001) or Alpha mule payment should appear near the top
    top_ids = [e["entity_id"] for e in high_value]
    assert "+919811100001" in top_ids or "mule.alpha@fakeupi" in top_ids


# -----------------------------------------------------------------------------
# 5. Explainable Relationship Path Traversal
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_explain_relationship_path(sync_service, analytics_service):
    """Test human-readable relationship traversal string generation."""
    await seed_synthetic_dataset(sync_service, analytics_service)
    paths = analytics_service.explain_relationship_path("alpha_1", "alpha_2")
    assert len(paths) >= 1

    # Should contain path format: Incident alpha_1 -> OBSERVED ... <- OBSERVED Incident alpha_2
    path_str = paths[0]
    assert "Incident alpha_1 -> OBSERVED" in path_str
    assert "<- OBSERVED Incident alpha_2" in path_str


# -----------------------------------------------------------------------------
# 6. Structured Graph Correlation Result Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_correlate_incident_result_structure(sync_service, analytics_service):
    """Verify correlate_incident returns structured GraphCorrelationResult objects."""
    await seed_synthetic_dataset(sync_service, analytics_service)
    results = await analytics_service.correlate_incident("alpha_1")
    assert len(results) >= 1

    r0 = results[0]
    assert r0.related_incident_id.startswith("alpha_")
    assert r0.graph_similarity > 0.0
    assert len(r0.relationship_paths) >= 1
    assert len(r0.shared_entities) >= 1
    assert r0.community_id is not None
    assert "Topological link discovered" in r0.explanation
