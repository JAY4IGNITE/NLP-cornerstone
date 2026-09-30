import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.preprocessing import clean_query, normalize_punctuation, normalize_whitespace


def test_clean_query():
    assert clean_query("What are the credits for CSE203?") == "What are the credits for CSE203?"
    assert clean_query("how many credits is cse203", lowercase=True) == "how many credits is cse203"
    assert clean_query("CSE-203 credits?") == "CSE-203 credits?"

def test_normalization():
    assert normalize_whitespace("  Tell me about   operating systems  ") == "Tell me about operating systems"
    assert normalize_punctuation("what subjects are there in sem 4‘s curriculum?") == "what subjects are there in sem 4's curriculum?"
