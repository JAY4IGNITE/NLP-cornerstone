"""Canonical intent catalog (DETAILS.md §2).

These 24 labels are frozen for v1. Changing them requires a DECISIONS.md record
plus updates to DATASET.md, training configs, tests and qrels (enforced socially,
and by test_intents.py which pins the list).
"""

from __future__ import annotations

# Order is significant: it defines the classifier label ids.
INTENTS: tuple[str, ...] = (
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

INTENT_SET = frozenset(INTENTS)
INTENT_TO_ID = {label: i for i, label in enumerate(INTENTS)}
ID_TO_INTENT = {i: label for i, label in enumerate(INTENTS)}
NUM_INTENTS = len(INTENTS)

# The label reserved for out-of-scope / unanswerable questions.
ABSTAIN_INTENT = "unsupported_or_unknown"

assert NUM_INTENTS == 24, "the canonical intent catalog must contain exactly 24 labels"


def is_valid_intent(label: str) -> bool:
    return label in INTENT_SET


def require_valid_intent(label: str) -> str:
    if label not in INTENT_SET:
        raise ValueError(f"unknown intent label: {label!r}")
    return label


# One-line human descriptions (used in docs / prompts / demo generation).
DESCRIPTIONS: dict[str, str] = {
    "course_subject_info": "What a specific course/subject covers.",
    "course_code_lookup": "Map a course name to its code, or a code to its name.",
    "course_credits": "Credit value of a specific course.",
    "course_prerequisite": "Prerequisites required before a course.",
    "course_objectives": "Stated objectives of a course.",
    "course_outcomes": "Course outcomes / learning outcomes.",
    "semester_subjects": "Subjects offered in a given semester.",
    "semester_credits": "Total credits in a given semester.",
    "curriculum_structure": "Overall program/curriculum structure and totals.",
    "elective_information": "Available electives and how to choose them.",
    "laboratory_information": "Laboratory courses and lab requirements.",
    "project_information": "Project / capstone requirements.",
    "academic_calendar": "Academic calendar dates and terms.",
    "exam_schedule": "Examination timetable / schedule.",
    "exam_rules": "Examination rules and regulations.",
    "attendance_rules": "Attendance requirements and policy.",
    "grading_rules": "Grading scheme and computation.",
    "promotion_rules": "Promotion / progression rules across years.",
    "faculty_department_info": "Faculty and department information.",
    "office_contact_info": "Office / administrative contact information.",
    "student_services": "Student services (library, hostel, scholarships, etc.).",
    "academic_process": "Administrative academic procedures (registration, etc.).",
    "document_location": "Where to find an official document.",
    "unsupported_or_unknown": "Out-of-scope, private, or unanswerable questions.",
}

# Keyword hints for the deterministic lexical fallback classifier and for
# DEMO_ONLY query-template generation. NOT authoritative facts — routing cues only.
KEYWORDS: dict[str, list[str]] = {
    "course_subject_info": ["about", "cover", "topics", "syllabus", "description", "subject"],
    "course_code_lookup": ["code", "course code", "subject code", "what is the code"],
    "course_credits": ["credits", "credit", "credit value", "how many credits"],
    "course_prerequisite": ["prerequisite", "prereq", "pre-requisite", "required before", "eligibility for"],
    "course_objectives": ["objective", "objectives", "aim", "goal of the course"],
    "course_outcomes": ["outcome", "outcomes", "learning outcome", "co", "after completing"],
    "semester_subjects": ["semester subjects", "subjects in semester", "sem subjects", "courses in semester", "papers in sem"],
    "semester_credits": ["semester credits", "credits in semester", "sem credits", "total credits in sem"],
    "curriculum_structure": ["curriculum", "structure", "total credits", "program structure", "scheme"],
    "elective_information": ["elective", "electives", "optional course", "open elective", "professional elective"],
    "laboratory_information": ["lab", "laboratory", "practical", "labs"],
    "project_information": ["project", "capstone", "mini project", "major project", "thesis"],
    "academic_calendar": ["calendar", "academic calendar", "term dates", "semester start", "holidays"],
    "exam_schedule": ["exam schedule", "exam timetable", "exam date", "when is the exam", "examination schedule"],
    "exam_rules": ["exam rules", "exam regulation", "examination rules", "malpractice", "re-exam"],
    "attendance_rules": ["attendance", "minimum attendance", "attendance percentage", "condonation"],
    "grading_rules": ["grade", "grading", "gpa", "cgpa", "marks to grade", "grade points"],
    "promotion_rules": ["promotion", "promoted", "detained", "progression", "carry over", "backlog rule"],
    "faculty_department_info": ["faculty", "professor", "hod", "department", "teacher", "who teaches"],
    "office_contact_info": ["contact", "office", "email", "phone", "reach", "helpdesk number"],
    "student_services": ["library", "hostel", "scholarship", "wifi", "canteen", "transport", "services"],
    "academic_process": ["register", "registration", "apply", "procedure", "how to", "process", "form"],
    "document_location": ["where can i find", "download", "where is", "link to", "which document"],
    "unsupported_or_unknown": ["password", "hack", "predict", "my marks", "personal", "weather", "stock"],
}

