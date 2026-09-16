"""Build a 1,000,000-row dataset strictly from 100% Pure Education and Academic Datasets.
All datasets are sourced from Hugging Face:
1. StackExchange Academia (academia.stackexchange.com): University admissions, degrees, GPA, professors, research
2. StackExchange Computer Science & CS Theory (cs, cstheory): Algorithms, data structures, computation
3. StackExchange Physics (physics): Mechanics, circuits, electrodynamics, thermodynamics, quantum
4. StackExchange Chemistry & Biology (chemistry, biology): Organic/inorganic chemistry, genetics, cell biology
5. StackExchange Statistics (stats): Probability, regression, mathematical statistics, inference
6. StackExchange Mathematics (math): College calculus, linear algebra, discrete math, analysis
7. SetFit Student Question Categories (SetFit/student-question-categories): Real student STEM queries

Zero non-education datasets. Yahoo Answers and OS troubleshooting tech dumps have been completely removed.
"""
import gzip
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
CACHE_DIR = DATA_DIR / "cache" / "hf_downloads"

for d in [DATA_DIR, PROCESSED_DIR, REPORTS_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TARGET_ROWS = 1_000_000

COLLEGE_INTENTS = [
    "college_academics_and_admissions",
    "computer_science_and_engineering",
    "mathematics_and_calculus",
    "physics_and_engineering_sciences",
    "chemistry_and_life_sciences",
    "campus_life_and_student_services",
    "curriculum_syllabi_and_regulations"
]

def clean_question_text(texts: list) -> str:
    """Format title and optional body snippet into clean academic question."""
    if not texts or len(texts) == 0:
        return ""
    title = str(texts[0]).strip().replace("\n", " ")
    body = str(texts[1]).strip().replace("\n", " ") if len(texts) > 1 else ""
    if len(title) < 45 and body:
        return (title + " - " + body[:140]).strip()
    return title

def load_academia_corpus() -> pd.DataFrame:
    """Load StackExchange Academia (34,331 university & college inquiries)."""
    p = CACHE_DIR / "academia.jsonl.gz"
    if not p.exists():
        print(f"[Dataset] {p.name} not found, skipping...")
        return pd.DataFrame()

    print(f"[Dataset] Loading University Academia & Higher Education from {p.name}...")
    records = []
    with gzip.open(p, "rt", encoding="utf-8") as gz:
        for line in gz:
            item = json.loads(line)
            q = clean_question_text(item.get("texts", []))
            if len(q) < 6:
                continue
            tags = [str(t).lower() for t in item.get("tags", [])]
            tag_str = " ".join(tags)
            q_lower = q.lower()

            if any(w in tag_str or w in q_lower for w in ["curriculum", "syllabus", "credit", "prerequisite", "grading", "exam", "grade", "gpa"]):
                intent = "curriculum_syllabi_and_regulations"
            elif any(w in tag_str or w in q_lower for w in ["housing", "hostel", "dorm", "scholarship", "funding", "tuition", "fee", "library", "campus"]):
                intent = "campus_life_and_student_services"
            else:
                intent = "college_academics_and_admissions"

            records.append({
                "question": q,
                "intent": intent,
                "source": "Hugging Face (StackExchange Academia QA Corpus)"
            })

    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} university academic & higher education questions.")
    return df

def load_cs_corpus() -> pd.DataFrame:
    """Load Computer Science and CS Theory StackExchange (48,956 questions)."""
    records = []
    for fn, src in [
        ("cs.jsonl.gz", "StackExchange Computer Science QA"),
        ("cstheory.jsonl.gz", "StackExchange Theoretical Computer Science QA")
    ]:
        p = CACHE_DIR / fn
        if not p.exists():
            continue
        print(f"[Dataset] Loading Computer Science Education from {fn}...")
        with gzip.open(p, "rt", encoding="utf-8") as gz:
            for line in gz:
                item = json.loads(line)
                q = clean_question_text(item.get("texts", []))
                if len(q) < 6:
                    continue
                records.append({
                    "question": q,
                    "intent": "computer_science_and_engineering",
                    "source": f"Hugging Face ({src})"
                })
    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} Computer Science questions.")
    return df

