import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import JUDGMENT_PROMPT

load_dotenv()


def format_evidence_for_prompt(evidence: list) -> str:
    """
    Converts the evidence list into readable text for the LLM.

    Why we format instead of dumping raw JSON:
    LLMs understand natural language better than raw JSON structures.
    Formatting evidence as numbered sources with clear labels
    helps the LLM reason about each source individually
    rather than treating the whole thing as one blob of text.
    """
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


def judge_claim(claim: dict, evidence: list, llm) -> dict:
    """
    Brain 5 — The Judge.

    This is the final step of the ReAct loop.
    The LLM receives the original company claim and all
    retrieved external evidence, then makes a judgment.

    Three possible verdicts:
    - Verified: external evidence clearly supports the claim
    - Unverified: not enough evidence to confirm or deny
    - Contradicted: evidence directly conflicts with the claim

    Why the prompt says "do not use your own knowledge":
    This is critical for audit integrity. If the LLM uses its
    training data to judge a claim, the verdict is based on
    potentially outdated information. We want verdicts based
    ONLY on freshly retrieved evidence from Brain 4.
    This is called grounding — keeping the LLM anchored
    to retrieved facts rather than hallucinated ones.

    Why confidence score matters:
    A verdict of "Contradicted" with confidence 30 is very
    different from "Contradicted" with confidence 92.
    The score tells the auditor how much to trust the verdict.
    Low confidence = needs human review.
    High confidence = can be flagged automatically.

    Why we default to Unverified on failure:
    If the judgment step crashes, we must not produce a false
    verdict. Defaulting to Unverified is the safe choice —
    it flags the claim for human review rather than incorrectly
    marking it as Verified or Contradicted.
    In audit work, a false clear is worse than no verdict.
    """
    evidence_text = format_evidence_for_prompt(evidence)

    prompt = JUDGMENT_PROMPT.format(
        claim_text=claim.get("claim_text", ""),
        evidence_text=evidence_text
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        # strip markdown code blocks if present
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    raw = part
                    break

        result = json.loads(raw)

        # validate verdict is one of the three allowed values
        allowed_verdicts = ["Verified", "Unverified", "Contradicted"]
        if result.get("verdict") not in allowed_verdicts:
            print(f"[Brain 5 — Judgment] Invalid verdict received, defaulting to Unverified")
            result["verdict"] = "Unverified"

        # clamp confidence between 0 and 100
        raw_confidence = result.get("confidence", 50)
        try:
            result["confidence"] = max(0, min(100, int(raw_confidence)))
        except (TypeError, ValueError):
            result["confidence"] = 50

        # ensure reasoning exists
        if "reasoning" not in result or not result["reasoning"]:
            result["reasoning"] = "No reasoning provided by judgment model."

        print(f"[Brain 5 — Judgment] Verdict: {result['verdict']} | Confidence: {result['confidence']}%")
        return result

    except json.JSONDecodeError as e:
        print(f"[Brain 5 — Judgment] JSON parse failed: {e}")
        return {
            "verdict": "Unverified",
            "confidence": 0,
            "reasoning": "Judgment could not be completed due to a response parsing error. Human review required."
        }

    except Exception as e:
        print(f"[Brain 5 — Judgment] Failed: {e}")
        return {
            "verdict": "Unverified",
            "confidence": 0,
            "reasoning": f"Judgment could not be completed due to an unexpected error. Human review required."
        }
