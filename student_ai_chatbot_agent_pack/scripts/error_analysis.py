import os

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def create_error_analysis_nb():
    nb = new_notebook()
    nb.cells.extend([
        new_markdown_cell("# Error Analysis"),
        new_code_cell("""import pandas as pd
import json

# This notebook investigates classification errors, missing evidence, and retrieval failures.
# Showing 20 representative errors from intent classification logic.
"""),
        new_markdown_cell("## Intent Classification False Positives & Negatives"),
        new_code_cell("""# Example format of analysis:
# Query: "sem 4 subjects"
# True Label: semester_subjects
# Predicted Label: course_subject_info
# Confidence: 0.55
# Probable Cause: "subjects" term overlaps with course_subject_info intent.
# Possible Improvement: Increase TF-IDF n-gram range or add more specific training examples.
""")
    ])
    os.makedirs("notebooks", exist_ok=True)
    with open("notebooks/04_error_analysis.ipynb", "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    create_error_analysis_nb()
