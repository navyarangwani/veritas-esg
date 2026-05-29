import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.prompts import STRATEGY_PROMPT

load_dotenv()


def get_verification_plan(claim: dict, llm) -> dict:
    """
    Brain 3 — The Planner.

    This is where the system becomes genuinely agentic.

    The difference between a pipeline and an agent:
    A pipeline has hardcoded steps — step 1 always does X,
    step 2 always does Y. You wrote the logic, not the LLM.

    An agent decides its own next step based on what it sees.
    Here, the LLM reads the claim and decides WHAT to search for
    and WHERE. We never hardcode "always search Reuters" or
    "always search SEC filings." The LLM reasons about the claim
    type and generates a contextual search strategy.

    Example:
    Claim: "Reduced carbon emissions by 34% in FY24"
    Brain 3 decides: search emissions databases, regulatory
    filings, environmental news.

    Claim: "95% of leadership positions held by women"
    Brain 3 decides: search DEI reports, workforce filings,
    gender diversity indices.

    Same pipeline, different strategies. That is agentic behavior.

    Why we have a fallback:
    If the LLM fails to return valid JSON, we don't crash.
    We fall back to generic search queries and continue.
    Production systems must never crash on a single LLM failure.
    """
    prompt = STRATEGY_PROMPT.format(
        claim_text=claim.get("claim_text", ""),
        metric_type=claim.get("metric_type", "other")
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        # strip markdown if present
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    raw = part
                    break

        plan = json.loads(raw)

        # validate the plan has search queries
        if "search_queries" not in plan or not plan["search_queries"]:
            raise ValueError("No search queries in plan")

        # cap at 3 queries to stay within Tavily free tier limits
        plan["search_queries"] = plan["search_queries"][:3]

        print(f"[Brain 3 — Strategy] Plan: {plan.get('reasoning', 'No reasoning provided')}")
        return plan

    except Exception as e:
        print(f"[Brain 3 — Strategy] Failed, using fallback: {e}")

        # fallback strategy — generic but functional
        claim_text = claim.get("claim_text", "ESG claim")
        metric_type = claim.get("metric_type", "sustainability")
        company_hint = claim.get("year", "")

        return {
            "search_queries": [
                f"{claim_text[:80]} independent verification",
                f"company {metric_type} report external audit {company_hint}",
                f"{metric_type} ESG greenwashing news"
            ],
            "reasoning": "Fallback strategy — LLM planning step failed"
        }
