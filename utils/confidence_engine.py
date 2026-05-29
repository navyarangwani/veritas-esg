def get_color(verdict: str) -> str:
    """
    Maps a verdict to a Streamlit color string.

    Why we have a separate function for this:
    Color logic is UI concern, not business logic.
    Keeping it here means if we change the frontend,
    we change it in one place only.
    """
    mapping = {
        "Verified": "green",
        "Contradicted": "red",
        "Unverified": "orange"
    }
    return mapping.get(verdict, "grey")


def get_badge_emoji(verdict: str) -> str:
    """
    Returns an emoji for quick visual scanning of the dashboard.

    Why emojis:
    When an auditor scans 20 claims, they need to spot
    contradicted claims instantly. A red emoji is faster
    to process than reading the word "Contradicted" 20 times.
    This is a UX decision rooted in how auditors actually work.
    """
    mapping = {
        "Verified": "✅",
        "Unverified": "⚠️",
        "Contradicted": "🚨"
    }
    return mapping.get(verdict, "❓")


def get_risk_level(verdict: str, confidence: int) -> str:
    """
    Combines verdict and confidence into a human-readable risk level.

    Why risk level matters:
    A contradicted claim with 40% confidence is medium risk —
    the agent isn't sure enough to flag it definitively.
    A contradicted claim with 95% confidence is high risk —
    act on this immediately.

    This is the kind of nuance real audit tools need.
    Binary verdicts alone are not enough for enterprise use.
    """
    if verdict == "Contradicted":
        if confidence >= 75:
            return "🔴 High Risk"
        else:
            return "🟠 Medium Risk"
    elif verdict == "Unverified":
        if confidence >= 75:
            return "🟠 Medium Risk"
        else:
            return "🟡 Low Risk"
    else:  # Verified
        return "🟢 Low Risk"


def build_result_object(claim: dict, verdict_data: dict, evidence: list) -> dict:
    """
    Assembles the final result object for the dashboard.

    This is the single data structure that flows from the
    pipeline into the Streamlit UI. Everything the dashboard
    needs to display is in this object.

    Why we build this here instead of in the orchestrator:
    Single responsibility. The orchestrator coordinates brains.
    This file handles result formatting. Clean separation.
    """
    verdict = verdict_data.get("verdict", "Unverified")
    confidence = verdict_data.get("confidence", 0)

    return {
        # claim details
        "claim_text": claim.get("claim_text", ""),
        "metric_type": claim.get("metric_type", "other"),
        "value": claim.get("value", "N/A"),
        "year": claim.get("year") or "N/A",
        "page": claim.get("page", "N/A"),

        # verdict details
        "verdict": verdict,
        "confidence": confidence,
        "reasoning": verdict_data.get("reasoning", ""),

        # display helpers
        "color": get_color(verdict),
        "badge": get_badge_emoji(verdict),
        "risk_level": get_risk_level(verdict, confidence),

        # evidence sources — top 3 URLs only
        "sources": [
            {"title": e.get("title", ""), "url": e.get("url", "")}
            for e in evidence[:3]
        ]
    }