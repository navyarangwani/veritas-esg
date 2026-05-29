import fitz  # this is PyMuPDF, imported as fitz
import os

def extract_pages(pdf_path: str) -> list:
    """
    Opens a PDF and extracts text from each page.
    Returns a list of dicts: [{"page": int, "text": str}, ...]
    
    Why we store page numbers:
    Every claim we extract will know which page it came from.
    In a real audit, you must be able to say "this claim appears on page 42."
    That is called evidence traceability.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # extract plain text from page

        if text.strip():  # skip completely empty pages
            pages.append({
                "page": page_num + 1,  # page_num is 0-indexed, humans count from 1
                "text": text
            })

    doc.close()
    print(f"[Brain 1 — PDF Parser] Extracted {len(pages)} pages")
    return pages