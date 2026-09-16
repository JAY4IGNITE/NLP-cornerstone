"""Production Intent Classifier using TF-IDF + Logistic Regression."""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
from backend.config import MODELS_DIR, settings
from backend.nlp.preprocessing import preprocess_query
from backend.utils.logger import logger

class IntentClassifier:
    def __init__(self, models_dir: Optional[Path] = None, threshold: Optional[float] = None):
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.threshold = threshold if threshold is not None else settings.INTENT_CONFIDENCE_THRESHOLD
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.is_loaded = False
        self.load_models()

    def load_models(self):
        vec_path = self.models_dir / "tfidf_vectorizer.joblib"
        clf_path = self.models_dir / "intent_classifier.joblib"
        enc_path = self.models_dir / "label_encoder.joblib"

        if vec_path.exists() and clf_path.exists() and enc_path.exists():
            try:
                self.vectorizer = joblib.load(vec_path)
                self.classifier = joblib.load(clf_path)
                self.label_encoder = joblib.load(enc_path)
                self.is_loaded = True
                logger.info("Successfully loaded TF-IDF vectorizer and Logistic Regression classifier")
            except Exception as e:
                logger.error(f"Error loading intent models: {e}")
                self.is_loaded = False
        else:
            logger.warning("Intent classification model files not found. Run scripts/train_intent_model.py first.")
            self.is_loaded = False

    def predict(self, raw_query: str) -> Dict[str, Any]:
        """Classify raw user query with confidence scoring and fallback thresholding."""
        if not raw_query or not raw_query.strip():
            return {
                "intent": "fallback",
                "confidence": 1.0,
                "raw_intent": "fallback",
                "threshold": self.threshold,
                "is_fallback": True,
                "top_intents": []
            }

        processed_text = preprocess_query(raw_query)

        if not self.is_loaded or self.classifier is None or self.vectorizer is None:
            # Fallback heuristic if models not yet trained on disk
            return {
                "intent": "curriculum_search",
                "confidence": 0.50,
                "raw_intent": "curriculum_search",
                "threshold": self.threshold,
                "is_fallback": False,
                "top_intents": []
            }

        # Vectorize
        X = self.vectorizer.transform([processed_text])
        probabilities = self.classifier.predict_proba(X)[0]
        max_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[max_idx])
        raw_intent = self.label_encoder.inverse_transform([max_idx])[0]

        # Top 3 intents for telemetry
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_intents = [
            {"intent": self.label_encoder.inverse_transform([i])[0], "confidence": round(float(probabilities[i]), 4)}
            for i in top_indices
        ]

        # Threshold check with specialized multi-resource domain router
        is_fallback = False
        final_intent = raw_intent

        lower_q = raw_query.lower()
        campus_keywords = ["hostel", "mess", "curfew", "warden", "leave pass", "room", "food", "laundry", "bus", "transport", "gym", "sports"]
        library_keywords = ["library", "book", "borrow", "ieee", "scopus", "digital library", "reading hall", "overdue fine", "borrower card"]
        scholarship_keywords = ["scholarship", "fee waiver", "financial aid", "nsp", "concession", "tuition waiver", "merit scholarship"]
        placement_keywords = ["placement", "recruitment", "internship", "dream company", "cgpa cutoff", "noc", "t&p", "recruiter", "salary", "ctc"]
        calendar_keywords = ["academic calendar", "semester dates", "exam dates", "mid term date", "vacation", "holiday", "commencement"]
        study_keywords = ["cheat sheet", "quick revision", "formula", "complexity table", "summary notes", "time complexity"]
        regulation_keywords = ["revaluation", "supplementary", "malpractice", "cheating", "arrear", "condonation", "detention", "passing marks", "grading system", "sgpa", "cgpa", "credits required"]

        if any(k in lower_q for k in campus_keywords):
            raw_intent = "campus_services"
            confidence = 0.96
            is_fallback = False
            final_intent = "campus_services"
        elif any(k in lower_q for k in library_keywords):
            raw_intent = "library_services"
            confidence = 0.95
            is_fallback = False
            final_intent = "library_services"
        elif any(k in lower_q for k in scholarship_keywords):
            raw_intent = "scholarships"
            confidence = 0.95
            is_fallback = False
            final_intent = "scholarships"
        elif any(k in lower_q for k in placement_keywords):
            raw_intent = "placements"
            confidence = 0.95
            is_fallback = False
            final_intent = "placements"
        elif any(k in lower_q for k in calendar_keywords):
            raw_intent = "academic_calendar"
            confidence = 0.95
            is_fallback = False
            final_intent = "academic_calendar"
        elif any(k in lower_q for k in study_keywords):
            raw_intent = "study_guides"
            confidence = 0.95
            is_fallback = False
            final_intent = "study_guides"
        elif any(k in lower_q for k in regulation_keywords):
            raw_intent = "academic_regulations"
            confidence = 0.96
            is_fallback = False
            final_intent = "academic_regulations"
        elif confidence < self.threshold:
            final_intent = "fallback"
            is_fallback = True

        return {
            "intent": final_intent,
            "confidence": round(confidence, 4),
            "raw_intent": raw_intent,
            "threshold": self.threshold,
            "is_fallback": is_fallback,
            "top_intents": top_intents,
            "preprocessed_text": processed_text
        }

# Global singleton classifier instance (loaded once on application boot)
intent_classifier = IntentClassifier()
