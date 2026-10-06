import re

path = 'c:/Users/ramuv/NLP-cornerstone/backend/rag/reranker.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'    def _fallback_rerank.*?(?=    def rerank)', re.DOTALL)

replacement = """    def _fallback_rerank(self, query: str, chunks: List[Dict[str, Any]], intent: Optional[str] = None) -> List[Dict[str, Any]]:
        \"\"\"Aggressive local fallback reranker prioritizing lexical match to overcome random dense vectors.\"\"\"
        query_words = set(query.lower().split())
        scored = []

        intent_keywords = {
            "prerequisites": ["prerequisite", "prereq", "prior"],
            "course_outcome": ["outcome", "co", "learning outcome"],
            "course_objectives": ["objective", "aim", "goal"],
            "credits": ["credit", "l: ", "t: ", "p: "],
            "units": ["unit", "module"],
            "unit_topics": ["unit", "module", "topics"],
            "academic_regulations": ["attendance", "grading", "regulation", "cia", "credit requirements"]
        }

        target_kws = intent_keywords.get(intent or "", [])

        for orig_idx, chunk in enumerate(chunks):
            text = (chunk.get("text", "") + " " + (chunk.get("section_heading") or chunk.get("section") or "")).lower()
            text_words = set(text.split())

            # Keyword overlap Jaccard
            overlap = len(query_words.intersection(text_words))
            jaccard = overlap / max(1, len(query_words.union(text_words)))

            # Section intent keyword match bonus
            intent_bonus = 0.0
            for kw in target_kws:
                if kw in text:
                    intent_bonus = 0.60
                    break

            # Exact phrase bonus - huge bump to ensure exact matches bubble to the top
            phrase_bonus = 0.50 if any(w in text for w in query_words if len(w) > 4) else 0.0

            # Course code exact match bonus
            code_bonus = 0.40 if chunk.get("course_code") and chunk["course_code"].lower() in query.lower() else 0.0

            # Base retrieval score - heavily discounted since offline dense is random
            ret_score = chunk.get("retrieval_score", 0.5)

            # Heavily weight Jaccard and explicit lexical overlap
            score = round(min(1.0, 0.1 * ret_score + 0.60 * jaccard + phrase_bonus + code_bonus + intent_bonus), 4)

            item = dict(chunk)
            item["rerank_score"] = score
            item["original_rank"] = orig_idx + 1
            scored.append(item)

        # Sort by rerank score descending
        scored = sorted(scored, key=lambda x: x["rerank_score"], reverse=True)
        for new_rank, item in enumerate(scored, 1):
            item["new_rank"] = new_rank
        return scored[:self.top_k]

"""

new_content = pattern.sub(replacement, content)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated reranker.py")
