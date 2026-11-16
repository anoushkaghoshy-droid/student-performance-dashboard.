
import os
import sys
import unittest
import tempfile
import pandas as pd
import numpy as np

# Add project root to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from student_record import StudentRecord, is_valid_score, score_to_grade
from generate_data import load_csv, validate_rows, save_csv, DEFAULT_CSV_PATH
from student_dashboard import (
    iqr_mask, get_outliers_mask, analysis_for, correlation, interpretation
)


class TestStudentDashboard(unittest.TestCase):

    def setUp(self):
        self.csv_path = DEFAULT_CSV_PATH
        self.assertTrue(os.path.exists(self.csv_path), f"Default CSV not found at {self.csv_path}")
        self.valid_df, self.rejected = load_csv(self.csv_path)

    # --------------------------------------------------------------------------
    # Test Case 1: Sample startup
    # --------------------------------------------------------------------------
    def test_01_sample_startup(self):
        """Verify startup builds records: 123 accepted and 2 rejected rows."""
        self.assertEqual(len(self.valid_df), 123, "Expected exactly 123 valid student records.")
        self.assertEqual(len(self.rejected), 2, "Expected exactly 2 rejected input rows.")
        
        # Verify courses present
        courses = set(self.valid_df["course"].unique())
        self.assertEqual(courses, {"Biology", "Business", "Computing", "Maths"})

    # --------------------------------------------------------------------------
    # Test Case 2: Invalid score (140) rejection
    # --------------------------------------------------------------------------
    def test_02_invalid_score_rejection(self):
        """Verify that score > 100 or < 0 raises ValueError and fails validation."""
        self.assertFalse(is_valid_score(140))
        self.assertFalse(is_valid_score(-5.5))
        self.assertFalse(is_valid_score("invalid"))

        with self.assertRaises(ValueError):
            StudentRecord(student_id="S_TEST", course="Computing", study_hours=12.0, score=140.0)

        with self.assertRaises(ValueError):
            score_to_grade(140.0)

        # Check that row 124 in sample dataset was rejected due to score 140
        score_rejections = [r for r in self.rejected if "140" in str(r.get("score", ""))]
        self.assertTrue(len(score_rejections) > 0, "Row with score 140 was not properly rejected.")

    # --------------------------------------------------------------------------
    # Test Case 3: Blank study hours rejection
    # --------------------------------------------------------------------------
    def test_03_blank_study_hours_rejection(self):
        """Verify that blank, non-numeric, or out-of-range study hours are rejected."""
        with self.assertRaises(ValueError):
            StudentRecord.from_dict({
                "student_id": "S_TEST", "course": "Biology", "study_hours": "", "score": 75.0
            })

        with self.assertRaises(ValueError):
            StudentRecord(student_id="S_TEST", course="Biology", study_hours="N/A", score=75.0)

        with self.assertRaises(ValueError):
            StudentRecord(student_id="S_TEST", course="Biology", study_hours=200.0, score=75.0)

        blank_rejections = [r for r in self.rejected if r.get("study_hours", "").strip() == ""]
        self.assertTrue(len(blank_rejections) > 0, "Row with blank study_hours was not properly rejected.")

    # --------------------------------------------------------------------------
    # Test Case 4: Default IQR (k = 1.5) outlier detection
    # --------------------------------------------------------------------------
    def test_04_default_iqr_outlier_detection(self):
        """Verify default IQR threshold k=1.5 flags exactly 4 extreme records."""
        out_mask = get_outliers_mask(self.valid_df, k=1.5)
        outliers_df = self.valid_df[out_mask]
        self.assertEqual(len(outliers_df), 4, f"Expected 4 outliers, found {len(outliers_df)}.")
        
        flagged_ids = set(outliers_df["student_id"].tolist())
        expected_ids = {"S065", "S088", "S901", "S902"}
        self.assertEqual(flagged_ids, expected_ids, f"Expected outlier IDs {expected_ids}, got {flagged_ids}")

    # --------------------------------------------------------------------------
    # Test Case 5: Course selector filtering
    # --------------------------------------------------------------------------
    def test_05_course_selector_filter(self):
        """Verify filtering by course recalculates descriptive statistics correctly."""
        for c, expected_n in [("Biology", 35), ("Business", 21), ("Computing", 40), ("Maths", 27)]:
            sub_df = self.valid_df[self.valid_df["course"] == c]
            self.assertEqual(len(sub_df), expected_n, f"Expected {expected_n} records for {c}, got {len(sub_df)}")
            stats = analysis_for(sub_df, k=1.5)
            self.assertEqual(stats["n"], expected_n)
            self.assertTrue(0.0 <= stats["mean_score"] <= 100.0)
            self.assertTrue(0.0 <= stats["mean_hours"] <= 168.0)

    # --------------------------------------------------------------------------
    # Test Case 6: CSV import handling
    # --------------------------------------------------------------------------
    def test_06_csv_import_handling(self):
        """Verify DictReader properly detects bad headers and corrupt rows."""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
            tmp.write("student_id,wrong_header,study_hours,score\n")
            tmp.write("S999,Computing,10.0,80.0\n")
            tmp_path = tmp.name

        try:
            with self.assertRaises(ValueError):
                load_csv(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # --------------------------------------------------------------------------
    # Test Case 7: Hide outliers filter
    # --------------------------------------------------------------------------
    def test_07_hide_outliers_filter(self):
        """Verify exclusion of flagged outliers yields clean cohort of 119 records."""
        out_mask = get_outliers_mask(self.valid_df, k=1.5)
        clean_df = self.valid_df[~out_mask]
        self.assertEqual(len(clean_df), 119, f"Expected 119 records without outliers, got {len(clean_df)}")
        
        # Verify correlation comparison
        corr_all = correlation(self.valid_df, drop_outliers=False, k=1.5)
        corr_clean = correlation(self.valid_df, drop_outliers=True, k=1.5)
        self.assertGreater(corr_clean["pearson_r"], corr_all["pearson_r"],
                           "Pearson r should increase after removing extreme outliers.")

    # --------------------------------------------------------------------------
    # Test Case 8: Export filtered CSV
    # --------------------------------------------------------------------------
    def test_08_export_filtered_csv(self):
        """Verify filtered DataFrame exports to CSV and re-imports losslessly."""
        computing_df = self.valid_df[self.valid_df["course"] == "Computing"].copy()
        
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name

        try:
            save_csv(computing_df, tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            reloaded_df, rej = load_csv(tmp_path)
            self.assertEqual(len(reloaded_df), len(computing_df))
            self.assertEqual(len(rej), 0)
            self.assertTrue((reloaded_df["course"] == "Computing").all())
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # --------------------------------------------------------------------------
    # Test Case 9: Grade boundary conversions
    # --------------------------------------------------------------------------
    def test_09_grade_boundaries(self):
        """Verify grade mapping thresholds: A (70-100), B (60-69), C (50-59), D (40-49), F (<40)."""
        self.assertEqual(score_to_grade(100.0), 'A')
        self.assertEqual(score_to_grade(70.0), 'A')
        self.assertEqual(score_to_grade(69.9), 'B')
        self.assertEqual(score_to_grade(60.0), 'B')
        self.assertEqual(score_to_grade(59.9), 'C')
        self.assertEqual(score_to_grade(50.0), 'C')
        self.assertEqual(score_to_grade(49.9), 'D')
        self.assertEqual(score_to_grade(40.0), 'D')
        self.assertEqual(score_to_grade(39.9), 'F')
        self.assertEqual(score_to_grade(0.0), 'F')


if __name__ == "__main__":
    unittest.main(verbosity=2)
