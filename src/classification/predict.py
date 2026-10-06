import joblib
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
sys.path.insert(0, str(BASE_DIR))
from src.preprocessing.text_preprocessor import preprocess_query

class IntentPredictor:
    def __init__(self):
        self.vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
        self.clf = joblib.load(MODELS_DIR / "intent_classifier.joblib")
        self.label_encoder = joblib.load(MODELS_DIR / "label_encoder.joblib")
        
    def predict(self, query: str):
        q_clean = preprocess_query(query)
        q_vec = self.vectorizer.transform([q_clean])
        pred_idx = self.clf.predict(q_vec)[0]
        probs = self.clf.predict_proba(q_vec)[0]
        confidence = float(np.max(probs))
        intent = self.label_encoder.inverse_transform([pred_idx])[0]
        return intent, confidence
