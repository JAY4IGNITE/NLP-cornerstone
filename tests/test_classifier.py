import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.nlp.intent_classifier import intent_classifier

def test_known_intent():
    res = intent_classifier.predict("What is the minimum attendance required?")
    assert res["intent"] == "attendance_rules"
    assert res["confidence"] > 0.5

def test_ambiguous_query():
    res = intent_classifier.predict("Can you predict my GPA based on my astrology sign?")
    assert res["is_fallback"] == True or res["intent"] == "fallback"

def test_malformed_input():
    res = intent_classifier.predict("!@#$ %^&*")
    assert res["intent"] == "fallback" or res["is_fallback"] == True
