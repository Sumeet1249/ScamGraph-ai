# Leakage Prevention & Partitioning Architecture
**Phase 0C: Technical Framework**  
**Date:** October 24, 2026

---

## 1. Forms of Leakage in Scam Intelligence

1. **Exact Duplicate Leakage**: Identical messages broadcast by spam bots appearing in both training and evaluation splits.
2. **Template Leakage**: Messages with identical syntax where only entity variables (phone number, bank name, amount, link) differ.
3. **Campaign Leakage**: Splitting different messages from the same underlying infrastructure cluster across train and test.
4. **Temporal Leakage**: Evaluating on past data while training on future data.
5. **Synthetic Generator Leakage**: Testing on synthetic samples produced by the same prompt template used during training data synthesis.

---

## 2. Leakage Mitigation Architecture

The `LeakageAuditor` and `DatasetSplitter` enforce strict partitioning:
- Abstracting entities into structural tokens:
  ```python
  sig = extract_template_signature("Your SBI account will be blocked visit https://sbi.tk")
  # Produces: "your <BANK> account will be blocked visit <URL>"
  ```
- Partitioning by group keys so that zero records sharing an abstracted template signature cross between Train and Test splits.
- Automated assertion in test suites ensuring that any benchmark claiming `GOLD_BENCHMARK` status has zero exact or template overlaps with training corpora.
