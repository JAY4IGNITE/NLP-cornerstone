"""Optional dataset validation. Skips cleanly when processed data is absent."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.core.config import REPO_ROOT
from backend.app.models.intents import INTENT_TO_ID, INTENTS

DATA_DIR = REPO_ROOT / "data" / "processed"
JSONL_FILES = sorted(DATA_DIR.glob("campus_faq.*.jsonl")) if DATA_DIR.exists() else []

REQUIRED_KEYS = {"id", "question", "intent", "label_id", "out_of_scope"}


@pytest.mark.skipif(not JSONL_FILES, reason="no processed dataset (data/processed/*.jsonl) present")
@pytest.mark.parametrize("path", JSONL_FILES, ids=lambda p: p.name)
def test_dataset_rows_are_well_formed(path: Path):
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            assert REQUIRED_KEYS.issubset(row), f"missing keys in {path.name}: {row.get('id')}"
            assert row["question"].strip(), "question must be non-empty"
            assert row["intent"] in INTENTS, f"unknown intent {row['intent']!r}"
            # label_id must agree with the canonical catalog ordering
            assert row["label_id"] == INTENT_TO_ID[row["intent"]]
            assert isinstance(row["out_of_scope"], bool)
            n += 1
    assert n > 0, f"{path.name} had no rows"


@pytest.mark.skipif(not JSONL_FILES, reason="no processed dataset present")
def test_dataset_splits_present():
    names = {p.name for p in JSONL_FILES}
    # at least a train/test style split exists
    assert any("train" in n for n in names)
