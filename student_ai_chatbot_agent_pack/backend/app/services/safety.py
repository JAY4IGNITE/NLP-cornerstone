"""Pre-generation scope & safety gate (SECURITY_PRIVACY.md §Privacy).

The knowledge base holds only public, approved college information — never
per-student records. So a request for a *specific person's* academic record
(their marks, score, result, GPA, rank, ...) is both unanswerable from the
corpus and privacy-sensitive. Such a query must be refused BEFORE retrieval and
generation, even when the corpus happens to contain topically-related policy
text: otherwise the extractive generator can stitch unrelated policy sentences
into a confident-looking but non-responsive answer (a "grounded but wrong"
failure). The safe, correct response is abstention.

This gate is intentionally narrow — it fires only when a record noun is bound to
a specific person (first-person "my …", a possessive proper name "Jane Doe's …",
or "student <Name> …") — so that genuine *policy* questions ("what grade is a
pass?", "how are grades calculated?") are unaffected.
"""

from __future__ import annotations

import re

# Nouns denoting a personal academic record (as opposed to a public policy).
# Deliberately excludes broad policy words like "attendance"/"credits" unless
# bound to a person via the possessive/first-person patterns below.
_RECORD_NOUNS = {
    "marks", "mark", "score", "scores", "grade", "grades", "gpa", "cgpa",
    "sgpa", "result", "results", "rank", "ranking", "percentage",
    "backlog", "backlogs", "transcript", "attendance",
}

# First-person cues ("my marks", "our result").
_FIRST_PERSON = re.compile(r"\b(my|mine|our)\b", re.IGNORECASE)
# Possessive of a proper name ("Jane Doe's", "Rahul's") — case-sensitive so it
# does not fire on a lower-cased common word.
_NAME_POSSESSIVE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'s\b")
# "student <Name>" / "candidate <Name>" phrasing naming a specific person.
_NAMED_PERSON = re.compile(r"\b(?:student|candidate|classmate|roommate|friend)\s+[A-Z][a-z]+")


def is_private_record_query(query: str) -> bool:
    """True if the query asks for a specific person's private academic record.

    ``query`` should be the normalized (case-preserving) query text.
    """
    tokens = set(re.findall(r"[a-z]+", query.lower()))
    if not tokens & _RECORD_NOUNS:
        return False
    return bool(
        _FIRST_PERSON.search(query)
        or _NAME_POSSESSIVE.search(query)
        or _NAMED_PERSON.search(query)
    )
