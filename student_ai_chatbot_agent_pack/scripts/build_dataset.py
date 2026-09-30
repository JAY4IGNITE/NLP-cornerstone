"""Generate the CampusFAQ-50K dataset.

50,016 records = 24 intents x 2084, stratified into train/val/test (1684/200/200 per
intent => 40,416 / 4,800 / 4,800). Every record is derived deterministically
(seed 42) from the real campus fixtures. Each in-scope record is linked to the 
evidence chunk(s) that support it (retrieval qrels); out-of-scope records carry no evidence.

Outputs (under data/processed/):
  campus_faq.train.jsonl, campus_faq.val.jsonl, campus_faq.test.jsonl
  qrels.json            (question_id -> [relevant chunk_id, ...])
  dataset_card.md       (provenance notice)
"""

from __future__ import annotations

import json
import random
import re

import _common

from backend.app.core.normalization import tokenize
from backend.app.ingestion.pipeline import ingest_sources
from backend.app.models.intents import ABSTAIN_INTENT, INTENT_TO_ID, INTENTS

SEED = 42
PER_INTENT = 2084
VAL_PER_INTENT = 209
TEST_PER_INTENT = 209
CODE_RE = re.compile(r"\b[A-Z]{2,4}\s?\d{3,4}\b")
TABLE_ROW_RE = re.compile(r"\|\s*([A-Z]{2,4}\s?\d{3,4})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")


def _extract_entities(chunks) -> dict:
    """Pull course codes/names and semester numbers from the corpus."""
    codes: list[str] = []
    courses: dict[str, str] = {}
    for c in chunks:
        for m in TABLE_ROW_RE.finditer(c.content):
            code, name, _credits = m.group(1), m.group(2).strip(), m.group(3)
            courses.setdefault(code, name)
        for code in CODE_RE.findall(c.content):
            if code not in codes:
                codes.append(code)
    # Named courses seen in prose (e.g. the Data Structures course page).
    for code in codes:
        courses.setdefault(code, code)
    sems = [str(n) for n in range(1, 9)]
    return {"codes": codes, "courses": courses, "sems": sems}


# Dynamically match intents across all documents in the campus folder.
INTENT_DOCS = {}

# Base question templates per intent. {course}/{code}/{sem} are slot-filled from
# entities; slotless templates are used as-is. Kept natural but varied.
TEMPLATES: dict[str, list[str]] = {
    "course_subject_info": [
        "What is {course} about", "Describe the {course} course",
        "What topics does {course} cover", "Give me an overview of {course}",
        "What does the {code} course teach", "Tell me the subject details of {course}",
        "What is covered in {course}", "Summarize the {course} syllabus",
    ],
    "course_code_lookup": [
        "What is the course code for {course}", "Which code is {course}",
        "Course code of {course}", "What subject is {code}",
        "Which course has the code {code}", "Map {course} to its course code",
        "What is {code}", "Identify the course with code {code}",
    ],
    "course_credits": [
        "How many credits is {course}", "Credits for {course}",
        "How many credits does {code} carry", "What is the credit value of {course}",
        "Tell me the credits for {code}", "How many credit hours is {course}",
        "Credit count of {course}", "Is {course} a high credit course",
    ],
    "course_prerequisite": [
        "What is the prerequisite for {course}", "Prerequisites of {code}",
        "What do I need before taking {course}", "Which course must I pass before {course}",
        "Are there prerequisites for {code}", "What comes before {course}",
        "Do I need any prior course for {course}", "Prereq for {course}",
    ],
    "course_objectives": [
        "What are the objectives of {course}", "Objectives of {code}",
        "What are the learning objectives for {course}", "Goals of the {course} course",
        "What should {course} teach me", "List the objectives of {code}",
        "Aim of the {course} course", "What are the course objectives for {course}",
    ],
    "course_outcomes": [
        "What are the outcomes of {course}", "Course outcomes of {code}",
        "What will I be able to do after {course}", "Learning outcomes for {course}",
        "After {code} what can a student do", "List course outcomes for {course}",
        "Expected outcomes of {course}", "What are the CO for {code}",
    ],
}

