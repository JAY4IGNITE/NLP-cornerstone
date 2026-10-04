import json
import time
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import DATA_DIR
from backend.rag.embeddings import embedding_service
from backend.rag.cloudflare_vector_store import cloudflare_vector_store
from backend.utils.logger import logger

DATASETS_DIR = BASE_DIR / "datasets"
SCRAPED_MD = Path(r"C:\Users\ramuv\.gemini\antigravity-ide\brain\bf8bacb9-cc38-49d6-85d7-db12db2af377\.system_generated\steps\225\content.md")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n\n"
    except Exception as e:
        logger.error(f"Error reading {pdf_path}: {e}")
    return text

def chunk_text(text, source_name, category):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len
    )
    chunks = splitter.split_text(text)
    
    records = []
    for i, c in enumerate(chunks):
        chunk_id = f"custom_{source_name}_{i}_{int(time.time())}"
        records.append({
            "chunk_id": chunk_id,
            "category": category,
            "course_code": "",
            "course_name": source_name,
            "source_document": source_name,
            "section_heading": f"{source_name} - Part {i+1}",
            "page_number": 1,
            "text": f"Source: {source_name}\nContent:\n{c}"
        })
    return records

def main():
    print("Starting processing of user datasets and scraped website...")
    all_new_records = []

    # 1. Process PDFs
    for pdf_file in DATASETS_DIR.glob("*.pdf"):
        print(f"Processing PDF: {pdf_file.name}")
        text = extract_text_from_pdf(pdf_file)
        if text.strip():
            cat = "regulations" if "Regulation" in pdf_file.name else "curriculum"
            records = chunk_text(text, pdf_file.name, cat)
            all_new_records.extend(records)
            print(f"  -> Generated {len(records)} chunks.")

    # 2. Process Scraped Website Markdown
    if SCRAPED_MD.exists():
        print(f"Processing Scraped Website: Aditya University")
        with open(SCRAPED_MD, "r", encoding="utf-8") as f:
            text = f.read()
        records = chunk_text(text, "Aditya University Website", "campus_services")
        all_new_records.extend(records)
        print(f"  -> Generated {len(records)} chunks.")

    if not all_new_records:
        print("No new records to index.")
        return

    # Generate Embeddings
    print(f"Generating embeddings for {len(all_new_records)} chunks...")
    texts = [r["text"] for r in all_new_records]
    embeddings = embedding_service.get_embeddings(texts)

    # Insert into Cloudflare Vectorize (Local Edge fallback)
    print("Inserting chunks into vector store...")
    upserted_count = cloudflare_vector_store.insert_chunks(all_new_records, embeddings)

    # Append to indexed_chunks.json
    indexed_file = DATA_DIR / "indexed_chunks.json"
    existing_data = []
    if indexed_file.exists():
        with open(indexed_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    
    for r, vec in zip(all_new_records, embeddings):
        existing_data.append({
            **r,
            "embedding": vec
        })

    with open(indexed_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2)

    print(f"Successfully processed and indexed {len(all_new_records)} chunks!")

if __name__ == "__main__":
    main()
