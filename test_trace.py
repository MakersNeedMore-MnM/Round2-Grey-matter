import os
import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.database import SessionLocal, Base, engine
from backend.models import FoundItem, LostReport, ClaimChallenge
from backend.seed import init_db, generate_seed_images
from backend.scoring import compute_fused_score, compute_location_similarity, compute_time_similarity
from backend.verification import generate_challenge_question, verify_claim_answer, extract_key_terms
from backend.embeddings import cosine_similarity, get_text_embedding, get_image_embedding
from backend.main import app


class TraceSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        init_db()
        cls.client = TestClient(app)

    def test_01_seed_data_loaded(self):
        db = SessionLocal()
        found_count = db.query(FoundItem).count()
        lost_count = db.query(LostReport).count()
        db.close()
        self.assertGreaterEqual(found_count, 7, "Should have at least 7 seeded found items")
        self.assertGreaterEqual(lost_count, 7, "Should have at least 7 seeded lost reports")

    def test_02_text_embeddings_and_mismatched_wording(self):
        # Mismatched wording pair
        t1 = "navy blue canvas backpack with leather bottom"
        t2 = "black rucksack with dual straps"
        v1 = get_text_embedding(t1)
        v2 = get_text_embedding(t2)
        sim = cosine_similarity(v1, v2)
        self.assertGreater(sim, 0.35, "Mismatched terms for backpack should still yield meaningful semantic similarity")

    def test_03_time_decay_formula(self):
        now = datetime.utcnow()
        # Same day -> 1.0
        self.assertAlmostEqual(compute_time_similarity(now, now), 1.0, places=2)
        # 7 days apart -> 0.50
        self.assertAlmostEqual(compute_time_similarity(now, now - timedelta(days=7)), 0.50, places=2)
        # 14 days apart -> 0.0
        self.assertAlmostEqual(compute_time_similarity(now, now - timedelta(days=14)), 0.0, places=2)
        # 20 days apart -> floored at 0.0
        self.assertEqual(compute_time_similarity(now, now - timedelta(days=20)), 0.0)

    def test_04_fusion_scoring_weights(self):
        now = datetime.utcnow()
        # Score with photo
        scores_with_photo = compute_fused_score(
            found_description="Navy blue canvas backpack with leather bottom",
            found_location="Platform 4",
            found_at=now,
            found_photo_path="data/seed/images/found_navy_backpack.jpg",
            lost_description="Black rucksack with dual straps",
            lost_location="Near Ticket Counter",
            lost_at=now - timedelta(hours=2),
            lost_photo_path="data/seed/images/lost_black_rucksack.jpg",
        )
        self.assertTrue(scores_with_photo["has_photo"])
        self.assertGreater(scores_with_photo["fused_score"], 0.60)
        # Priority 1: Keyword score should be 0.0 for this mismatched pair
        self.assertEqual(scores_with_photo["keyword_score"], 0.0, "Legacy keyword search must return 0.0 for vocabulary mismatch")
        # Priority 3: Driver explanation should mention photo similarity
        self.assertIn("photo similarity", scores_with_photo["driver_explanation"].lower())

        # Score without photo (re-normalized weights: 50% text, 25% loc, 25% time)
        scores_no_photo = compute_fused_score(
            found_description="Gold wrist chronograph with black strap",
            found_location="Near Ticket Counter",
            found_at=now,
            found_photo_path="data/seed/images/found_gold_watch.jpg",
            lost_description="Yellow metal analog watch with dark band",
            lost_location="Main Concourse",
            lost_at=now - timedelta(days=1),
            lost_photo_path=None,
        )
        self.assertFalse(scores_no_photo["has_photo"])
        self.assertEqual(scores_no_photo["visual_score"], 0.0)
        self.assertGreater(scores_no_photo["fused_score"], 0.50)

    def test_05_challenge_question_and_keyword_claim_check(self):
        hidden_attr = "airline baggage tag with initials R.S. on top handle"
        key_terms = "r.s., baggage tag, initials"

        # 1. Challenge question should be generated
        q = generate_challenge_question(hidden_attr)
        self.assertTrue(len(q) > 10)
        # Shouldn't leak the exact initials
        self.assertNotIn("R.S.", q)

        # 2. Correct answer check -> True
        correct_ans = "It has my airline baggage tag on the handle with my initials R.S."
        res_correct = verify_claim_answer(correct_ans, hidden_attr, key_terms)
        self.assertTrue(res_correct["is_match"])
        self.assertIn("r.s.", res_correct["matched_keywords"])

        # 3. Wrong answer check (false claim) -> False
        wrong_ans = "There is a blue ribbon tied around the zipper."
        res_wrong = verify_claim_answer(wrong_ans, hidden_attr, key_terms)
        self.assertFalse(res_wrong["is_match"])
        self.assertEqual(len(res_wrong["matched_keywords"]), 0)

    def test_06_fastapi_endpoints_flow(self):
        # 1. GET /dashboard/queue
        r_queue = self.client.get("/dashboard/queue")
        self.assertEqual(r_queue.status_code, 200)
        queue_data = r_queue.json()
        self.assertGreater(len(queue_data), 0)
        first_item_id = queue_data[0]["found_item"]["id"]

        # 2. GET /found-items/{id}/matches
        r_matches = self.client.get(f"/found-items/{first_item_id}/matches")
        self.assertEqual(r_matches.status_code, 200)
        matches = r_matches.json()
        self.assertLessEqual(len(matches), 5)
        self.assertGreater(len(matches), 0)
        top = matches[0]
        self.assertIn("fused_score", top)
        self.assertIn("visual_score", top)
        self.assertIn("text_score", top)
        self.assertIn("location_score", top)
        self.assertIn("time_score", top)

        # 3. POST /found-items/{id}/challenge
        r_chal = self.client.post(f"/found-items/{first_item_id}/challenge")
        self.assertEqual(r_chal.status_code, 200)
        challenge = r_chal.json()
        chal_id = challenge["id"]
        self.assertIn("question_text", challenge)

        # 4. POST /challenges/{id}/answer with correct answer
        r_ans = self.client.post(f"/challenges/{chal_id}/answer", json={"answer": "It has a tear on the left strap"})
        self.assertEqual(r_ans.status_code, 200)
        ans_data = r_ans.json()
        self.assertTrue(ans_data["is_match"])


if __name__ == "__main__":
    unittest.main()
