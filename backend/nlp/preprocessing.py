"""Domain-aware NLP Preprocessing pipeline.
Preserves university acronyms, course codes, unit numbers, and curriculum entities.
"""
import re
from typing import List, Set
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Protected university entities and acronyms that must not be mutilated or removed
PROTECTED_ENTITIES: Set[str] = {
    "dbms", "os", "cn", "ml", "ai", "dsa", "wt", "se", "cd", "cc",
    "cse", "cs", "it", "ece", "eee", "mech", "civil",
    "cs101", "cs102", "cs201", "cs202", "cs203", "cs204", "cs205", "cs206",
    "cs301", "cs302", "cs303", "cs304", "cs305", "cs306",
    "cs401", "cs402", "cs403", "ma201", "ma202",
    "co1", "co2", "co3", "co4", "co5",
    "unit", "module", "sem", "semester", "credits", "prereq", "prerequisite",
    "sql", "tcp", "udp", "ip", "cpu", "cia", "sgpa", "cgpa", "srs", "uml"
}

# Domain-specific stop words (excluding interrogatives like 'what', 'which', 'how' if they determine intent)
STOP_WORDS: Set[str] = set(stopwords.words("english")) - {
    "what", "which", "how", "who", "where", "why", "before", "after", "not", "all", "between"
}

lemmatizer = WordNetLemmatizer()

class TextPreprocessor:
    def __init__(self, remove_stopwords: bool = False, lemmatize: bool = True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize

    def clean_text(self, text: str) -> str:
        """Lowercase and whitespace normalization."""
        if not text:
            return ""
        text = text.lower()
        # Normalize various quotes and dashes
        text = re.sub(r"[\u2018\u2019]", "'", text)
        text = re.sub(r"[\u201c\u201d]", '"', text)
        text = re.sub(r"[\u2013\u2014]", "-", text)
        # Collapse multiple whitespaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenize preserving alphanumeric course codes, unit specifications, and acronyms."""
        cleaned = self.clean_text(text)
        # Token pattern matches words, hyphenated words, course codes like cs301, unit numbers like unit-3
        tokens = re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+)*\b", cleaned)
        return tokens

    def preprocess(self, text: str) -> str:
        """Full pipeline: clean -> tokenize -> domain filter -> lemmatize -> join."""
        tokens = self.tokenize(text)
        processed_tokens: List[str] = []

        for token in tokens:
            # Check if token is protected
            if token in PROTECTED_ENTITIES:
                processed_tokens.append(token)
                continue

            # Optional stopword removal
            if self.remove_stopwords and token in STOP_WORDS:
                continue

            # Lemmatization
            if self.lemmatize:
                # NLTK lemmatizer works best for nouns/verbs
                lemma = lemmatizer.lemmatize(token)
                processed_tokens.append(lemma)
            else:
                processed_tokens.append(token)

        return " ".join(processed_tokens)

    def clean_tokens(self, text: str) -> List[str]:
        return self.tokenize(self.preprocess(text))

# Default singleton preprocessor for training and inference
preprocessor = TextPreprocessor(remove_stopwords=False, lemmatize=True)
nlp_preprocessor = preprocessor

def preprocess_query(query: str) -> str:
    """Convenience helper for inference queries."""
    return preprocessor.preprocess(query)
