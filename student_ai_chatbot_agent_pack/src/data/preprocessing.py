import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters to NFKC."""
    return unicodedata.normalize('NFKC', text)

def normalize_whitespace(text: str) -> str:
    """Normalize multiple whitespaces into a single space, strip edges."""
    return re.sub(r'\s+', ' ', text).strip()

def normalize_punctuation(text: str) -> str:
    """Normalize common punctuation variations but keep them intact.
    For instance, converting smart quotes to straight quotes."""
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('–', '-').replace('—', '-')
    return text

def remove_control_characters(text: str) -> str:
    """Remove unwanted control characters except typical whitespace."""
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ['\t', '\n', '\r'])

def clean_query(text: str, lowercase: bool = False) -> str:
    """Complete query cleaning pipeline."""
    if not text:
        return ""
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = normalize_punctuation(text)
    if lowercase:
        text = text.lower()
    text = normalize_whitespace(text)
    return text

class LabelEncoder:
    """Simple label encoder to avoid heavy dependencies if possible."""
    def __init__(self):
        self.classes_ = []
        self._class_to_idx = {}
        
    def fit(self, labels: list[str]):
        self.classes_ = sorted(set(labels))
        self._class_to_idx = {c: i for i, c in enumerate(self.classes_)}
        return self
        
    def transform(self, labels: list[str]) -> list[int]:
        return [self._class_to_idx[lbl] for lbl in labels]
        
    def fit_transform(self, labels: list[str]) -> list[int]:
        return self.fit(labels).transform(labels)
        
    def inverse_transform(self, indices: list[int]) -> list[str]:
        return [self.classes_[idx] for idx in indices]
