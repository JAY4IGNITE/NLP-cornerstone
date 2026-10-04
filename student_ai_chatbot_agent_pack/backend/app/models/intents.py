"""Canonical intent catalog (DETAILS.md §2).

These 24 labels are frozen for v1. Changing them requires a DECISIONS.md record
plus updates to DATASET.md, training configs, tests and qrels (enforced socially,
and by test_intents.py which pins the list).
"""

from __future__ import annotations

# Order is significant: it defines the classifier label ids.
INTENTS: tuple[str, ...] = (
    "course_registration",
    "exam_schedule",
    "grades_gpa",
    "academic_calendar",
    "graduation_requirements",
    "major_minor",
    "academic_advisor",
    "study_abroad",
    "tutoring_center",
    "attendance_policy",
    "academic_probation",
    "transfer_credits",
    "online_classes",
    "syllabus_request",
    "class_location",
    "tuition_fees",
    "financial_aid",
    "scholarships",
    "payment_deadline",
    "payment_methods",
    "refunds",
    "student_employment",
    "tax_forms",
    "meal_plan_cost",
    "housing_cost",
    "library_hours",
    "parking_permits",
    "dorm_maintenance",
    "housing_application",
    "campus_dining",
    "gym_recreation",
    "student_clubs",
    "health_center",
    "campus_security",
    "it_helpdesk",
    "id_card",
    "transportation",
    "bookstore",
    "career_services",
    "printing_services",
    "admissions_status",
    "campus_tour",
    "orientation",
    "alumni_services",
    "transcript_request",
    "international_students",
    "veteran_services",
    "disability_services",
    "university_history",
    "unsupported_or_unknown",
)

INTENT_SET = frozenset(INTENTS)
INTENT_TO_ID = {label: i for i, label in enumerate(INTENTS)}
ID_TO_INTENT = {i: label for i, label in enumerate(INTENTS)}
NUM_INTENTS = len(INTENTS)

# The label reserved for out-of-scope / unanswerable questions.
ABSTAIN_INTENT = "unsupported_or_unknown"

assert NUM_INTENTS == 50, "the canonical intent catalog must contain exactly 24 labels"


def is_valid_intent(label: str) -> bool:
    return label in INTENT_SET


def require_valid_intent(label: str) -> str:
    if label not in INTENT_SET:
        raise ValueError(f"unknown intent label: {label!r}")
    return label


# One-line human descriptions (used in docs / prompts / demo generation).
DESCRIPTIONS: dict[str, str] = {
    "course_registration": "Information about course registration.",
    "exam_schedule": "Information about exam schedule.",
    "grades_gpa": "Information about grades gpa.",
    "academic_calendar": "Information about academic calendar.",
    "graduation_requirements": "Information about graduation requirements.",
    "major_minor": "Information about major minor.",
    "academic_advisor": "Information about academic advisor.",
    "study_abroad": "Information about study abroad.",
    "tutoring_center": "Information about tutoring center.",
    "attendance_policy": "Information about attendance policy.",
    "academic_probation": "Information about academic probation.",
    "transfer_credits": "Information about transfer credits.",
    "online_classes": "Information about online classes.",
    "syllabus_request": "Information about syllabus request.",
    "class_location": "Information about class location.",
    "tuition_fees": "Information about tuition fees.",
    "financial_aid": "Information about financial aid.",
    "scholarships": "Information about scholarships.",
    "payment_deadline": "Information about payment deadline.",
    "payment_methods": "Information about payment methods.",
    "refunds": "Information about refunds.",
    "student_employment": "Information about student employment.",
    "tax_forms": "Information about tax forms.",
    "meal_plan_cost": "Information about meal plan cost.",
    "housing_cost": "Information about housing cost.",
    "library_hours": "Information about library hours.",
    "parking_permits": "Information about parking permits.",
    "dorm_maintenance": "Information about dorm maintenance.",
    "housing_application": "Information about housing application.",
    "campus_dining": "Information about campus dining.",
    "gym_recreation": "Information about gym recreation.",
    "student_clubs": "Information about student clubs.",
    "health_center": "Information about health center.",
    "campus_security": "Information about campus security.",
    "it_helpdesk": "Information about it helpdesk.",
    "id_card": "Information about id card.",
    "transportation": "Information about transportation.",
    "bookstore": "Information about bookstore.",
    "career_services": "Information about career services.",
    "printing_services": "Information about printing services.",
    "admissions_status": "Information about admissions status.",
    "campus_tour": "Information about campus tour.",
    "orientation": "Information about orientation.",
    "alumni_services": "Information about alumni services.",
    "transcript_request": "Information about transcript request.",
    "international_students": "Information about international students.",
    "veteran_services": "Information about veteran services.",
    "disability_services": "Information about disability services.",
    "university_history": "Information about university history.",
    "unsupported_or_unknown": "Information about unsupported or unknown.",
}

