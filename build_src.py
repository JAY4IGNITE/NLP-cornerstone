import os
from pathlib import Path

base = Path(r"c:\Users\ramuv\NLP-cornerstone\src")
dirs = [
    "preprocessing",
    "classification",
    "retrieval",
    "evaluation"
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)
    with open(base / d / "__init__.py", "w") as f:
        pass
with open(base / "__init__.py", "w") as f:
    pass

# src/preprocessing/text_preprocessor.py
with open(base / "preprocessing/text_preprocessor.py", "w", encoding="utf-8") as f:
    f.write("""import re

def preprocess_query(text: str) -> str:
    \"\"\"Domain-aware text normalization.\"\"\"
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\\s]', '', text)
    text = re.sub(r'\\s+', ' ', text)
    return text.strip()
""")

# src/classification/train.py
with open(base / "classification/train.py", "w", encoding="utf-8") as f:
    f.write("""import os
import sys
import time
import json
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.preprocessing.text_preprocessor import preprocess_query

DATASET_PATH = BASE_DIR / "data/benchmark/CampusFAQ-50K-v1.0/data/campusfaq_50k_v1.0.csv"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_intent_model():
    print("[Trainer] Loading synthetic CampusFAQ-50K benchmark...")
    df = pd.read_csv(DATASET_PATH)
    
    # Preprocessing
    print("[Trainer] Preprocessing queries...")
    df['query'] = df['query'].fillna("").astype(str)
    
    # Verify column names
    query_col = 'query' if 'query' in df.columns else 'question'
    
    # Check for predefined splits
    if 'split' in df.columns:
        train_df = df[df['split'] == 'train']
        test_df = df[df['split'] == 'test']
    else:
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=0.1, random_state=42, stratify=df['intent'])
        
    X_train = [preprocess_query(q) for q in train_df[query_col]]
    X_test = [preprocess_query(q) for q in test_df[query_col]]
    
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(train_df['intent'])
    y_test = label_encoder.transform(test_df['intent'])
    
    print("[Trainer] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("[Trainer] Training Logistic Regression...")
    clf = LogisticRegression(C=2.5, max_iter=500, random_state=42, solver='lbfgs')
    clf.fit(X_train_vec, y_train)
    
    print("[Trainer] Saving models...")
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "intent_classifier.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    
    print("[Trainer] Evaluating...")
    y_pred = clf.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    print(f"Test Accuracy: {acc:.4f}")
    print(report)
    
if __name__ == '__main__':
    train_intent_model()
""")

# src/classification/predict.py
with open(base / "classification/predict.py", "w", encoding="utf-8") as f:
    f.write("""import joblib
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
""")

# src/retrieval/retriever.py
with open(base / "retrieval/retriever.py", "w", encoding="utf-8") as f:
    f.write("""import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.preprocessing.text_preprocessor import preprocess_query

class SemanticRetriever:
    def __init__(self):
        self.knowledge_base = []
        self.kb_vectors = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.load_documents()
        
    def load_documents(self):
        kb_path = BASE_DIR / "data/benchmark/CampusFAQ-50K-v1.0/data/demo_knowledge_chunks.jsonl"
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    doc = json.loads(line)
                    self.knowledge_base.append(doc)
        
        if self.knowledge_base:
            texts = [doc.get('content', doc.get('text', '')) for doc in self.knowledge_base]
            self.kb_vectors = self.vectorizer.fit_transform(texts)
            
    def retrieve(self, query: str, top_k=1):
        if not self.knowledge_base:
            return None, 0.0
            
        q_vec = self.vectorizer.transform([preprocess_query(query)])
        similarities = cosine_similarity(q_vec, self.kb_vectors).flatten()
        best_idx = np.argmax(similarities)
        score = float(similarities[best_idx])
        return self.knowledge_base[best_idx], score
""")

# src/pipeline.py
with open(base / "pipeline.py", "w", encoding="utf-8") as f:
    f.write("""import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.classification.predict import IntentPredictor
from src.retrieval.retriever import SemanticRetriever

class HybridPipeline:
    def __init__(self):
        self.classifier = IntentPredictor()
        self.retriever = SemanticRetriever()
        
    def process_query(self, query: str):
        intent, conf = self.classifier.predict(query)
        evidence, retrieval_score = self.retriever.retrieve(query)
        
        # Abstention logic
        if conf < 0.3 or retrieval_score < 0.1:
            return {
                "query": query,
                "intent": intent,
                "confidence": conf,
                "response": "I could not find sufficiently reliable information in the available university knowledge base.",
                "evidence": None,
                "source": None
            }
            
        content = evidence.get('content', evidence.get('text', str(evidence))) if evidence else "No details found."
        source = evidence.get('source', evidence.get('document_id', 'Unknown')) if evidence else 'Unknown'
        
        response = f"Based on {source} ({intent}): {content}"
        
        return {
            "query": query,
            "intent": intent,
            "confidence": conf,
            "response": response,
            "evidence": content,
            "source": source
        }
""")

print("Source scaffolding complete.")
