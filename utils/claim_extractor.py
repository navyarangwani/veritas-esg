import json
import re
import os
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import CLAIM_EXTRACTION_PROMPT
from utils.llm_provider import get_extraction_llm

load_dotenv()

def get_llm():
    return get_extraction_llm()


def clean_json_response(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    start = raw.find('[')
    end = raw.rfind(']')
    if start != -1 and end != -1 and end > start:
        return raw[start:end+1]

    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1 and end > start:
        return f"[{raw[start:end+1]}]"

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