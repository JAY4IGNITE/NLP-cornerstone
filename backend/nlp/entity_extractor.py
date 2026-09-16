"""Hybrid Entity Extraction Engine.
Combines dictionary lookup, regex pattern matching, string normalization, and fuzzy matching.
Extracts: course, course_code, branch, semester, unit.
"""
import difflib
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.config import DATA_DIR
from backend.utils.logger import logger

ROMAN_NUMERALS = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8
}

WORD_NUMBERS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

class EntityExtractor:
    def __init__(self, courses_file: Optional[Path] = None):
        self.courses_file = Path(courses_file) if courses_file else (DATA_DIR / "courses.json")
        self.courses_db: List[Dict[str, Any]] = []
        self.alias_to_course: Dict[str, Dict[str, Any]] = {}
        self.code_to_course: Dict[str, Dict[str, Any]] = {}
        self.all_alias_strings: List[str] = []
        self.load_courses()

    def load_courses(self):
        if not self.courses_file.exists():
            logger.warning(f"Course file not found at {self.courses_file}")
            return

        try:
            with open(self.courses_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.courses_db = data.get("courses", [])

            for c in self.courses_db:
                code_norm = c["course_code"].upper().replace(" ", "").replace("-", "")
                self.code_to_course[code_norm] = c

                # Register primary course name
                name_norm = c["course_name"].lower().strip()
                self.alias_to_course[name_norm] = c
                self.all_alias_strings.append(name_norm)

                # Register code
                self.alias_to_course[c["course_code"].lower()] = c
                self.all_alias_strings.append(c["course_code"].lower())

                # Register aliases
                for a in c.get("aliases", []):
                    a_norm = a.lower().strip()
                    self.alias_to_course[a_norm] = c
                    self.all_alias_strings.append(a_norm)

            self.all_alias_strings = sorted(list(set(self.all_alias_strings)), key=len, reverse=True)
            logger.info(f"Loaded {len(self.courses_db)} courses and {len(self.alias_to_course)} alias mappings")
        except Exception as e:
            logger.error(f"Failed to load course dictionary: {e}")

    def extract(self, query: str) -> Dict[str, Any]:
        """Extract all curriculum entities from the student query."""
        if not query:
            return {
                "course": None,
                "course_code": None,
                "branch": None,
                "semester": None,
                "unit": None,
                "canonical_course_name": None
            }

        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Regex Extraction for Course Code
        course_code = None
        code_match = re.search(r"\b([A-Za-z]{2,3})\s*[-]?\s*(\d{3})\b", q_clean)
        if code_match:
            raw_code = f"{code_match.group(1).upper()}{code_match.group(2)}"
            if raw_code in self.code_to_course:
                course_code = raw_code

        # 2. Semester Extraction
        semester = None
        # e.g., semester 5, sem 5, 5th semester, sem-5, sem v
        sem_match = re.search(r"\b(?:semester|sem)\s*[-]?\s*([1-8]|i{1,3}|iv|v|vi{1,3}|viii)\b", q_lower)
        if sem_match:
            val = sem_match.group(1)
            semester = int(val) if val.isdigit() else ROMAN_NUMERALS.get(val)
        else:
            ord_match = re.search(r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th)\s*(?:semester|sem)\b", q_lower)
            if ord_match:
                semester = int(ord_match.group(1)[0])

        # 3. Unit Extraction
        unit = None
        # e.g., unit 3, module 3, unit-3, unit iii, 3rd unit
        unit_match = re.search(r"\b(?:unit|module)\s*[-]?\s*([1-5]|i{1,3}|iv|v)\b", q_lower)
        if unit_match:
            val = unit_match.group(1)
            unit = int(val) if val.isdigit() else ROMAN_NUMERALS.get(val)
        else:
            unit_ord = re.search(r"\b(1st|2nd|3rd|4th|5th)\s*(?:unit|module)\b", q_lower)
            if unit_ord:
                unit = int(unit_ord.group(1)[0])

        # 4. Branch Extraction
        branch = None
        if re.search(r"\b(cse|computer science and engineering|computer science|cs)\b", q_lower):
            branch = "CSE"
        elif re.search(r"\b(it|information technology)\b", q_lower):
            branch = "IT"
        elif re.search(r"\b(ece|electronics)\b", q_lower):
            branch = "ECE"

        # 5. Course Name: Dictionary Exact / Substring Matching
        matched_course_obj = None
        matched_alias = None

        if course_code and course_code in self.code_to_course:
            matched_course_obj = self.code_to_course[course_code]
            matched_alias = course_code
        else:
            # Check sorted aliases (longer matches first to avoid partial matches)
            for alias in self.all_alias_strings:
                # Use word boundaries for short acronyms like os, cn, ml, cd, wt, se, ai
                if len(alias) <= 4:
                    pattern = rf"\b{re.escape(alias)}\b"
                else:
                    pattern = rf"{re.escape(alias)}"

                if re.search(pattern, q_lower):
                    matched_course_obj = self.alias_to_course[alias]
                    matched_alias = alias
                    break

            # 6. Fuzzy Matching Fallback if no exact match found
            if not matched_course_obj:
                words = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", q_lower) if w not in {"what", "which", "give", "tell", "explain", "semester", "topics", "syllabus"}]
                for word in words:
                    close_matches = difflib.get_close_matches(word, self.all_alias_strings, n=1, cutoff=0.82)
                    if close_matches:
                        matched_alias = close_matches[0]
                        matched_course_obj = self.alias_to_course[matched_alias]
                        break

        course_name = None
        canonical_name = None
        if matched_course_obj:
            canonical_name = matched_course_obj["course_name"]
            course_code = matched_course_obj["course_code"]
            # Default branch and semester from course if not explicitly stated
            if not semester:
                semester = matched_course_obj.get("semester")
            if not branch:
                branch = matched_course_obj.get("branch")
            # Present matched acronym or canonical name
            course_name = matched_alias.upper() if len(matched_alias or "") <= 4 else canonical_name

        return {
            "course": course_name,
            "canonical_course_name": canonical_name,
            "course_code": course_code,
            "branch": branch,
            "semester": semester,
            "unit": unit
        }

entity_extractor = EntityExtractor()
