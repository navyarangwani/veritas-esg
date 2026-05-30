import json
import os
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import STRATEGY_PROMPT
from utils.llm_provider import get_llm as get_provider_llm

load_dotenv()


def get_llm():
    return get_provider_llm()


def get_verification_plan(claim: dict, llm) -> dict:
    prompt = STRATEGY_PROMPT.format(
        company=claim.get("company", "the company"),
        claim_text=claim.get("claim_text", ""),
        metric_type=claim.get("metric_type", "other")
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    raw = part
                    break

        # find JSON object
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw = raw[start:end+1]

        plan = json.loads(raw)

        if "search_queries" not in plan or not plan["search_queries"]:
            raise ValueError("No search queries in plan")

        plan["search_queries"] = plan["search_queries"][:3]
        print(f"[Brain 3 — Strategy] Plan: {plan.get('reasoning', 'No reasoning provided')}")
        return plan

    except Exception as e:
        print(f"[Brain 3 — Strategy] Failed, using fallback: {e}")
        claim_text = claim.get("claim_text", "ESG claim")
        metric_type = claim.get("metric_type", "sustainability")
        company = claim.get("company", "the company")
        year = claim.get("year", "")

        return {
            "search_queries": [
                f"{company} {claim_text[:60]} verification",
                f"{company} {metric_type} sustainability report {year}",
                f"{company} ESG {metric_type} external audit"
            ],
            "reasoning": "Fallback strategy — LLM planning step failed"
        }