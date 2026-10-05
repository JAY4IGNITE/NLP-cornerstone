import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.nlp.preprocessing import nlp_preprocessor

def test_empty_input():
    assert nlp_preprocessor.clean_text("") == ""
    assert nlp_preprocessor.preprocess("") == ""

def test_normal_query():
    text = "What is the minimum attendance required?"
    res = nlp_preprocessor.preprocess(text)
    assert "attendance" in res

def test_punctuation():
    text = "Where is the ADD/DROP page?!"
    res = nlp_preprocessor.preprocess(text)
    assert "drop" in res

def test_whitespace():
    text = "  How    do I   register?  "
    res = nlp_preprocessor.clean_text(text)
    assert res == "how do i register?"

def test_mixed_case():
    text = "CS101 Is VERy HARD"
    res = nlp_preprocessor.preprocess(text)
    assert "cs101" in res # preserved entity
    assert "hard" in res
