"""Curriculum Document Ingestion and Vector Indexing Pipeline.
Reads curriculum PDFs, executes structure-aware chunking, generates embeddings,
and stores payload records into Qdrant.
Outputs reports/indexing_summary.json.
"""
import json
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import DOCUMENTS_DIR, REPORTS_DIR, DATA_DIR
from backend.rag.pdf_loader import PDFLoader
from backend.rag.chunker import StructureAwareChunker
from backend.rag.embeddings import embedding_service, EMBEDDING_DIM
from backend.rag.vector_store import vector_store

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def index_curriculum():
    print("=== Starting Curriculum Indexing Pipeline ===")
    t0 = time.time()
    curriculum_dir = DOCUMENTS_DIR
    pdf_loader = PDFLoader(curriculum_dir)
    chunker = StructureAwareChunker()
    pdf_files = list(curriculum_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {curriculum_dir}. Running PDF creation script first...")
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "create_curriculum_pdfs.py")], check=True)
        pdf_files = list(curriculum_dir.glob("*.pdf"))

    print(f"Found {len(pdf_files)} curriculum PDF documents to ingest.")

    pages = pdf_loader.load_documents()
    print(f"Extracted {len(pages)} total pages from PDFs.")

    all_chunks = chunker.chunk_pages(pages)
    print(f"Extracted {len(all_chunks)} structural chunks across curriculum.")

    doc_stats = []
    for pdf_path in sorted(pdf_files):
        p_chunks = [c for c in all_chunks if c.get("source_document") == pdf_path.name]
        p_pages = len(set(c.get("page_number") for c in p_chunks))
        doc_stats.append({
            "filename": pdf_path.name,
            "pages": p_pages,
            "chunks_created": len(p_chunks)
        })

    # Compute chunk length metrics
    lengths = [len(c["text"]) for c in all_chunks]
    avg_len = round(sum(lengths) / len(lengths), 2) if lengths else 0
    max_len = max(lengths) if lengths else 0
    min_len = min(lengths) if lengths else 0

    # Generate embeddings
    print(f"\nGenerating embeddings for {len(all_chunks)} chunks using {embedding_service.model}...")
    texts_to_embed = [c["text"] for c in all_chunks]
    t_emb0 = time.time()
    embeddings = embedding_service.get_embeddings(texts_to_embed, input_type="passage")
    emb_time = round(time.time() - t_emb0, 2)
    print(f"Completed embeddings in {emb_time}s. Dimension verified: {len(embeddings[0]) if embeddings else 0}")

    # Insert into Qdrant
    print(f"Upserting chunks into Qdrant collection '{vector_store.collection_name}'...")
    inserted_count = vector_store.insert_chunks(all_chunks, embeddings)

    # Save chunks index locally for sparse BM25 retrieval
    chunks_file = DATA_DIR / "indexed_chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"Saved local chunk registry to {chunks_file}")

    total_time = round(time.time() - t0, 2)
    qdrant_points = vector_store.get_total_chunks()

    summary = {
        "status": "SUCCESS",
        "total_documents_processed": len(pdf_files),
        "total_chunks_created": len(all_chunks),
        "total_qdrant_points": qdrant_points,
        "average_chunk_characters": avg_len,
        "min_chunk_characters": min_len,
        "max_chunk_characters": max_len,
        "vector_dimension": EMBEDDING_DIM,
        "embedding_model": embedding_service.model,
        "qdrant_collection": vector_store.collection_name,
        "processing_time_seconds": total_time,
        "documents": doc_stats
    }

    summary_file = REPORTS_DIR / "indexing_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Indexing Summary ===")
    print(json.dumps(summary, indent=2))
    print(f"Indexing report written to {summary_file}")

if __name__ == "__main__":
    index_curriculum()
