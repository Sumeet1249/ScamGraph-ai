# Multimodal Evidence Fusion Specification

## 1. Objective: Corroboration vs. Dependency
Evidence fusion in ScamGraph is not naive score averaging. Its primary job is:
1. **Tree Lineage Tracking**: Mapping each observation back to its root artifact.
2. **Preventing Double Counting**: 
   - Example: Screenshot $\to$ OCR text $\to$ Phone extraction.
   - Count: 1 independent source, not 3 pieces of evidence.
3. **Detecting Independent Corroboration**:
   - Example: Screenshot contains UPI VPA `payee@oksbi` AND a physically separate QR image contains `payee@oksbi`.
   - Distinct root source IDs prove cross-modal independent corroboration, boosting assessment confidence.

## 2. Contradiction Resolution
If OCR indicates an authorized institutional notice while URL domain analysis indicates an unverified punycode or dynamic DNS host, the contradiction is preserved and elevated as high risk.
