import sys
import re

path = 'c:/Users/ramuv/NLP-cornerstone/backend/rag/generator.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'    def _fallback_synthesis.*?(?=    def generate)', re.DOTALL)

replacement = """    def _fallback_synthesis(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> str:
        \"\"\"Deterministic, grounded synthesis directly from verified curriculum chunks.\"\"\"
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

            lines.append(f"#### **{sec}** *(Source: {doc_name}, Page {page})*")

            cleaned_lines = [l.strip() for l in text.split("\\n") if l.strip() and not l.startswith("Page ") and not l.startswith("DEPARTMENT")]
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

        lines.append("---\\n*Note: The above information is extracted directly from the verified university curriculum documents.*")
        return "\\n".join(lines)

"""

new_content = pattern.sub(replacement, content)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated generator.py")
