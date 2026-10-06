"""Grounded Answer Generator using NVIDIA NIM LLM with offline factual synthesis fallback.
Enforces strict grounding, source attribution, and anti-hallucination guardrails.
"""
import json
import re
from typing import List, Dict, Any, Optional
import requests

from backend.config import settings
from backend.utils.logger import logger

SYSTEM_PROMPT = """You are the official University Academic Curriculum Assistant.
Your mission is to provide strictly factual, precise, and verified curriculum information to students.

STRICT OPERATIONAL RULES:
1. Grounding: Answer ONLY using facts directly stated in the provided official curriculum context.
2. Anti-Hallucination: Do NOT invent, assume, extrapolate, or guess courses, prerequisites, unit topics, or regulations.
3. Source Citation: You must explicitly cite the course code, document name, and page number for every key statement (e.g., [CS301, Page 2]).
4. Unknown Information: If the context does not contain the answer, explicitly state: "This information is not available in the official university curriculum handbook."
5. Formatting: Use structured, clean Markdown with bullet points and bold section headings.
"""

CONVERSATIONAL_RESPONSES = {
    "greeting": (
        "Hello! I am your official University Curriculum & Academic Assistant. "
        "I can assist you with course syllabi, unit topics, prerequisites, credit structures, "
        "semester schedules, academic regulations, examination schemes, and department electives. "
        "What course or academic topic would you like to inquire about?"
    ),
    "thanks": (
        "You're very welcome! If you have any further questions about your B.Tech CSE curriculum, "
        "prerequisites, or examination guidelines, feel free to ask. Best of luck with your studies!"
    ),
    "help": (
        "### How I Can Help You:\n"
        "- **Course Syllabi & Topics**: Ask about what is covered in any course or unit (e.g., *'What topics are in Unit 3 of DBMS?'*)\n"
        "- **Prerequisites & Credits**: Inquire about eligibility (e.g., *'What are the prerequisites for Compiler Design?'*)\n"
        "- **Semester Offerings**: Find subjects per semester (e.g., *'Which subjects are offered in Semester 5?'*)\n"
        "- **Academic Regulations**: Ask about attendance rules, CIA/internal evaluation, and 10-point grading scales.\n"
        "- **Subject Comparison**: Compare two courses (e.g., *'Compare DBMS and Operating Systems'*)"
    ),
    "fallback": (
        "I specialize strictly in official university curriculum and academic regulations for B.Tech Computer Science & Engineering. "
        "I am unable to answer general or off-topic queries. Please ask about courses (e.g., DBMS, OS, Networks, ML), "
        "syllabi, units, credits, prerequisites, or examination rules."
    )
}

class AnswerGenerator:
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL

    def _fallback_synthesis(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Deterministic, grounded synthesis directly from verified curriculum chunks."""
        if not chunks:
            return (
                "The requested information is not available in the official university curriculum handbook. "
                "Please verify the course title, code, or semester and try again."
            )

        # Generate a detailed summary directly from the verified curriculum chunks.
        lines = ["Here is a detailed summary based on the academic resources:", ""]

        course_name = entities.get("canonical_course_name") or chunks[0].get("course_name")
        course_code = entities.get("course_code") or chunks[0].get("course_code")

        if course_name or course_code:
            focus = " ".join(value for value in [course_name, f"({course_code})" if course_code else None] if value)
            lines.append(f"### **{focus}**")
            lines.append("")

        for i, chunk in enumerate(chunks[:4], 1):
            text = chunk.get("text", "").strip()
            doc_name = chunk.get("source_document") or chunk.get("document_name") or "Curriculum Handbook"
            page = chunk.get("page_number") or chunk.get("page", 1)
            sec = chunk.get("section_heading") or chunk.get("section") or f"Section {i}"

            lines.append(f"#### **{sec}** *[{doc_name}, Page {page}]*")

            cleaned_lines = [l.strip() for l in text.split("\n") if l.strip() and not l.startswith("Page ") and not l.startswith("DEPARTMENT")]
            if cleaned_lines:
                paragraph = ""
                for line in cleaned_lines:
                    if line.isupper() or len(line) < 30:
                        if paragraph:
                            lines.append(f"{paragraph}")
                            paragraph = ""
                        lines.append(f"- **{line}**")
                    else:
                        paragraph += f" {line}"
                if paragraph:
                    lines.append(f"{paragraph}")
            lines.append("")

        lines.append("---\n*Note: The above information is extracted directly from the verified university curriculum documents.*")
        return "\n".join(lines)

    def generate(
        self,
        query: str,
        intent_data: Dict[str, Any],
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response via NVIDIA NIM or grounded synthesizer."""
        intent = intent_data.get("intent", "fallback")

        # Conversational / System responses
        if intent in CONVERSATIONAL_RESPONSES:
            return CONVERSATIONAL_RESPONSES[intent]

        if intent == "course_code_lookup" and entities.get("course_code") and entities.get("canonical_course_name"):
            return f"The course code for **{entities['canonical_course_name']}** is **{entities['course_code']}**."

        if not chunks:
            return (
                "No relevant curriculum documents were found matching your query. "
                "Please check the course code, subject name, or unit number and ask again."
            )

        # Context assembly
        context_blocks = []
        for idx, chunk in enumerate(chunks, 1):
            c_id = chunk.get("chunk_id", f"chunk_{idx}")
            doc = chunk.get("source_document") or chunk.get("document_name") or "Curriculum.pdf"
            page = chunk.get("page_number") or chunk.get("page", 1)
            course = chunk.get("course_name") or "Curriculum"
            code = chunk.get("course_code") or ""
            text = chunk.get("text", "")
            context_blocks.append(
                f"[Chunk ID: {c_id} | Document: {doc} | Page: {page} | Course: {course} ({code})]\n{text}"
            )
        full_context = "\n\n---\n\n".join(context_blocks)

        # If NVIDIA API Key is provided
        if self.api_key and not self.api_key.startswith("nvapi-placeholder") and len(self.api_key) > 20:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]

                # Include past turns if present
                if chat_history:
                    for turn in chat_history[-3:]:
                        messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

                user_prompt = (
                    f"STUDENT QUERY: {query}\n\n"
                    f"DETECTED INTENT: {intent}\n"
                    f"EXTRACTED ENTITIES: {json.dumps(entities)}\n\n"
                    f"OFFICIAL CURRICULUM CONTEXT:\n{full_context}\n\n"
                    f"Please provide an accurate, grounded response with exact citations."
                )
                messages.append({"role": "user", "content": user_prompt})

                url = f"{self.base_url}/chat/completions"
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "max_tokens": 1024
                }

                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json["choices"][0]["message"]["content"]
                    logger.info(f"Generated grounded answer via NVIDIA NIM ({self.model})")
                    return content
                else:
                    logger.warning(f"NVIDIA NIM chat completion failed ({response.status_code}): {response.text[:200]}")
            except Exception as e:
                logger.warning(f"Error calling NVIDIA NIM LLM: {e}")

        # Grounded fallback synthesizer
        return self._fallback_synthesis(query, intent, entities, chunks)

answer_generator = AnswerGenerator()
