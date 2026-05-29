from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_pages(pages: list) -> list:
    """
    Splits cleaned pages into overlapping chunks.

    Why we chunk:
    LLMs have a context window limit — you cannot send a 160-page
    PDF in one prompt. We split it into smaller pieces.

    Why overlap:
    Imagine a claim that starts on the last line of chunk 1 and
    finishes on the first line of chunk 2. Without overlap, that
    claim gets cut in half and never extracted properly.
    300 characters of overlap means each chunk shares 300 chars
    with the next one — no claim gets lost at a boundary.

    chunk_size=3000: roughly 500-600 words per chunk
    chunk_overlap=300: ~50 words of overlap between chunks

    RecursiveCharacterTextSplitter is smart — it tries to split at:
    1. Paragraph breaks first (\\n\\n)
    2. Then line breaks (\\n)
    3. Then sentence endings (.)
    4. Then spaces ( )
    It never cuts in the middle of a word.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = []

    for p in pages:
        page_chunks = splitter.split_text(p["text"])

        for chunk in page_chunks:
            if chunk.strip():  # skip empty chunks
                chunks.append({
                    "page": p["page"],
                    "text": chunk.strip()
                })

    print(f"[Brain 2 — Chunker] Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks