import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.core.classification.predict import IntentPredictor
from backend.core.retrieval.retriever import SemanticRetriever

class HybridPipeline:
    def __init__(self):
        self.classifier = IntentPredictor()
        self.retriever = SemanticRetriever()
        
    def process_query(self, query: str):
        # Quick greeting/help check before going to classifier
        query_lower = query.strip().lower()
        import re
        
        def has_word(w):
            return bool(re.search(rf"\b{re.escape(w)}\b", query_lower))

        if any(has_word(k) for k in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "who are you"]):
            return {
                "query": query,
                "intent": "greeting",
                "confidence": 1.0,
                "response": "Hello! I am your university chatbot. How can I help you today?",
                "evidence": None,
                "source": None
            }
            
        if any(has_word(k) for k in ["help", "support", "what can you do"]):
            return {
                "query": query,
                "intent": "help",
                "confidence": 1.0,
                "response": "I can help you with course information, curriculum details, academic policies, and general campus questions. What would you like to know?",
                "evidence": None,
                "source": None
            }

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
        
        if intent == "course_code_lookup":
            # Extract just the course code from the content if possible
            import re
            code_match = re.search(r"Course Code:\s*([A-Za-z]+\d+)", content)
            if code_match:
                response = f"The course code is {code_match.group(1)}."
            else:
                response = "I could not find the specific course code."
        else:
            response = f"Based on {source} ({intent}): {content}"
        
        return {
            "query": query,
            "intent": intent,
            "confidence": conf,
            "response": response,
            "evidence": content,
            "source": source
        }