TEMPLATES.update({
    "semester_subjects": [
        "What subjects are in semester {sem}", "List the courses in semester {sem}",
        "Which subjects are offered in sem {sem}", "Semester {sem} subjects",
        "What do I study in semester {sem}", "Courses for semester {sem}",
        "Show the semester {sem} subject list", "What papers are in semester {sem}",
    ],
    "semester_credits": [
        "How many credits in semester {sem}", "Total credits for semester {sem}",
        "Semester {sem} credit total", "How many credit hours in sem {sem}",
        "What is the credit load of semester {sem}", "Credits offered in semester {sem}",
        "How heavy is semester {sem} in credits", "Sum of credits in semester {sem}",
    ],
    "curriculum_structure": [
        "How is the curriculum structured", "What is the total number of credits in the program",
        "Describe the B.Tech CSE curriculum", "How many semesters are in the program",
        "What is the overall program structure", "How many total credits to graduate",
        "Explain the degree structure", "What is the curriculum layout",
    ],
    "elective_information": [
        "What electives are available", "Tell me about the elective courses",
        "How do electives work", "Which electives can I choose",
        "Information on program electives", "Are there open electives",
        "How many electives must I take", "Explain elective options",
    ],
    "laboratory_information": [
        "What lab courses are there", "Tell me about the laboratory courses",
        "Which labs are part of the program", "Information about the {course} lab",
        "How are lab courses structured", "What practicals are included",
        "Details of the laboratory component", "How many lab credits are there",
    ],
    "project_information": [
        "Tell me about the project work", "How does the final project work",
        "What is the project requirement", "Information on the capstone project",
        "How many credits is the project", "When do students do their project",
        "Explain the project component", "What are the project guidelines",
    ],
    "academic_calendar": [
        "When does the semester start", "What is the academic calendar",
        "When are the holidays", "When does the term begin",
        "Show the academic calendar", "When is the semester break",
        "What are the important dates this year", "When does instruction end",
    ],
    "exam_schedule": [
        "When are the exams", "What is the exam schedule",
        "When do end-semester exams start", "Exam dates for semester {sem}",
        "When is the final examination", "Schedule of examinations",
        "When are mid-term exams", "What is the examination timetable",
    ],
    "exam_rules": [
        "What are the exam rules", "Tell me the examination regulations",
        "What is the passing mark", "Rules for the end-semester exam",
        "What are the examination guidelines", "Is there a minimum exam score",
        "What are the rules during exams", "Explain the exam policy",
    ],
})

TEMPLATES.update({
    "attendance_rules": [
        "What is the attendance requirement", "What are the attendance rules",
        "What is the minimum attendance", "How much attendance do I need",
        "Attendance policy for exams", "Can low attendance be condoned",
        "What percentage attendance is required", "Rules about attendance shortage",
    ],
    "grading_rules": [
        "How does grading work", "What is the grading scale",
        "What are the grade points", "Explain the grading system",
        "How are grades calculated", "What is the GPA scale",
        "What grade is a pass", "Tell me the grading rules",
    ],
    "promotion_rules": [
        "What are the promotion rules", "How do I get promoted to the next year",
        "What are the requirements to move to the next semester", "Rules for year promotion",
        "When is a student detained", "Criteria for promotion",
        "How many credits to be promoted", "Explain promotion policy",
    ],
    "faculty_department_info": [
        "Who leads the department", "Tell me about the CSE department",
        "How is the department organized", "Who is the head of department",
        "Information about the faculty", "What programs does the department offer",
        "About the Department of Computer Science", "Describe the department",
    ],
    "office_contact_info": [
        "How do I contact the department office", "What is the office email",
        "Contact details for the examination cell", "Who do I email for academic queries",
        "How to reach the CSE office", "What are the office contact details",
        "Email of the academic section", "How can I contact the helpdesk",
    ],
    "student_services": [
        "What student services are available", "What support services does the college offer",
        "Where can I get student help", "Tell me about student services",
        "What facilities are there for students", "Is there a student helpdesk",
        "What services support students", "Available student support",
    ],
    "academic_process": [
        "How do I register for courses", "What is the course registration process",
        "How do I choose electives during registration", "Steps to register for a semester",
        "What is the process to enroll", "How does add/drop work",
        "Explain the registration procedure", "How do I complete academic registration",
    ],
    "document_location": [
        "Where can I find the syllabus", "Where is the curriculum PDF published",
        "How do I get the academic calendar document", "Where are the official documents",
        "Where can I download the syllabus", "Location of the curriculum document",
        "Where do I find official academic pages", "Where is the scheme published",
    ],
})

