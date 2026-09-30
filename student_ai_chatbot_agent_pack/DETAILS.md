# Detailed System Specification

## 1. Canonical user flow

1. User submits a question.
2. API validates request.
3. Text normalization runs.
4. Intent classifier predicts:
   - intent
   - confidence
   - optional entities
5. Query router chooses the retrieval strategy.
6. Hybrid retrieval returns candidate passages.
7. Optional reranker orders candidates.
8. Evidence filter removes chunks failing source/status rules.
9. Generator receives:
   - original question
   - predicted intent
   - approved evidence
   - answer rules
10. Generator returns structured output:
   - answer
   - citations
   - confidence/status
11. Citation validator checks referenced source IDs.
12. API returns answer + trace ID.
13. Audit logger stores safe metadata.

## 2. 24 intent classes

The dataset and classifier MUST use exactly these labels in v1:

1. `course_subject_info`
2. `course_code_lookup`
3. `course_credits`
4. `course_prerequisite`
5. `course_objectives`
6. `course_outcomes`
7. `semester_subjects`
8. `semester_credits`
9. `curriculum_structure`
10. `elective_information`
11. `laboratory_information`
12. `project_information`
13. `academic_calendar`
14. `exam_schedule`
15. `exam_rules`
16. `attendance_rules`
17. `grading_rules`
18. `promotion_rules`
19. `faculty_department_info`
20. `office_contact_info`
21. `student_services`
22. `academic_process`
23. `document_location`
24. `unsupported_or_unknown`

Do not add or rename labels without updating `DECISIONS.md`, `DATASET.md`, training configs, tests, and evaluation qrels.

## 3. Supported answer types

- direct fact
- short list
- procedure
- comparison
- source-location answer
- clarification request
- abstention

## 4. Query normalization

Allowed:

- Unicode normalization
- whitespace normalization
- harmless casing normalization
- punctuation normalization

Do not change words in ways that could alter academic meaning.

Example:
`sem 4 credits?` -> `sem 4 credits?`

Do NOT automatically expand ambiguous abbreviations unless a deterministic campus glossary defines them.

## 5. Entity extraction

MVP entities:

- department
- program
- semester
- academic year
- course code
- course name
- regulation/version
- document type

Entities are optional. A wrong entity should not silently change the factual answer.

## 6. Source precedence

Default precedence, only when all sources are official:

1. current officially approved regulation / circular
2. current curriculum/syllabus document
3. official department page
4. official central academic page
5. archived official source

When source dates/versioning conflict and the correct precedence cannot be established from metadata, abstain and ask the user to clarify.

## 7. Response style

- concise
- student-friendly
- no invented claims
- no unnecessary background
- cite sources
- state uncertainty when evidence is incomplete
- use numbered steps for procedures

## 8. Structured response contract

Conceptual schema:

```json
{
  "status": "answered|abstained|error",
  "answer": "string",
  "citations": [
    {
      "document_id": "string",
      "title": "string",
      "location": "page/section/chunk"
    }
  ],
  "intent": {
    "label": "string",
    "confidence": 0.0
  },
  "trace_id": "string"
}
```
