# ML Evaluation Framework

ScamGraph's comprehensive evaluation infrastructure for dataset quality, model benchmarking, and production readiness.

## Components

### `benchmark_runner.py`
Orchestrates model evaluation across multiple test sets and generates comparison reports.

**Key Classes:**
- `ModelMetrics`: Canonical metric set (F1, precision, recall, FPR, ROC-AUC, confusion matrix)
- `BenchmarkResult`: Single model evaluation result
- `BenchmarkRunner`: Orchestrates benchmarking and report generation

**Usage:**
```python
from ml.evaluation.benchmark_runner import BenchmarkRunner

runner = BenchmarkRunner(output_dir="path/to/output")
runner.record_result(
    model_name="My Model",
    model_id="my_model_v1",
    test_set_name="In-Distribution Test",
    test_set_id="in_dist_main",
    y_true=test_labels,
    y_pred=predictions,
    y_prob=probabilities,
)
runner.save_results("benchmark_results.json")
runner.save_report("benchmark_report.txt")
```

### `leakage_checks.py`
Detects data leakage between train and test sets.

**Detects:**
1. **Exact Duplicates**: Identical strings in both sets
2. **Semantic Duplicates**: High-similarity variations (default threshold: 95%)
3. **Campaign Leakage**: Same scam template in both sets
4. **Source Dataset Contamination**: Same dataset split improperly

**Usage:**
```python
from ml.evaluation.leakage_checks import check_leakage

report = check_leakage(train_records, test_records)
print(f"Clean split: {report.is_clean}")
for warning in report.warnings:
    print(f"  ⚠ {warning}")
```

### `calibration.py`
Analyzes model probability calibration (do predicted probabilities match observed frequencies?).

**Metrics:**
- **ECE (Expected Calibration Error)**: Average difference per probability bin
- **MCE (Maximum Calibration Error)**: Worst-case bin error
- Per-bin reliability scores

**Interpretation:**
- ECE < 0.05: Excellent calibration → trust predicted probabilities
- 0.05 < ECE < 0.2: Moderate → consider calibration if threshold is critical
- ECE > 0.2: Poor → adjust decision threshold

**Usage:**
```python
from ml.evaluation.calibration import CalibrationAnalyzer, calibration_report

analyzer = CalibrationAnalyzer()
metrics = analyzer.analyze_calibration(y_true, y_prob)
print(calibration_report(y_true, y_prob, "My Model"))
```

### `phase_1_2_test.py`
End-to-end test suite for Phase 1-2.

**PHASE 1: Dataset Validation**
- Verify unreviewed records are excluded
- Check for exact duplicates
- Validate language preservation
- Check provenance distribution

**PHASE 2: Model Benchmarking**
- Train baseline (TF-IDF + Logistic Regression)
- Check for data leakage
- Analyze model calibration
- [Optional] Load and benchmark multilingual transformer

**Usage:**
```bash
# Phase 1 only
python ml/evaluation/phase_1_2_test.py --phase 1

# Phase 2 only
python ml/evaluation/phase_1_2_test.py --phase 2

# Both phases
python ml/evaluation/phase_1_2_test.py --phase all
```

## Test Set Types

The framework supports multiple test set types:

| Test Set | Purpose | Notes |
|----------|---------|-------|
| **In-Distribution** | Familiar patterns with deduplication | Main evaluation |
| **Unseen Campaign** | New templates not in training | Tests generalization |
| **Language-Specific** | English, Hindi, Hinglish separately | Tests multilingual robustness |
| **Hard Negatives** | Legitimate notifications resembling scams | Tests false positive rate |
| **Time-Based** | Older training vs newer test | Tests temporal drift |
| **Calibration** | Probability reliability | Tests confidence calibration |

## Key Metrics

### Main Metrics
- **F1**: Harmonic mean of precision and recall
- **Precision**: Of predicted scams, what % are actually scams?
- **Recall**: Of actual scams, what % are detected?
- **False Positive Rate**: Legitimate messages falsely flagged as scam
- **ROC-AUC**: Area under receiver operating characteristic

### Interpretation Guidance

**Better for Scam Detection:**
- Higher recall (catch more scams, accept higher FPR)
- Lower false negative rate (don't miss scams)

**Better for Legitimate Messages:**
- Higher precision (fewer false alarms)
- Lower false positive rate (don't over-flag legitimate messages)

**Choose threshold based on cost:**
- Missed scam (false negative): Very costly → maximize recall
- False alarm (false positive): Moderately costly → balance with precision

## Critical Fixes (Phase 1)

### Fixed Dataset Loader Bug
**Issue**: `load_indian_scam_sms_synthetic()` was NOT filtering unreviewed records, despite the registry documenting 1,350 unreviewed examples.

**Fix**: Added `exclude_unreviewed=True` parameter (now default).

```python
# Before (incorrect):
if exclude_rejected and audit_action == "reject":
    continue
# Missing: unreviewed filtering

# After (correct):
if exclude_rejected and audit_action == "reject":
    rejected_count += 1
    continue
if exclude_unreviewed and audit_action == "unreviewed":
    unreviewed_count += 1
    continue
```

**Impact**: Improves data quality by excluding records marked for review.

## Next Steps

1. **Run Phase 1**: Validate dataset quality
   ```bash
   python ml/evaluation/phase_1_2_test.py --phase 1
   ```

2. **Run Phase 2**: Benchmark models
   ```bash
   python ml/evaluation/phase_1_2_test.py --phase 2
   ```

3. **Review Reports**: Check generated JSON and TXT reports
   - `ml/message/artifacts/benchmarks/benchmark_results.json`
   - `ml/message/artifacts/benchmarks/benchmark_report.txt`

4. **Add Hard Negatives**: Create test set with legitimate notifications

5. **Benchmark Multilingual Model**: Test on Hindi/Hinglish subset

6. **Compare Against URLBERT**: Evaluate URL detection specialist

## References

- Leakage detection: Inspired by MLOps best practices (Zeller et al.)
- Calibration: Expected Calibration Error (Guo et al., 2017)
- Benchmark framework: Follows scikit-learn and industry standards
