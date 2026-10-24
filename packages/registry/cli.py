"""CLI utility to validate datasets.yaml and models.yaml governance constraints."""

import sys
from packages.registry.validator import validate_registry


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "validate-registries":
        print("=" * 60)
        print(" ScamGraph AI — Dataset & Model Registry Validation ")
        print("=" * 60)
        
        result = validate_registry()
        
        # Datasets
        if result["dataset_errors"]:
            print("\n[ERROR] DATASET ERRORS:")
            for err in result["dataset_errors"]:
                print(f"  * {err}")
        else:
            print("\n[OK] Datasets Registry (v2.0.0): VALID")

        if result["dataset_warnings"]:
            print("\n[WARN] DATASET WARNINGS:")
            for w in result["dataset_warnings"]:
                print(f"  * {w}")

        # Models
        if result["model_errors"]:
            print("\n[ERROR] MODEL ERRORS:")
            for err in result["model_errors"]:
                print(f"  * {err}")
        else:
            print("[OK] Models Registry (v1.0.0): VALID")

        if result["model_warnings"]:
            print("\n[WARN] MODEL WARNINGS:")
            for w in result["model_warnings"]:
                print(f"  * {w}")

        print("\n" + "=" * 60)
        if result["valid"]:
            print(" ALL REGISTRIES CONFORM TO GOVERNANCE POLICIES ")
            print("=" * 60)
            sys.exit(0)
        else:
            print(" REGISTRY VALIDATION FAILED ")
            print("=" * 60)
            sys.exit(1)
    else:
        print("Usage: python -m packages.registry.cli validate-registries")
        sys.exit(1)


if __name__ == "__main__":
    main()
