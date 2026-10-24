"""Unit tests for Phase 0B Data Foundation V2 and AI/Dataset Registry."""

import pytest
from datetime import datetime, timezone

from packages.schemas.common import (
    generate_id,
    RiskLevelV2,
    ConfidenceLevelV2,
    UrgencyLevelV2,
    PrivacyClassification,
)
from packages.schemas.artifact import Artifact, ArtifactType
from packages.schemas.entity import Entity, EntityType, EntityVerificationState
from packages.schemas.incident import Incident, IncidentStatus
from packages.schemas.provenance import (
    AnnotationRecord,
    AnnotationType,
    ModelExecutionRecord,
    DatasetLineageRecord,
    SourceProvenanceRecord,
    SourceProvenanceType,
)
from packages.schemas.dataset import (
    LanguageMetadata,
    QualityMetadata,
    ScamGraphRecordV2,
    SplitMetadata,
    SplitType,
)
from packages.schemas.events import Event, EventType, ActorRole, MessagePayload
from packages.schemas.signals import EvidenceSignal, ProvenanceRecord, SignalDimension
from packages.utils.normalization import (
    normalize_domain_or_url,
    normalize_email,
    normalize_phone,
    normalize_vpa,
)
from packages.utils.privacy import (
    canonical_hash,
    mask_bank_account,
    mask_email,
    mask_phone,
    mask_vpa,
)
from packages.registry.validator import (
    RegistryService,
    get_dataset,
    get_model,
    list_datasets,
    list_models,
    validate_registry,
)


def test_stable_id_generator():
    """Verify prefixing, opacity, and collision resistance."""
    art_id = generate_id("art")
    inc_id = generate_id("inc")
    ent_id = generate_id("ent")
    
    assert art_id.startswith("art_")
    assert inc_id.startswith("inc_")
    assert ent_id.startswith("ent_")
    assert art_id != generate_id("art")
    assert len(art_id) >= 20


def test_masking_utilities():
    """Verify that identifiers are securely masked without leaking raw data."""
    # Phone
    assert mask_phone("9876543210") == "******3210"
    assert mask_phone("+91-9876543210") == "********3210"
    assert mask_phone("123") == "****"

    # Email
    assert mask_email("person@example.com") == "p***@example.com"
    assert mask_email("a@gmail.com") == "***@gmail.com"

    # UPI VPA
    assert mask_vpa("sumeet@oksbi") == "s***@oksbi"
    assert mask_vpa("x@icici") == "***@icici"

    # Bank Account
    assert mask_bank_account("123456789012") == "********9012"


def test_normalization_utilities():
    """Verify deterministic canonical normalization."""
    # Phone
    assert normalize_phone("9876543210") == "+919876543210"
    assert normalize_phone("+91 98765 43210") == "+919876543210"
    assert normalize_phone("09876543210") == "+919876543210"

    # Email
    assert normalize_email(" User.Name@Example.COM ") == "user.name@example.com"

    # VPA
    assert normalize_vpa(" JohnDoe@OkSBI ") == "johndoe@oksbi"

    # URL / Domain
    assert normalize_domain_or_url("https://www.Bank-Secure.tk/login?ref=1") == "bank-secure.tk"
    assert normalize_domain_or_url("http://sbi-kyc.in") == "sbi-kyc.in"


def test_canonical_hashing():
    """Verify deterministic hashing and HMAC distinction."""
    v1 = "user@oksbi"
    v2 = "USER@oksbi"
    # Normalizing before hashing
    h1 = canonical_hash(normalize_vpa(v1))
    h2 = canonical_hash(normalize_vpa(v2))
    assert h1 == h2
    assert len(h1) == 64  # SHA-256

    # With HMAC secret
    h_secret = canonical_hash(normalize_vpa(v1), secret="my-secret-key")
    assert h_secret != h1


def test_artifact_contract():
    """Verify Artifact creation, defaults, and serialization."""
    art = Artifact(
        artifact_type=ArtifactType.MESSAGE,
        channel="SMS",
        normalized_content="Your electricity power will be cut tonight at 9:30 PM",
        privacy_classification=PrivacyClassification.SENSITIVE,
    )
    assert art.schema_version == "2.0"
    assert art.artifact_id.startswith("art_")
    assert art.artifact_type == ArtifactType.MESSAGE
    d = art.model_dump()
    assert d["channel"] == "SMS"
    assert d["privacy_classification"] == "SENSITIVE"


def test_entity_contract():
    """Verify Entity creation with masked and hashed values."""
    raw_phone = "+919876543210"
    norm_phone = normalize_phone(raw_phone)
    entity = Entity(
        entity_type=EntityType.PHONE,
        canonical_value=norm_phone,
        masked_value=mask_phone(norm_phone),
        canonical_hash=canonical_hash(norm_phone),
        verification_state=EntityVerificationState.OBSERVED,
    )
    assert entity.entity_id.startswith("ent_")
    assert entity.masked_value == "********3210"
    assert entity.verification_state == EntityVerificationState.OBSERVED
    assert len(entity.canonical_hash) == 64


