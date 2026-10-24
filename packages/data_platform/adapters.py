"""Concrete dataset adapters for external research and community datasets."""

import hashlib
from typing import Any, Dict, List, Optional
from packages.data_platform.base_adapter import DatasetAdapter
from packages.schemas.common import generate_id
from packages.schemas.dataset import LanguageMetadata, ScamGraphRecordV2, SplitMetadata, SplitType
from packages.schemas.provenance import AnnotationRecord, AnnotationType, SourceProvenanceRecord, SourceProvenanceType


class ScamHamIndiaAdapter(DatasetAdapter):
    """Adapter for anmolshrivastav/scam-ham-india (2,272 SMS)."""

    @property
    def dataset_id(self) -> str:
        return "scam-ham-india"

    @property
    def declared_license(self) -> str:
        return "apache-2.0"

    def load_raw(self, source_path_or_df: Any) -> List[Any]:
        if hasattr(source_path_or_df, "to_dict"):
            return source_path_or_df.to_dict(orient="records")
        return list(source_path_or_df)

    def map_record(self, raw_item: Dict[str, Any]) -> ScamGraphRecordV2:
        text = str(raw_item.get("text", "")).strip()
        label_raw = str(raw_item.get("label", "ham")).lower().strip()
        label = 1 if label_raw in ("spam", "scam", "1") else 0
        
        # Provenance: PUBLIC_MIXED (not 100% verified real)
        prov = SourceProvenanceRecord(
            source_name="anmolshrivastav/scam-ham-india",
            source_type=SourceProvenanceType.PUBLIC_MIXED,
            source_uri="https://huggingface.co/datasets/anmolshrivastav/scam-ham-india",
            dataset_id=self.dataset_id,
            license=self.declared_license,
        )
        return ScamGraphRecordV2(
            record_id=f"shi_{hashlib.sha256(text.encode()).hexdigest()[:12]}",
            content=text,
            provenance=prov,
            labels={"is_scam": label},
            annotations=[
                AnnotationRecord(
                    label_name="is_scam",
                    label_value=label,
                    annotation_type=AnnotationType.SOURCE_PROVIDED,
                )
            ],
            language=LanguageMetadata(primary_language="en"),
        )


class ICFD31kAdapter(DatasetAdapter):
    """Adapter for rishia2220/icfd-31k (Conversational synthetic phone calls)."""

    @property
    def dataset_id(self) -> str:
        return "rishia2220-icfd-31k"

    @property
    def declared_license(self) -> str:
        return "cc-by-nc-4.0"

    def load_raw(self, source_path_or_df: Any) -> List[Any]:
        return list(source_path_or_df)

    def map_record(self, raw_item: Dict[str, Any]) -> ScamGraphRecordV2:
        dialogue = str(raw_item.get("conversation", raw_item.get("text", ""))).strip()
        label = 1 if str(raw_item.get("label", "scam")).lower() in ("scam", "fraud", "1") else 0
        scam_type = str(raw_item.get("scam_type", "phone_fraud"))

        # Strictly classified as SYNTHETIC_LLM
        prov = SourceProvenanceRecord(
            source_name="rishia2220/icfd-31k",
            source_type=SourceProvenanceType.SYNTHETIC_LLM,
            source_uri="https://huggingface.co/datasets/rishia2220/icfd-31k",
            dataset_id=self.dataset_id,
            license=self.declared_license,
            generator_model="LLM Phone Simulation",
        )
        return ScamGraphRecordV2(
            record_id=f"icfd_{hashlib.sha256(dialogue.encode()).hexdigest()[:12]}",
            content=dialogue,
            provenance=prov,
            labels={"is_scam": label, "scam_type": scam_type},
            annotations=[
                AnnotationRecord(
                    label_name="is_scam",
                    label_value=label,
                    annotation_type=AnnotationType.SYNTHETIC_GROUND_TRUTH,
                )
            ],
            language=LanguageMetadata(primary_language="en", code_mixed=True),
        )


class HinglishScamAdapter(DatasetAdapter):
    """Adapter for bolewara/hinglish-scam-text-dataset (3,787 messages)."""

    @property
    def dataset_id(self) -> str:
        return "bolewara-hinglish-scam-text-dataset"

    @property
    def declared_license(self) -> str:
        return "mit"

    def load_raw(self, source_path_or_df: Any) -> List[Any]:
        return list(source_path_or_df)

    def map_record(self, raw_item: Dict[str, Any]) -> ScamGraphRecordV2:
        text = str(raw_item.get("text", raw_item.get("message", ""))).strip()
        label_raw = str(raw_item.get("label", "ham")).lower()
        label = 1 if label_raw in ("spam", "scam", "1") else 0
        hinglish_markers = ["karo", "aapse", "bhejo", "karein", "hai", "apna", "bijli", "bharein", "nahi", "turant", "hogi"]
        is_hinglish = bool(raw_item.get("is_hinglish", False)) or any(w in text.lower() for w in hinglish_markers)

        prov = SourceProvenanceRecord(
            source_name="bolewara/hinglish-scam-text-dataset",
            source_type=SourceProvenanceType.PUBLIC_MIXED,
            source_uri="https://huggingface.co/datasets/bolewara/hinglish-scam-text-dataset",
            dataset_id=self.dataset_id,
            license=self.declared_license,
        )
        return ScamGraphRecordV2(
            record_id=f"hng_{hashlib.sha256(text.encode()).hexdigest()[:12]}",
            content=text,
            provenance=prov,
            labels={"is_scam": label},
            annotations=[
                AnnotationRecord(
                    label_name="is_scam",
                    label_value=label,
                    annotation_type=AnnotationType.SOURCE_PROVIDED,
                )
            ],
            language=LanguageMetadata(
                primary_language="hi" if is_hinglish else "en",
                script="Latn",
                code_mixed=is_hinglish,
                transliterated=is_hinglish,
            ),
        )
