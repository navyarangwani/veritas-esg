import json
import re
import os
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import JUDGMENT_PROMPT
from utils.llm_provider import get_llm as get_provider_llm

load_dotenv()


def get_llm():
    return get_provider_llm()


def format_evidence_for_prompt(evidence: list) -> str:
    if not evidence:
        return "No external evidence found for this claim."

    formatted = []
    for i, e in enumerate(evidence, 1):
        formatted.append(
            f"Source {i}:\n"
            f"Title: {e.get('title', 'Unknown')}\n"
            f"URL: {e.get('url', 'Unknown')}\n"
            f"Content: {e.get('snippet', 'No content available')}\n"
        )
    return "\n---\n".join(formatted)


def extract_json_from_response(raw: str) -> dict:
    """
    Aggressively extracts JSON from LLM response.
    Handles all the ways Mistral and other models return JSON:
    - Pure JSON
    - JSON wrapped in markdown
    - JSON followed by explanation text
    - JSON preceded by preamble
    """
    raw = raw.strip()

    # remove markdown code blocks
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    # find the first { and its matching }
    # this handles "extra data" after the JSON object
    start = raw.find('{')
    if start == -1:
        raise ValueError("No JSON object found in response")

    # find matching closing brace
    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == '{':
            depth += 1
        elif raw[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        raise ValueError("No matching closing brace found")

    json_str = raw[start:end+1]
    return json.loads(json_str)


def judge_claim(claim: dict, evidence: list, llm) -> dict:
    """
    Brain 5 — The Judge.
    Compares company claim against external evidence.
    Returns verdict, confidence score, and reasoning.
    """
    evidence_text = format_evidence_for_prompt(evidence)

    prompt = JUDGMENT_PROMPT.format(
        claim_text=claim.get("claim_text", ""),
        evidence_text=evidence_text
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content

        result = extract_json_from_response(raw)

        # validate verdict
        allowed_verdicts = ["Verified", "Unverified", "Contradicted"]
        if result.get("verdict") not in allowed_verdicts:
            print(f"[Brain 5 — Judgment] Invalid verdict '{result.get('verdict')}', defaulting to Unverified")
            result["verdict"] = "Unverified"

        # clamp confidence between 0 and 100
        try:
            result["confidence"] = max(0, min(100, int(result.get("confidence", 50))))
        except (TypeError, ValueError):
            result["confidence"] = 50

        # ensure reasoning exists
        if not result.get("reasoning"):
            result["reasoning"] = "No reasoning provided."

        print(f"[Brain 5 — Judgment] Verdict: {result['verdict']} | Confidence: {result['confidence']}%")
        return result

    except Exception as e:
        print(f"[Brain 5 — Judgment] Failed: {e}")
        print(f"[Brain 5 — Judgment] Raw response was: {response.content[:200] if 'response' in locals() else 'no response'}")
        return {
            "verdict": "Unverified",
            "confidence": 40,
            "reasoning": "Automated judgment could not be completed for this claim. Manual review recommended."
        }