def load_physics_corpus() -> pd.DataFrame:
    """Load Physics StackExchange (173,307 questions)."""
    p = CACHE_DIR / "physics.jsonl.gz"
    if not p.exists():
        return pd.DataFrame()

    print(f"[Dataset] Loading Physics & Engineering Sciences from {p.name}...")
    records = []
    with gzip.open(p, "rt", encoding="utf-8") as gz:
        for line in gz:
            item = json.loads(line)
            q = clean_question_text(item.get("texts", []))
            if len(q) < 6:
                continue
            records.append({
                "question": q,
                "intent": "physics_and_engineering_sciences",
                "source": "Hugging Face (StackExchange Physics QA Corpus)"
            })
    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} Physics questions.")
    return df

def load_chemistry_biology_corpus() -> pd.DataFrame:
    """Load Chemistry and Biology StackExchange (58,953 questions)."""
    records = []
    for fn, src in [
        ("chemistry.jsonl.gz", "StackExchange Chemistry QA"),
        ("biology.jsonl.gz", "StackExchange Biology QA")
    ]:
        p = CACHE_DIR / fn
        if not p.exists():
            continue
        print(f"[Dataset] Loading Chemistry/Biology Sciences from {fn}...")
        with gzip.open(p, "rt", encoding="utf-8") as gz:
            for line in gz:
                item = json.loads(line)
                q = clean_question_text(item.get("texts", []))
                if len(q) < 6:
                    continue
                records.append({
                    "question": q,
                    "intent": "chemistry_and_life_sciences",
                    "source": f"Hugging Face ({src})"
                })
    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} Chemistry & Life Sciences questions.")
    return df

def load_stats_corpus() -> pd.DataFrame:
    """Load Statistics & Probability StackExchange (173,466 questions)."""
    p = CACHE_DIR / "stats.jsonl.gz"
    if not p.exists():
        return pd.DataFrame()

    print(f"[Dataset] Loading Statistics & Probability Education from {p.name}...")
    records = []
    with gzip.open(p, "rt", encoding="utf-8") as gz:
        for line in gz:
            item = json.loads(line)
            q = clean_question_text(item.get("texts", []))
            if len(q) < 6:
                continue
            tags = [str(t).lower() for t in item.get("tags", [])]
            tag_str = " ".join(tags)
            if any(w in tag_str for w in ["machine-learning", "deep-learning", "neural-networks", "python", "r"]):
                intent = "computer_science_and_engineering"
            else:
                intent = "mathematics_and_calculus"
            records.append({
                "question": q,
                "intent": intent,
                "source": "Hugging Face (StackExchange CrossValidated Stats QA)"
            })
    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} Statistics questions.")
    return df

def load_student_stem_questions() -> pd.DataFrame:
    """Load SetFit/student-question-categories (117,487 student curriculum questions)."""
    p = CACHE_DIR / "student_questions.parquet"
    if not p.exists():
        return pd.DataFrame()

    print(f"[Dataset] Loading STEM student curriculum questions from {p.name}...")
    table = pq.read_table(p)
    df = table.to_pandas()
    label_map = {
        "Maths": "mathematics_and_calculus",
        "Physics": "physics_and_engineering_sciences",
        "Chemistry": "chemistry_and_life_sciences",
        "Biology": "chemistry_and_life_sciences"
    }
    df["intent"] = df["label_text"].map(label_map).fillna("mathematics_and_calculus")
    df["question"] = df["text"].fillna("").astype(str).str.strip().str.replace("\n", " ")
    df = df[df["question"].str.len() > 5].copy()
    df["source"] = "Hugging Face (SetFit/student-question-categories)"
    print(f"  Loaded {len(df):,} student STEM questions.")
    return df[["question", "intent", "source"]]

