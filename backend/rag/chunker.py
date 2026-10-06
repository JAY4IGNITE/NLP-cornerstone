"""Structure-aware chunking for academic curriculum documents."""
import re
from typing import List, Dict, Any

class StructureAwareChunker:
    def __init__(self, target_chunk_size: int = 400, chunk_overlap: int = 60):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []

        for page_data in pages:
            doc_name = page_data["document_name"]
            page_num = page_data["page"]
            text = page_data["text"]

            # Infer course and branch from page text
            course_code_match = re.search(r"Course Code:\s*([A-Z]{2}\d{3})", text, re.IGNORECASE)
            course_code = course_code_match.group(1).upper() if course_code_match else None

            branch_match = re.search(r"Branch:\s*([A-Z]+)", text, re.IGNORECASE)
            branch = branch_match.group(1).upper() if branch_match else "CSE"

            semester_match = re.search(r"Semester:\s*(\d+)", text, re.IGNORECASE)
            semester = int(semester_match.group(1)) if semester_match else None

            course_name_match = re.search(r"COURSE SPECIFICATION:\s*([^\n\r|]+)", text, re.IGNORECASE)
            if course_name_match:
                course_name = course_name_match.group(1).strip()
            else:
                # Secondary course name deduction
                if course_code == "CS301":
                    course_name = "Database Management Systems"
                elif course_code == "CS302":
                    course_name = "Operating Systems"
                elif course_code == "CS303":
                    course_name = "Computer Networks"
                elif course_code == "CS304":
                    course_name = "Compiler Design"
                elif course_code == "CS401":
                    course_name = "Machine Learning"
                elif course_code == "CS201":
                    course_name = "Data Structures and Algorithms"
                elif course_code == "CS305":
                    course_name = "Web Technologies"
                elif course_code == "CS306":
                    course_name = "Software Engineering"
                elif course_code == "CS402":
                    course_name = "Artificial Intelligence"
                elif course_code == "CS403":
                    course_name = "Cloud Computing"
                else:
                    course_name = "General Curriculum / Academic Regulations"

            # Check if this is the regulations document
            if "Regulations" in doc_name:
                sections = text.split("\n\n")
                for s_idx, sec_text in enumerate(sections):
                    if len(sec_text.strip()) > 20:
                        sec_title = "Academic Regulations"
                        first_line = sec_text.strip().splitlines()[0]
                        if len(first_line) < 60:
                            sec_title = first_line

                        chunk_id = f"reg_{page_num}_{s_idx+1:02d}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "document_name": doc_name,
                            "branch": branch,
                            "course_code": None,
                            "course_name": "Academic Regulations",
                            "semester": None,
                            "section": sec_title,
                            "page": page_num,
                            "text": sec_text.strip()
                        })
                continue

            # If this is program overview (Page 1 of Curriculum)
            if page_num == 1:
                chunks.append({
                    "chunk_id": f"cse_overview_p1_01",
                    "document_name": doc_name,
                    "branch": branch,
                    "course_code": None,
                    "course_name": "Computer Science & Engineering Curriculum Overview",
                    "semester": None,
                    "section": "Program Overview & Degree Structure",
                    "page": page_num,
                    "text": text
                })
                continue

            # Standard course specification page: break into logical sections:
            # 1. Overview & Meta & Prerequisites & Objectives
            # 2. Course Outcomes (COs)
            # 3. Units 1, 2, 3, 4, 5
            c_code_clean = (course_code or "gen").lower()

            # Find sections
            sections_map = [
                ("Overview & Objectives", r"Course Objectives:(.*?)(?=Course Outcomes \(COs\):|$)", "Course Objectives"),
                ("Course Outcomes", r"Course Outcomes \(COs\):(.*?)(?=Syllabus Breakdown by Units:|$)", "Course Outcomes"),
                ("Unit 1", r"Unit 1:(.*?)(?=Unit 2:|$)", "Unit 1: Introduction"),
                ("Unit 2", r"Unit 2:(.*?)(?=Unit 3:|$)", "Unit 2"),
                ("Unit 3", r"Unit 3:(.*?)(?=Unit 4:|$)", "Unit 3"),
                ("Unit 4", r"Unit 4:(.*?)(?=Unit 5:|$)", "Unit 4"),
                ("Unit 5", r"Unit 5:(.*?)(?=Page \d+|$)", "Unit 5"),
            ]

            chunk_counter = 1
            # Add general header chunk including metadata, credits, prerequisites
            header_match = re.search(r"(Course Code:.*?(?=Course Objectives:|$))", text, re.DOTALL | re.IGNORECASE)
            if header_match:
                header_text = f"Course: {course_name} ({course_code})\n{header_match.group(1).strip()}"
                chunks.append({
                    "chunk_id": f"{c_code_clean}_{page_num}_{chunk_counter:02d}",
                    "document_name": doc_name,
                    "branch": branch,
                    "course_code": course_code,
                    "course_name": course_name,
                    "semester": semester,
                    "section": "Course Metadata & Prerequisites",
                    "page": page_num,
                    "text": header_text
                })
                chunk_counter += 1

            for sec_name, pattern, sec_title in sections_map:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    body = match.group(1).strip()
                    if body:
                        chunk_text = f"Course: {course_name} ({course_code})\nSection: {sec_title}\n{body}"
                        chunks.append({
                            "chunk_id": f"{c_code_clean}_{page_num}_{chunk_counter:02d}",
                            "document_name": doc_name,
                            "branch": branch,
                            "course_code": course_code,
                            "course_name": course_name,
                            "semester": semester,
                            "section": sec_title,
                            "page": page_num,
                            "text": chunk_text
                        })
                        chunk_counter += 1

        return chunks
