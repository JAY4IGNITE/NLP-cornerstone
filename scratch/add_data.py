import csv
import random

templates = [
    "I want to apply for a photocopy of my answer script",
    "How can I see my evaluated exam paper?",
    "What is the procedure for answer script inspection?",
    "Can I request a digital copy of my answer sheet?",
    "Fee for answer script photocopy",
    "Deadline to apply for script inspection",
    "Where do I apply to see my answer script?",
    "Show me my exam script",
    "I need a photocopy of my mid-term script",
    "Process to get evaluated answer script",
    "I want to check my answers for the end-semester exam",
    "Is there a way to verify my exam paper?",
    "Can I get my script re-evaluated after inspection?",
    "I paid Rs 500 for the script photocopy, when will I get it?",
    "Answer script photocopy link",
    "How many days do I have to request my exam script?"
]

new_rows = []
for i in range(11, 420):
    text = random.choice(templates)
    new_rows.append([
        f"campusfaq50k_900{str(i).zfill(3)}",
        text,
        "answer_script_inspection",
        "You can apply for a photocopy of your answer script within 7 days of results.",
        "DOC-ACAD-REG",
        "2026-27-demo",
        "[]",
        "{}",
        "True",
        "easy",
        "train",
        "DEMO_ONLY_SYNTHETIC",
        "Custom Add"
    ])

with open("data/benchmark/campusfaq_50k.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)
print("Added training data")
