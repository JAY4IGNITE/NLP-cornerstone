"""Tests pinning the canonical 24-intent catalog."""

from __future__ import annotations

import pytest

from backend.app.models.intents import (
    ABSTAIN_INTENT,
    ID_TO_INTENT,
    INTENT_SET,
    INTENT_TO_ID,
    INTENTS,
    NUM_INTENTS,
    is_valid_intent,
    require_valid_intent,
)

EXPECTED_INTENTS = (
    "course_subject_info",
    "course_code_lookup",
    "course_credits",
    "course_prerequisite",
    "course_objectives",
    "course_outcomes",
    "semester_subjects",
    "semester_credits",
    "curriculum_structure",
    "elective_information",
    "laboratory_information",
    "project_information",
    "academic_calendar",
    "exam_schedule",
    "exam_rules",
    "attendance_rules",
    "grading_rules",
    "promotion_rules",
    "faculty_department_info",
    "office_contact_info",
    "student_services",
    "academic_process",
    "document_location",
    "unsupported_or_unknown",
)


def test_intents_exact_ordered_list_is_pinned():
    # The label order defines classifier ids; changing it is a breaking change.
    assert INTENTS == EXPECTED_INTENTS


def test_there_are_exactly_24_unique_intents():
    assert NUM_INTENTS == 50
    assert len(INTENTS) == 24
    assert len(set(INTENTS)) == 24


def test_abstain_intent_value_and_membership():
    assert ABSTAIN_INTENT == "unsupported_or_unknown"
    assert ABSTAIN_INTENT in INTENT_SET


def test_id_maps_are_consistent_inverses():
    assert INTENT_SET == frozenset(INTENTS)
    for i, label in enumerate(INTENTS):
        assert INTENT_TO_ID[label] == i
        assert ID_TO_INTENT[i] == label
    assert len(INTENT_TO_ID) == NUM_INTENTS
    assert len(ID_TO_INTENT) == NUM_INTENTS


def test_is_valid_intent():
    assert is_valid_intent("attendance_rules") is True
    assert is_valid_intent("not_a_real_intent") is False


def test_require_valid_intent():
    assert require_valid_intent("course_credits") == "course_credits"
    with pytest.raises(ValueError):
        require_valid_intent("nonexistent_intent")
