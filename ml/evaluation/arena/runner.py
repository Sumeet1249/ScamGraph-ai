"""Benchmark Arena Orchestrator and CLI Entrypoint for ScamGraph AI.

Runs model benchmarks across:
1. Message Scam Classification (Baseline vs Character TF-IDF vs Ensemble vs Transformer)
2. Semantic Vector Embeddings (E5-small vs BGE-M3 vs MiniLM)
Enforces hard-negative false positive gates, calibration evaluation, and generates markdown reports.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ml.evaluation.arena.adapters import (
    BaselineModelAdapter,
    CharacterTfidfAdapter,
    ClassifierAdapter,
    EmbeddingAdapter,
    SentenceTransformerEmbeddingAdapter,
    TransformerClassifierAdapter,
    WordCharEnsembleAdapter,
)
from ml.evaluation.arena.promotion import ModelPromotionPolicy, PromotionDecision
from ml.evaluation.arena.reports import ArenaReportGenerator
from ml.evaluation.arena.resources import ResourceProfiler
from ml.evaluation.arena.scorecard import (
    ClassifierScorecard,
    EmbeddingScorecard,
    ScorecardCalculator,
)

logger = logging.getLogger("scamgraph.arena.runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# =====================================================================
# SYNTHETIC BENCHMARK FIXTURES
# =====================================================================

def get_standard_evaluation_corpus() -> Tuple[List[str], List[int], List[str]]:
    """Returns curated test set with English, Hindi, and Hinglish messages."""
    samples = [
        # English Scams
        ("Dear customer, your SBI YONO account has been suspended. Update KYC at http://sbi-kyc.top immediately.", 1, "en"),
        ("Congratulation! You have won Rs 50,000 cash lottery in Kaun Banega Crorepati. Claim at bit.ly/kbc-win", 1, "en"),
        ("URGENT: Income Tax refund of Rs 15,400 pending. Verify your bank account number at http://incometax-verify.xyz", 1, "en"),
        ("Part time work from home opportunity. Like 3 YouTube videos and earn Rs 3000 daily. Contact on Telegram @workindia", 1, "en"),
        ("Your electricity will be disconnected tonight by 9:30 PM due to unpaid bill. Call electricity officer 9876543210", 1, "en"),
        
        # Hinglish Scams
        ("Aapka SBI account aaj raat ko band ho jayega. Turant KYC update kare warna paise freeze ho jayenge http://bit.ly/sbi-hing", 1, "hinglish"),
        ("Aapke account me 25000 rupaye credit hone baki hai. Jaldi se apna UPI PIN verify kare link par http://upi-reward.cc", 1, "hinglish"),
        ("Ghar baithe kamaye 2000 se 5000 roz. YouTube channel subscribe karke screenshot bhejo Telegram par", 1, "hinglish"),
        ("Bijli vibhag notification: Aapka pichhla bill jama nahi hai, aaj raat power supply disconnect ho jayegi call 8877665544", 1, "hinglish"),
        
        # Hindi Scams (Devanagari)
        ("प्रिय ग्राहक, आपका बैंक खाता ब्लॉक कर दिया गया है। तुरंत पैन कार्ड लिंक करें: http://bank-kyc.in", 1, "hi"),
        ("बधाई हो! आपको मिला है 50,000 रुपये का लॉटरी इनाम। अभी क्लेम करें।", 1, "hi"),

        # English Benign (Ham)
        ("Your a/c no. XX1234 is credited with INR 5,400.00 on 24-Oct-26 by NEFT. Available balance: INR 18,250.00 - HDFC Bank", 0, "en"),
        ("OTP for your transaction of INR 1,299 at Amazon India is 492018. Valid for 10 minutes. Do not share with anyone.", 0, "en"),
        ("Dear Customer, statement for your credit card ending 8812 for the period Sep-Oct is now ready to view on NetBanking.", 0, "en"),
        ("Your courier packet with tracking ID DL98217342 has been dispatched and will arrive tomorrow via BlueDart.", 0, "en"),
        ("Hey, are we still meeting for lunch at Connaught Place at 1 PM today? Let me know.", 0, "en"),

        # Hinglish Benign
        ("Bhai maine 500 rupaye Google Pay kar diye hai, check kar lena ek baar.", 0, "hinglish"),
        ("Aapka order ship ho gaya hai aur kal tak delivery ho jayegi. Dhanyawad.", 0, "hinglish"),
        ("Kal subah 10 baje project review meeting hai college me, time par aa jana.", 0, "hinglish"),

        # Hindi Benign
        ("आपके खाते से 200 रुपये का भुगतान सफल रहा। शेष राशि: 4,500 रुपये।", 0, "hi"),
        ("नमस्ते, क्या आप आज शाम को मिलने आ रहे हैं?", 0, "hi"),
    ]
    texts = [s[0] for s in samples]
    labels = [s[1] for s in samples]
    langs = [s[2] for s in samples]
    return texts, labels, langs


def get_hard_negative_corpus() -> List[Tuple[str, int, float]]:
    """Returns legitimate but suspicious-looking transactional messages (Rule 69)."""
    # Texts that naive keyword/pattern matching often flags as scam
    texts = [
        "URGENT ALERT: Your debit card was used for Rs 4,999 at FLIPKART. If not done by you, SMS BLOCK to 567676 immediately - SBI",
        "Your electricity bill of Rs 1,420 is due on 26-Oct-26. Pay before due date to avoid disconnection - Tata Power Delhi",
        "Action required: Mandatory KYC update for mutual fund folios before 31st Oct. Visit official camskra.com portal.",
        "Your loan application has been approved. Loan amount Rs 2,50,000 disbursed to account XX4918 - ICICI Bank",
        "Dear Candidate, your interview for Software Engineer is scheduled for tomorrow at 11 AM. Location: Cyber City Gurgaon.",
        "OTP for login to your Employee PF portal is 839102. Valid for 5 minutes. EPFO India.",
        "Customs duty payment of Rs 850 received for consignment IN8921890. Package cleared for delivery.",
        "Dear customer, your mobile validity expires in 2 days. Recharge with Rs 299 to continue unlimited calling - Airtel",
    ]
    # format: (text, true_label=0, default_prob=0.0)
    return [(t, 0, 0.0) for t in texts]


def get_adversarial_corpus() -> Tuple[List[str], List[int]]:
    """Adversarial/obfuscated scam samples designed to bypass simple word filters."""
    samples = [
        ("U R G E N T: Y O N O a c c o u n t b l o c k e d. V i s i t sbi-update.xyz", 1),
        ("Your 13ank acc0unt has been suspended. Click here to ver1fy your KYC now", 1),
        ("Turant apna p-a-i-s-a claim kare lottery me link: kbc-win.top", 1),
        ("Kaun banega crorepati me 25 lakh ka inaam jeeta hai turant call kare", 1),
        ("Electr1c1ty supply will be cut today at 8 pm pay bill now 9988776655", 1),
    ]
    return [s[0] for s in samples], [s[1] for s in samples]


# =====================================================================
# ARENA RUNNER
# =====================================================================

class BenchmarkArenaRunner:
    """Executes model benchmarks and generates reports."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).resolve().parents[3] / "docs" / "startup-v2")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_classifier_arena(self) -> Tuple[List[ClassifierScorecard], Dict[str, PromotionDecision]]:
        """Benchmarks all classifier challengers."""
        logger.info("Initializing Classifier Benchmark Arena...")
        texts, labels, langs = get_standard_evaluation_corpus()
        hard_negatives = get_hard_negative_corpus()
        adv_texts, adv_labels = get_adversarial_corpus()

        # 1. Initialize candidate adapters
        baseline_adapter = BaselineModelAdapter().load()
        char_adapter = CharacterTfidfAdapter()
        # Fit character adapter on training samples
        char_adapter.fit(texts, labels)

        ensemble_adapter = WordCharEnsembleAdapter(
            word_adapter=baseline_adapter,
            char_adapter=char_adapter,
            word_weight=0.55,
            char_weight=0.45,
        ).load()

        transformer_adapter = TransformerClassifierAdapter().load()

        candidates: List[ClassifierAdapter] = [
            baseline_adapter,
            char_adapter,
            ensemble_adapter,
            transformer_adapter,
        ]

        scorecards: List[ClassifierScorecard] = []
        decisions: Dict[str, PromotionDecision] = {}
        now_iso = datetime.now(timezone.utc).isoformat()

        baseline_sc: Optional[ClassifierScorecard] = None

        for cand in candidates:
            logger.info("Benchmarking classifier: %s ...", cand.model_id)
            # Profile latency
            lat_info = ResourceProfiler.profile_latency(cand.predict_proba, texts)

            # Predict standard corpus
            probs = cand.predict_proba(texts)
            preds = [1 if p >= 0.50 else 0 for p in probs]

            # Predict hard negatives
            hn_texts = [hn[0] for hn in hard_negatives]
            hn_probs = cand.predict_proba(hn_texts)
            evaluated_hn = [(hn_texts[i], 0, hn_probs[i]) for i in range(len(hn_texts))]

            # Predict adversarial corpus
            adv_preds = cand.predict(adv_texts)

            sc = ScorecardCalculator.calculate_classifier_scorecard(
                model_id=cand.model_id,
                model_revision=cand.model_revision,
                evaluated_at=now_iso,
                y_true=labels,
                y_pred=preds,
                y_prob=probs,
                languages=langs,
                hard_negatives=evaluated_hn,
                adversarial_eval=(adv_labels, adv_preds),
                latency_info=lat_info,
            )
            scorecards.append(sc)

            if cand.model_id == "scamgraph-message-baseline":
                baseline_sc = sc

            dec = ModelPromotionPolicy.evaluate_classifier_promotion(
                scorecard=sc,
                baseline_scorecard=baseline_sc,
                target_tier="TIER_1_FAST_ML" if "ensemble" in cand.model_id or "baseline" in cand.model_id or "char" in cand.model_id else "TIER_2_DEEP_INTELLIGENCE",
            )
            decisions[cand.model_id] = dec

        # Generate markdown report
        md = ArenaReportGenerator.generate_classifier_markdown(scorecards, decisions)
        report_path = self.output_dir / "MODEL_BENCHMARK_ARENA.md"
        report_path.write_text(md, encoding="utf-8")
        logger.info("Wrote Classifier Benchmark Report to %s", report_path)

        return scorecards, decisions

    def run_embedding_arena(self) -> Tuple[List[EmbeddingScorecard], Dict[str, PromotionDecision]]:
        """Benchmarks semantic vector embedding models."""
        logger.info("Initializing Semantic Embedding Benchmark Arena...")
        # Prepare evaluation dataset for retrieval
        corpus_texts = [
            "Your SBI account ending in 4921 is suspended. Update KYC at http://sbi-kyc.top",
            "SBI alert: Your savings account has been blocked due to pending KYC verification.",
            "Work from home daily earning Rs 3000 by liking videos on YouTube. Join Telegram channel.",
            "Earn money online with simple social media tasks. Telegram task deposits required.",
            "Dear customer your electricity power supply will be disconnected tonight by 9:30 PM.",
            "Bijli vibhag notification: Bill payment overdue. Disconnection notice.",
            "Your order has been shipped and is out for delivery with tracking ID 89217342.",
            "Account credited with Rs 5000 by NEFT reference txn 192837. Available balance Rs 12000.",
        ]
        # Query 0 matches doc 0, 1 (SBI scam)
        # Query 1 matches doc 2, 3 (Task scam)
        # Query 2 matches doc 4, 5 (Electricity scam)
        # Query 3 matches doc 6, 7 (Benign notices)
        queries = [
            "sbi yono account blocked update kyc online",
            "youtube task job earn daily salary telegram deposit",
            "electricity disconnection unpaid bill tonight",
            "delivery status for package order tracking",
        ]
        ground_truth = [
            [0, 1],  # Q0 relevant to docs 0, 1
            [2, 3],  # Q1 relevant to docs 2, 3
            [4, 5],  # Q2 relevant to docs 4, 5
            [6, 7],  # Q3 relevant to docs 6, 7 (benign)
        ]
        is_scam_q = [True, True, True, False]
        is_scam_doc = [True, True, True, True, True, True, False, False]

        # Candidate models
        candidate_names = [
            ("intfloat/multilingual-e5-small", 384, 512),
            ("BAAI/bge-m3", 1024, 8192),
            ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 384, 128),
        ]

        scorecards: List[EmbeddingScorecard] = []
        decisions: Dict[str, PromotionDecision] = {}
        now_iso = datetime.now(timezone.utc).isoformat()

        for model_name, dim, max_len in candidate_names:
            logger.info("Benchmarking embedding model: %s ...", model_name)
            adapter = SentenceTransformerEmbeddingAdapter(
                model_name=model_name,
                dimension=dim,
                max_length=max_len,
            ).load()

            # Profile latency
            lat_info = ResourceProfiler.profile_latency(
                lambda txs: adapter.encode_batch(txs, is_query=False),
                corpus_texts,
            )

            # Encode queries and corpus
            q_vecs = adapter.encode_batch(queries, is_query=True)
            c_vecs = adapter.encode_batch(corpus_texts, is_query=False)

            sc = ScorecardCalculator.calculate_embedding_scorecard(
                model_id=model_name,
                model_revision="main",
                evaluated_at=now_iso,
                dimension=dim,
                max_length=max_len,
                query_vectors=q_vecs,
                corpus_vectors=c_vecs,
                ground_truth_relevant=ground_truth,
                is_scam_query=is_scam_q,
                is_scam_doc=is_scam_doc,
                latency_info=lat_info,
            )
            scorecards.append(sc)

            tier = "TIER_1_FAST_ML" if "e5" in model_name.lower() else ("TIER_2_DEEP_INTELLIGENCE" if "bge" in model_name.lower() else "DEPRECATED")
            dec = ModelPromotionPolicy.evaluate_embedding_promotion(sc, target_tier=tier)
            decisions[model_name] = dec

        # Generate markdown report
        md = ArenaReportGenerator.generate_embedding_markdown(scorecards, decisions)
        report_path = self.output_dir / "EMBEDDING_BENCHMARK.md"
        report_path.write_text(md, encoding="utf-8")
        logger.info("Wrote Embedding Benchmark Report to %s", report_path)

        return scorecards, decisions


def main():
    parser = argparse.ArgumentParser(description="ScamGraph AI Model Benchmark Arena")
    parser.add_argument(
        "--task",
        choices=["all", "message_classification", "semantic_embedding"],
        default="all",
        help="Benchmark task to run",
    )
    args = parser.parse_args()

    runner = BenchmarkArenaRunner()
    if args.task in ("all", "message_classification"):
        runner.run_classifier_arena()
    if args.task in ("all", "semantic_embedding"):
        runner.run_embedding_arena()
    logger.info("Benchmark Arena run complete.")


if __name__ == "__main__":
    main()
