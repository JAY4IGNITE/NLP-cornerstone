import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from backend.core.preprocessing.text_preprocessor import preprocess_query

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
