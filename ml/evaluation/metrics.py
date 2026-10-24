"""Core metric computation for binary classification, FPR/FNR, and journey lead time."""

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
)

from packages.schemas.evaluation import ClassificationMetrics, LeadTimeMetrics


def compute_classification_metrics(
    y_true: List[int],
    y_pred: List[int],
    y_prob: Optional[List[float]] = None,
) -> ClassificationMetrics:
    """Compute comprehensive classification metrics with prominent FPR/FNR visibility."""
    y_t = np.array(y_true, dtype=int)
    y_p = np.array(y_pred, dtype=int)
    
    cm = confusion_matrix(y_t, y_p, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    # False Positive Rate = FP / (FP + TN)
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    # False Negative Rate = FN / (FN + TP)
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
    # Specificity = TN / (TN + FP)
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    acc = float(accuracy_score(y_t, y_p))
    prec = float(precision_score(y_t, y_p, zero_division=0))
    rec = float(recall_score(y_t, y_p, zero_division=0))
    f1 = float(f1_score(y_t, y_p, zero_division=0))
    macro_f1 = float(f1_score(y_t, y_p, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_t, y_p, average="weighted", zero_division=0))
    bal_acc = float(balanced_accuracy_score(y_t, y_p))
    
    roc_auc = None
    pr_auc = None
    if y_prob is not None and len(np.unique(y_t)) > 1:
        try:
            roc_auc = float(roc_auc_score(y_t, y_prob))
            pr_auc = float(average_precision_score(y_t, y_prob))
        except Exception:
            pass

    return ClassificationMetrics(
        accuracy=round(acc, 4),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1=round(f1, 4),
        macro_f1=round(macro_f1, 4),
        weighted_f1=round(weighted_f1, 4),
        false_positive_rate=round(fpr, 4),
        false_negative_rate=round(fnr, 4),
        specificity=round(specificity, 4),
        balanced_accuracy=round(bal_acc, 4),
        roc_auc=round(roc_auc, 4) if roc_auc is not None else None,
        pr_auc=round(pr_auc, 4) if pr_auc is not None else None,
        confusion_matrix={"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        sample_count=len(y_t),
        positive_count=int(tp + fn),
        negative_count=int(tn + fp),
    )


def compute_lead_time_metrics(
    journey_timelines: List[Dict[str, Any]]
) -> LeadTimeMetrics:
    """Compute Pre-Loss Detection Rate and Warning Lead Time across labeled journeys.
    
    Expected format per journey:
    {
        "journey_id": "j_01",
        "has_loss": True,
        "loss_timestamp_sec": 1200,     # Time of major transfer / loss
        "first_warning_sec": 450,       # Time ScamGraph first raised >= MEDIUM risk
        "detected_early": True          # Warned before initial payment attempt
    }
    """
    if not journey_timelines:
        return LeadTimeMetrics()
        
    evaluated_count = len(journey_timelines)
    pre_loss_success = 0
    early_detected_count = 0
    lead_times_sec: List[float] = []

    for j in journey_timelines:
        has_loss = j.get("has_loss", False)
        loss_ts = j.get("loss_timestamp_sec")
        warn_ts = j.get("first_warning_sec")
        
        if j.get("detected_early"):
            early_detected_count += 1
            
        if has_loss and loss_ts is not None and warn_ts is not None:
            if warn_ts <= loss_ts:
                pre_loss_success += 1
                lead_times_sec.append(float(loss_ts - warn_ts))

    lead_times_arr = np.array(lead_times_sec) if lead_times_sec else None

    return LeadTimeMetrics(
        pre_loss_detection_rate=round(float(pre_loss_success / evaluated_count), 4) if evaluated_count else 0.0,
        early_detection_rate=round(float(early_detected_count / evaluated_count), 4) if evaluated_count else 0.0,
        median_warning_lead_time_sec=round(float(np.median(lead_times_arr)), 1) if lead_times_arr is not None and len(lead_times_arr) else None,
        mean_warning_lead_time_sec=round(float(np.mean(lead_times_arr)), 1) if lead_times_arr is not None and len(lead_times_arr) else None,
        p25_lead_time_sec=round(float(np.percentile(lead_times_arr, 25)), 1) if lead_times_arr is not None and len(lead_times_arr) else None,
        p75_lead_time_sec=round(float(np.percentile(lead_times_arr, 75)), 1) if lead_times_arr is not None and len(lead_times_arr) else None,
        p90_lead_time_sec=round(float(np.percentile(lead_times_arr, 90)), 1) if lead_times_arr is not None and len(lead_times_arr) else None,
        evaluated_journeys_count=evaluated_count,
    )
