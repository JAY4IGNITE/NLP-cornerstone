# Intent evaluation (DEMO_ONLY)

- backend: **lexical-fallback** | test rows: 1200
- accuracy: **0.6725** | macro-F1: **0.6616** | abstain recall: 0.02

| intent | support | precision | recall | f1 |
|---|---|---|---|---|
| course_subject_info | 50 | 0.2396 | 0.46 | 0.3151 |
| course_code_lookup | 50 | 0.4021 | 0.78 | 0.5306 |
| course_credits | 50 | 0.4579 | 0.98 | 0.6242 |
| course_prerequisite | 50 | 0.5778 | 0.52 | 0.5474 |
| course_objectives | 50 | 0.8409 | 0.74 | 0.7872 |
| course_outcomes | 50 | 1.0 | 0.82 | 0.9011 |
| semester_subjects | 50 | 0.7031 | 0.9 | 0.7895 |
| semester_credits | 50 | 1.0 | 0.2 | 0.3333 |
| curriculum_structure | 50 | 0.4526 | 0.86 | 0.5931 |
| elective_information | 50 | 0.9574 | 0.9 | 0.9278 |
| laboratory_information | 50 | 0.6471 | 0.22 | 0.3284 |
| project_information | 50 | 1.0 | 0.86 | 0.9247 |
| academic_calendar | 50 | 0.8056 | 0.58 | 0.6744 |
| exam_schedule | 50 | 0.6471 | 0.88 | 0.7458 |
| exam_rules | 50 | 1.0 | 0.4 | 0.5714 |
| attendance_rules | 50 | 1.0 | 1.0 | 1.0 |
| grading_rules | 50 | 1.0 | 0.8 | 0.8889 |
| promotion_rules | 50 | 1.0 | 0.58 | 0.7342 |
| faculty_department_info | 50 | 0.9677 | 0.6 | 0.7407 |
| office_contact_info | 50 | 0.9231 | 0.96 | 0.9412 |
| student_services | 50 | 1.0 | 0.36 | 0.5294 |
| academic_process | 50 | 0.7463 | 1.0 | 0.8547 |
| document_location | 50 | 0.4557 | 0.72 | 0.5581 |
| unsupported_or_unknown | 50 | 0.25 | 0.02 | 0.037 |
