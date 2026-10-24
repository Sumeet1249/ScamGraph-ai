# ScamFingerprintV2 to ScamDNA V3 Migration Specification

## 1. Executive Summary
This document defines the architectural evolution from `ScamFingerprintV2` (a 5-attribute dictionary-based representation) to `ScamDNA V3` (an 8-dimensional decoupled behavioral engine).

---

## 2. Component Disposition Matrix

| Component | Disposition | Details & Rationale |
| :--- | :--- | :--- |
| **`ScamFingerprint` (V1)** | **`DEPRECATED`** | Maintained strictly for legacy test compatibility. |
| **`ScamFingerprintV2` (V2)** | **`RETAINED / COMPATIBLE`** | Retained as a valid schema model. Downstream services seamlessly convert between V2 and V3 using `ScamFingerprintV2Adapter`. |
| **`ScamFingerprintSimilarityEngine`**| **`REFACTORED`** | Retains existing interface while routing advanced comparisons to the 8-dimensional `ScamDNASimilarityEngine`. |
| **`ScamDNABuilder`** | **`NEW (V3)`** | Core builder creating 8-dimensional ScamDNA models with privacy safeguards. |
| **`ScamDNASimilarityEngine`** | **`NEW (V3)`** | 8-dimensional similarity engine with dynamic re-normalization and contradiction penalties. |
| **`DNACandidateIndex`** | **`NEW (V3)`** | Inverted index preventing $O(N^2)$ comparison bottlenecks. |
| **`EmergingVariantDetector`** | **`REFACTORED`** | Accepts `ScamDNA` directly alongside `ScamFingerprintV2`. |

---

## 3. Backward Compatibility Layer
The `ScamFingerprintV2Adapter` class provides bidirectional conversion:
- `ScamFingerprintV2Adapter.to_dna(fp_v2) -> ScamDNA`
- `ScamFingerprintV2Adapter.to_fingerprint_v2(dna) -> ScamFingerprintV2`

Existing databases, JSON payloads, or test fixtures utilizing `ScamFingerprintV2` can be converted on the fly without loss of provenance. Missing dimensions in legacy records are marked `available=False` and gracefully handled during similarity computation.
