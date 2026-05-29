import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# These domains are excluded because they are either the company's
# own promotional content or press release wires that companies
# pay to publish on. They cannot be considered independent evidence.
# This is an audit integrity decision — not a technical one.
# Mention this in your interview. It shows domain understanding.
EXCLUDED_DOMAINS = [
    "prnewswire.com",
    "businesswire.com",
    "globenewswire.com",
    "einpresswire.com",
    "accesswire.com"
]


def is_excluded(url: str) -> bool:
    """Check if a URL belongs to an excluded domain."""
    return any(domain in url for domain in EXCLUDED_DOMAINS)


def get_evidence(search_queries: list) -> list:
    """
    Brain 4 — The Investigator.

    Takes the search queries from Brain 3 and actually
    goes out to the web to find real evidence.

    Why Tavily and not Google Search API:
    Tavily is built specifically for LLM agents. It returns
    clean text snippets that are ready to send to an LLM —
    no HTML parsing, no JavaScript rendering issues.
    Google Search API costs money. Tavily has a free tier.

    Why we filter excluded domains:
    If a company publishes a press release saying they reduced
    emissions by 34%, that press release cannot verify the claim.
    The company wrote it. Independent verification requires
    independent sources — news outlets, regulators, NGOs,
    academic sources, government databases.

    Why we cap at 8 results:
    We send evidence to the LLM in the judgment prompt.
    LLMs have context limits. 8 well-chosen sources is enough
    for a confident verdict without overloading the context window.

    Why we sort by score:
    Tavily returns a relevance score per result.
    We show the most relevant evidence to the judgment brain first.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    all_evidence = []
    seen_urls = set()

    for query in search_queries:
        try:
            print(f"[Brain 4 — Evidence] Searching: '{query}'")

            results = client.search(
                query=query,
                max_results=5,
                search_depth="basic"
                # use "advanced" for deeper search
                # but it uses more API credits
                # stick to "basic" during development
            )

            for result in results.get("results", []):
                url = result.get("url", "")

                # skip if we already have this URL
                if url in seen_urls:
                    continue

                # skip excluded promotional domains
                if is_excluded(url):
                    print(f"[Brain 4 — Evidence] Excluded: {url}")
                    continue

                seen_urls.add(url)
                all_evidence.append({
                    "title": result.get("title", "Untitled"),
                    "url": url,
                    "snippet": result.get("content", "")[:600],
                    "score": float(result.get("score", 0))
                })

        except Exception as e:
            print(f"[Brain 4 — Evidence] Search failed for '{query}': {e}")
            continue  # never crash — just skip this query

    if not all_evidence:
        print("[Brain 4 — Evidence] No evidence found for any query")
        return []

    # sort by relevance score — best evidence first
    all_evidence.sort(key=lambda x: x["score"], reverse=True)

    # return top 8 most relevant pieces
    top_evidence = all_evidence[:8]
    print(f"[Brain 4 — Evidence] Collected {len(top_evidence)} evidence pieces")
    return top_evidence