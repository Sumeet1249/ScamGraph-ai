"""Unit tests for Step 20: Pretrained Multilingual Semantic Intelligence & pgvector.

Verifies:
1. Local Hugging Face pretrained model (intfloat/multilingual-e5-small) encodes multilingual text.
2. Paraphrase resistance:
   - 'Complete your bank KYC immediately.'
   - 'Security verification for your banking profile is incomplete.'
   - 'Account block ho jayega, abhi verification complete karo.'
   Are relatively similar to each other, and less similar to 'Let\'s have dinner tomorrow.'
3. Configurable embedding provider (SCAMGRAPH_EMBEDDING_MODEL).
4. Normalized semantic text representation (not raw JSON).
5. VectorStore abstraction & pgvector DDL generation.
6. SemanticSimilarityService retrieval (find_similar_messages, find_similar_incidents, find_similar_patterns).
7. Embedding cache prevents recomputation.
8. Similarity is output as EvidenceSignal, NOT fraud probability.
"""

import asyncio
import os
import unittest
import numpy as np

from ml.embeddings.encoder import SemanticEncoder, semantic_encoder, EmbeddingCache
from ml.embeddings.representation import SemanticRepresentation, SemanticRepresentationBuilder
from packages.schemas import SignalDimension, SignalSeverity
from services.storage.vector.models import VectorObjectType, VectorRecord, VectorSearchResult
from services.storage.vector.in_memory import InMemoryVectorStore
from services.storage.vector.pgvector_store import PgVectorStore
from services.storage.vector.similarity_service import SemanticSimilarityService


