import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.core.preprocessing.text_preprocessor import preprocess_query

def test_preprocessing():
    assert preprocess_query("Hello World!") == "hello world"
    assert preprocess_query("   extra   spaces   ") == "extra spaces"
    assert preprocess_query("") == ""
