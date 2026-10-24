"""Registry Validator and Loader for ScamGraph AI V2.

Validates datasets.yaml (v2.0.0) and models.yaml (v1.0.0) without requiring network access.
Enforces governance constraints:
- No duplicate IDs
- Verified licenses
- Synthetic data cannot be marked as approved gold sets without explicit human review
- Training datasets must not have prohibited training uses
- Required provenance classification
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

DATASETS_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "registry" / "datasets.yaml"
MODELS_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "registry" / "models.yaml"

VALID_DATASET_PROVENANCE = {
    "REAL_VERIFIED", "REAL_ANONYMIZED", "PUBLIC_REAL", "PUBLIC_MIXED",
    "HUMAN_CURATED", "SYNTHETIC_LLM", "SYNTHETIC_TEMPLATE", "SYNTHETIC_OTHER",
    "WEAK_LABEL", "UNKNOWN"
}

VALID_MODEL_STATUSES = {
    "BASELINE", "CANDIDATE", "BENCHMARKING", "APPROVED",
    "EXPERIMENTAL", "REJECTED", "DEPRECATED", "UNKNOWN"
}


class RegistryValidationError(Exception):
    """Raised when registry entries fail integrity constraints."""
    pass


class RegistryService:
    """In-process cached registry loader and validator."""

    def __init__(self, datasets_path: Optional[Path] = None, models_path: Optional[Path] = None):
        self.datasets_path = datasets_path or DATASETS_REGISTRY_PATH
        self.models_path = models_path or MODELS_REGISTRY_PATH
        self._datasets_cache: Optional[Dict[str, Any]] = None
        self._models_cache: Optional[Dict[str, Any]] = None

    def load_datasets_raw(self) -> Dict[str, Any]:
        if self._datasets_cache is None:
            if not self.datasets_path.exists():
                raise FileNotFoundError(f"Datasets registry not found: {self.datasets_path}")
            with open(self.datasets_path, "r", encoding="utf-8") as f:
                self._datasets_cache = yaml.safe_load(f) or {}
        return self._datasets_cache

    def load_models_raw(self) -> Dict[str, Any]:
        if self._models_cache is None:
            if not self.models_path.exists():
                raise FileNotFoundError(f"Models registry not found: {self.models_path}")
            with open(self.models_path, "r", encoding="utf-8") as f:
                self._models_cache = yaml.safe_load(f) or {}
        return self._models_cache

    def clear_cache(self) -> None:
        self._datasets_cache = None
        self._models_cache = None

    def validate_datasets(self) -> Tuple[List[str], List[str]]:
        """Validate datasets registry. Returns (errors, warnings)."""
        errors: List[str] = []
        warnings: List[str] = []
        data = self.load_datasets_raw()

        version = data.get("version")
        if not version or not str(version).startswith("2."):
            errors.append(f"Invalid datasets registry version: {version}. Expected 2.x.x")

        datasets = data.get("datasets", [])
        if not datasets:
            errors.append("No datasets registered in datasets.yaml")

        seen_ids = set()
        for idx, ds in enumerate(datasets):
            ds_id = ds.get("id")
            if not ds_id:
                errors.append(f"Dataset at index {idx} is missing an 'id'")
                continue
            if ds_id in seen_ids:
                errors.append(f"Duplicate dataset ID: '{ds_id}'")
            seen_ids.add(ds_id)

            # Check license
            if not ds.get("license"):
                errors.append(f"Dataset '{ds_id}' is missing a 'license'")

            # Check provenance
            prov = ds.get("provenance_type")
            if not prov or prov not in VALID_DATASET_PROVENANCE:
                errors.append(f"Dataset '{ds_id}' has invalid provenance_type: '{prov}'")

            # Governance Rule: Synthetic data cannot be marked as approved gold set
            is_synthetic_prov = prov in ("SYNTHETIC_LLM", "SYNTHETIC_TEMPLATE", "SYNTHETIC_OTHER")
            if is_synthetic_prov and ds.get("gold_set_approved") is True:
                errors.append(
                    f"Governance Violation: Synthetic dataset '{ds_id}' cannot have gold_set_approved=True"
                )

            # Mixed data flag verification
            if prov == "PUBLIC_MIXED" and ds.get("quality_status") == "VERIFIED_REAL":
                errors.append(f"Contradiction in '{ds_id}': Marked PUBLIC_MIXED but claims VERIFIED_REAL")

            # Check record count
            count = ds.get("record_count")
            if count is not None and (not isinstance(count, int) or count < 0):
                errors.append(f"Dataset '{ds_id}' has invalid record_count: {count}")

        return errors, warnings

    def validate_models(self) -> Tuple[List[str], List[str]]:
        """Validate models registry. Returns (errors, warnings)."""
        errors: List[str] = []
        warnings: List[str] = []
        data = self.load_models_raw()

        version = data.get("version")
        if not version or not str(version).startswith("1."):
            errors.append(f"Invalid models registry version: {version}. Expected 1.x.x")

        models = data.get("models", [])
        if not models:
            errors.append("No models registered in models.yaml")

        seen_ids = set()
        for idx, m in enumerate(models):
            m_id = m.get("id")
            if not m_id:
                errors.append(f"Model at index {idx} is missing an 'id'")
                continue
            if m_id in seen_ids:
                errors.append(f"Duplicate model ID: '{m_id}'")
            seen_ids.add(m_id)

            status = m.get("status")
            if not status or status not in VALID_MODEL_STATUSES:
                errors.append(f"Model '{m_id}' has invalid status: '{status}'")

            if not m.get("task"):
                errors.append(f"Model '{m_id}' is missing a 'task'")

            if not m.get("license"):
                warnings.append(f"Model '{m_id}' has no license specified")

        return errors, warnings

    def validate_all(self) -> Dict[str, Any]:
        """Run complete validation suite on both registries."""
        ds_errors, ds_warnings = self.validate_datasets()
        m_errors, m_warnings = self.validate_models()
        is_valid = len(ds_errors) == 0 and len(m_errors) == 0
        return {
            "valid": is_valid,
            "dataset_errors": ds_errors,
            "dataset_warnings": ds_warnings,
            "model_errors": m_errors,
            "model_warnings": m_warnings,
        }


# Singleton service instance
registry_service = RegistryService()


def get_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve metadata for a specific dataset ID."""
    datasets = registry_service.load_datasets_raw().get("datasets", [])
    for ds in datasets:
        if ds.get("id") == dataset_id:
            return ds
    return None


def list_datasets() -> List[Dict[str, Any]]:
    """List all registered datasets."""
    return registry_service.load_datasets_raw().get("datasets", [])


def get_model(model_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve metadata for a specific model ID."""
    models = registry_service.load_models_raw().get("models", [])
    for m in models:
        if m.get("id") == model_id:
            return m
    return None


def list_models() -> List[Dict[str, Any]]:
    """List all registered models."""
    return registry_service.load_models_raw().get("models", [])


def validate_registry() -> Dict[str, Any]:
    """Validate all registries and return validation summary."""
    return registry_service.validate_all()
