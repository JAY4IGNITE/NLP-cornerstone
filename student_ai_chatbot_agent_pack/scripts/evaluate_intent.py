"""Intent-classifier evaluation (MODEL_PLAN.md §6, TEST_PLAN.md §Model).

Scores the active intent classifier on the CampusFAQ test split: overall
accuracy, macro-averaged precision/recall/F1, per-intent breakdown, and the
abstain-class recall (does the model route out-of-scope questions to
``unsupported_or_unknown``?). Uses whatever backend the app would use — a
fine-tuned DistilBERT under artifacts/models/intent if present, else the
deterministic lexical fallback — so the numbers reflect real behaviour.

Offline and deterministic. Writes artifacts/eval/intent_report.{json,md}.
"""

from __future__ import annotations

import json
from collections import defaultdict

import _common

from backend.app.core.normalization import normalize_query
from backend.app.models.intents import ABSTAIN_INTENT, INTENTS
from backend.app.services.intent import IntentClassifier

SPLIT_CANDIDATES = ("intent_test.jsonl", "campus_faq.test.jsonl")


def _load_test() -> list[dict]:
    base = _common.ROOT / "data" / "processed"
    for name in SPLIT_CANDIDATES:
        p = base / name
        if p.exists():
            rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
            out = []
            for r in rows:
                text = r.get("text") or r.get("question") or ""
                out.append({
                    "text": normalize_query(text).normalized,
                    "intent": r["intent"],
                    "out_of_scope": bool(r.get("out_of_scope", False)),
                })
            return out
    return []


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging("WARNING")
    _common.banner("Intent classifier evaluation")

    rows = _load_test()
    if not rows:
        _common.fail("no test split found — run scripts/build_dataset.py (and optionally preprocess.py)")
        return 1

    model_dir = settings.path(settings.intent_model_dir)
    clf = IntentClassifier(
        str(model_dir) if (model_dir / "config.json").exists() else None,
        settings.intent_max_length,
    )
    print(f"  backend={clf.backend} | test_rows={len(rows)}\n")

    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)
    correct = 0
    for r in rows:
        pred = clf.predict_intent(r["text"]).label
        gold = r["intent"]
        if pred == gold:
            correct += 1
            tp[gold] += 1
        else:
            fp[pred] += 1
            fn[gold] += 1

    per_intent = {}
    macro_p = macro_r = macro_f = 0.0
    present = [i for i in INTENTS if (tp[i] + fn[i]) > 0]
    for intent in present:
        p, r, f = _prf(tp[intent], fp[intent], fn[intent])
        per_intent[intent] = {"support": tp[intent] + fn[intent],
                              "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}
        macro_p += p
        macro_r += r
        macro_f += f
    n = len(present) or 1
    accuracy = round(correct / len(rows), 4)

    report = {
        "backend": clf.backend,
        "test_rows": len(rows),
        "accuracy": accuracy,
        "macro_precision": round(macro_p / n, 4),
        "macro_recall": round(macro_r / n, 4),
        "macro_f1": round(macro_f / n, 4),
        "abstain_intent": ABSTAIN_INTENT,
        "abstain_recall": per_intent.get(ABSTAIN_INTENT, {}).get("recall", 0.0),
        "per_intent": per_intent,
    }

    out_dir = _common.artifacts_dir("eval")
    (out_dir / "intent_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Intent evaluation (DEMO_ONLY)", "",
             f"- backend: **{clf.backend}** | test rows: {len(rows)}",
             f"- accuracy: **{accuracy}** | macro-F1: **{report['macro_f1']}** | "
             f"abstain recall: {report['abstain_recall']}", "",
             "| intent | support | precision | recall | f1 |", "|---|---|---|---|---|"]
    for intent, m in sorted(per_intent.items(), key=lambda kv: -kv[1]["support"]):
        lines.append(f"| {intent} | {m['support']} | {m['precision']} | {m['recall']} | {m['f1']} |")
    (out_dir / "intent_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    _common.ok(f"accuracy={accuracy} macro_f1={report['macro_f1']} "
               f"abstain_recall={report['abstain_recall']} (backend={clf.backend})")
    _common.ok(f"wrote intent_report.* to {out_dir.relative_to(_common.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
