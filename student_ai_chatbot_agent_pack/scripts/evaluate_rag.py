"""End-to-end RAG quality & safety evaluation (TEST_PLAN.md §RAG, PRD §Success).

The headline evaluation for the core mandate — "never fabricate a college-
specific fact." Runs the full pipeline (intent -> retrieval -> grounded
generation -> citation validation -> abstention) over the test split with the
offline extractive provider and reports:

  * Safety (out-of-scope): hallucination rate — the share of out-of-scope
    questions that were ANSWERED instead of abstained. The target is 0.
  * Coverage (in-scope): answer rate and the mean grounding score (share of
    answer tokens found in the cited evidence — extractive answers should be
    ~fully grounded).
  * Integrity: every citation returned is one the retriever actually surfaced
    (no fabricated sources) — asserted on every case.

Offline and deterministic. Honors env RAG_EVAL_LIMIT to cap rows for a quick
run. Writes artifacts/eval/rag_report.{json,md}.
"""

from __future__ import annotations

import json
import os

import _common

from backend.app.core.normalization import tokenize
from backend.app.llm.base import ABSTENTION_MESSAGE
from backend.app.runtime import build_state


def _load_rows() -> list[dict]:
    p = _common.ROOT / "data" / "processed" / "campus_faq.test.jsonl"
    if not p.exists():
        return []
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    limit = os.environ.get("RAG_EVAL_LIMIT")
    if limit and limit.isdigit():
        rows = rows[: int(limit)]
    return rows


def _grounding(answer: str, cited_texts: list[str]) -> float:
    ans = tokenize(answer)
    if not ans:
        return 0.0
    ev: set[str] = set()
    for t in cited_texts:
        ev |= set(tokenize(t))
    return sum(1 for t in ans if t in ev) / len(ans)


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging("WARNING")
    _common.banner("End-to-end RAG evaluation")
    state = build_state(settings)
    rows = _load_rows()
    if not rows:
        _common.fail("missing test split — run scripts/build_dataset.py first")
        return 1
    print(f"  kb={state.kb.size} | provider={state.provider.name} | "
          f"intent={state.intent.backend} | rows={len(rows)}\n")

    in_scope = out_scope = 0
    answered_in = abstained_in = 0
    hallucinated = abstained_oos = 0
    integrity_violations = 0
    grounding_sum = 0.0
    grounding_n = 0

    for r in rows:
        out = state.orchestrator.answer(r["question"])
        retrieved = set(out.retrieved_chunk_ids)
        for c in out.citations:
            if c.chunk_id not in retrieved:
                integrity_violations += 1

        if r.get("out_of_scope"):
            out_scope += 1
            if out.status == "answered":
                hallucinated += 1
            else:
                abstained_oos += 1
        else:
            in_scope += 1
            if out.status == "answered":
                answered_in += 1
                if out.answer.strip() != ABSTENTION_MESSAGE.strip():
                    cited_texts: list[str] = []
                    for cs in out.citations:
                        ch = state.kb.get_chunk(cs.chunk_id)
                        if ch is not None:
                            cited_texts.append(ch.content)
                    grounding_sum += _grounding(out.answer, cited_texts)
                    grounding_n += 1
            else:
                abstained_in += 1

    report = {
        "provider": state.provider.name,
        "rows": len(rows),
        "in_scope": {
            "total": in_scope,
            "answered": answered_in,
            "abstained": abstained_in,
            "answer_rate": round(answered_in / in_scope, 4) if in_scope else 0.0,
            "mean_grounding": round(grounding_sum / grounding_n, 4) if grounding_n else 0.0,
        },
        "out_of_scope": {
            "total": out_scope,
            "abstained": abstained_oos,
            "hallucinated": hallucinated,
            "hallucination_rate": round(hallucinated / out_scope, 4) if out_scope else 0.0,
            "abstention_rate": round(abstained_oos / out_scope, 4) if out_scope else 0.0,
        },
        "citation_integrity_violations": integrity_violations,
    }

    out_dir = _common.artifacts_dir("eval")
    (out_dir / "rag_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# End-to-end RAG evaluation (DEMO_ONLY)", "",
             f"- provider: {state.provider.name} | rows: {len(rows)}",
             f"- **hallucination rate (OOS answered): {report['out_of_scope']['hallucination_rate']}** "
             f"(target 0.0)",
             f"- OOS abstention rate: {report['out_of_scope']['abstention_rate']} | "
             f"citation-integrity violations: {integrity_violations} (target 0)",
             f"- in-scope answer rate: {report['in_scope']['answer_rate']} | "
             f"mean grounding: {report['in_scope']['mean_grounding']}", "",
             "| segment | total | answered | abstained |", "|---|---|---|---|",
             f"| in-scope | {in_scope} | {answered_in} | {abstained_in} |",
             f"| out-of-scope | {out_scope} | {hallucinated} | {abstained_oos} |"]
    (out_dir / "rag_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    _common.ok(f"OOS hallucination_rate={report['out_of_scope']['hallucination_rate']} "
               f"abstention_rate={report['out_of_scope']['abstention_rate']}")
    _common.ok(f"in-scope answer_rate={report['in_scope']['answer_rate']} "
               f"mean_grounding={report['in_scope']['mean_grounding']}")
    _common.ok(f"citation_integrity_violations={integrity_violations}")
    _common.ok(f"wrote rag_report.* to {out_dir.relative_to(_common.ROOT)}")

    # Safety gate: any OOS hallucination or fabricated citation is a hard failure.
    if hallucinated > 0 or integrity_violations > 0:
        _common.fail("SAFETY REGRESSION: hallucinated OOS answer or fabricated citation")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