def test_incident_contract():
    """Verify Incident creation and decoupled event/artifact referencing."""
    inc = Incident(
        status=IncidentStatus.ANALYZING,
        current_risk=RiskLevelV2.HIGH,
        current_confidence=ConfidenceLevelV2.MEDIUM,
        current_urgency=UrgencyLevelV2.HIGH,
        likely_scam_family="electricity_bill",
        event_ids=["evt_001", "evt_002"],
        artifact_ids=["art_001"],
    )
    assert inc.schema_version == "2.0"
    assert inc.incident_id.startswith("inc_")
    assert inc.current_risk == RiskLevelV2.HIGH
    assert len(inc.event_ids) == 2


def test_event_schema_backward_compatibility():
    """Verify Event schema works with both legacy and V2 fields."""
    legacy_event = Event(
        incident_id="inc_test",
        sequence_number=1,
        event_type=EventType.MESSAGE_RECEIVED,
        payload=MessagePayload(
            sender_id="+919876543210",
            recipient_id_hash="hash123",
            text="Hello world",
        )
    )
    assert legacy_event.schema_version == "2.0"
    assert legacy_event.actor_role == ActorRole.UNKNOWN
    assert legacy_event.artifact_ids == []

    v2_event = Event(
        incident_id="inc_test",
        sequence_number=2,
        event_type=EventType.MESSAGE_RECEIVED,
        payload={"raw": "custom"},
        actor_role=ActorRole.USER,
        artifact_ids=["art_999"],
    )
    assert v2_event.actor_role == ActorRole.USER
    assert v2_event.artifact_ids == ["art_999"]


def test_provenance_record_extension():
    """Verify ProvenanceRecord supports legacy and V2 lineage fields."""
    prov = ProvenanceRecord(
        source_service="services/investigation",
        detector_name="NLP Urgency",
        target_artifact="text",
        model_id="scamgraph-message-baseline",
        model_version="v1.0.0",
        reliability_score=0.95,
    )
    assert prov.model_id == "scamgraph-message-baseline"
    assert prov.reliability_score == 0.95


def test_scamgraph_record_v2_and_adapters():
    """Verify ScamGraphRecordV2 serialization and legacy round-trip conversion."""
    record = ScamGraphRecordV2(
        content="Dear SBI user your account will be suspended today update KYC at link",
        provenance=SourceProvenanceRecord(
            source_name="anmolshrivastav/scam-ham-india",
            source_type=SourceProvenanceType.PUBLIC_MIXED,
        ),
        annotations=[
            AnnotationRecord(
                label_name="is_scam",
                label_value=1,
                annotation_type=AnnotationType.SOURCE_PROVIDED,
            ),
            AnnotationRecord(
                label_name="scam_type",
                label_value="fake_kyc",
                annotation_type=AnnotationType.RULE_INFERRED,
                notes="Regex inferred",
            ),
        ],
        labels={"is_scam": 1, "scam_type": "fake_kyc"},
        split_metadata=SplitMetadata(split=SplitType.TEST),
    )
    
    assert record.schema_version == "2.0"
    assert record.is_synthetic is False

    # Convert to legacy dict
    legacy = record.to_legacy()
    assert legacy["text"] == record.content
    assert legacy["label"] == 1
    assert legacy["scam_type"] == "fake_kyc"
    assert legacy["split"] == "test"

    # Convert back from legacy dict
    roundtrip = ScamGraphRecordV2.from_legacy(legacy)
    assert roundtrip.content == record.content
    assert roundtrip.labels["is_scam"] == 1
    # Check that heuristic label was properly marked as RULE_INFERRED
    type_ann = [a for a in roundtrip.annotations if a.label_name == "scam_type"][0]
    assert type_ann.annotation_type == AnnotationType.RULE_INFERRED


def test_model_execution_record():
    """Verify ModelExecutionRecord captures latency and hashed input reference."""
    exec_rec = ModelExecutionRecord(
        model_id="scamgraph-message-baseline",
        model_revision="v1.0.0",
        task="text_classification",
        latency_ms=3.45,
        input_reference=canonical_hash("Check this suspicious text"),
        confidence=0.98,
    )
    assert exec_rec.execution_id.startswith("exe_")
    assert exec_rec.latency_ms == 3.45
    assert len(exec_rec.input_reference) == 64


def test_registry_validation():
    """Verify dataset and model registry validation."""
    val_result = validate_registry()
    assert val_result["valid"] is True, f"Registry validation failed: {val_result}"
    assert len(val_result["dataset_errors"]) == 0
    assert len(val_result["model_errors"]) == 0

    # Test query functions
    ds = get_dataset("scam-ham-india")
    assert ds is not None
    assert ds["provenance_type"] == "PUBLIC_MIXED"
    assert ds["gold_set_approved"] is False

    m = get_model("scamgraph-message-baseline")
    assert m is not None
    assert m["status"] == "BASELINE"

    m_distil = get_model("distilbert-scam-detector-india")
    assert m_distil is not None
    assert m_distil["status"] == "REJECTED"


def test_registry_governance_rules():
    """Verify that governance rules trigger errors on invalid entries."""
    service = RegistryService()
    
    # Check that synthetic data cannot have gold_set_approved=True
    invalid_data = {
        "version": "2.0.0",
        "datasets": [
            {
                "id": "bad-synthetic-gold",
                "license": "mit",
                "provenance_type": "SYNTHETIC_LLM",
                "gold_set_approved": True,  # Violation!
            }
        ]
    }
    service._datasets_cache = invalid_data
    errors, _ = service.validate_datasets()
    assert any("Synthetic dataset 'bad-synthetic-gold' cannot have gold_set_approved=True" in e for e in errors)
