import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.core.classification.predict import IntentPredictor

def test_classifier_loads():
    predictor = IntentPredictor()
    assert predictor is not None
