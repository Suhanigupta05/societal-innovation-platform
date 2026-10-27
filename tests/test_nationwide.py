"""
Comprehensive Automated Test Suite for Nationwide India Support Upgrade
Societal Innovation Collaboration Platform
"""

import unittest
import os
import json
import sqlite3
from fastapi.testclient import TestClient

from main import app, resolve_and_validate_location
from app.database import (
    init_db,
    get_db_connection,
    insert_problem,
    get_all_problems,
    get_problem_by_id,
    get_dashboard_analytics,
    get_all_solutions
)
from app.ai_engine import ai_engine
from app.seed_data import seed_database


class TestNationwideSupport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize and seed database if not already populated
        init_db()
        seed_database()
        cls.client = TestClient(app)

    def test_01_app_starts_and_home_loads_without_template_errors(self):
        """Verify homepage loads 200 OK and contains nationwide elements."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.text
        self.assertIn("Societal Innovation", html)
        self.assertIn("Coverage: Nationwide India (28 States & 8 UTs)", html)
        self.assertIn('id="p-state"', html)
        self.assertIn('id="p-district"', html)
        self.assertIn('id="viva-state"', html)
        self.assertIn('id="viva-district"', html)
        self.assertNotIn("Focus: Jharkhand Districts", html)

    def test_02_locations_api_coverage(self):
        """Verify /api/locations returns all 28 states and 8 union territories."""
        response = self.client.get("/api/locations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("states", data)
        states = [s for s in data["states"] if s["type"] == "State"]
        uts = [s for s in data["states"] if s["type"] == "Union Territory"]
        self.assertEqual(len(states), 28)
        self.assertEqual(len(uts), 8)

        # Verify Jharkhand exists with its districts
        jh = next((s for s in data["states"] if s["name"] == "Jharkhand"), None)
        self.assertIsNotNone(jh)
        self.assertIn("Ranchi", jh["districts"])
        self.assertIn("Palamu", jh["districts"])

        # Verify Jammu and Kashmir exists with its districts
        jk = next((s for s in data["states"] if s["name"] == "Jammu and Kashmir"), None)
        self.assertIsNotNone(jk)
        self.assertIn("Srinagar", jk["districts"])
        self.assertIn("Anantnag", jk["districts"])

    def test_03_submit_problem_from_jharkhand(self):
        """Verify submitting a problem from Jharkhand works and stores state correctly."""
        payload = {
            "title": "Severe Arsenic in Drinking Tubewells in Sahibganj",
            "description": "High levels of arsenic contamination (>0.06 mg/L) detected in shallow village handpumps along the Ganga river basin causing skin keratosis among local farmers.",
            "state": "Jharkhand",
            "district": "Sahibganj",
            "locality": "Udhwa Block, Radhanagar",
            "citizen_name": "Suresh Mandal",
            "citizen_contact": "suresh.mandal@gmail.com",
            "urgency": "Critical",
            "impact": "Multiple Villages / Block"
        }
        response = self.client.post("/api/problems", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        prob_id = data["problem_id"]
        self.assertTrue(prob_id.startswith("JH-2026-"))

        # Verify fetched problem
        get_res = self.client.get(f"/api/problems/{prob_id}")
        self.assertEqual(get_res.status_code, 200)
        prob = get_res.json()["problem"]
        self.assertEqual(prob["state"], "Jharkhand")
        self.assertEqual(prob["district"], "Sahibganj")

    def test_04_submit_problem_from_another_state_jammu_and_kashmir(self):
        """Verify submitting a problem from Jammu and Kashmir works."""
        payload = {
            "title": "Cloudburst Flash Flood and Embankment Erosion in Jhelum Basin",
            "description": "Severe flash flood warning and heavy siltation threatening low-lying apple orchards in Anantnag and Srinagar. Real-time IoT water telemetry sensors urgently needed.",
            "state": "Jammu and Kashmir",
            "district": "Srinagar",
            "locality": "Rajbagh Flood Channel",
            "citizen_name": "Tariq Ahmad Rather",
            "citizen_contact": "tariq.rather@jammukashmir.org",
            "urgency": "Critical",
            "impact": "Entire District"
        }
        response = self.client.post("/api/problems", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        prob_id = data["problem_id"]
        self.assertTrue(prob_id.startswith("JK-2026-"))

        # Check detail endpoint
        get_res = self.client.get(f"/api/problems/{prob_id}")
        self.assertEqual(get_res.status_code, 200)
        prob = get_res.json()["problem"]
        self.assertEqual(prob["state"], "Jammu and Kashmir")
        self.assertEqual(prob["district"], "Srinagar")

    def test_05_legacy_database_migration_and_compatibility(self):
        """Verify existing records without a state column or with empty state load cleanly as Jharkhand."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert a raw simulated legacy row where state might be NULL or empty
        legacy_id = "JH-LEGACY-099"
        cursor.execute("DELETE FROM problems WHERE id = ?", (legacy_id,))
        cursor.execute("""
        INSERT INTO problems (
            id, title, description, state, district, locality, citizen_name, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            legacy_id,
            "Legacy Historical Problem Without Explicit State",
            "Historical community water issue in early pilot.",
            None,
            "Ranchi",
            "Namkum",
            "Legacy Reporter",
            "Submitted",
            "2026-01-01T00:00:00"
        ))
        conn.commit()
        conn.close()

        # Query single
        prob = get_problem_by_id(legacy_id)
        self.assertIsNotNone(prob)
        self.assertEqual(prob["state"], "Jharkhand")

        # Query all
        all_p = get_all_problems()
        legacy_found = next((p for p in all_p if p["id"] == legacy_id), None)
        self.assertIsNotNone(legacy_found)
        self.assertEqual(legacy_found["state"], "Jharkhand")

        # Re-run init_db() to prove migration is completely safe and idempotent
        init_db()

    def test_06_ai_analysis_endpoint_and_classification(self):
        """Verify /api/ai/analyze accurately classifies domain, flags duplicates, and matches universities."""
        payload = {
            "title": "Severe Fluoride Contamination in Palamu Ground Water",
            "description": "High fluoride levels exceeding permissible limits causing dental fluorosis in children. Community water filtration required.",
            "state": "Jharkhand",
            "district": "Palamu",
            "urgency": "Critical",
            "impact": "Multiple Villages / Block"
        }
        response = self.client.post("/api/ai/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertIn("nlp_classification", result)
        self.assertIn("duplicate_detection", result)
        self.assertIn("recommended_universities", result)
        self.assertIn("priority", result)

        # Water management classification
        self.assertEqual(result["nlp_classification"]["predicted_domain"], "Water Management")
        self.assertGreater(result["nlp_classification"]["confidence"], 25.0)

        # Proximity rationale check for Jharkhand
        top_uni = result["recommended_universities"][0]
        self.assertIn("Active presence in Palamu", top_uni["rationale"])

    def test_07_ai_matching_honesty_for_out_of_state_locations(self):
        """Verify cross-state problem does NOT fabricate local proximity and explains remote alignment."""
        payload = {
            "title": "Subsurface Geotechnical Sinkholes and Road Subsidence in Shimla Hills",
            "description": "Heavy rainfall inducing ground subsidence, structural cracks in mountain roads and landslide threats along steep slopes.",
            "state": "Himachal Pradesh",
            "district": "Shimla",
            "urgency": "High",
            "impact": "Entire District"
        }
        response = self.client.post("/api/ai/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        result = response.json()

        recommended = result["recommended_universities"]
        self.assertGreater(len(recommended), 0)
        # Rationale must honestly acknowledge remote national partner
        top_match = recommended[0]
        self.assertIn("National research partner", top_match["rationale"])
        self.assertIn("Remote", top_match["rationale"])

    def test_08_core_endpoints_remain_intact(self):
        """Verify universities, domains, analytics, and solutions endpoints work intact."""
        # /api/universities
        unis = self.client.get("/api/universities").json()
        self.assertEqual(len(unis), 7)
        self.assertEqual(unis[0]["state"], "Jharkhand")

        # /api/domains
        domains = self.client.get("/api/domains").json()
        self.assertEqual(len(domains), 8)
        self.assertIn("Agriculture", domains)
        self.assertIn("Water Management", domains)

        # /api/analytics
        analytics = self.client.get("/api/analytics").json()
        self.assertIn("total_problems", analytics)
        self.assertIn("domain_distribution", analytics)
        self.assertIn("priority_distribution", analytics)

        # /api/solutions
        sols = self.client.get("/api/solutions").json()
        self.assertIsInstance(sols, list)

    def test_09_multipart_upload_submission_across_states(self):
        """Verify problem submission with file upload for nationwide states."""
        files = {
            "file": ("test_report.txt", b"Ground inspection report data for water salinity.", "text/plain")
        }
        data = {
            "title": "Coastal Ground Water Salinity in Kutch",
            "description": "Rising sea water ingress contaminating local drinking wells in Mandvi coastal villages.",
            "state": "Gujarat",
            "district": "Kutch",
            "locality": "Mandvi Coastal Taluka",
            "citizen_name": "Bhavesh Patel",
            "citizen_contact": "bhavesh.patel@gujarat.in",
            "urgency": "High",
            "impact": "Multiple Villages / Block"
        }
        res = self.client.post("/api/problems/upload", data=data, files=files)
        self.assertEqual(res.status_code, 200)
        json_res = res.json()
        self.assertTrue(json_res["success"])
        self.assertTrue(json_res["problem_id"].startswith("GJ-2026-"))

        # Verify saved state and file
        prob = self.client.get(f"/api/problems/{json_res['problem_id']}").json()["problem"]
        self.assertEqual(prob["state"], "Gujarat")
        self.assertEqual(prob["district"], "Kutch")
        self.assertIn("test_report.txt", prob["evidence_media"])

    def test_10_solution_proposal_and_industry_pledge_lifecycle(self):
        """Verify end-to-end lifecycle: assignment, solution proposal submission, and CSR pledge."""
        # Submit a problem
        p_res = self.client.post("/api/problems", json={
            "title": "Severe Soil Acidity Affecting Mustard Cultivation",
            "description": "Depleted soil pH < 4.8 causing widespread crop failure across 200 acres.",
            "state": "Jharkhand",
            "district": "Khunti",
            "locality": "Murhu Block",
            "citizen_name": "Birsa Kisan Group",
            "citizen_contact": "birsa.khunti@kisan.org",
            "urgency": "Medium",
            "impact": "Multiple Villages / Block"
        }).json()
        prob_id = p_res["problem_id"]

        # Assign to Birsa Agricultural University
        assign_res = self.client.post(f"/api/problems/{prob_id}/assign", data={
            "university_id": "u1",
            "university_name": "Birsa Agricultural University (BAU), Ranchi"
        }).json()
        self.assertTrue(assign_res["success"])

        # Submit Solution Proposal
        sol_res = self.client.post("/api/solutions", json={
            "problem_id": prob_id,
            "university_id": "u1",
            "university_name": "Birsa Agricultural University (BAU), Ranchi",
            "lead_faculty": "Dr. Rameshwar Oraon",
            "student_team": "Team Soil-Revive",
            "solution_title": "Bio-Liming and Organic Neutralization Compost Pellets",
            "proposal_summary": "Low-cost local bio-liming formulation using waste eggshells and dolomitic limestone.",
            "technical_approach": "Field application of 200 kg/acre pelletized bio-neutralizer with microbial inoculants.",
            "estimated_budget": 185000.0,
            "timeline_months": 4,
            "milestones": [
                {"name": "Soil Sampling & Lab Assay", "status": "Completed"},
                {"name": "Bio-Pellet Batch Production", "status": "Pending"},
                {"name": "Field Pilot Demonstration", "status": "Pending"}
            ]
        }).json()
        self.assertTrue(sol_res["success"])
        sol_id = sol_res["solution_id"]

        # CSR Pledge
        ind_res = self.client.post("/api/industry", json={
            "problem_id": prob_id,
            "solution_id": sol_id,
            "company_name": "AgriGrow CSR Foundation",
            "support_type": "Grant & Soil Testing Equipment",
            "amount_pledged": 200000.0,
            "mentor_name": "Dr. V. K. Sharma (Chief Agronomist)"
        }).json()
        self.assertTrue(ind_res["success"])

        # Verify problem detail reflects complete lifecycle
        detail = self.client.get(f"/api/problems/{prob_id}").json()
        self.assertEqual(detail["problem"]["status"], "Industry_Funded")
        self.assertEqual(len(detail["solutions"]), 1)
        self.assertEqual(detail["solutions"][0]["solution_title"], "Bio-Liming and Organic Neutralization Compost Pellets")


if __name__ == "__main__":
    unittest.main()
