"""Unit tests for Step 21: Message Intelligence & Dataset Registry.

Validates:
1. Dataset registry cataloging (data/registry/datasets.yaml)
2. Canonical MessageRecord schema
3. Deduplication and leakage-free splitting
4. Baseline TF-IDF + Logistic Regression training, evaluation, and artifacts
5. Transformer vs Baseline evaluation comparison
6. MessageIntelligenceService EvidenceSignal generation
7. Compliance with Constitutional Rule 10 (no single signal declares fraud)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest
import yaml

from ml.message import (
    BaselineMessageModel,
    MessageIntelligenceService,
    MessagePreprocessor,
    MessageRecord,
    load_all_datasets,
)
from ml.message.dataset_loader import (
    load_canonical_journeys,
    load_indian_scam_sms_synthetic,
    load_scam_ham_india,
)
from ml.message.preprocessor import (
    compute_jaccard_similarity,
    compute_template_fingerprint,
    normalize_message_text,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def test_dataset_registry_yaml_exists_and_valid():
    """Verify data/registry/datasets.yaml contains all required metadata."""
    registry_file = ROOT_DIR / "data" / "registry" / "datasets.yaml"
    assert registry_file.exists(), "data/registry/datasets.yaml must exist"

    with open(registry_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "datasets" in data
    datasets = data["datasets"]
    assert len(datasets) >= 3

    dataset_ids = [d["id"] for d in datasets]
    assert "scam-ham-india" in dataset_ids
    assert "indian-scam-sms-synthetic-audited" in dataset_ids
    assert "scamgraph-canonical-journeys" in dataset_ids

    # Validate required metadata schema
    required_keys = [
        "name",
        "source",
        "url",
        "license",
        "real_or_synthetic",
        "intended_use",
        "limitations",
        "status",
    ]
    for d in datasets:
        for k in required_keys:
            assert k in d, f"Missing key '{k}' in dataset {d.get('id')}"


def test_canonical_message_record_creation():
    """Verify canonical MessageRecord properties and serialization."""
    rec = MessageRecord(
        id="test_001",
        text="Dear customer, your PAN card update is pending at SBI.",
        label=1,
        scam_type="fake_kyc",
        language="en",
        source_dataset="anmolshrivastav/scam-ham-india",
        is_synthetic=False,
        campaign_id="sbi_kyc_campaign",
        split="train",
    )
    d = rec.to_dict()
    assert d["id"] == "test_001"
    assert d["label"] == 1
    assert d["is_synthetic"] is False
    assert d["campaign_id"] == "sbi_kyc_campaign"


def test_dataset_loaders():
    """Test individual loaders for datasets."""
    # 1. Canonical journeys
    journeys = load_canonical_journeys()
    assert len(journeys) > 0
    assert any(j.label == 1 for j in journeys)
    assert any(j.label == 0 for j in journeys)

    # 2. Base datasets exist and return non-empty records
    sh_records = load_scam_ham_india()
    assert len(sh_records) >= 2000

    ridham_records = load_indian_scam_sms_synthetic(exclude_unreviewed=False)
    assert len(ridham_records) >= 1000

    # 3. Unified loader
    all_records = load_all_datasets(ridham_path="data/synthetic/synthetic_audited.csv")
    assert len(all_records) >= 2000


def test_text_normalization_and_template_fingerprint():
    """Test whitespace normalization and template fingerprinting."""
    raw1 = "  SBI   Alert:   INR 10,000 debited from a/c 12345678. Visit https://sbi.co.in/net  "
    raw2 = "SBI Alert: INR 25,000 debited from a/c 99998888. Visit https://sbi-fake.example/kyc"

    norm1 = normalize_message_text(raw1)
    norm2 = normalize_message_text(raw2)

    assert "   " not in norm1
    assert norm1.startswith("SBI Alert:")

    # Template fingerprints should match because amounts, accounts, and URLs are parameterized
    fp1 = compute_template_fingerprint(norm1)
    fp2 = compute_template_fingerprint(norm2)
    assert fp1 == fp2, "Parameterized variants of the same template must yield identical fingerprint"


def test_preprocessor_deduplication():
    """Verify exact duplicate removal."""
    recs = [
        MessageRecord("1", "Hello world, lottery won", 1, "lottery", "en", "src", False, "camp1"),
        MessageRecord("2", "hello world, lottery won ", 1, "lottery", "en", "src", False, "camp1"),
        MessageRecord("3", "Completely different text", 0, "benign", "en", "src", False, "camp2"),
    ]
    preprocessor = MessagePreprocessor()
    deduped, removed = preprocessor.deduplicate(recs)
    assert len(deduped) == 2
    assert removed == 1


def test_leakage_free_partitioning():
    """Verify variants sharing template fingerprint are grouped in the same split."""
    recs = [
        MessageRecord("1", "Update PAN now for account 1234 at http://link1.test", 1, "kyc", "en", "src", True, "camp1"),
        MessageRecord("2", "Update PAN now for account 5678 at http://link2.test", 1, "kyc", "en", "src", True, "camp1"),
        MessageRecord("3", "Unrelated routine salary credited INR 50000", 0, "benign", "en", "src", False, "camp2"),
    ]
    preprocessor = MessagePreprocessor(test_ratio=0.5, random_seed=42)
    partitioned, stats = preprocessor.partition_leakage_free(recs)

    rec1 = next(r for r in partitioned if r.id == "1")
    rec2 = next(r for r in partitioned if r.id == "2")
    assert rec1.split == rec2.split, "Template variants must be assigned to the same partition to prevent leakage"
    assert stats.total_deduplicated == 3


def test_baseline_message_model_lifecycle(tmp_path):
    """Test model fitting, prediction, evaluation, and persistence."""
    train_texts = [
        "Your bank account is blocked due to KYC. Click here immediately.",
        "Electricity bill unpaid. Power will be disconnected tonight.",
        "Congratulations you won a cash prize of INR 50,000 call now.",
        "Your monthly statement is ready for download.",
        "Salary of INR 45,000 credited to your account XX1234.",
        "Meeting confirmed for tomorrow at 10 AM.",
    ]
    train_labels = [1, 1, 1, 0, 0, 0]

    model = BaselineMessageModel()
    model.fit(train_texts, train_labels)

    pred = model.predict_single("Your electricity power is disconnected tonight update now")
    assert pred["is_scam"] is True
    assert pred["scam_probability"] > 0.5
    assert 0.0 <= pred["confidence"] <= 1.0

    eval_res = model.evaluate(train_texts, train_labels)
    assert eval_res["accuracy"] >= 0.80

    # Save & reload
    save_dir = tmp_path / "artifacts"
    model.save(save_dir)
    assert (save_dir / "model.joblib").exists()
    assert (save_dir / "vectorizer.joblib").exists()

    loaded = BaselineMessageModel.load(save_dir)
    pred_loaded = loaded.predict_single("Your electricity power is disconnected tonight")
    assert pred_loaded["is_scam"] == pred["is_scam"]


def test_model_comparison_artifact_exists():
    """Verify comparative evaluation metrics were persisted to artifacts."""
    comparison_file = ROOT_DIR / "ml" / "message" / "artifacts" / "model_comparison.json"
    assert comparison_file.exists(), "ml/message/artifacts/model_comparison.json must exist"

    with open(comparison_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "models" in data
    assert "tfidf_logistic_regression" in data["models"]
    assert "distilbert_transformer" in data["models"]

    tfidf_f1 = data["models"]["tfidf_logistic_regression"]["f1_score"]
    assert tfidf_f1 >= 0.85, f"Baseline TF-IDF F1 score must be high (got {tfidf_f1})"


def test_message_intelligence_service_threat_signals():
    """Test that suspicious messages generate appropriate semantic evidence signals."""
    service = MessageIntelligenceService()

    msg = "Urgent: SBI Netbanking blocked! Update your KYC and verify OTP immediately at https://sbi-secure.test"
    analysis = service.analyze_message(text=msg, incident_id="inc_test_123", include_embedding=False)

    assert analysis.classification_signal["is_scam"] is True
    assert analysis.classification_signal["scam_probability"] > 0.70

    # Check extracted linguistic signals
    assert analysis.extracted_signals["has_urgency"] is True
    assert "SBI" in analysis.extracted_signals["impersonated_entities"]
    assert analysis.extracted_signals["solicits_credentials"] is True

    # Check generated EvidenceSignals
    signal_types = [s["signal_type"] for s in analysis.evidence_signals]
    assert "URGENCY_PRESSURE_DETECTED" in signal_types
    assert "OFFICIAL_ENTITY_IMPERSONATION" in signal_types
    assert "SENSITIVE_CREDENTIAL_SOLICITATION" in signal_types

    # Ensure dimension is SEMANTIC
    for s in analysis.evidence_signals:
        assert s["dimension"] == "SEMANTIC"
        assert s["provenance"]["source_service"] == "services/investigation/message_ai"


def test_message_intelligence_service_counter_evidence():
    """Test that benign transactional updates generate counter-evidence."""
    service = MessageIntelligenceService()

    msg = "Dear Customer, INR 3,500.00 credited to your A/C XX8812 on 20-Oct-2026. Avail Bal: INR 35,420.00. Ref 10928374."
    analysis = service.analyze_message(text=msg, incident_id="inc_test_456", include_embedding=False)

    assert analysis.extracted_signals["is_routine_transaction"] is True
    assert analysis.extracted_signals["has_urgency"] is False

    # Must contain counter-evidence
    counter_signals = [s for s in analysis.evidence_signals if s.get("is_counter_evidence")]
    assert len(counter_signals) >= 1
    assert counter_signals[0]["signal_type"] == "LEGITIMATE_TRANSACTION_NOTIFICATION"


def test_constitutional_rule_10_no_autonomous_verdict():
    """Constitutional Rule 10: Message intelligence outputs evidence signals, never final fraud verdict."""
    service = MessageIntelligenceService()
    analysis = service.analyze_message(
        text="Claim your lottery prize now at https://fake.test",
        incident_id="inc_rule10",
        include_embedding=False,
    )

    d = analysis.to_dict()
    # Output must NOT have automated verdict keys like 'final_fraud_verdict' or 'block_user'
    assert "final_verdict" not in d
    assert "block_transaction" not in d
    assert "automated_decision" not in d

    # Instead, outputs structured classification signal and evidence signals for fusion engine
    assert "classification_signal" in d
    assert "evidence_signals" in d
    assert isinstance(d["evidence_signals"], list)
