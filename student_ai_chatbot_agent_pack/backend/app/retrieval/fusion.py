"""Deterministic rank fusion (Reciprocal Rank Fusion).

RRF combines the lexical and dense rankings without needing their score scales
to be comparable. The fused score is normalized to (0, 1] so a single
``MIN_FUSED_SCORE`` threshold is interpretable and calibratable.
"""

from __future__ import annotations

from dataclasses import dataclass

RRF_K = 60


@dataclass(frozen=True)
class FusedHit:
    idx: object  # item id (int corpus index or str chunk_id)
    fused_score: float
    dense_score: float
    lexical_score: float
    dense_rank: int | None
    lexical_rank: int | None


def reciprocal_rank_fusion(
    dense_hits: list[tuple[object, float]],
    lexical_hits: list[tuple[object, float]],
    *,
    k: int = RRF_K,
) -> list[FusedHit]:
    dense_rank = {idx: r for r, (idx, _) in enumerate(dense_hits)}
    lexical_rank = {idx: r for r, (idx, _) in enumerate(lexical_hits)}
    dense_score = {idx: s for idx, s in dense_hits}
    lexical_score = {idx: s for idx, s in lexical_hits}

    # Normalize by the best achievable RRF (top rank in both channels).
    max_possible = 2.0 * (1.0 / (k + 1))

    fused: dict[int, float] = {}
    for idx, r in dense_rank.items():
        fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + 1 + r)
    for idx, r in lexical_rank.items():
        fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + 1 + r)

    hits = [
        FusedHit(
            idx=idx,
            fused_score=raw / max_possible,
            dense_score=dense_score.get(idx, 0.0),
            lexical_score=lexical_score.get(idx, 0.0),
            dense_rank=dense_rank.get(idx),
            lexical_rank=lexical_rank.get(idx),
        )
        for idx, raw in fused.items()
    ]
    hits.sort(key=lambda h: (-h.fused_score, h.idx))
    return hits