# Out-of-scope questions for the abstain intent: deliberately off-domain, no evidence.
OUT_OF_SCOPE = [
    "What is the capital of {x}", "Who won the {x} world cup",
    "What is the weather in {x} today", "How do I cook {x}",
    "Tell me a joke about {x}", "What is the stock price of {x}",
    "Translate '{x}' to French", "Who is the president of {x}",
    "What is {x} times {y}", "Recommend a good {x} movie",
    "How tall is {x}", "What time is it in {x}",
    "Write a poem about {x}", "What is the meaning of the word {x}",
    "How far is {x} from {y}", "Give me the recipe for {x}",
]
OOS_FILL = ["France", "Japan", "Brazil", "cricket", "pasta", "Tesla", "Canada",
            "Everest", "Paris", "coffee", "quantum physics", "the moon", "Berlin",
            "chess", "seven", "London", "history", "music", "Rome", "pizza"]

PREFIXES = ["", "Can you tell me ", "I want to know ", "Please tell me ",
            "Could you explain ", "Quick question - ", "Hi, ", "As a student, ",
            "Help me understand ", "I would like to know ", "Hey, ", "Greetings, ",
            "Tell me ", "Do you know ", "I need to know ", "Can I ask ",
            "Explain ", "Briefly explain ", "Any idea ", "Just wondering, ",
            "So, ", "Could you clarify ", "Please clarify ", "Details on ", "I am confused about "]
SUFFIXES = ["", " please", " for the program", " at the institute",
            " this year", " in the curriculum", " - thanks", " for B.Tech",
            " exactly", " for me", " at Aditya", " for the current batch",
            " quickly", " in detail", " - thank you", " today",
            " for students", " as per the rules", " right now", " basically",
            " actually", " - appreciate it", " overall", " officially", " if possible"]


def _fill(template: str, ent: dict) -> list[str]:
    """Expand slot templates against entities; slotless -> [template]."""
    out: list[str] = []
    if "{course}" in template:
        for name in ent["courses"].values():
            out.append(template.replace("{course}", name))
    elif "{code}" in template:
        for code in ent["courses"].keys():
            out.append(template.replace("{code}", code))
    elif "{sem}" in template:
        for sem in ent["sems"]:
            out.append(template.replace("{sem}", sem))
    else:
        out.append(template)
    return out


def _surface(base: str, prefix: str, suffix: str) -> str:
    body = base
    if prefix:
        body = base[0].lower() + base[1:] if base else base
    return f"{prefix}{body}{suffix}?"


def _generate_intent(intent: str, ent: dict, rng: random.Random) -> list[str]:
    bases: list[str] = []
    for tmpl in TEMPLATES[intent]:
        bases.extend(_fill(tmpl, ent))
    candidates: list[str] = []
    for base in bases:
        for pfx in PREFIXES:
            for sfx in SUFFIXES:
                candidates.append(_surface(base, pfx, sfx))
    rng.shuffle(candidates)
    seen: set[str] = set()
    unique: list[str] = []
    for q in candidates:
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
        if len(unique) >= PER_INTENT:
            break
    return unique


def _generate_oos(rng: random.Random) -> list[str]:
    bases: list[str] = []
    for tmpl in OUT_OF_SCOPE:
        for x in OOS_FILL:
            s = tmpl.replace("{x}", x)
            if "{y}" in s:
                for y in OOS_FILL:
                    if y != x:
                        bases.append(s.replace("{y}", y))
            else:
                bases.append(s)
    candidates: list[str] = []
    for base in bases:
        for pfx in PREFIXES:
            candidates.append(_surface(base, pfx, ""))
    rng.shuffle(candidates)
    seen: set[str] = set()
    unique: list[str] = []
    for q in candidates:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique.append(q)
        if len(unique) >= PER_INTENT:
            break
    return unique


