"""Stratified multilingual, scam-family, and provenance performance evaluation."""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix


def evaluate_by_subgroup(
    records: List[Any],
    y_true: List[int],
    y_pred: List[int],
    group_extractor: Callable[[Any], str],
    min_samples: int = 5,
) -> Dict[str, Dict[str, Any]]:
    """Compute precision, recall, F1, FPR, and support stratified by subgroup.
    
    Enforces Low-Sample Policy: Subgroups with N < min_samples are marked INSUFFICIENT_SAMPLE_SIZE.
    """
    groups: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: {"true": [], "pred": []})
    
    for r, yt, yp in zip(records, y_true, y_pred):
        grp = group_extractor(r) or "UNKNOWN"
        groups[grp]["true"].append(int(yt))
        groups[grp]["pred"].append(int(yp))
        
    results: Dict[str, Dict[str, Any]] = {}
    
    for grp_name, data in groups.items():
        n = len(data["true"])
        if n < min_samples:
            results[grp_name] = {
                "support": n,
                "status": "INSUFFICIENT_SAMPLE_SIZE",
                "notes": f"N={n} below minimum threshold of {min_samples}",
            }
            continue
            
        yt_arr = np.array(data["true"])
        yp_arr = np.array(data["pred"])
        
        cm = confusion_matrix(yt_arr, yp_arr, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        
        prec = float(precision_score(yt_arr, yp_arr, zero_division=0))
        rec = float(recall_score(yt_arr, yp_arr, zero_division=0))
        f1 = float(f1_score(yt_arr, yp_arr, zero_division=0))
        
        results[grp_name] = {
            "support": n,
            "status": "VALID",
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "positive_count": int(tp + fn),
            "negative_count": int(tn + fp),
        }
        
    return results


def evaluate_multilingual(
    records: List[Any],
    y_true: List[int],
    y_pred: List[int],
    language_extractor: Callable[[Any], str] = lambda r: getattr(r, "language", "en"),
) -> Dict[str, Dict[str, Any]]:
    """Evaluate performance stratified across English, Hindi, Hinglish, etc."""
    return evaluate_by_subgroup(records, y_true, y_pred, group_extractor=language_extractor)


def evaluate_by_scam_family(
    records: List[Any],
    y_true: List[int],
    y_pred: List[int],
    family_extractor: Callable[[Any], str] = lambda r: getattr(r, "scam_type", "unassigned"),
) -> Dict[str, Dict[str, Any]]:
    """Evaluate performance per scam family (KYC, electricity, job scam, etc.)."""
    return evaluate_by_subgroup(records, y_true, y_pred, group_extractor=family_extractor)


def evaluate_by_provenance(
    records: List[Any],
    y_true: List[int],
    y_pred: List[int],
    provenance_extractor: Callable[[Any], str] = lambda r: getattr(r, "source_dataset", "unknown"),
) -> Dict[str, Dict[str, Any]]:
    """Evaluate performance stratified by source dataset and provenance type."""
    return evaluate_by_subgroup(records, y_true, y_pred, group_extractor=provenance_extractor)
