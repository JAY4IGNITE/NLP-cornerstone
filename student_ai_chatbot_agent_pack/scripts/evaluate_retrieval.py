"""Hybrid-retrieval evaluation (RAG.md §10, TEST_PLAN.md §Retrieval).

Scores the hybrid retriever (dense + BM25 -> RRF -> evidence filter) against the
dataset qrels: Recall@k, Hit@k, MRR and nDCG@5 over the in-scope test questions,
plus the "silence" rate on out-of-scope questions (they should surface no
evidence and thus drive an abstention downstream).

Caveat, stated honestly: the DEMO qrels were produced by the same token-overlap
linker that attaches evidence during dataset build, so this measures whether the
hybrid retriever recovers those linked chunks — not human-judged relevance. On a
real corpus, replace qrels with human annotations.

Offline and deterministic. Writes artifacts/eval/retrieval_report.{json,md}.
"""

from __future__ import annotations

import json
import math

import _common

from backend.app.core.normalization import normalize_query
from backend.app.runtime import build_state

K_VALUES = (1, 3, 5)


def _load_rows() -> list[dict]:
    p = _common.ROOT / "data" / "processed" / "campus_faq.test.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _load_qrels() -> dict:
    p = _common.ROOT / "data" / "processed" / "qrels.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _ndcg(retrieved: list[str], relevant: set[str], k: int) -> float:
    dcg = 0.0
    for i, cid in enumerate(retrieved[:k]):
        if cid in relevant:
            dcg += 1.0 / math.log2(i + 2)
    ideal = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg else 0.0


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging("WARNING")
    _common.banner("Hybrid retrieval evaluation")
    state = build_state(settings)
    rows = _load_rows()
    qrels = _load_qrels()
    if not rows or not qrels:
        _common.fail("missing test split or qrels — run scripts/build_dataset.py first")
        return 1
    print(f"  kb={state.kb.size} | embed={state.embedder.mode} | "
          f"index={state.index_source} | test_rows={len(rows)}\n")

    recall = {k: 0.0 for k in K_VALUES}
    hit = {k: 0.0 for k in K_VALUES}
    ndcg5 = 0.0
    mrr = 0.0
    scored = 0
    oos_total = 0
    oos_silent = 0

    for r in rows:
        retrieved = state.retrieval.retrieve(normalize_query(r["question"]).normalized).chunk_ids
        if r.get("out_of_scope"):
            oos_total += 1
            if not retrieved:
                oos_silent += 1
            continue
        relevant = set(qrels.get(r["id"], []) or r.get("evidence_chunk_ids", []))
        if not relevant:
            continue
        scored += 1
        # first relevant rank -> reciprocal rank
        rr = 0.0
        for i, cid in enumerate(retrieved):
            if cid in relevant:
                rr = 1.0 / (i + 1)
                break
        mrr += rr
        for k in K_VALUES:
            topk = set(retrieved[:k])
            inter = len(topk & relevant)
            recall[k] += inter / len(relevant)
            hit[k] += 1.0 if inter > 0 else 0.0
        ndcg5 += _ndcg(retrieved, relevant, 5)

    s = scored or 1
    report = {
        "embedding_mode": state.embedder.mode,
        "index_source": state.index_source,
        "in_scope_scored": scored,
        "recall_at_k": {str(k): round(recall[k] / s, 4) for k in K_VALUES},
        "hit_at_k": {str(k): round(hit[k] / s, 4) for k in K_VALUES},
        "mrr": round(mrr / s, 4),
        "ndcg_at_5": round(ndcg5 / s, 4),
        "out_of_scope": {
            "total": oos_total,
            "silent": oos_silent,
            "silence_rate": round(oos_silent / oos_total, 4) if oos_total else 0.0,
        },
        "note": "qrels are linker-derived (DEMO_ONLY); not human relevance judgements",
    }

    out_dir = _common.artifacts_dir("eval")
    (out_dir / "retrieval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Retrieval evaluation (DEMO_ONLY)", "",
             f"- embedding: {state.embedder.mode} | index: {state.index_source} | "
             f"in-scope scored: {scored}",
             f"- MRR: **{report['mrr']}** | nDCG@5: **{report['ndcg_at_5']}** | "
             f"OOS silence rate: {report['out_of_scope']['silence_rate']}", "",
             "| k | recall@k | hit@k |", "|---|---|---|"]
    for k in K_VALUES:
        lines.append(f"| {k} | {report['recall_at_k'][str(k)]} | {report['hit_at_k'][str(k)]} |")
    lines.append(f"\n> {report['note']}")
    (out_dir / "retrieval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    _common.ok(f"recall@5={report['recall_at_k']['5']} hit@5={report['hit_at_k']['5']} "
               f"mrr={report['mrr']} ndcg@5={report['ndcg_at_5']}")
    _common.ok(f"OOS silence rate={report['out_of_scope']['silence_rate']} "
               f"({oos_silent}/{oos_total})")
    _common.ok(f"wrote retrieval_report.* to {out_dir.relative_to(_common.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
