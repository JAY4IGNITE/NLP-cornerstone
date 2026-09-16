"""Dataset quality validator and auditor.
Verifies uniqueness, label integrity, absence of data leakage, and length anomalies.
Outputs reports/dataset_quality_report.json.
"""
import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_INTENTS = {
    "course_overview", "course_outcome", "course_objectives", "syllabus",
    "course_code", "credits", "prerequisites", "units", "unit_topics",
    "semester_subjects", "branch_subjects", "faculty_information",
    "academic_regulations", "examination_information", "lab_information",
    "elective_information", "course_structure", "subject_comparison",
    "curriculum_search", "greeting", "thanks", "help", "fallback"
}

def validate():
    csv_path = DATA_DIR / "intents.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")

    df = pd.read_csv(csv_path)
    total_samples = len(df)

    # 1. Null Checks
    null_questions = int(df["question"].isna().sum())
    null_intents = int(df["intent"].isna().sum())

    # 2. Uniqueness & Duplicates
    clean_questions = df["question"].fillna("").astype(str).str.strip().str.lower()
    unique_count = int(clean_questions.nunique())
    duplicate_count = total_samples - unique_count
    uniqueness_pct = round((unique_count / total_samples) * 100, 2)

    # 3. Invalid labels
    found_intents = set(df["intent"].dropna().unique())
    invalid_labels = list(found_intents - EXPECTED_INTENTS)
    missing_intents = list(EXPECTED_INTENTS - found_intents)

    # 4. Length distributions
    lengths = df["question"].str.len()
    short_questions = int((lengths < 3).sum())
    long_questions = int((lengths > 300).sum())

    # 5. Class balance
    counts = df["intent"].value_counts()
    min_count = int(counts.min())
    max_count = int(counts.max())
    imbalance_ratio = round(max_count / min_count, 2) if min_count > 0 else None

    # 6. Data leakage check between train/val/test
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test.csv")

    train_set = set(train_df["question"].str.strip().str.lower())
    val_set = set(val_df["question"].str.strip().str.lower())
    test_set = set(test_df["question"].str.strip().str.lower())

    train_val_overlap = len(train_set.intersection(val_set))
    train_test_overlap = len(train_set.intersection(test_set))
    val_test_overlap = len(val_set.intersection(test_set))

    passed_uniqueness = uniqueness_pct >= 95.0
    passed_labels = len(invalid_labels) == 0 and len(missing_intents) == 0
    passed_no_nulls = null_questions == 0 and null_intents == 0
    overall_status = "PASSED" if (passed_uniqueness and passed_labels and passed_no_nulls) else "FAILED"

    report = {
        "status": overall_status,
        "total_samples": total_samples,
        "unique_questions": unique_count,
        "uniqueness_percentage": uniqueness_pct,
        "target_met_gte_95_percent": passed_uniqueness,
        "duplicate_count": duplicate_count,
        "null_questions": null_questions,
        "null_intents": null_intents,
        "expected_intent_count": len(EXPECTED_INTENTS),
        "present_intent_count": len(found_intents),
        "invalid_labels": invalid_labels,
        "missing_intents": missing_intents,
        "short_questions_lt_3_chars": short_questions,
        "long_questions_gt_300_chars": long_questions,
        "class_balance": {
            "min_samples_per_class": min_count,
            "max_samples_per_class": max_count,
            "imbalance_ratio": imbalance_ratio
        },
        "data_leakage_audit": {
            "train_val_overlap_count": train_val_overlap,
            "train_test_overlap_count": train_test_overlap,
            "val_test_overlap_count": val_test_overlap,
            "leakage_detected": (train_val_overlap > 0 or train_test_overlap > 0 or val_test_overlap > 0)
        }
    }

    report_path = REPORTS_DIR / "dataset_quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Quality Audit Completed: Status={overall_status}, Uniqueness={uniqueness_pct}%")
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    validate()
