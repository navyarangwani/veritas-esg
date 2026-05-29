import re

def clean_text(text: str) -> str:
    """
    Removes common PDF noise from extracted text.
    
    Why we clean:
    PDFs are messy. Page numbers, headers, footers, and broken
    line wraps all end up in the extracted text. If we don't clean,
    the LLM will try to extract claims from "Page 42" and "© 2024
    Tata Motors Limited" — wasting tokens and producing junk.
    """

    # remove lines that are just a number (page numbers)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # remove lines that are just dashes, underscores, or equals (table borders)
    text = re.sub(r'^\s*[-_=]{3,}\s*$', '', text, flags=re.MULTILINE)

    # fix broken hyphenated line wraps
    # example: "sustain-\nability" becomes "sustainability"
    text = re.sub(r'-\n(\w)', r'\1', text)

    # collapse 3+ newlines into 2 (preserve paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # collapse multiple spaces into one
    text = re.sub(r' {2,}', ' ', text)

    # strip each line individually
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def clean_pages(pages: list) -> list:
    """
    Runs clean_text on every page.
    Skips pages that become empty after cleaning.
    
    Input:  [{"page": int, "text": str}, ...]
    Output: [{"page": int, "text": str}, ...] with cleaned text
    """
    cleaned = []

    for p in pages:
        cleaned_text = clean_text(p["text"])
        if cleaned_text:  # only keep page if it has content after cleaning
            cleaned.append({
                "page": p["page"],
                "text": cleaned_text
            })

    print(f"[Brain 1 — Cleaner] Cleaned {len(cleaned)} pages")
    return cleaned