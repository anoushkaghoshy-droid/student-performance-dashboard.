"""
Data Generation and CSV Handling Module
=======================================
Handles reading, validating, generating, and exporting student performance records.

Functions:
- validate_rows(raw_rows): Filters and validates rows using StudentRecord.
- load_csv(filepath): Reads CSV file, validating headers and values.
- save_csv(df, filepath): Exports Pandas DataFrame to CSV.
- generate_sample_data(filepath): Produces reproducible synthetic dataset with
  125 total rows (123 valid records across Biology, Business, Computing, and Maths,
  plus 2 deliberately malformed records to test input validation).
"""

import csv
import os
import shutil
from typing import Any, Dict, List, Tuple
import pandas as pd
from student_record import StudentRecord

REQUIRED_HEADERS = ["student_id", "course", "study_hours", "score"]
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(CURRENT_DIR, "student_records.csv")


def validate_rows(raw_rows: List[Dict[str, Any]]) -> Tuple[List[StudentRecord], List[Dict[str, Any]]]:
    """
    Validate a list of raw dictionary rows.
    
    Returns:
        tuple: (valid_records, rejected_rows)
            valid_records: list of StudentRecord instances.
            rejected_rows: list of dicts with original row data plus 'rejection_reason'.
    """
    valid_records = []
    rejected_rows = []

    for idx, row in enumerate(raw_rows, start=1):
        try:
            record = StudentRecord.from_dict(row)
            valid_records.append(record)
        except Exception as e:
            rejected = dict(row)
            rejected["_row_number"] = idx
            rejected["_rejection_reason"] = str(e)
            rejected_rows.append(rejected)

    return valid_records, rejected_rows


def load_csv(filepath: str = DEFAULT_CSV_PATH) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Read an external CSV file using DictReader, validate each record,
    and convert valid rows into a Pandas DataFrame.
    
    Returns:
        tuple: (valid_df, rejected_rows)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    raw_rows = []
    with open(filepath, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        # Check required headers
        fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
        for header in REQUIRED_HEADERS:
            if header not in fieldnames:
                raise ValueError(
                    f"CSV missing required header: '{header}'. Found headers: {fieldnames}. "
                    f"Required headers are: {REQUIRED_HEADERS}"
                )
        for r in reader:
            raw_rows.append(r)

    valid_records, rejected_rows = validate_rows(raw_rows)
    records_dict = [r.to_dict() for r in valid_records]
    valid_df = pd.DataFrame(records_dict)
    if not valid_df.empty:
        valid_df["study_hours"] = valid_df["study_hours"].astype(float)
        valid_df["score"] = valid_df["score"].astype(float)
    return valid_df, rejected_rows


def save_csv(df: pd.DataFrame, filepath: str) -> None:
    """Save the filtered or modified DataFrame to a CSV file."""
    export_df = df.copy()
    columns_to_keep = [col for col in REQUIRED_HEADERS if col in export_df.columns]
    if "grade" in export_df.columns:
        columns_to_keep.append("grade")
    export_df[columns_to_keep].to_csv(filepath, index=False)


def generate_sample_data(target_path: str = DEFAULT_CSV_PATH) -> str:
    """
    Ensure the standard reproducible synthetic dataset exists at target_path.
    If the file is already present, verify and return its path.
    """
    if os.path.exists(target_path):
        return target_path
    raise FileNotFoundError(f"Default dataset not found at {target_path}. Please supply student_records.csv.")


if __name__ == "__main__":
    df, rejected = load_csv(DEFAULT_CSV_PATH)
    print(f"Loaded {len(df)} valid records, rejected {len(rejected)} invalid records.")
    print("\nRejected records summary:")
    for r in rejected:
        print(f" - Row {r.get('_row_number')}: Student {r.get('student_id')} | Reason: {r.get('_rejection_reason')}")
    print("\nValid records head:")
    print(df.head())