def load_math_corpus(needed_samples: int) -> pd.DataFrame:
    """Load sample from Mathematics StackExchange (up to needed_samples from 1.2M available)."""
    p = CACHE_DIR / "math.jsonl.gz"
    if not p.exists():
        print(f"[Dataset] {p.name} not found, skipping...")
        return pd.DataFrame()

    print(f"[Dataset] Loading College Mathematics & Calculus from {p.name} (target {needed_samples:,})...")
    records = []
    with gzip.open(p, "rt", encoding="utf-8") as gz:
        for line in gz:
            item = json.loads(line)
            q = clean_question_text(item.get("texts", []))
            if len(q) < 6:
                continue
            records.append({
                "question": q,
                "intent": "mathematics_and_calculus",
                "source": "Hugging Face (StackExchange Mathematics QA Corpus)"
            })
            if len(records) >= needed_samples + 20_000:
                break
    df = pd.DataFrame(records)
    print(f"  Loaded {len(df):,} College Mathematics & Calculus questions.")
    return df

def build_dataset():
    t0 = time.time()
    print("=" * 70)
    print("BUILDING 1,000,000 DATASET STRICTLY FROM PURE EDUCATION DATASETS")
    print("=" * 70)

    academia_df = load_academia_corpus()
    cs_df = load_cs_corpus()
    physics_df = load_physics_corpus()
    chem_bio_df = load_chemistry_biology_corpus()
    stats_df = load_stats_corpus()
    student_df = load_student_stem_questions()

    base_dfs = [academia_df, cs_df, physics_df, chem_bio_df, stats_df, student_df]
    base_df = pd.concat([d for d in base_dfs if len(d) > 0], ignore_index=True)
    base_df["_clean"] = base_df["question"].str.strip().str.lower()
    base_df = base_df.drop_duplicates(subset=["_clean"]).drop(columns=["_clean"]).reset_index(drop=True)
    print(f"\n[Dataset] Unique education questions before math fill: {len(base_df):,}")

    needed_math = max(0, TARGET_ROWS - len(base_df))
    print(f"[Dataset] Fetching {needed_math:,} College Math queries to reach exactly {TARGET_ROWS:,} rows...")
    math_df = load_math_corpus(needed_math)

    full_df = pd.concat([base_df, math_df], ignore_index=True)
    full_df["_clean"] = full_df["question"].str.strip().str.lower()
    full_df = full_df.drop_duplicates(subset=["_clean"]).drop(columns=["_clean"]).reset_index(drop=True)

    if len(full_df) > TARGET_ROWS:
        print(f"[Dataset] Stratified trimming down to exactly {TARGET_ROWS:,} rows...")
        full_df = full_df.groupby("intent", group_keys=False).apply(
            lambda x: x.sample(n=min(len(x), int(TARGET_ROWS * (len(x) / len(full_df)) + 100)), random_state=42),
            include_groups=True
        ).sample(n=TARGET_ROWS, random_state=42).reset_index(drop=True)

    full_df["id"] = range(1, len(full_df) + 1)
    print(f"\n[Dataset] Final Pure Education Dataset Size: {len(full_df):,} rows")
    print("[Dataset] Category Breakdown for Student AI Chatbot:")
    dist = full_df["intent"].value_counts().to_dict()
    for intent, count in sorted(dist.items(), key=lambda x: -x[1]):
        pct = (count / len(full_df)) * 100
        print(f"  {intent:38s}: {count:,} ({pct:.1f}%)")

    # Save master Parquet file
    master_parquet = DATA_DIR / "huge_nlp_dataset.parquet"
    print(f"\n[Dataset] Saving master college dataset to {master_parquet}...")
    full_df.to_parquet(master_parquet, index=False, compression="snappy")
    print(f"  Saved master dataset ({master_parquet.stat().st_size / (1024*1024):.1f} MB)")

    # Generate Train (80%) / Val (10%) / Test (10%) splits
    shuffled = full_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    n = len(shuffled)
    train_end = int(0.80 * n)
    val_end = int(0.90 * n)

    train_df = shuffled.iloc[:train_end]
    val_df = shuffled.iloc[train_end:val_end]
    test_df = shuffled.iloc[val_end:]

    print(f"\n[Dataset] Splits: Train={len(train_df):,}, Val={len(val_df):,}, Test={len(test_df):,}")
    train_df.to_parquet(PROCESSED_DIR / "train.parquet", index=False, compression="snappy")
    val_df.to_parquet(PROCESSED_DIR / "val.parquet", index=False, compression="snappy")
    test_df.to_parquet(PROCESSED_DIR / "test.parquet", index=False, compression="snappy")

    # High-performance CSV subsets
    sample_train = train_df.groupby("intent", group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), 4000), random_state=42),
        include_groups=True
    )
    sample_val = val_df.groupby("intent", group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), 500), random_state=42),
        include_groups=True
    )
    sample_test = test_df.groupby("intent", group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), 500), random_state=42),
        include_groups=True
    )

    sample_train.to_csv(PROCESSED_DIR / "train.csv", index=False)
    sample_val.to_csv(PROCESSED_DIR / "val.csv", index=False)
    sample_test.to_csv(PROCESSED_DIR / "test.csv", index=False)

    intents_export = sample_train[["id", "question", "intent"]].copy()
    intents_export["course"] = ""
    intents_export["course_code"] = ""
    intents_export["branch"] = ""
    intents_export["semester"] = ""
    intents_export["unit"] = ""
    intents_export.to_csv(DATA_DIR / "intents.csv", index=False)
    print(f"  Exported {len(intents_export):,} sample rows to {DATA_DIR / 'intents.csv'}")

    lengths = full_df["question"].str.split().str.len()
    stats = {
        "dataset_name": "100% Pure Education & Academic College Chatbot Dataset",
        "domain": "College / University Student Academic & STEM Education",
        "sources": [
            "Hugging Face (StackExchange Academia - Higher Education & Admissions)",
            "Hugging Face (StackExchange CS & CS Theory - Computer Science Education)",
            "Hugging Face (StackExchange Physics - Physics & Engineering Sciences)",
            "Hugging Face (StackExchange Chemistry & Biology - Natural & Life Sciences)",
            "Hugging Face (StackExchange Stats - Statistics & Probability)",
            "Hugging Face (StackExchange Math - Higher Mathematics & Calculus)",
            "Hugging Face (SetFit/student-question-categories - Real Student STEM Inquiries)"
        ],
        "is_synthetic": False,
        "synthetic_rows": 0,
        "non_educational_datasets_removed": True,
        "total_samples": len(full_df),
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "num_classes": len(dist),
        "classes": sorted(list(dist.keys())),
        "class_distribution": dist,
        "text_statistics": {
            "avg_word_count": round(float(lengths.mean()), 2),
            "median_word_count": int(lengths.median()),
            "min_word_count": int(lengths.min()),
            "max_word_count": int(lengths.max())
        },
        "target_audience": "College & University Students, Academic Staff, Higher Education",
        "splits_info": {
            "train_parquet": "data/processed/train.parquet",
            "val_parquet": "data/processed/val.parquet",
            "test_parquet": "data/processed/test.parquet",
            "master_parquet": "data/huge_nlp_dataset.parquet"
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    stats_file = DATA_DIR / "dataset_statistics.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"[Dataset] Saved pure education dataset statistics to {stats_file}")
    print("=" * 70)
    print("SUCCESS: 1,000,000 PURE EDUCATION DATASET BUILT & INDEXED")
    print(f"Time elapsed: {time.time() - t0:.1f}s")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    build_dataset()
