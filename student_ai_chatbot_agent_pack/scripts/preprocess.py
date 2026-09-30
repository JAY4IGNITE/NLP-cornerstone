"""Preprocess CampusFAQ into a clean intent-training view (MODEL_PLAN.md §4).

Reads the generated CampusFAQ splits, applies the same conservative query
normalization used at inference time, drops exact duplicates within a split, and
writes a compact ``{text, label_id, intent, out_of_scope}`` view per split under
data/processed/intent_{train,val,test}.jsonl. Also prints class balance and
length statistics so training/eval start from a known, reproducible input.

Deterministic and offline. Safe to re-run.
"""

from __future__ import annotations

import json
from collections import Counter

import _common

from backend.app.core.normalization import normalize_query
from backend.app.models.intents import INTENT_TO_ID

SPLITS = ("train", "val", "test")


def _load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path, rows) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    _common.configure_logging("WARNING")
    _common.banner("Preprocess 50K intent-training view")
    base = _common.ROOT / "data" / "processed"
    src_file = _common.ROOT / "data" / "campusfaq_50k_v1.0.jsonl"
    
    if not src_file.exists():
        _common.fail(f"Dataset {src_file} missing")
        return 1

    grand_total = 0
    all_rows = _load_jsonl(src_file)
    
    split_rows = {"train": [], "val": [], "test": []}
    for r in all_rows:
        s = r.get("split", "train")
        if s in split_rows:
            split_rows[s].append(r)

    for split in SPLITS:
        rows = split_rows[split]
        seen: set[str] = set()
        out_rows = []
        lengths: list[int] = []
        per_intent: Counter[str] = Counter()
        dropped = 0
        for r in rows:
            text = normalize_query(r["query"]).normalized
            key = text.lower()
            if not text or key in seen:
                dropped += 1
                continue
            seen.add(key)
            intent = r["intent"]
            label_id = INTENT_TO_ID.get(intent)
            if label_id is None:
                _common.fail(f"{split}: label mismatch for record {r.get('id')!r}")
                return 1
            out_rows.append({
                "text": text,
                "label_id": label_id,
                "intent": intent,
                "out_of_scope": bool(r.get("out_of_scope", False)),
            })
            lengths.append(len(text))
            per_intent[intent] += 1

        _write_jsonl(base / f"intent_{split}.jsonl", out_rows)
        grand_total += len(out_rows)
        avg_len = sum(lengths) / len(lengths) if lengths else 0
        n_intents = len(per_intent)
        lo = min(per_intent.values()) if per_intent else 0
        hi = max(per_intent.values()) if per_intent else 0
        _common.ok(
            f"{split}: {len(out_rows)} rows (dropped {dropped} dup/empty) | "
            f"{n_intents} intents [{lo}..{hi}/intent] | avg_len={avg_len:.1f} chars"
        )

    _common.ok(f"wrote intent_* views ({grand_total} rows) to {base.relative_to(_common.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
