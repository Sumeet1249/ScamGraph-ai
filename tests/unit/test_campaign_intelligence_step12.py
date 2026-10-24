"""Comprehensive Unit Tests for Campaign Intelligence V2 & Scam Outbreak Radar (Phase 3C).

Tests Part O requirements (Sections 101-116):
- Campaign formation from CandidateIncidentGroup
- Same-family negative control (refusal to form campaign on family alone)
- Rapid growth and outbreak detection
- Ingestion spike resistance (historical observed_at)
- Duplicate report spike filtering
- Resurgence detection after dormancy
- Mutation tracking (phone, UPI, channel migration)
- Auditable merge & split proposals
- Privacy-safe consumer warning signals
- Outbreak radar summary, blip projections across 3 rings, and signals
- FastAPI REST endpoints
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient

from packages.schemas.campaign import (
    CampaignLifecycleState,
    CampaignVelocityState,
    ScamCampaign,
)
from packages.schemas.correlation import CandidateIncidentGroup
from packages.schemas.radar import OutbreakSignalType, RadarSeverity
from services.api.app.main import app
from services.campaign_engine.config import CampaignConfig
from services.campaign_engine.discovery import CampaignDiscoveryEngine
from services.campaign_engine.lifecycle import CampaignLifecycleManager
from services.campaign_engine.radar import ScamOutbreakRadarService
from services.campaign_engine.service import CampaignIntelligenceService, campaign_service
from services.campaign_engine.velocity import CampaignVelocityEngine


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def config() -> CampaignConfig:
    return CampaignConfig({
        "lifecycle_thresholds": {
            "candidate_min_incidents": 3,
            "active_min_incidents": 5,
            "relationship_density_threshold": 0.50,
            "strong_edge_min_ratio": 0.40,
            "dormant_inactivity_days": 30,
        },
        "velocity_thresholds": {
            "baseline_window_days": 14,
            "rising_growth_multiplier": 1.50,
            "surging_growth_multiplier": 2.20,
            "outbreak_growth_multiplier": 3.50,
            "outbreak_min_volume_24h": 6,
            "emerging_min_volume_24h": 3,
        },
    })


def test_campaign_formation(config: CampaignConfig):
    """Section 101: 10 strongly related task-scam incidents with multi-signal evidence."""
    discovery = CampaignDiscoveryEngine(config)
    member_ids = [f"inc_{i}" for i in range(10)]

    group = CandidateIncidentGroup(
        group_id="grp_task_strong_01",
        member_incident_ids=member_ids,
        relationship_density=0.85,
        strong_edge_count=38,
        evidence_diversity=["SHARED_PAYMENT(vip.task@sbi)", "HIGH_SCAM_DNA_SIMILARITY", "JOURNEY_ALIGNMENT"],
        primary_family="TASK_SCAM",
        first_seen=datetime.now(timezone.utc) - timedelta(days=5),
        last_seen=datetime.now(timezone.utc),
        growth_velocity=2.0,
    )

    campaign = discovery.evaluate_candidate_group(group)
    assert campaign is not None
    assert campaign.scam_family == "TASK_SCAM"
    assert campaign.incident_count == 10
    assert campaign.lifecycle_state == CampaignLifecycleState.ACTIVE
    assert campaign.confidence >= 0.80
    assert campaign.strongly_related_incident_count == 38


def test_same_family_negative(config: CampaignConfig):
    """Section 102: 10 unrelated task scams with family match only. Refuses automatic campaign."""
    discovery = CampaignDiscoveryEngine(config)
    member_ids = [f"inc_unrelated_{i}" for i in range(10)]

    group = CandidateIncidentGroup(
        group_id="grp_family_only",
        member_incident_ids=member_ids,
        relationship_density=0.20,
        strong_edge_count=1,
        evidence_diversity=["SAME_FAMILY(TASK_SCAM)"],  # Zero independent entity/infra/DNA evidence
        primary_family="TASK_SCAM",
        first_seen=datetime.now(timezone.utc) - timedelta(days=5),
        last_seen=datetime.now(timezone.utc),
        growth_velocity=0.5,
    )

    campaign = discovery.evaluate_candidate_group(group)
    assert campaign is None, "Campaign should NOT form on same scam family alone without independent evidence"


def test_rapid_growth_and_outbreak(config: CampaignConfig):
    """Section 103: Baseline 2/day, suddenly 25 incidents/day -> detected as OUTBREAK."""
    velocity_engine = CampaignVelocityEngine(config)
    now = datetime.now(timezone.utc)

    campaign = ScamCampaign(
        campaign_id="camp_growth_test",
        title="Test Growth Campaign",
        scam_family="DIGITAL_ARREST",
        confidence=0.90,
    )

    # 14 days of baseline incidents: ~2/day (26 incidents across days 13 to 1 ago)
    incidents = []
    for day in range(1, 14):
        for k in range(2):
            incidents.append({
                "id": f"inc_base_{day}_{k}",
                "observed_at": now - timedelta(days=day, hours=k * 2),
            })

    # Sudden surge: 25 incidents in the last 24h
    for j in range(25):
        incidents.append({
            "id": f"inc_surge_{j}",
            "observed_at": now - timedelta(hours=j % 20),
        })

    vel_state, cur_vel, base_vel, growth_mult, accel, reasons = velocity_engine.calculate_velocity(
        campaign, incidents, current_time=now
    )

    assert cur_vel == 25.0
    assert base_vel == pytest.approx(2.0, abs=0.5)
    assert growth_mult >= config.outbreak_growth_multiplier
    assert vel_state == CampaignVelocityState.OUTBREAK
    assert any("ABNORMAL_SURGE" in r for r in reasons)


def test_ingestion_spike_resistance(config: CampaignConfig):
    """Section 104: Bulk import of 1,000 old incidents today -> NO fake outbreak."""
    velocity_engine = CampaignVelocityEngine(config)
    now = datetime.now(timezone.utc)

    campaign = ScamCampaign(
        campaign_id="camp_bulk_import",
        title="Historical Ingestion Campaign",
        scam_family="KYC_IMPERSONATION",
        confidence=0.85,
    )

    # 1,000 historical incidents ingested today (created_at=now), but observed_at is 40 days ago
    historical_date = now - timedelta(days=40)
    incidents = []
    for i in range(1000):
        incidents.append({
            "id": f"inc_hist_{i}",
            "created_at": now,  # Ingested right now
            "observed_at": historical_date + timedelta(minutes=i),  # Actual occurrence is old
        })

    vel_state, cur_vel, base_vel, growth_mult, accel, reasons = velocity_engine.calculate_velocity(
        campaign, incidents, current_time=now
    )

    # In the last 24h, zero real-world incidents occurred
    assert cur_vel == 0.0
    assert vel_state == CampaignVelocityState.NORMAL
    assert "ABNORMAL_SURGE_OVER_BASELINE" not in reasons


def test_duplicate_spike_dedup(config: CampaignConfig):
    """Section 105: 100 duplicate reports of the same incident -> dedup prevents fake outbreak."""
    velocity_engine = CampaignVelocityEngine(config)
    now = datetime.now(timezone.utc)

    campaign = ScamCampaign(
        campaign_id="camp_dedup_test",
        title="Dedup Campaign",
        scam_family="PART_TIME_JOB",
        confidence=0.85,
    )

    # 100 duplicate submissions with identical fingerprint
    incidents = []
    for i in range(100):
        incidents.append({
            "id": f"inc_dup_{i}",
            "fingerprint": "identical_scam_report_hash_12345",
            "observed_at": now - timedelta(minutes=i % 60),
        })

    vel_state, cur_vel, base_vel, growth_mult, accel, reasons = velocity_engine.calculate_velocity(
        campaign, incidents, current_time=now
    )

    # After deduplication, effective report count is 1
    assert cur_vel == 1.0
    assert vel_state == CampaignVelocityState.NORMAL


def test_resurgence_after_dormancy(config: CampaignConfig):
    """Section 106: Campaign dormant for 60 days returns -> transitions to RESURGING."""
    lifecycle_manager = CampaignLifecycleManager(config)
    now = datetime.now(timezone.utc)

    campaign = ScamCampaign(
        campaign_id="camp_resurgent",
        title="Customs Parcel Scam",
        scam_family="CUSTOMS_PARCEL",
        lifecycle_state=CampaignLifecycleState.DORMANT,
        last_seen=now - timedelta(days=60),
    )

    new_state, reasons = lifecycle_manager.evaluate_lifecycle_transition(
        campaign,
        new_incidents_count=4,
        velocity_state=CampaignVelocityState.RISING,
        latest_incident_time=now,
    )

    assert new_state == CampaignLifecycleState.RESURGING
    assert any("RESURGENCE_AFTER_60_DAYS" in r for r in reasons)


def test_mutation_tracking(config: CampaignConfig):
    """Section 107: Campaign rotates phone numbers, UPI VPAs, and migrates channels."""
    lifecycle_manager = CampaignLifecycleManager(config)

    campaign = ScamCampaign(
        campaign_id="camp_mutate",
        title="Mutating Job Scam",
        scam_family="TASK_SCAM",
        payment_profile=["vip.old@paytm"],
        infrastructure_profile=["+919000000001"],
        channels=["WhatsApp"],
        tactic_profile=["FINANCIAL_REWARD"],
    )

    new_entities = [
        {"entity_type": "UPI_HANDLE", "canonical_value": "vip.new@sbi"},
        {"entity_type": "PHONE_NUMBER", "canonical_value": "+919999999999"},
    ]
    new_channels = ["WhatsApp", "Telegram"]
    new_tactics = ["SUNKEN_COST_ESCALATION"]

    mutations = lifecycle_manager.track_mutations(campaign, new_entities, new_channels, new_tactics)

    assert len(mutations) == 4
    assert "PAYMENT_ROTATION(vip.new@sbi)" in mutations
    assert "PHONE_ROTATION(+919999999999)" in mutations
    assert "CHANNEL_MIGRATION(Telegram)" in mutations
    assert "TACTIC_DRIFT(SUNKEN_COST_ESCALATION)" in mutations
    assert campaign.mutation_count == 4
    assert "vip.new@sbi" in campaign.payment_profile
    assert "+919999999999" in campaign.infrastructure_profile
    assert "Telegram" in campaign.channels


def test_merge_and_split_proposals(config: CampaignConfig):
    """Sections 108 & 109: Auditable merge and split proposals."""
    lifecycle_manager = CampaignLifecycleManager(config)

    camp_a = ScamCampaign(campaign_id="camp_a", title="Campaign Alpha", scam_family="LOAN_SCAM")
    camp_b = ScamCampaign(campaign_id="camp_b", title="Campaign Beta", scam_family="LOAN_SCAM")

    # Propose Merge
    merge_prop = lifecycle_manager.propose_merge(
        camp_a, camp_b, "Shared bank mule account and identical APK package", ["EVIDENCE_SHARED_MULE_123"]
    )
    assert merge_prop.proposal_type == "MERGE"
    assert merge_prop.source_campaign_ids == ["camp_a", "camp_b"]
    assert merge_prop.status == "PENDING_REVIEW"

    # Propose Split
    split_prop = lifecycle_manager.propose_split(
        camp_a, "Disjoint subgraphs operating in separate geographies with different VPAs", ["SUBGRAPH_BIFURCATION"]
    )
    assert split_prop.proposal_type == "SPLIT"
    assert split_prop.source_campaign_ids == ["camp_a"]
    assert split_prop.status == "PENDING_REVIEW"


def test_consumer_warning_privacy(config: CampaignConfig):
    """Section 113: Privacy test — ConsumerCampaignSignal must not leak victim PII or raw internal graph."""
    radar_service = ScamOutbreakRadarService(config)

    campaign = ScamCampaign(
        campaign_id="camp_priv_test",
        title="Digital Arrest Scam",
        scam_family="DIGITAL_ARREST",
        lifecycle_state=CampaignLifecycleState.OUTBREAK,
        confidence=0.92,
        incident_count=32,
    )

    signal = radar_service.create_consumer_signal(campaign)
    assert signal.campaign_matched is True
    assert signal.urgency_level == "HIGH"
    assert signal.confidence_level == "HIGH"
    assert signal.pre_loss_warning is True
    assert "Digital Arrest" in signal.warning_message
    assert "surging" in signal.warning_message.lower()

    # Verify no PII or sensitive keys
    dumped = signal.model_dump()
    for forbidden in ["victim", "phone", "upi", "address", "graph_id", "analyst_notes"]:
        for val in dumped.values():
            if isinstance(val, str):
                assert forbidden not in val.lower()


def test_radar_blip_projection_and_summary(config: CampaignConfig):
    """Section 37-43: Outbreak Radar concentric rings, pulse speed, and summary."""
    radar_service = ScamOutbreakRadarService(config)

    c_crit = ScamCampaign(
        campaign_id="camp_crit",
        title="Critical CBI Extortion",
        scam_family="DIGITAL_ARREST",
        lifecycle_state=CampaignLifecycleState.OUTBREAK,
        growth_multiplier=4.2,
        incident_count=50,
    )
    c_surg = ScamCampaign(
        campaign_id="camp_surg",
        title="Surging Task Scam",
        scam_family="TASK_SCAM",
        lifecycle_state=CampaignLifecycleState.SURGING,
        growth_multiplier=2.5,
        incident_count=20,
    )
    c_emerg = ScamCampaign(
        campaign_id="camp_emerg",
        title="Emerging Electricity Scam",
        scam_family="FAKE_SUPPORT",
        lifecycle_state=CampaignLifecycleState.EMERGING,
        growth_multiplier=1.2,
        incident_count=8,
    )

    blip_crit = radar_service.map_campaign_to_blip(c_crit)
    blip_surg = radar_service.map_campaign_to_blip(c_surg)
    blip_emerg = radar_service.map_campaign_to_blip(c_emerg)

    # Ring assignments
    assert blip_crit.ring == "CRITICAL"
    assert blip_crit.severity == RadarSeverity.CRITICAL
    assert blip_crit.radius_norm <= 0.35  # Inner ring

    assert blip_surg.ring == "SURGING"
    assert blip_surg.severity == RadarSeverity.HIGH
    assert 0.45 <= blip_surg.radius_norm <= 0.65  # Middle ring

    assert blip_emerg.ring == "EMERGING"
    assert blip_emerg.severity == RadarSeverity.WATCH
    assert blip_emerg.radius_norm >= 0.75  # Outer ring

    # Summary
    summary = radar_service.generate_radar_summary(
        [c_crit, c_surg, c_emerg],
        [],
        demo_mode=False,
    )
    assert summary.active_campaigns == 3
    assert summary.outbreak_count == 1
    assert summary.critical_count == 1
    assert summary.surging_count == 1
    assert summary.emerging_count == 1


def test_fastapi_endpoints(test_client: TestClient):
    """Verify REST endpoints for campaigns and radar."""
    # 1. GET /api/v1/radar/summary
    resp_sum = test_client.get("/api/v1/radar/summary?demo_mode=true")
    assert resp_sum.status_code == 200
    sum_data = resp_sum.json()
    assert sum_data["active_campaigns"] >= 4
    assert sum_data["outbreak_count"] >= 1
    assert sum_data["surging_count"] >= 1

    # 2. GET /api/v1/radar/blips
    resp_blips = test_client.get("/api/v1/radar/blips?demo_mode=true")
    assert resp_blips.status_code == 200
    blips = resp_blips.json()
    assert len(blips) >= 4
    rings = {b["ring"] for b in blips}
    assert "CRITICAL" in rings
    assert "SURGING" in rings
    assert "EMERGING" in rings

    # 3. GET /api/v1/radar/signals
    resp_sigs = test_client.get("/api/v1/radar/signals?demo_mode=true")
    assert resp_sigs.status_code == 200
    sigs = resp_sigs.json()
    assert len(sigs) >= 3

    # 4. GET /api/v1/campaigns
    resp_camps = test_client.get("/api/v1/campaigns?demo_mode=true")
    assert resp_camps.status_code == 200
    camps = resp_camps.json()
    assert len(camps) >= 4

    # 5. GET /api/v1/campaigns/{id}
    cid = camps[0]["campaign_id"]
    resp_single = test_client.get(f"/api/v1/campaigns/{cid}")
    assert resp_single.status_code == 200
    camp_obj = resp_single.json()
    assert camp_obj["campaign_id"] == cid
    assert "scam_family" in camp_obj
    assert "velocity_state" in camp_obj

    # 6. GET /api/v1/campaigns/{id}/velocity
    resp_vel = test_client.get(f"/api/v1/campaigns/{cid}/velocity")
    assert resp_vel.status_code == 200
    assert "current_velocity_per_day" in resp_vel.json()
