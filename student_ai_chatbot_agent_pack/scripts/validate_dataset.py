import json
import os
import sys


def main():
    dataset_path = "data/campusfaq_50k_v1.0.jsonl"
    chunks_path = "artifacts/index/chunks.jsonl"
    output_path = "artifacts/dataset_validation.json"

    # Ensure artifacts directory exists
    os.makedirs("artifacts", exist_ok=True)

    errors = []
    stats = {
        "total_records": 0,
        "intents": set(),
        "splits": {"train": 0, "val": 0, "test": 0},
        "answerable_with_evidence": 0,
        "unsupported_without_evidence": 0
    }
    
    # 1. Load knowledge chunks
    valid_chunk_ids = set()
    if not os.path.exists(chunks_path):
        errors.append(f"Knowledge chunks file missing: {chunks_path}")
    else:
        with open(chunks_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                try:
                    chunk = json.loads(line.strip())
                    valid_chunk_ids.add(chunk.get("chunk_id"))
                except json.JSONDecodeError:
                    errors.append(f"Malformed JSON in chunks file at line {line_idx+1}")

    # 2. Load and validate dataset
    record_ids = set()
    
    if not os.path.exists(dataset_path):
        errors.append(f"Dataset file missing: {dataset_path}")
        report = {"status": "failed", "errors": errors, "stats": {k: list(v) if isinstance(v, set) else v for k, v in stats.items()}}
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print("Dataset missing.")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            stats["total_records"] += 1
            
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"Malformed JSON in dataset at line {line_idx+1}")
                continue

            rec_id = record.get("id")
            if not rec_id:
                errors.append(f"Missing id at line {line_idx+1}")
            elif rec_id in record_ids:
                errors.append(f"Duplicate record ID: {rec_id}")
            else:
                record_ids.add(rec_id)
                
            query = record.get("query")
            if not query:
                errors.append(f"Missing query for record {rec_id}")
                
            intent = record.get("intent")
            if not intent:
                errors.append(f"Missing intent for record {rec_id}")
            else:
                stats["intents"].add(intent)
                
            split = record.get("split")
            if split in stats["splits"]:
                stats["splits"][split] += 1
            else:
                errors.append(f"Invalid split '{split}' for record {rec_id}")
                
            answerable = record.get("answerable", True)
            evidence = record.get("evidence", [])
            is_unsupported = intent == "unsupported_or_unknown"
            
            if answerable:
                if not evidence and not is_unsupported:
                    errors.append(f"Answerable record {rec_id} is missing evidence")
                else:
                    stats["answerable_with_evidence"] += 1
            else:
                if evidence:
                    errors.append(f"Unsupported/unanswerable record {rec_id} should not contain evidence")
                else:
                    stats["unsupported_without_evidence"] += 1

            for ev in evidence:
                chunk_id = ev.get("chunk_id")
                if chunk_id not in valid_chunk_ids:
                    errors.append(f"Evidence chunk ID '{chunk_id}' in record {rec_id} not found in {chunks_path}")

    # Removed strict length checks
    expected_intents = {
        "course_subject_info", "course_code_lookup", "course_credits", "course_prerequisite",
        "course_objectives", "course_outcomes", "semester_subjects", "semester_credits",
        "curriculum_structure", "elective_information", "laboratory_information",
        "project_information", "academic_calendar", "exam_schedule", "exam_rules",
        "attendance_rules", "grading_rules", "promotion_rules", "faculty_department_info",
        "office_contact_info", "student_services", "academic_process", "document_location",
        "unsupported_or_unknown"
    }
    
    unexpected = stats["intents"] - expected_intents
    if unexpected:
        errors.append(f"Unexpected intent labels found: {unexpected}")

    stats["intents"] = list(stats["intents"])

    report = {
        "status": "passed" if not errors else "failed",
        "errors": errors[:100],  # cap at 100 to prevent huge JSONs
        "total_errors": len(errors),
        "stats": stats
    }
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
        
    if errors:
        print(f"Validation failed with {len(errors)} errors. Check {output_path} for details.")
        for err in errors[:10]:
            print(" -", err)
        sys.exit(1)
    else:
        print("Validation passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
