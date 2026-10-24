"""Unit tests for Step 15: VECTPHISH concepts (Semantic Encoding, Cosine Similarity, DBSCAN Clustering)."""

import unittest
import importlib

encoder_mod = importlib.import_module("services.pattern-engine.semantic.encoder")
SemanticEncoder = encoder_mod.SemanticEncoder
semantic_encoder = encoder_mod.semantic_encoder

fp_mod = importlib.import_module("services.pattern-engine.semantic.fingerprint_builder")
ScamFingerprintBuilder = fp_mod.ScamFingerprintBuilder

sim_mod = importlib.import_module("services.pattern-engine.matcher.similarity")
SemanticSimilarityService = sim_mod.SemanticSimilarityService
similarity_service = sim_mod.similarity_service

cluster_mod = importlib.import_module("services.graph-engine.campaigns.clusterer")
CampaignClusterer = cluster_mod.CampaignClusterer


class TestVectphishStep15(unittest.TestCase):
    def test_semantic_encoder_dimension_and_normalization(self):
        vec = semantic_encoder.encode("Your electricity power will be cutoff tonight.")
        self.assertEqual(len(vec), 384)
        norm = float(encoder_mod.np.linalg.norm(vec))
        self.assertAlmostEqual(norm, 1.0, places=3)

    def test_paraphrased_scam_messages_closer_than_benign(self):
        # Scam variation 1: English
        scam_en = "Dear consumer, electricity power will be disconnected at 9:30 PM due to unpaid bill. Call officer immediately."
        # Scam variation 2: Hindi / Hinglish paraphrase
        scam_hi = "Bijli bill unpaid light will be cutoff tonight at 9:30. Contact electricity officer turant."
        # Benign message: Completely unrelated work note
        benign_msg = "Team meeting rescheduled to Thursday 3 PM in conference room B. Please bring project budget notes."

        vec_scam_en = semantic_encoder.encode(scam_en)
        vec_scam_hi = semantic_encoder.encode(scam_hi)
        vec_benign = semantic_encoder.encode(benign_msg)

        sim_scam_pair = semantic_encoder.cosine_similarity(vec_scam_en, vec_scam_hi)
        sim_scam_benign = semantic_encoder.cosine_similarity(vec_scam_en, vec_benign)

        # Paraphrased scam messages MUST be substantially closer to each other than to benign text
        self.assertGreater(sim_scam_pair, sim_scam_benign)
        self.assertGreater(sim_scam_pair, 0.40)
        self.assertGreater(sim_scam_pair - sim_scam_benign, 0.05)

    def test_fingerprint_builder(self):
        fp = ScamFingerprintBuilder.build(
            incident_id="inc_fp_01",
            message_summary="Electricity cutoff notice",
            claimed_identity="State Electricity Board",
            tactics=["IMMINENT_DEADLINE", "IMPERSONATION"],
            requested_action="PAY_BILL_UPDATE_FEE",
        )
        self.assertEqual(fp.incident_id, "inc_fp_01")
        self.assertEqual(fp.claimed_identity, "State Electricity Board")
        self.assertEqual(len(fp.semantic_embedding), 384)
        self.assertIn("IMPERSONATION", fp.social_engineering_tactics)

    def test_similarity_service_matches_seed_campaign(self):
        text = "Your electricity bill is pending power disconnect at 9 PM call officer."
        vec = semantic_encoder.encode(text).tolist()

        best_camp, score, signal = similarity_service.match_campaign("inc_match_01", vec)
        self.assertEqual(best_camp, "CAMP_ELECTRICITY_DISCONNECTION")
        self.assertGreater(score, 0.50)

    def test_dbscan_campaign_clustering(self):
        # 3 related electricity threats
        t1 = "Electricity cutoff tonight pay bill immediately."
        t2 = "Power disconnection notice bill unpaid contact officer."
        t3 = "Bijli cut off tonight pay pending amount."
        # 1 totally unrelated job scam
        t4 = "Work from home part time job earn daily 5000 like youtube video."

        vecs = [
            semantic_encoder.encode(t1).tolist(),
            semantic_encoder.encode(t2).tolist(),
            semantic_encoder.encode(t3).tolist(),
            semantic_encoder.encode(t4).tolist(),
        ]
        inc_ids = ["inc_1", "inc_2", "inc_3", "inc_4"]

        # Run DBSCAN clusterer with eps=0.55
        clusterer = CampaignClusterer(eps=0.55, min_samples=2)
        res = clusterer.cluster_fingerprints(inc_ids, vecs)

        # The 3 electricity incidents should cluster together
        self.assertGreaterEqual(res["total_clusters"], 1)
        clustered_incidents = [inc for cluster in res["clusters"].values() for inc in cluster]
        self.assertIn("inc_1", clustered_incidents)
        self.assertIn("inc_2", clustered_incidents)


if __name__ == "__main__":
    unittest.main()
