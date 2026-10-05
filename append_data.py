import pandas as pd
import json

df = pd.read_csv('data/benchmark/campusfaq_50k.csv')

new_data = [
    {
        "id": "campusfaq50k_900001", "query": "How can I get my answer script?", "intent": "answer_script_inspection", "response": "You can apply for a photocopy.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900002", "query": "What is the fee for script inspection?", "intent": "answer_script_inspection", "response": "Rs. 500.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900003", "query": "I want to apply for revaluation of my answer script", "intent": "answer_script_inspection", "response": "Apply for revaluation.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900004", "query": "Can I see my exam script?", "intent": "answer_script_inspection", "response": "Yes, within 7 days.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900005", "query": "Procedure for answer script photocopy", "intent": "answer_script_inspection", "response": "Apply within 7 days.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    # Let's add a few more for robustness!
    {
        "id": "campusfaq50k_900006", "query": "script revaluation rules", "intent": "answer_script_inspection", "response": "Revaluation rules.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900007", "query": "can we request answer scripts", "intent": "answer_script_inspection", "response": "Yes you can.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900008", "query": "show me my answer script paper", "intent": "answer_script_inspection", "response": "Photocopy allowed.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900009", "query": "how much for script checking", "intent": "answer_script_inspection", "response": "Rs 500.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
    {
        "id": "campusfaq50k_900010", "query": "deadline for answer script photocopy", "intent": "answer_script_inspection", "response": "7 days.",
        "document_id": "DOC-ACAD-REG", "document_version": "2026-27-demo", "evidence": "[]", "entities": "{}", "answerable": True, "difficulty": "easy",
        "split": "train", "source_authority": "DEMO_ONLY_SYNTHETIC", "provenance": "Custom Add"
    },
]

new_df = pd.DataFrame(new_data)
df = pd.concat([df, new_df], ignore_index=True)
df.to_csv('data/benchmark/campusfaq_50k.csv', index=False)
