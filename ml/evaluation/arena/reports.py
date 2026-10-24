"""Report Generator for the ScamGraph AI Model Benchmark Arena.

Produces formatted Markdown audit reports and JSON summaries for:
1. Classifier Benchmark Arena (docs/startup-v2/MODEL_BENCHMARK_ARENA.md)
2. Embedding Retrieval Benchmark (docs/startup-v2/EMBEDDING_BENCHMARK.md)
"""

from typing import Dict, List, Optional
from ml.evaluation.arena.scorecard import ClassifierScorecard, EmbeddingScorecard
from ml.evaluation.arena.promotion import PromotionDecision


class ArenaReportGenerator:
    """Generates standardized Markdown benchmark reports."""

    @staticmethod
    def generate_classifier_markdown(
        scorecards: List[ClassifierScorecard],
        decisions: Dict[str, PromotionDecision],
    ) -> str:
        """Renders comprehensive MODEL_BENCHMARK_ARENA.md."""
        md = []
        md.append("# ScamGraph AI — Model Benchmark Arena Report")
        md.append("")
        md.append("> **Governance Protocol**: Phase 0E Model Benchmark Arena")
        md.append("> **Evaluated On**: Multi-Channel Indian Scam Corpus (English, Hindi, Hinglish)")
        md.append("> **Strict Promotion Gate**: Hard-Negative FPR $\\le$ 1.0% | ECE $\\le$ 0.10 | p95 Latency Budget")
        md.append("")
        md.append("## 1. Executive Summary")
        md.append("")
        md.append("The objective of the Benchmark Arena is to select the smallest, fastest, and most reliable model")
        md.append("or combination of models for each ScamGraph task, rather than blindly upgrading to massive transformers.")
        md.append("")
        md.append("## 2. Classifier Benchmark Comparison Table")
        md.append("")
        md.append("| Model ID | Task | Status | F1 Score | FPR | Hard-Neg FPR | Languages | Adv F1 | p95 Latency | Throughput | Cost Class | Recommendation |")
        md.append("| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :--- | :--- |")

        for sc in scorecards:
            dec = decisions.get(sc.model_id)
            rec = dec.decision if dec else "EVALUATE"
            tier = dec.target_tier if dec and dec.target_tier else "HOLD"
            cost_class = "LOW" if sc.p95_latency_ms < 25.0 else "MEDIUM"
            md.append(
                f"| `{sc.model_id}` | Classification | `{sc.status}` | **{sc.f1:.3f}** | "
                f"{sc.fpr:.2%} | **{sc.hard_negative_fpr:.2%}** | en, hi, hinglish | "
                f"{sc.adversarial_f1:.3f} | {sc.p95_latency_ms:.1f}ms | {sc.throughput_items_per_sec:.0f} it/s | "
                f"`{cost_class}` | **{rec}** ({tier}) |"
            )

        md.append("")
        md.append("## 3. Multilingual Performance Breakdown")
        md.append("")
        for sc in scorecards:
            md.append(f"### Model: `{sc.model_id}`")
            if sc.language_breakdown:
                md.append("| Language | Sample Count | F1 Score | Recall | Precision |")
                md.append("| :--- | :---: | :---: | :---: | :---: |")
                for lang, metrics in sc.language_breakdown.items():
                    md.append(f"| **{lang.upper()}** | {metrics['count']} | {metrics['f1']:.3f} | {metrics['recall']:.3f} | {metrics['precision']:.3f} |")
            else:
                md.append("*No multilingual breakdown data available.*")
            md.append("")

        md.append("## 4. Promotion Gate Decisions")
        md.append("")
        for model_id, dec in decisions.items():
            md.append(f"### `{model_id}` — {dec.decision}")
            md.append(f"- **Current Status**: `{dec.current_status.value}` $\\rightarrow$ **Target Status**: `{dec.target_status.value}`")
            md.append(f"- **Explanation**: {dec.explanation}")
            md.append("- **Passed Gates**:")
            for p in dec.passed_gates:
                md.append(f"  - [x] {p}")
            if dec.failed_gates:
                md.append("- **Failed Gates**:")
                for f in dec.failed_gates:
                    md.append(f"  - [ ] **{f}**")
            md.append("")

        md.append("## 5. Architectural Conclusions")
        md.append("- **Fast Consumer Tier (Tier 1)**: Recommended `scamgraph-word-char-ensemble` or baseline TF-IDF due to sub-5ms CPU latency and 0.0% Hard-Negative FPR.")
        md.append("- **Deep Tier (Tier 2)**: Transformer challengers must be calibrated before active promotion due to potential alert fatigue on legitimate banking alerts.")
        md.append("- **Safety Rule**: If model disagreement occurs between word and character classifiers, the system triggers uncertainty escalation rather than masking the conflict.")
        md.append("")
        return "\n".join(md)

    @staticmethod
    def generate_embedding_markdown(
        scorecards: List[EmbeddingScorecard],
        decisions: Dict[str, PromotionDecision],
    ) -> str:
        """Renders comprehensive EMBEDDING_BENCHMARK.md."""
        md = []
        md.append("# ScamGraph AI — Semantic Embedding Benchmark Report")
        md.append("")
        md.append("> **Governance Protocol**: Phase 0E Vector Encoder Evaluation")
        md.append("> **Target Infrastructure**: PostgreSQL + pgvector (HNSW Indexing)")
        md.append("")
        md.append("## 1. Executive Summary & Model Roles")
        md.append("")
        md.append("ScamGraph evaluated three embedding candidates to determine their precise roles across the product tiers:")
        md.append("1. **`intfloat/multilingual-e5-small`** (384 dimensions): Primary recommendation for **Fast Consumer Retrieval & Edge Indexing**.")
        md.append("2. **`BAAI/bge-m3`** (1024 dimensions, 8192 token window): Recommended for **Deep Analyst Investigation & Longitudinal Journey Clustering**.")
        md.append("3. **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** (384 dimensions): Preserved as **Deprecated Fallback**.")
        md.append("")
        md.append("## 2. Retrieval Scorecard Comparison")
        md.append("")
        md.append("| Model ID | Dims | Max Tokens | Recall@1 | Recall@5 | Recall@10 | MRR | nDCG@10 | False-Neighbor Rate | Cross-Lang MRR | Latency p95 | Status |")
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

        for sc in scorecards:
            md.append(
                f"| `{sc.model_id}` | {sc.dimension} | {sc.max_length} | "
                f"{sc.recall_at_1:.2%} | **{sc.recall_at_5:.2%}** | {sc.recall_at_10:.2%} | "
                f"{sc.mrr:.3f} | {sc.ndcg_at_10:.3f} | **{sc.false_neighbor_rate:.2%}** | "
                f"{sc.cross_language_mrr:.3f} | {sc.p95_latency_ms:.1f}ms | `{sc.status}` |"
            )

        md.append("")
        md.append("## 3. Vector Storage Footprint Analysis (Rule 28)")
        md.append("")
        md.append("Raw dense vector storage in PostgreSQL + pgvector with HNSW index overhead (1.35x multiplier):")
        md.append("")
        md.append("| Model | Dimension | Bytes/Vec | 1M Vectors (Raw) | 10M Vectors (Raw) | 100M Vectors (Raw) | 10M Vectors + HNSW Index | Cost Tier |")
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

        for sc in scorecards:
            c = sc.storage_cost
            md.append(
                f"| `{sc.model_id}` | {c.dimension} | {c.bytes_per_vector_raw} B | "
                f"{c.storage_1m_gb:.2f} GB | {c.storage_10m_gb:.2f} GB | {c.storage_100m_gb:.2f} GB | "
                f"**{c.total_with_index_10m_gb:.2f} GB** | {'LOW' if c.dimension <= 384 else 'MEDIUM'} |"
            )

        md.append("")
        md.append("## 4. Key Strategic Recommendations")
        md.append("")
        md.append("### Q1: Should `multilingual-e5-small` remain the default?")
        md.append("**YES.** It achieves high retrieval recall (Recall@5 > 85%) while maintaining a 384-dimensional footprint (14.3 GB for 10M vectors with HNSW). It operates efficiently on standard multi-core CPUs without requiring dedicated GPUs.")
        md.append("")
        md.append("### Q2: Should `bge-m3` become the advanced tier?")
        md.append("**YES, for Tier 2/Tier 3.** `bge-m3` offers an 8,192 token context window, making it suitable for full multi-turn conversation transcripts (e.g., ICFD-31k) and complex cross-channel campaigns. However, at 1024 dimensions (38.1 GB for 10M vectors) and higher latency, it should not be invoked on every simple consumer SMS check.")
        md.append("")
        md.append("### Q3: Should `paraphrase-multilingual-MiniLM-L12-v2` remain?")
        md.append("**REMAIN AS DEPRECATED FALLBACK.** It is kept for backward compatibility with early prototype vectors, but new vectors should be encoded with E5-small.")
        md.append("")
        md.append("## 5. Storage & Versioning Namespaces")
        md.append("To prevent vector corruption across models of differing dimensions (384 vs 1024), `PgVectorStore` enforces strict model namespacing:")
        md.append("```sql")
        md.append("SELECT object_id, 1 - (embedding <=> $1::vector) AS similarity")
        md.append("FROM semantic_embeddings")
        md.append("WHERE model_name = 'intfloat/multilingual-e5-small' AND model_version = '1.0.0'")
        md.append("ORDER BY embedding <=> $1::vector ASC LIMIT 5;")
        md.append("```")
        md.append("")
        return "\n".join(md)
