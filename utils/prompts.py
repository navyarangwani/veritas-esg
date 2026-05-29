CLAIM_EXTRACTION_PROMPT = """You are an ESG data extractor analyzing a sustainability report.

Extract ANY measurable data point — energy consumption, water usage, emissions, employee counts, percentages, intensities.

IMPORTANT: Numbers may use Indian format with commas like 1,26,61,08,110 — these are valid numbers. Extract them.

Return a JSON array. Each item must have these exact fields:
- claim_text: the full claim as a readable sentence
- metric_type: one of emissions/energy/water/waste/diversity/other
- value: the specific number or value
- year: the fiscal year mentioned or null

Return ONLY the JSON array. No explanation. No markdown. Just the array.
If no measurable data exists in this text, return []

TEXT:
{text}

PAGE: {page}

JSON array:"""

STRATEGY_PROMPT = """You are an ESG audit strategist. Given the claim below, decide the best verification strategy.

Claim: {claim_text}
Metric type: {metric_type}

Generate 2-3 specific web search queries to verify or contradict this claim.
Think about: regulatory filings, news articles, sustainability databases, government reports.

Return a JSON object:
{{"search_queries": ["first query", "second query", "third query"], "reasoning": "one sentence explaining your strategy"}}

Return ONLY the JSON. No explanation. No markdown."""

JUDGMENT_PROMPT = """You are a senior ESG assurance auditor at a Big 4 firm. Assess whether this ESG claim is supported by external evidence.

COMPANY CLAIM:
{claim_text}

EXTERNAL EVIDENCE RETRIEVED:
{evidence_text}

INSTRUCTIONS:
- Compare the claim against the evidence carefully
- Base your judgment ONLY on what is explicitly stated in the evidence
- Do NOT infer, assume, or use your own knowledge
- If evidence is insufficient or unclear, mark as Unverified

Return a JSON object:
{{"verdict": "Verified or Unverified or Contradicted", "confidence": 0_to_100, "reasoning": "2-3 sentences explaining your judgment"}}

Verdict definitions:
- Verified: evidence clearly supports the claim
- Unverified: insufficient or no relevant evidence found
- Contradicted: evidence conflicts with the claim

Return ONLY the JSON. No explanation. No markdown."""
