# Gold Evaluation Set (`data/gold/`)

## Intended Purpose
The Gold Evaluation Set represents the sacred, verified ground truth for ScamGraph AI. It is used exclusively to measure true generalization against realistic Indian scam scenarios.

## Strict Governance Policies
1. **INDEPENDENT EVALUATION ONLY**: Data in this directory must NEVER be used for:
   - Model training
   - Training data augmentation
   - Synthetic prompt generation
   - Feature engineering or hyperparameter tuning
2. **NO CONTAMINATION**: Model developers must not iteratively inspect or overfit models against the final held-out gold test splits.
3. **HUMAN CONSENSUS GROUND TRUTH**: All records in the Gold Set must have `AnnotationType.HUMAN_VERIFIED` or `HUMAN_MULTI_REVIEW`. Synthetic data cannot be marked as approved gold data without an explicit architectural override and human review.
4. **TEMPLATE ISOLATION**: No message sharing a template cluster ID with training records may enter the gold set.
