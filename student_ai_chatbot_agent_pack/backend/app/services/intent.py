"""Intent classification service.

Primary: a fine-tuned DistilBERT model loaded from ``INTENT_MODEL_DIR`` when
present (produced by scripts/train_intent.py). Fallback: a deterministic lexical
model over the canonical keyword hints, so the service works with zero training
and fully offline. Both expose ``predict_intent(query) -> IntentPrediction``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from backend.app.core.logging import get_logger
from backend.app.core.normalization import tokenize
from backend.app.models.intents import (
    ABSTAIN_INTENT,
    INTENTS,
    KEYWORDS,
)

logger = get_logger("intent")


@dataclass
class IntentPrediction:
    label: str
    confidence: float
    top3: list[tuple[str, float]]


class LexicalIntentModel:
    """Deterministic keyword-overlap classifier (offline fallback)."""

    backend = "lexical-fallback"

    def __init__(self) -> None:
        # Precompute keyword token sets per intent.
        self._kw = {
            intent: [tuple(tokenize(k)) for k in kws] for intent, kws in KEYWORDS.items()
        }

    def _scores(self, query: str) -> dict[str, float]:
        q_tokens = tokenize(query)
        q_set = set(q_tokens)
        q_join = " ".join(q_tokens)
        scores: dict[str, float] = {}
        for intent in INTENTS:
            score = 0.0
            for phrase in self._kw[intent]:
                if len(phrase) == 1:
                    if phrase[0] in q_set:
                        score += 1.0
                else:
                    # phrase match (bonus) or partial token overlap
                    if " ".join(phrase) in q_join:
                        score += 1.5
                    else:
                        score += 0.4 * len(set(phrase) & q_set) / len(phrase)
            scores[intent] = score
        return scores

    def predict_intent(self, query: str) -> IntentPrediction:
        scores = self._scores(query)
        best = max(scores.values())
        if best <= 0.0:
            # No signal at all -> treat as out of scope.
            return IntentPrediction(ABSTAIN_INTENT, 0.30, [(ABSTAIN_INTENT, 0.30)])
        # softmax over positive scores for a calibrated-ish confidence
        exp = {k: math.exp(v) for k, v in scores.items()}
        total = sum(exp.values())
        probs = sorted(((k, v / total) for k, v in exp.items()), key=lambda kv: -kv[1])
        label, conf = probs[0]
        return IntentPrediction(label=label, confidence=round(conf, 4), top3=probs[:3])


class IntentClassifier:
    def __init__(self, model_dir: str | None = None, max_length: int = 128) -> None:
        self.max_length = max_length
        self._model = None
        self._vectorizer = None
        self._label_encoder = None
        self.backend = "lexical-fallback"
        self._fallback = LexicalIntentModel()
        if model_dir:
            self._try_load(Path(model_dir))

    def _try_load(self, path: Path) -> None:
        if not (path / "model.joblib").exists():
            logger.info("no trained intent model at %s; using lexical fallback", path)
            return
        try:
            import joblib

            self._vectorizer = joblib.load(path / "vectorizer.joblib")
            self._model = joblib.load(path / "model.joblib")
            self._label_encoder = joblib.load(path / "label_encoder.joblib")
            self.backend = "logistic"
            logger.info("loaded fine-tuned classical intent model from %s", path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("failed to load intent model (%s); using fallback", type(exc).__name__)
            self._model = None

    def predict_intent(self, query: str) -> IntentPrediction:
        if self._model is None:
            return self._fallback.predict_intent(query)
        
        X = self._vectorizer.transform([query])
        probs = self._model.predict_proba(X)[0]
        classes = self._label_encoder.classes_
        
        ordered = sorted(
            ((classes[i], float(p)) for i, p in enumerate(probs)), key=lambda kv: -kv[1]
        )
        label, conf = ordered[0]
        return IntentPrediction(label=label, confidence=round(conf, 4), top3=ordered[:3])
