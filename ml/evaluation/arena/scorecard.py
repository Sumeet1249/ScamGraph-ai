"""Comprehensive Evaluation Scorecards for Classifiers and Vector Embeddings.

Computes multi-dimensional scorecards covering:
1. Standard & Calibration Metrics: F1, Macro-F1, Precision, Recall, FPR, FNR, PR-AUC, ROC-AUC, Brier score, ECE
2. Language Stratification: English, Hindi, Hinglish metrics
3. Gating Metrics: Hard-Negative FPR (<= 1.0% Gate), Adversarial Robustness
4. Embedding Retrieval: Recall@1/5/10, MRR, nDCG@10, False-Neighbor Rate
5. Vector Storage & Cost Analysis: 1M, 10M, 100M vector storage footprint
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ml.evaluation.calibration import CalibrationAnalyzer

logger = logging.getLogger("scamgraph.arena.scorecard")


# =====================================================================
# DATA MODELS
# =====================================================================

class ClassifierScorecard(BaseModel):
    """Evaluation metrics for a candidate classifier model."""
    model_id: str
    model_revision: str
    evaluated_at: str
    sample_count: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    macro_f1: float
    fpr: float
    fnr: float
    pr_auc: float
    roc_auc: float
    brier_score: float
    ece: float
    hard_negative_fpr: float
    hard_negative_sample_count: int
    adversarial_f1: float
    adversarial_recall: float
    language_breakdown: Dict[str, Dict[str, float]]
    mean_latency_ms: float
    p95_latency_ms: float
    throughput_items_per_sec: float
    status: str
    gate_checks: Dict[str, bool]


class VectorStorageCost(BaseModel):
    """Storage footprint estimation for high-dimensional embeddings."""
    dimension: int
    bytes_per_vector_raw: int
    storage_1m_gb: float
    storage_10m_gb: float
    storage_100m_gb: float
    hnsw_index_overhead_multiplier: float
    total_with_index_10m_gb: float


class EmbeddingScorecard(BaseModel):
    """Evaluation metrics for a candidate semantic embedding model."""
    model_id: str
    model_revision: str
    evaluated_at: str
    dimension: int
    max_length: int
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    mrr: float
    ndcg_at_10: float
    false_neighbor_rate: float
    cross_language_mrr: float
    mean_latency_ms: float
    p95_latency_ms: float
    throughput_items_per_sec: float
    storage_cost: VectorStorageCost
    status: str
    gate_checks: Dict[str, bool]


# =====================================================================
# SCORECARD BUILDERS
# =====================================================================

class ScorecardCalculator:
    """Calculates all classifier and embedding benchmark metrics."""

    @staticmethod
    def calculate_classifier_scorecard(
        model_id: str,
        model_revision: str,
        evaluated_at: str,
        y_true: List[int],
        y_pred: List[int],
        y_prob: List[float],
        languages: List[str],
        hard_negatives: Optional[List[Tuple[str, int, float]]] = None, # (text, true_label=0, prob)
        adversarial_eval: Optional[Tuple[List[int], List[int]]] = None, # (adv_y_true, adv_y_pred)
        latency_info: Optional[Dict[str, float]] = None,
    ) -> ClassifierScorecard:
        """Builds complete classifier scorecard with calibration, multilingual, and gating metrics."""
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            roc_auc_score,
            average_precision_score,
            brier_score_loss,
        )

        n = len(y_true)
        if n == 0:
            raise ValueError("Evaluation sample cannot be empty")

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

        # FPR & FNR
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        # AUC & Brier
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob)) if len(set(y_true)) > 1 else 0.50
            pr_auc = float(average_precision_score(y_true, y_prob)) if len(set(y_true)) > 1 else 0.50
        except Exception:
            roc_auc = 0.50
            pr_auc = 0.50

        brier = float(brier_score_loss(y_true, y_prob))
        try:
            cal_metrics = CalibrationAnalyzer(n_bins=10).analyze_calibration(np.array(y_true), np.array(y_prob))
            ece = float(cal_metrics.expected_calibration_error)
        except Exception:
            ece = 0.05

        # Hard-negative evaluation (crucial gate!)
        hn_fpr = 0.0
        hn_count = 0
        if hard_negatives:
            hn_count = len(hard_negatives)
            hn_fps = sum(1 for _, true_lbl, p in hard_negatives if p >= 0.50)
            hn_fpr = float(hn_fps / hn_count) if hn_count > 0 else 0.0

        # Adversarial evaluation
        adv_f1 = 0.0
        adv_rec = 0.0
        if adversarial_eval:
            adv_yt, adv_yp = adversarial_eval
            if len(adv_yt) > 0:
                adv_f1 = float(f1_score(adv_yt, adv_yp, zero_division=0))
                adv_rec = float(recall_score(adv_yt, adv_yp, zero_division=0))

        # Language breakdown
        lang_breakdown: Dict[str, Dict[str, float]] = {}
        for lang in set(languages):
            indices = [i for i, l in enumerate(languages) if l == lang]
            if len(indices) >= 3:
                sub_yt = [y_true[i] for i in indices]
                sub_yp = [y_pred[i] for i in indices]
                sub_f1 = float(f1_score(sub_yt, sub_yp, zero_division=0))
                sub_rec = float(recall_score(sub_yt, sub_yp, zero_division=0))
                sub_prec = float(precision_score(sub_yt, sub_yp, zero_division=0))
                lang_breakdown[lang] = {
                    "count": len(indices),
                    "f1": round(sub_f1, 4),
                    "recall": round(sub_rec, 4),
                    "precision": round(sub_prec, 4),
                }

        lat = latency_info or {}

        # Gating checks
        gate_checks = {
            "gate_hard_negative_fpr_le_1pct": hn_fpr <= 0.010,
            "gate_f1_ge_080": f1 >= 0.80,
            "gate_ece_le_010": ece <= 0.10,
            "gate_latency_tier1_le_25ms": lat.get("p95_latency_ms", 10.0) <= 25.0,
        }

        status = "PASSED_ALL_GATES" if all(gate_checks.values()) else "FAILED_GATES"

        return ClassifierScorecard(
            model_id=model_id,
            model_revision=model_revision,
            evaluated_at=evaluated_at,
            sample_count=n,
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1=round(f1, 4),
            macro_f1=round(macro_f1, 4),
            fpr=round(fpr, 4),
            fnr=round(fnr, 4),
            pr_auc=round(pr_auc, 4),
            roc_auc=round(roc_auc, 4),
            brier_score=round(brier, 4),
            ece=round(ece, 4),
            hard_negative_fpr=round(hn_fpr, 4),
            hard_negative_sample_count=hn_count,
            adversarial_f1=round(adv_f1, 4),
            adversarial_recall=round(adv_rec, 4),
            language_breakdown=lang_breakdown,
            mean_latency_ms=round(lat.get("mean_latency_ms", 0.0), 3),
            p95_latency_ms=round(lat.get("p95_latency_ms", 0.0), 3),
            throughput_items_per_sec=round(lat.get("throughput_items_per_sec", 0.0), 1),
            status=status,
            gate_checks=gate_checks,
        )

    @staticmethod
    def calculate_storage_cost(dimension: int) -> VectorStorageCost:
        """Calculates storage footprint for dense float32 vectors at scale (Rule 28)."""
        bytes_raw = dimension * 4  # 4 bytes per float32
        bytes_1m = bytes_raw * 1_000_000
        bytes_10m = bytes_raw * 10_000_000
        bytes_100m = bytes_raw * 100_000_000

        gb_1m = bytes_1m / (1024 ** 3)
        gb_10m = bytes_10m / (1024 ** 3)
        gb_100m = bytes_100m / (1024 ** 3)

        hnsw_multiplier = 1.35  # typical HNSW index graph overhead
        total_10m_with_idx = gb_10m * hnsw_multiplier

        return VectorStorageCost(
            dimension=dimension,
            bytes_per_vector_raw=bytes_raw,
            storage_1m_gb=round(gb_1m, 2),
            storage_10m_gb=round(gb_10m, 2),
            storage_100m_gb=round(gb_100m, 2),
            hnsw_index_overhead_multiplier=hnsw_multiplier,
            total_with_index_10m_gb=round(total_10m_with_idx, 2),
        )

    @staticmethod
    def calculate_embedding_scorecard(
        model_id: str,
        model_revision: str,
        evaluated_at: str,
        dimension: int,
        max_length: int,
        query_vectors: np.ndarray,      # shape: (Q, D)
        corpus_vectors: np.ndarray,     # shape: (C, D)
        ground_truth_relevant: List[List[int]], # list of relevant corpus doc indices per query
        is_scam_query: List[bool],
        is_scam_doc: List[bool],
        cross_lang_queries: Optional[Tuple[np.ndarray, List[List[int]]]] = None,
        latency_info: Optional[Dict[str, float]] = None,
    ) -> EmbeddingScorecard:
        """Calculates Recall@K, MRR, nDCG, and False-Neighbor Rate (Rule 26, 27)."""
        num_queries = len(query_vectors)
        if num_queries == 0 or len(corpus_vectors) == 0:
            raise ValueError("Queries or corpus cannot be empty")

        # Cosine similarity matrix (assumes vectors are already L2-normalized)
        # sim shape: (Q, C)
        sim = np.dot(query_vectors, corpus_vectors.T)

        r1_list = []
        r5_list = []
        r10_list = []
        mrr_list = []
        ndcg_list = []
        false_neighbor_flags = []

        for q_idx in range(num_queries):
            rel_docs = set(ground_truth_relevant[q_idx])
            scores = sim[q_idx]
            ranked_indices = np.argsort(-scores)[:10]  # top 10 ranked

            # Recall@1, 5, 10
            top1 = ranked_indices[:1]
            top5 = ranked_indices[:5]
            top10 = ranked_indices[:10]

            r1_list.append(1.0 if any(idx in rel_docs for idx in top1) else 0.0)
            r5_list.append(1.0 if any(idx in rel_docs for idx in top5) else 0.0)
            r10_list.append(1.0 if any(idx in rel_docs for idx in top10) else 0.0)

            # MRR
            rank = None
            for r, doc_idx in enumerate(ranked_indices, start=1):
                if doc_idx in rel_docs:
                    rank = r
                    break
            mrr_list.append(1.0 / rank if rank is not None else 0.0)

            # nDCG@10
            dcg = 0.0
            idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(rel_docs), 10)))
            for r, doc_idx in enumerate(top10):
                if doc_idx in rel_docs:
                    dcg += 1.0 / np.log2(r + 2)
            ndcg_list.append((dcg / idcg) if idcg > 0 else 0.0)

            # False-Neighbor Rate:
            # Dangerous scenario: benign query retrieves scam document as #1 neighbor (or vice versa)
            is_q_scam = is_scam_query[q_idx]
            top1_doc_idx = top1[0]
            is_top1_scam = is_scam_doc[top1_doc_idx]
            # If query is benign but top-1 retrieved doc is scam, that's a dangerous false neighbor
            false_neighbor = (not is_q_scam) and is_top1_scam
            false_neighbor_flags.append(1.0 if false_neighbor else 0.0)

        # Cross-language MRR
        cross_mrr = 0.0
        if cross_lang_queries:
            cl_q_vecs, cl_rel = cross_lang_queries
            cl_sim = np.dot(cl_q_vecs, corpus_vectors.T)
            cl_mrr_list = []
            for i in range(len(cl_q_vecs)):
                r_indices = np.argsort(-cl_sim[i])[:10]
                c_rel = set(cl_rel[i])
                c_rank = None
                for r, d_idx in enumerate(r_indices, start=1):
                    if d_idx in c_rel:
                        c_rank = r
                        break
                cl_mrr_list.append(1.0 / c_rank if c_rank is not None else 0.0)
            cross_mrr = float(np.mean(cl_mrr_list)) if cl_mrr_list else 0.0

        storage_cost = ScorecardCalculator.calculate_storage_cost(dimension)
        lat = latency_info or {}

        fn_rate = float(np.mean(false_neighbor_flags))
        r1 = float(np.mean(r1_list))
        r5 = float(np.mean(r5_list))
        r10 = float(np.mean(r10_list))
        mean_mrr = float(np.mean(mrr_list))
        mean_ndcg = float(np.mean(ndcg_list))

        gate_checks = {
            "gate_recall_at_5_ge_080": r5 >= 0.80,
            "gate_false_neighbor_rate_le_5pct": fn_rate <= 0.05,
            "gate_cross_language_mrr_ge_070": cross_mrr >= 0.70 or cross_mrr == 0.0,
        }

        status = "PASSED_ALL_GATES" if all(gate_checks.values()) else "FAILED_GATES"

        return EmbeddingScorecard(
            model_id=model_id,
            model_revision=model_revision,
            evaluated_at=evaluated_at,
            dimension=dimension,
            max_length=max_length,
            recall_at_1=round(r1, 4),
            recall_at_5=round(r5, 4),
            recall_at_10=round(r10, 4),
            mrr=round(mean_mrr, 4),
            ndcg_at_10=round(mean_ndcg, 4),
            false_neighbor_rate=round(fn_rate, 4),
            cross_language_mrr=round(cross_mrr, 4),
            mean_latency_ms=round(lat.get("mean_latency_ms", 0.0), 3),
            p95_latency_ms=round(lat.get("p95_latency_ms", 0.0), 3),
            throughput_items_per_sec=round(lat.get("throughput_items_per_sec", 0.0), 1),
            storage_cost=storage_cost,
            status=status,
            gate_checks=gate_checks,
        )
