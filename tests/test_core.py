"""
ROADGUARD AI - Core System Verification & Unit Tests
Validates database integrity, scoring engine logic, detection fallback,
PDF generation, and image processing workflows.
"""

import unittest
import os
import shutil
from pathlib import Path
from PIL import Image
import io

from config import BASE_DIR, REPORTS_DIR, DB_PATH
from database.db import (
    init_db,
    add_report,
    get_report_by_id,
    update_report_status,
    delete_report,
    get_dashboard_stats,
    get_filtered_reports,
    create_user,
    authenticate_user
)
from severity.scoring import calculate_visual_priority_score
from detection.detector import RoadDamageDetector
from utils.image_processing import save_image_to_disk
from utils.pdf_generator import generate_pdf_report
from utils.helpers import generate_report_id, reports_to_csv_bytes

class TestRoadGuardCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes database schema for testing."""
        init_db()

    def test_01_scoring_engine(self):
        """Verifies visual priority scoring calculation and transparent breakdown."""
        # Case A: Empty detections
        assessment_empty = calculate_visual_priority_score([])
        self.assertEqual(assessment_empty.score, 0.0)
        self.assertEqual(assessment_empty.band, "LOW")

        # Case B: High priority pothole with wet conditions on highway
        detections = [
            {
                "class_id": 0,
                "class_name": "Pothole",
                "confidence": 0.92,
                "box_x1": 100, "box_y1": 150, "box_x2": 400, "box_y2": 450,
                "area_ratio": 0.15
            }
        ]
        assessment = calculate_visual_priority_score(
            detections=detections,
            road_type="Highway / Expressway",
            traffic_volume="Heavy (Trucks / Public Transit)",
            weather_condition="Wet / Rainy"
        )
        self.assertGreaterEqual(assessment.score, 70.0)
        self.assertEqual(assessment.band, "HIGH")
        self.assertIn("class_points", assessment.factor_breakdown)
        self.assertIn("area_points", assessment.factor_breakdown)
        self.assertIn("combined_context_multiplier", assessment.factor_breakdown)
        self.assertIn("2D photo cannot measure structural sub-base", assessment.technical_disclaimer)

    def test_02_database_crud_and_audit(self):
        """Verifies database insertion, status audit logging, and deletion."""
        test_id = generate_report_id()
        report_data = {
            "id": test_id,
            "damage_type": "Pothole",
            "primary_class": "Pothole",
            "detection_count": 1,
            "max_confidence": 0.89,
            "avg_confidence": 0.89,
            "priority_score": 85.0,
            "priority_band": "HIGH",
            "urgency_level": "Immediate Action Required",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "location_address": "Test Corridor #10",
            "location_source": "Device GPS",
            "road_type": "Highway / Expressway",
            "traffic_volume": "Heavy (Trucks / Public Transit)",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "New",
            "reporter_name": "Test Officer",
            "reporter_role": "authority",
            "notes": "Automated test defect record",
            "score_breakdown": {"class_points": 35.0, "area_points": 20.0},
            "is_demo_data": 0
        }
        detections = [
            {
                "class_id": 0,
                "class_name": "Pothole",
                "confidence": 0.89,
                "box_x1": 50, "box_y1": 50, "box_x2": 200, "box_y2": 200,
                "area_ratio": 0.08
            }
        ]

        # 1. Insert
        saved_id = add_report(report_data, detections)
        self.assertEqual(saved_id, test_id)

        # 2. Retrieve
        fetched = get_report_by_id(test_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["damage_type"], "Pothole")
        self.assertEqual(len(fetched["detections"]), 1)
        self.assertGreaterEqual(len(fetched["history"]), 1)

        # 3. Update Status
        updated = update_report_status(test_id, "Inspection Scheduled", "Engineer Sharma", "Inspection team dispatched")
        self.assertTrue(updated)
        refetched = get_report_by_id(test_id)
        self.assertEqual(refetched["status"], "Inspection Scheduled")
        self.assertEqual(len(refetched["history"]), 2)

        # 4. Check Stats
        stats = get_dashboard_stats()
        self.assertGreaterEqual(stats["total_reports"], 1)

        # 5. Delete
        deleted = delete_report(test_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_report_by_id(test_id))

    def test_03_detector_fallback_and_diagnostics(self):
        """Verifies detector reports missing weights honestly and tags demo fallback correctly."""
        detector = RoadDamageDetector(model_path="models/non_existent_weights.pt")
        status = detector.get_status_info()
        self.assertFalse(status["is_custom"])

        dummy_img = Image.new("RGB", (400, 300), color=(100, 100, 100))

        # Predict without demo fallback should report missing weights cleanly
        pred_no_demo = detector.predict(dummy_img, allow_demo_fallback=False)
        self.assertFalse(pred_no_demo["success"])
        self.assertIn("No trained YOLO model weights found", pred_no_demo["error"])

        # Predict with explicit demo fallback must be tagged as demo
        pred_demo = detector.predict(dummy_img, allow_demo_fallback=True)
        self.assertTrue(pred_demo["success"])
        self.assertTrue(pred_demo["is_demo"])
        self.assertIn("[DEMO SIMULATION]", pred_demo["detections"][0]["class_name"])

    def test_04_pdf_generation(self):
        """Verifies ReportLab PDF generation pipeline."""
        dummy_report = {
            "id": "RGD-2026-TEST",
            "damage_type": "Pothole",
            "primary_class": "Pothole",
            "detection_count": 1,
            "priority_score": 88.0,
            "priority_band": "HIGH",
            "urgency_level": "Immediate Action Required",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "location_address": "Connaught Place Radial 1",
            "location_source": "Device GPS",
            "road_type": "Arterial Road",
            "traffic_volume": "Heavy",
            "weather_condition": "Dry / Clear",
            "original_image_path": "",
            "annotated_image_path": "",
            "status": "New",
            "reporter_name": "Test Inspector",
            "reporter_role": "authority",
            "notes": "Severe cavity test",
            "detections": [
                {
                    "class_name": "Pothole",
                    "confidence": 0.91,
                    "area_ratio": 0.12,
                    "box_x1": 50, "box_y1": 50, "box_x2": 250, "box_y2": 250
                }
            ],
            "is_demo_data": 0
        }
        pdf_path = generate_pdf_report(dummy_report)
        self.assertTrue(Path(pdf_path).exists())
        self.assertGreater(Path(pdf_path).stat().st_size, 1000)

    def test_05_csv_export(self):
        """Verifies CSV conversion utility."""
        dummy_reports = [
            {"id": "RGD-001", "created_at": "2026-11-22T10:00:00", "damage_type": "Pothole", "priority_score": 85.0, "status": "New"}
        ]
        csv_bytes = reports_to_csv_bytes(dummy_reports)
        self.assertIn(b"RGD-001", csv_bytes)
        self.assertIn(b"Pothole", csv_bytes)

    def test_06_authentication(self):
        """Verifies password hashing and role verification."""
        test_user = "test_engineer"
        test_pass = "SecurePass2026!"
        created = create_user(test_user, test_pass, "Test Engineer", "authority")
        # Might already exist if rerun
        auth_success = authenticate_user(test_user, test_pass)
        self.assertIsNotNone(auth_success)
        self.assertEqual(auth_success["role"], "authority")

        auth_fail = authenticate_user(test_user, "WrongPassword")
        self.assertIsNone(auth_fail)

    def test_07_priority_queue_sorting_and_filtering(self):
        """Verifies maintenance queue ranks highest visual priority reports first and filters correctly."""
        id_high = generate_report_id()
        id_low = generate_report_id()

        # Add low priority report
        add_report({
            "id": id_low, "damage_type": "Transverse Crack", "primary_class": "Transverse Crack",
            "detection_count": 1, "priority_score": 25.0, "priority_band": "LOW",
            "status": "New", "location_address": "Test Low Corridor"
        }, [])

        # Add high priority report
        add_report({
            "id": id_high, "damage_type": "Pothole", "primary_class": "Pothole",
            "detection_count": 2, "priority_score": 92.5, "priority_band": "HIGH",
            "status": "New", "location_address": "Test High Corridor"
        }, [])

        # Fetch sorted by priority_desc
        queue = get_filtered_reports(sort_by="priority_desc")
        scores = [float(r["priority_score"]) for r in queue]
        # Verify monotonically non-increasing order
        self.assertEqual(scores, sorted(scores, reverse=True))

        # Filter by Pothole
        potholes = get_filtered_reports(damage_type="Pothole")
        self.assertTrue(all("Pothole" in p["damage_type"] or "Pothole" in p["primary_class"] for p in potholes))

        # Cleanup
        delete_report(id_high)
        delete_report(id_low)

    def test_08_location_handling_and_coordinates(self):
        """Verifies geocoded vs unlocated reports separation logic."""
        id_geo = generate_report_id()
        id_unloc = generate_report_id()

        add_report({
            "id": id_geo, "damage_type": "Pothole", "primary_class": "Pothole",
            "detection_count": 1, "priority_score": 60.0, "priority_band": "MEDIUM",
            "latitude": 28.5700, "longitude": 77.2400, "location_source": "Device GPS",
            "status": "New"
        }, [])

        add_report({
            "id": id_unloc, "damage_type": "Crack", "primary_class": "Longitudinal Crack",
            "detection_count": 1, "priority_score": 45.0, "priority_band": "MEDIUM",
            "latitude": None, "longitude": None, "location_source": "Not Provided",
            "status": "New"
        }, [])

        rep_geo = get_report_by_id(id_geo)
        rep_unloc = get_report_by_id(id_unloc)

        self.assertIsNotNone(rep_geo["latitude"])
        self.assertIsNotNone(rep_geo["longitude"])
        self.assertIsNone(rep_unloc["latitude"])
        self.assertIsNone(rep_unloc["longitude"])
        self.assertEqual(rep_unloc["location_source"], "Not Provided")

        # Cleanup
        delete_report(id_geo)
        delete_report(id_unloc)

if __name__ == "__main__":
    unittest.main()