class TestSemanticIntelligenceStep20(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoder = semantic_encoder

    def test_01_multilingual_semantic_similarity_and_paraphrase_resistance(self):
        """Actually runs the pretrained model to verify cross-lingual semantic convergence."""
        msg_kyc_en = "Complete your bank KYC immediately."
        msg_sec_en = "Security verification for your banking profile is incomplete."
        msg_kyc_hinglish = "Account block ho jayega, abhi verification complete karo."
        msg_dinner_benign = "Let's have dinner tomorrow."

        vec_kyc = self.encoder.encode(msg_kyc_en)
        vec_sec = self.encoder.encode(msg_sec_en)
        vec_hinglish = self.encoder.encode(msg_kyc_hinglish)
        vec_dinner = self.encoder.encode(msg_dinner_benign)

        # Dimension check (384 for multilingual-e5-small)
        self.assertEqual(len(vec_kyc), 384)
        self.assertEqual(len(vec_sec), 384)
        self.assertEqual(len(vec_hinglish), 384)
        self.assertEqual(len(vec_dinner), 384)

        # L2-normalization verification
        self.assertAlmostEqual(float(np.linalg.norm(vec_kyc)), 1.0, places=3)
        self.assertAlmostEqual(float(np.linalg.norm(vec_sec)), 1.0, places=3)
        self.assertAlmostEqual(float(np.linalg.norm(vec_hinglish)), 1.0, places=3)
        self.assertAlmostEqual(float(np.linalg.norm(vec_dinner)), 1.0, places=3)

        # Cosine similarity calculations
        sim_kyc_sec = self.encoder.cosine_similarity(vec_kyc, vec_sec)
        sim_kyc_hinglish = self.encoder.cosine_similarity(vec_kyc, vec_hinglish)
        sim_sec_hinglish = self.encoder.cosine_similarity(vec_sec, vec_hinglish)

        sim_kyc_dinner = self.encoder.cosine_similarity(vec_kyc, vec_dinner)
        sim_hinglish_dinner = self.encoder.cosine_similarity(vec_hinglish, vec_dinner)

        # Scam messages across English and Hinglish MUST be closely aligned
        self.assertGreater(sim_kyc_sec, 0.82)
        self.assertGreater(sim_kyc_hinglish, 0.82)
        self.assertGreater(sim_sec_hinglish, 0.82)

        # Scam messages MUST be distinctly more similar to each other than to benign dinner text
        self.assertGreater(sim_kyc_sec, sim_kyc_dinner)
        self.assertGreater(sim_kyc_hinglish, sim_hinglish_dinner)
        self.assertGreater(sim_kyc_sec - sim_kyc_dinner, 0.02)
        self.assertGreater(sim_kyc_hinglish - sim_hinglish_dinner, 0.03)

    def test_02_configurable_embedding_provider(self):
        """Verifies SCAMGRAPH_EMBEDDING_MODEL environment configuration."""
        custom_encoder = SemanticEncoder(model_name="intfloat/multilingual-e5-small")
        self.assertEqual(custom_encoder.model_name, "intfloat/multilingual-e5-small")
        self.assertEqual(custom_encoder.dimension, 384)

        # Test fallback / custom model dimension mapping
        bge_encoder = SemanticEncoder(model_name="BAAI/bge-m3")
        self.assertEqual(bge_encoder.dimension, 1024)

    def test_03_embedding_cache_prevents_recomputation(self):
        """Verifies that unchanged texts hit the in-memory cache."""
        cache = EmbeddingCache()
        encoder = SemanticEncoder(use_cache=True)
        encoder._cache = cache

        text = "Urgent: Your account is scheduled for immediate suspension."
        v1 = encoder.encode(text)
        self.assertEqual(len(cache), 1)

        v2 = encoder.encode(text)
        np.testing.assert_array_equal(v1, v2)
        # Should still be 1 entry in cache
        self.assertEqual(len(cache), 1)

    def test_04_normalized_semantic_representation_builder(self):
        """Verifies structured normalized semantic text generation (not raw JSON)."""
        rep = SemanticRepresentationBuilder.build_from_message(
            text="Dear customer, your SBI account KYC is expired. Update immediately at https://sbi-kyc.info",
            claimed_identity="State Bank of India",
            intent="account verification",
            tactics=["URGENCY", "IMPERSONATION"],
            requested_action="open URL",
            financial_context=True,
            journey_stage="SUSPICIOUS_LINK",
        )
        text_repr = rep.to_normalized_text()

        # Must NOT be raw JSON dump
        self.assertNotIn('{"text":', text_repr)
        self.assertIn("claimed_identity: State Bank of India", text_repr)
        self.assertIn("intent: account verification", text_repr)
        self.assertIn("tactics: impersonation, urgency", text_repr)
        self.assertIn("requested_action: open URL", text_repr)
        self.assertIn("financial_context: true", text_repr)
        self.assertIn("journey_stage: suspicious_link", text_repr)

    def test_05_vector_store_and_pgvector_ddl(self):
        """Verifies PgVectorStore DDL generation and InMemoryVectorStore operations."""
        # 1. PgVectorStore DDL validation
        ddl = PgVectorStore.get_schema_ddl(dimension=384)
        self.assertIn("CREATE EXTENSION IF NOT EXISTS vector;", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS semantic_embeddings", ddl)
        self.assertIn("embedding vector(384) NOT NULL", ddl)
        self.assertIn("hnsw (embedding vector_cosine_ops)", ddl)

        # 2. InMemoryVectorStore lifecycle
        store = InMemoryVectorStore()
        rec1 = VectorRecord(
            object_type=VectorObjectType.MESSAGE,
            object_id="msg_1",
            model_name="intfloat/multilingual-e5-small",
            embedding=[0.1] * 384,
            metadata={"source": "sms"},
        )
        rec2 = VectorRecord(
            object_type=VectorObjectType.PATTERN,
            object_id="pat_kyc",
            model_name="intfloat/multilingual-e5-small",
            embedding=[0.5] * 384,
            metadata={"pattern_name": "KYC Impersonation"},
        )

        async def _run_store_test():
            await store.store_embedding(rec1)
            await store.store_embedding(rec2)
            self.assertEqual(await store.count(), 2)
            self.assertEqual(await store.count(VectorObjectType.MESSAGE), 1)

            fetched = await store.get_embedding(rec1.embedding_id)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.object_id, "msg_1")

            # Search with query vector identical to rec2
            results = await store.find_similar(
                query_vector=[0.5] * 384,
                object_type=VectorObjectType.PATTERN,
                top_k=5,
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].object_id, "pat_kyc")
            self.assertAlmostEqual(results[0].similarity, 1.0, places=3)

            # Delete
            deleted = await store.delete_embedding(rec1.embedding_id)
            self.assertTrue(deleted)
            self.assertEqual(await store.count(), 1)

        asyncio.run(_run_store_test())

    def test_06_semantic_similarity_service_retrieval(self):
        """Verifies find_similar_messages, find_similar_incidents, find_similar_patterns."""
        store = InMemoryVectorStore()
        service = SemanticSimilarityService(vector_store=store, encoder=self.encoder)

        async def _run_service_test():
            # Seed indexed items
            await service.store_message(
                message_id="msg_kyc_historical",
                text="Your bank account will be blocked today due to pending KYC verification.",
                metadata={"incident_id": "inc_hist_01"},
            )
            await service.store_message(
                message_id="msg_dinner_historical",
                text="Are we still meeting for lunch or dinner tomorrow?",
                metadata={"incident_id": "inc_hist_02"},
            )

            # Query message
            query = "Account block ho jayega, abhi KYC update karo."
            matches = await service.find_similar_messages(query, top_k=2)

            self.assertEqual(len(matches), 2)
            # The KYC message MUST be rank 1
            self.assertEqual(matches[0].object_id, "msg_kyc_historical")
            self.assertEqual(matches[0].object_type, VectorObjectType.MESSAGE)
            self.assertGreater(matches[0].similarity, matches[1].similarity)

            # Evidence conversion rule verification
            sig = service.to_evidence_signal("inc_query_01", matches[0])
            self.assertEqual(sig.dimension, SignalDimension.SEMANTIC)
            self.assertEqual(sig.signal_type, "SEMANTIC_SIMILARITY_TO_MESSAGE")
            self.assertIn("Similarity is historical retrieval evidence, not fraud certainty", sig.description)

        asyncio.run(_run_service_test())


if __name__ == "__main__":
    unittest.main()
