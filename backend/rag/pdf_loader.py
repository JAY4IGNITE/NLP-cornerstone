"""PyMuPDF-based curriculum document loader."""
from pathlib import Path
from typing import List, Dict, Any
import pymupdf
from backend.utils.logger import logger

class PDFLoader:
    def __init__(self, pdf_dir: Path):
        self.pdf_dir = Path(pdf_dir)

    def load_documents(self) -> List[Dict[str, Any]]:
        """Extract pages and metadata from all PDFs in directory."""
        extracted_pages = []
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF documents found in {self.pdf_dir}")
            return extracted_pages

        for pdf_path in sorted(pdf_files):
            doc_name = pdf_path.name
            try:
                doc = pymupdf.open(str(pdf_path))
                page_count = len(doc)
                for page_idx in range(page_count):
                    page = doc[page_idx]
                    raw_text = page.get_text()
                    cleaned_text = self._clean_text(raw_text)
                    if cleaned_text:
                        extracted_pages.append({
                            "document_name": doc_name,
                            "page": page_idx + 1,
                            "text": cleaned_text,
                            "file_path": str(pdf_path)
                        })
                doc.close()
                logger.info(f"Loaded {page_count} pages from {doc_name}")
            except Exception as e:
                logger.error(f"Failed to load PDF {pdf_path}: {e}")

        return extracted_pages

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted PDF text while preserving structural line boundaries."""
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines()]
        filtered_lines = [l for l in lines if l]
        return "\n".join(filtered_lines)
