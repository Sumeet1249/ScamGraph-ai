"""Dataset loaders for ScamGraph AI Message Intelligence.

Provides robust loaders for:
1. anmolshrivastav/scam-ham-india (India base, 2,272 msgs)
2. Ridham115/indian-scam-sms-synthetic-audited (multilingual / code-mixed, 1,580 msgs)
3. Internal ScamGraph synthetic journey messages (data/scenarios)

Bypasses Python 3.14 dill/arrow pickler bugs by reading CSV/JSON directly.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass
class MessageRecord:
    """Canonical representation of a single message data point."""

    id: str
    text: str
    label: int  # 0 = benign/ham, 1 = scam/spam
    scam_type: str  # e.g., 'fake_kyc', 'electricity_bill', 'loan_offer', 'benign'
    language: str  # e.g., 'en', 'hinglish', 'hi', 'bn_en', etc.
    source_dataset: str
    is_synthetic: bool
    campaign_id: str
    split: str = "train"  # 'train' or 'test'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_scamgraph_record_v2(self) -> Any:
        """Convert legacy MessageRecord to canonical ScamGraphRecordV2."""
        from packages.schemas.dataset import ScamGraphRecordV2
        return ScamGraphRecordV2.from_legacy(self)


def _compute_stable_id(text: str, source: str) -> str:
    """Compute a deterministic hash ID for a message."""
    h = hashlib.sha256(f"{source}:{text.strip()}".encode("utf-8")).hexdigest()
    return f"{source[:8]}_{h[:12]}"


def _infer_scam_type_from_text(text: str, label: int) -> str:
    """Heuristic scam type extraction for unannotated scam datasets."""
    if label == 0:
        return "benign"
    lower = text.lower()
    if any(k in lower for k in ["kyc", "pan", "aadhaar", "block", "freeze", "sbi", "hdfc", "icici", "pnb"]):
        return "fake_kyc"
    if any(k in lower for k in ["electricity", "power", "discom", "bill unpaid", "bijli", "line cut"]):
        return "electricity_bill"
    if any(k in lower for k in ["loan", "approved", "instant loan", "credit limit", "disbursed"]):
        return "loan_offer"
    if any(k in lower for k in ["job", "work from home", "wfh", "salary", "hiring", "part time", "daily income"]):
        return "job_offer"
    if any(k in lower for k in ["lottery", "won", "prize", "cashback", "lucky draw", "reward"]):
        return "lottery"
    if any(k in lower for k in ["courier", "parcel", "customs", "delivery", "fedex", "dhl", "indiapost"]):
        return "courier_customs"
    if any(k in lower for k in ["otp", "pin", "cvv", "verification code"]):
        return "fake_bank_otp"
    return "generic_scam"


def load_scam_ham_india(csv_path: Optional[str] = None) -> List[MessageRecord]:
    """Load anmolshrivastav/scam-ham-india dataset."""
    if not csv_path:
        from huggingface_hub import hf_hub_download

        csv_path = hf_hub_download(
            repo_id="anmolshrivastav/scam-ham-india",
            filename="scam_hum_india.csv",
            repo_type="dataset",
        )

    df = pd.read_csv(csv_path)
    records: List[MessageRecord] = []

    for _, row in df.iterrows():
        raw_text = str(row.get("text", "")).strip()
        if not raw_text:
            continue
        raw_label = str(row.get("label", "ham")).lower().strip()
        int_label = 1 if raw_label in ("spam", "scam", "1") else 0
        scam_type = _infer_scam_type_from_text(raw_text, int_label)
        record_id = _compute_stable_id(raw_text, "scam_ham_india")

        records.append(
            MessageRecord(
                id=record_id,
                text=raw_text,
                label=int_label,
                scam_type=scam_type,
                language="en",
                source_dataset="anmolshrivastav/scam-ham-india",
                is_synthetic=False,  # base dataset mixes real/synthetic without explicit labels
                campaign_id=scam_type,
            )
        )
    return records


def load_indian_scam_sms_synthetic(
    csv_path: Optional[str] = None,
    exclude_rejected: bool = True,
    exclude_unreviewed: bool = True,
) -> List[MessageRecord]:
    """Load Ridham115/indian-scam-sms-synthetic-audited dataset.
    
    Args:
        csv_path: Path to CSV file (default: download from HF)
        exclude_rejected: Skip rows with audit_action='reject' (default: True)
        exclude_unreviewed: Skip rows with audit_action='unreviewed' (default: True)
    """
    if not csv_path:
        from huggingface_hub import hf_hub_download

        csv_path = hf_hub_download(
            repo_id="Ridham115/indian-scam-sms-synthetic-audited",
            filename="data/synthetic_audited.csv",
            repo_type="dataset",
        )

    df = pd.read_csv(csv_path)
    records: List[MessageRecord] = []
    rejected_count = 0
    unreviewed_count = 0

    for _, row in df.iterrows():
        raw_text = str(row.get("text", "")).strip()
        if not raw_text:
            continue

        audit_action = str(row.get("audit_action", "unreviewed")).lower().strip()
        
        # Filter rejected records
        if exclude_rejected and audit_action == "reject":
            rejected_count += 1
            continue
        
        # Filter unreviewed records (critical: was missing before)
        if exclude_unreviewed and audit_action == "unreviewed":
            unreviewed_count += 1
            continue

        raw_label = str(row.get("label", "safe")).lower().strip()
        int_label = 1 if raw_label in ("scam", "1") else 0

        scam_type = str(row.get("scam_type", "none")).lower().strip()
        if scam_type in ("none", ""):
            scam_type = "benign" if int_label == 0 else "generic_scam"

        language = str(row.get("language", "en")).lower().strip()
        campaign_id = str(row.get("topic", scam_type)).lower().strip()
        row_id = str(row.get("row_id", ""))
        rec_id = f"ridham_{row_id}" if row_id else _compute_stable_id(raw_text, "ridham")

        records.append(
            MessageRecord(
                id=rec_id,
                text=raw_text,
                label=int_label,
                scam_type=scam_type,
                language=language,
                source_dataset="Ridham115/indian-scam-sms-synthetic-audited",
                is_synthetic=True,
                campaign_id=campaign_id,
            )
        )
    
    if exclude_rejected or exclude_unreviewed:
        logger.info(
            f"Ridham115 filtering: rejected={rejected_count}, unreviewed={unreviewed_count}, "
            f"kept={len(records)}"
        )
    
    return records


def load_canonical_journeys(scenarios_dir: Optional[str] = None) -> List[MessageRecord]:
    """Extract message events from canonical journey scenarios in data/scenarios."""
    target_dir = Path(scenarios_dir) if scenarios_dir else ROOT_DIR / "data" / "scenarios"
    records: List[MessageRecord] = []

    if not target_dir.exists():
        return records

    for file_path in sorted(target_dir.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read scenario {file_path}: {e}")
            continue

        scenario_id = data.get("id", file_path.stem)
        expected_risk = data.get("expected_risk_level", "LOW")
        int_label = 0 if expected_risk in ("LOW", "BENIGN") else 1
        expected_pattern = str(data.get("expected_pattern") or "BENIGN").lower()

        events = data.get("events", [])
        for idx, event in enumerate(events):
            channel = str(event.get("channel", "")).upper()
            event_type = str(event.get("event_type", "")).upper()
            desc = str(event.get("description", "")).strip()

            # Filter for message-bearing events
            if channel in ("SMS", "WHATSAPP", "EMAIL", "TELEGRAM") or event_type in (
                "MESSAGE_RECEIVED",
                "CREDENTIAL_REQUEST",
                "PAYMENT_REQUEST",
            ):
                if not desc:
                    continue
                # Clean up prefix like "SMS: " or "WhatsApp: "
                clean_text = desc
                for prefix in ["SMS: ", "WhatsApp: ", "Email: ", "Telegram: "]:
                    if clean_text.startswith(prefix):
                        clean_text = clean_text[len(prefix) :].strip()

                rec_id = f"journey_{scenario_id}_{idx}"
                records.append(
                    MessageRecord(
                        id=rec_id,
                        text=clean_text,
                        label=int_label,
                        scam_type=expected_pattern if int_label == 1 else "benign",
                        language="en",
                        source_dataset="scamgraph-canonical-journeys",
                        is_synthetic=True,
                        campaign_id=scenario_id,
                    )
                )

    return records


def load_all_datasets(
    scam_ham_path: Optional[str] = None,
    ridham_path: Optional[str] = None,
    scenarios_dir: Optional[str] = None,
) -> List[MessageRecord]:
    """Load and unify all three message datasets."""
    all_records: List[MessageRecord] = []

    try:
        sh_records = load_scam_ham_india(scam_ham_path)
        logger.info(f"Loaded {len(sh_records)} records from scam-ham-india")
        all_records.extend(sh_records)
    except Exception as e:
        logger.error(f"Failed to load scam-ham-india: {e}")

    try:
        ridham_records = load_indian_scam_sms_synthetic(ridham_path)
        logger.info(f"Loaded {len(ridham_records)} records from Ridham115 synthetic audited")
        all_records.extend(ridham_records)
    except Exception as e:
        logger.error(f"Failed to load Ridham115 dataset: {e}")

    try:
        journey_records = load_canonical_journeys(scenarios_dir)
        logger.info(f"Loaded {len(journey_records)} records from canonical journeys")
        all_records.extend(journey_records)
    except Exception as e:
        logger.error(f"Failed to load canonical journeys: {e}")

    return all_records
