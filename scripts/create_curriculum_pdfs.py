"""Script to generate authoritative official Curriculum and Regulations PDFs using PyMuPDF (fitz)."""
import json
from pathlib import Path
import fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "courses.json"
OUTPUT_DIR = BASE_DIR / "documents" / "curriculum"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_curriculum_pdf():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open()

    # Page 1: Title & Department Overview
    page = doc.new_page(width=595, height=842)
    pno = 1
    page.insert_text((50, 60), "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", fontsize=16, fontname="helv", color=(0.1, 0.2, 0.5))
    page.insert_text((50, 85), "OFFICIAL CURRICULUM & SYLLABUS HANDBOOK (2024-2028)", fontsize=13, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text((50, 110), "Branch: Computer Science & Engineering (CSE) | Degree: Bachelor of Technology (B.Tech)", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    page.draw_line((50, 120), (545, 120), color=(0.1, 0.2, 0.5), width=1.5)

    y = 145
    page.insert_text((50, y), "Program Overview & Degree Structure", fontsize=12, fontname="helv", color=(0.1, 0.2, 0.5))
    y += 20
    overview_text = (
        "The Bachelor of Technology in Computer Science and Engineering is a 4-year full-time academic program.\n"
        "Total Degree Credits: 160 credits across 8 semesters.\n"
        "Semester 3: Data Structures and Algorithms (CS201, 4 Credits)\n"
        "Semester 5: Database Management Systems (CS301, 4 Credits), Operating Systems (CS302, 4 Credits), Computer Networks (CS303, 3 Credits)\n"
        "Semester 6: Compiler Design (CS304, 4 Credits), Web Technologies (CS305, 3 Credits), Software Engineering (CS306, 3 Credits)\n"
        "Semester 7: Machine Learning (CS401, 4 Credits), Artificial Intelligence (CS402, 3 Credits)\n"
        "Semester 8: Cloud Computing (CS403, 3 Credits), Capstone Project & Internship (10 Credits)\n"
    )
    rect = fitz.Rect(50, y, 545, y + 160)
    page.insert_textbox(rect, overview_text, fontsize=9.5, fontname="helv")
    page.insert_text((270, 810), f"Page {pno}", fontsize=9, fontname="helv")

    # Add each course on dedicated pages
    courses = data["courses"]
    for c in courses:
        page = doc.new_page(width=595, height=842)
        pno += 1
        
        # Header
        page.insert_text((50, 50), f"COURSE SPECIFICATION: {c['course_name'].upper()}", fontsize=13, fontname="helv", color=(0.1, 0.2, 0.5))
        page.draw_line((50, 60), (545, 60), color=(0.1, 0.2, 0.5), width=1)

        # Meta Info
        meta = (
            f"Course Code: {c['course_code']}  |  Branch: {c['branch']}  |  Semester: {c['semester']}  |  Credits: {c['credits']} (L: {c['lecture_hours']}, T: {c['tutorial_hours']}, P: {c['practical_hours']})\n"
            f"Prerequisites: {', '.join(c['prerequisites'])}\n"
        )
        page.insert_textbox(fitz.Rect(50, 70, 545, 115), meta, fontsize=9, fontname="helv")

        # Objectives
        y_pos = 120
        page.insert_text((50, y_pos), "Course Objectives:", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
        y_pos += 15
        obj_text = "\n".join([f"• {obj}" for obj in c["objectives"]])
        rect_obj = fitz.Rect(50, y_pos, 545, y_pos + 70)
        page.insert_textbox(rect_obj, obj_text, fontsize=8.5, fontname="helv")

        # Course Outcomes
        y_pos = 200
        page.insert_text((50, y_pos), "Course Outcomes (COs):", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
        y_pos += 15
        co_text = "\n".join([f"• {co['code']}: {co['description']}" for co in c["course_outcomes"]])
        rect_co = fitz.Rect(50, y_pos, 545, y_pos + 85)
        page.insert_textbox(rect_co, co_text, fontsize=8.5, fontname="helv")

        # Units & Syllabus Breakdown
        y_pos = 295
        page.insert_text((50, y_pos), "Syllabus Breakdown by Units:", fontsize=10, fontname="helv", color=(0.1, 0.2, 0.5))
        y_pos += 15

        for u in c["units"]:
            u_header = f"Unit {u['unit_number']}: {u['title']}"
            page.insert_text((50, y_pos), u_header, fontsize=9, fontname="helv", color=(0.2, 0.3, 0.6))
            y_pos += 12
            rect_u = fitz.Rect(55, y_pos, 545, y_pos + 65)
            page.insert_textbox(rect_u, u["topics"], fontsize=8, fontname="helv")
            y_pos += 70

        page.insert_text((270, 810), f"Page {pno}", fontsize=9, fontname="helv")

    curriculum_pdf_path = OUTPUT_DIR / "CSE_Curriculum_2025.pdf"
    doc.save(str(curriculum_pdf_path))
    doc.close()
    print(f"Generated {curriculum_pdf_path} ({pno} pages)")

    # Generate Regulations PDF
    reg_doc = fitz.open()
    reg_page = reg_doc.new_page(width=595, height=842)
    reg_page.insert_text((50, 60), "OFFICIAL ACADEMIC REGULATIONS & EXAMINATION RULES", fontsize=15, fontname="helv", color=(0.1, 0.2, 0.5))
    reg_page.insert_text((50, 85), "Academic Year: 2024-2025 | B.Tech Programs", fontsize=11, fontname="helv")
    reg_page.draw_line((50, 95), (545, 95), color=(0.1, 0.2, 0.5), width=1)

    reg_content = (
        "1. Attendance Regulations:\n"
        + data["academic_regulations"]["attendance_requirement"] + "\n\n"
        "2. Evaluation & Examination Pattern:\n"
        + data["academic_regulations"]["examination_pattern"] + "\n\n"
        "3. 10-Point Grading System:\n"
        + data["academic_regulations"]["grading_system"] + "\n\n"
        "4. Degree Credit Requirements:\n"
        + data["academic_regulations"]["credit_requirements"] + "\n"
    )
    reg_page.insert_textbox(fitz.Rect(50, 115, 545, 600), reg_content, fontsize=9.5, fontname="helv")
    reg_page.insert_text((270, 810), "Page 1", fontsize=9, fontname="helv")

    reg_pdf_path = OUTPUT_DIR / "Academic_Regulations_2025.pdf"
    reg_doc.save(str(reg_pdf_path))
    reg_doc.close()
    print(f"Generated {reg_pdf_path} (1 page)")

if __name__ == "__main__":
    generate_curriculum_pdf()