# Keyword hints for the deterministic lexical fallback classifier and for
# DEMO_ONLY query-template generation. NOT authoritative facts — routing cues only.
KEYWORDS: dict[str, list[str]] = {
    "course_registration": ["course registration", "course"],
    "exam_schedule": ["exam schedule", "exam"],
    "grades_gpa": ["grades gpa", "grades"],
    "academic_calendar": ["academic calendar", "academic"],
    "graduation_requirements": ["graduation requirements", "graduation"],
    "major_minor": ["major minor", "major"],
    "academic_advisor": ["academic advisor", "academic"],
    "study_abroad": ["study abroad", "study"],
    "tutoring_center": ["tutoring center", "tutoring"],
    "attendance_policy": ["attendance policy", "attendance"],
    "academic_probation": ["academic probation", "academic"],
    "transfer_credits": ["transfer credits", "transfer"],
    "online_classes": ["online classes", "online"],
    "syllabus_request": ["syllabus request", "syllabus"],
    "class_location": ["class location", "class"],
    "tuition_fees": ["tuition fees", "tuition"],
    "financial_aid": ["financial aid", "financial"],
    "scholarships": ["scholarships", "scholarships"],
    "payment_deadline": ["payment deadline", "payment"],
    "payment_methods": ["payment methods", "payment"],
    "refunds": ["refunds", "refunds"],
    "student_employment": ["student employment", "student"],
    "tax_forms": ["tax forms", "tax"],
    "meal_plan_cost": ["meal plan cost", "meal"],
    "housing_cost": ["housing cost", "housing"],
    "library_hours": ["library hours", "library"],
    "parking_permits": ["parking permits", "parking"],
    "dorm_maintenance": ["dorm maintenance", "dorm"],
    "housing_application": ["housing application", "housing"],
    "campus_dining": ["campus dining", "campus"],
    "gym_recreation": ["gym recreation", "gym"],
    "student_clubs": ["student clubs", "student"],
    "health_center": ["health center", "health"],
    "campus_security": ["campus security", "campus"],
    "it_helpdesk": ["it helpdesk", "it"],
    "id_card": ["id card", "id"],
    "transportation": ["transportation", "transportation"],
    "bookstore": ["bookstore", "bookstore"],
    "career_services": ["career services", "career"],
    "printing_services": ["printing services", "printing"],
    "admissions_status": ["admissions status", "admissions"],
    "campus_tour": ["campus tour", "campus"],
    "orientation": ["orientation", "orientation"],
    "alumni_services": ["alumni services", "alumni"],
    "transcript_request": ["transcript request", "transcript"],
    "international_students": ["international students", "international"],
    "veteran_services": ["veteran services", "veteran"],
    "disability_services": ["disability services", "disability"],
    "university_history": ["university history", "university"],
    "unsupported_or_unknown": ["unsupported or unknown", "unsupported"],
}

