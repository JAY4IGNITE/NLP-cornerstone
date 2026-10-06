import sys
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