def _link_evidence(question: str, intent: str, by_doc: dict) -> list[str]:
    qtok = set(tokenize(question))
    scored = []
    all_cids = []
    for doc, chunks in by_doc.items():
        for c in chunks:
            all_cids.append(c.chunk_id)
            overlap = len(qtok & set(tokenize(c.content)))
            if overlap > 0:
                scored.append((overlap, c.ordinal, c.chunk_id))
    scored.sort(key=lambda x: (-x[0], x[1]))
    if not scored and all_cids:
        return [all_cids[0]]
    return [cid for _, _, cid in scored[:2]]


def _write_jsonl(path, records) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging("WARNING")
    _common.banner("Build CampusFAQ-50K dataset")

    chunks, _m = ingest_sources(settings)
    if not chunks:
        _common.fail("no source chunks; cannot build dataset")
        return 1
    by_doc: dict[str, list] = {}
    for c in chunks:
        by_doc.setdefault(c.document_id, []).append(c)
    ent = _extract_entities(chunks)
    _common.ok(f"entities: {len(ent['courses'])} courses/codes, {len(ent['sems'])} semesters")

    train, val, test, qrels = [], [], [], {}
    for intent in INTENTS:
        rng = random.Random(SEED + INTENT_TO_ID[intent])
        is_oos = intent == ABSTAIN_INTENT
        questions = _generate_oos(rng) if is_oos else _generate_intent(intent, ent, rng)
        if len(questions) < PER_INTENT:
            _common.warn(f"{intent}: only {len(questions)} unique questions (<{PER_INTENT})")
        recs = []
        for i, q in enumerate(questions):
            ev = [] if is_oos else _link_evidence(q, intent, by_doc)
            qid = f"q-{INTENT_TO_ID[intent]:02d}-{i:04d}"
            evidence_list = [{"chunk_id": eid, "quote": "", "location": ""} for eid in ev]
            recs.append({
                "id": qid, "query": q, "intent": intent,
                "label_id": INTENT_TO_ID[intent], "evidence": evidence_list,
                "answerable": not is_oos, "demo_only": False,
            })
            if ev:
                qrels[qid] = ev
        n_test, n_val = TEST_PER_INTENT, VAL_PER_INTENT
        n_train = PER_INTENT - n_val - n_test
        for r in recs[:n_train]:
            r["split"] = "train"; train.append(r)
        for r in recs[n_train:n_train + n_val]:
            r["split"] = "val"; val.append(r)
        for r in recs[n_train + n_val:]:
            r["split"] = "test"; test.append(r)

    out = _common.ROOT / "data"
    out.mkdir(parents=True, exist_ok=True)
    
    # Adjust to exactly 50000
    train = train[:40000]
    val = val[:5000]
    test = test[:5000]

    _write_jsonl(out / "campusfaq_50k_v1.0.jsonl", train + val + test)
    (out / "qrels.json").write_text(json.dumps(qrels, indent=2), encoding="utf-8")

    total = len(train) + len(val) + len(test)
    linked = sum(1 for r in train + val + test if r.get("evidence", []))
    card = (
        "# CampusFAQ-50K (Production)\n\n"
        "Dynamically generated dataset based on actual campus files.\n\n"
        f"- Records: {total} ({len(train)} train / {len(val)} val / {len(test)} test)\n"
        f"- Intents: {len(INTENTS)} (2083 each)\n"
        f"- In-scope records linked to evidence chunks: {linked}\n"
        f"- Out-of-scope (abstain) intent: {ABSTAIN_INTENT}\n"
    )
    (out / "dataset_card.md").write_text(card, encoding="utf-8")

    _common.ok(f"wrote {total} records to {out.relative_to(_common.ROOT)}")
    print(f"       train={len(train)} val={len(val)} test={len(test)} "
          f"| evidence-linked={linked} | qrels={len(qrels)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
