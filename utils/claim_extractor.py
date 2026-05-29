import json
import re
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import CLAIM_EXTRACTION_PROMPT

load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )


def clean_json_response(raw: str) -> str:
    """
    Aggressively cleans LLM response to extract valid JSON.
    Handles all the weird ways LLMs return JSON.
    """
    raw = raw.strip()

    # remove markdown code blocks
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    # find the first [ and last ] — extract just the array
    start = raw.find('[')
    end = raw.rfind(']')

    if start != -1 and end != -1 and end > start:
        raw = raw[start:end+1]
        return raw

    # if no array found, try finding an object and wrap it
    start = raw.find('{')
    end = raw.rfind('}')

    if start != -1 and end != -1 and end > start:
        raw = raw[start:end+1]
        return f"[{raw}]"

    return "[]"


def extract_claims_from_chunk(chunk: dict, llm) -> list:
    prompt = CLAIM_EXTRACTION_PROMPT.format(
        text=chunk["text"],
        page=chunk["page"]
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content
        cleaned = clean_json_response(raw)

        claims = json.loads(cleaned)

        if not isinstance(claims, list):
            return []

        valid_claims = []
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            if "claim_text" not in claim or "value" not in claim:
                continue
            if not str(claim["claim_text"]).strip():
                continue

            claim["page"] = chunk["page"]
            claim.setdefault("metric_type", "other")
            claim.setdefault("year", None)

            valid_claims.append(claim)

        return valid_claims

    except json.JSONDecodeError as e:
        print(f"[Brain 2 — Extractor] JSON parse failed on page {chunk['page']}: {e}")
        return []
    except Exception as e:
        print(f"[Brain 2 — Extractor] Failed on page {chunk['page']}: {e}")
        return []


def extract_all_claims(chunks: list) -> list:
    llm = get_llm()
    all_claims = []

    for i, chunk in enumerate(chunks):
        print(f"[Brain 2 — Extractor] Processing chunk {i+1}/{len(chunks)} (page {chunk['page']})")
        claims = extract_claims_from_chunk(chunk, llm)
        all_claims.extend(claims)
        if claims:
            print(f"[Brain 2 — Extractor] Found {len(claims)} claims in chunk {i+1}")

    print(f"[Brain 2 — Extractor] Found {len(all_claims)} raw claims total")
    return all_claims
