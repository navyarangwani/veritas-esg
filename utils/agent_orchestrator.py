import os
import time
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.pdf_parser import extract_pages
from utils.cleaner import clean_pages
from utils.chunker import chunk_pages
from utils.claim_extractor import extract_all_claims
from utils.claim_normalizer import normalize_claims
from utils.strategy_brain import get_verification_plan
from utils.evidence_brain import get_evidence
from utils.judgment_brain import judge_claim
from utils.confidence_engine import build_result_object

load_dotenv()


def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )


def run_pipeline(pdf_path: str, progress_callback=None) -> list:

    def log(msg: str):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("[INIT] Initializing Veritas ESG agent...")
    llm = get_llm()

    log("[Brain 1] Extracting text from PDF...")
    pages = extract_pages(pdf_path)

    if not pages:
        log("[ERROR] Could not extract any text from this PDF.")
        return []

    log(f"[Brain 1] Extracted {len(pages)} pages. Cleaning...")
    pages = clean_pages(pages)

    log(f"[Brain 2] Chunking {len(pages)} pages into segments...")
    chunks = chunk_pages(pages)

    log(f"[Brain 2] Extracting ESG claims from {len(chunks)} chunks...")
    log("    This may take 1-2 minutes depending on document size...")
    raw_claims = extract_all_claims(chunks)

    if not raw_claims:
        log("[WARNING] No quantitative ESG claims found in this document.")
        log("    Try a different ESG report with measurable sustainability data.")
        return []

    log("[Brain 2] Deduplicating claims...")
    claims = normalize_claims(raw_claims)

    log(f"[OK] Found {len(claims)} unique verifiable claims.")

    # Filter to only high-priority ESG claims and cap at 20
    claims = [c for c in claims if c.get("metric_type") in ["emissions", "energy", "water", "waste", "diversity"]][:20]
    log(f"[FILTER] Kept {len(claims)} high-priority ESG claims for verification.")

    if not claims:
        log("[WARNING] No high-priority ESG claims found after filtering.")
        return []

    log("[LOOP] Starting agentic verification loop...")
    log("    Each claim goes through Brain 3 -> Brain 4 -> Brain 5")

    results = []

    for i, claim in enumerate(claims):
        claim_preview = claim.get("claim_text", "")[:60]
        log(f"\n[Claim {i+1}/{len(claims)}] {claim_preview}...")

        log("   [Brain 3] Planning verification strategy...")
        plan = get_verification_plan(claim, llm)
        search_queries = plan.get("search_queries", [])

        if not search_queries:
            log("   [WARNING] No search queries generated. Skipping claim.")
            continue

        log("   [Brain 4] Retrieving external evidence...")
        evidence = get_evidence(search_queries)

        if not evidence:
            log("   [WARNING] No evidence found. Marking as Unverified.")

        log("   [Brain 5] Evaluating claim against evidence...")
        verdict_data = judge_claim(claim, evidence, llm)

        result = build_result_object(claim, verdict_data, evidence)
        results.append(result)

        log(f"   -> {result['badge']} {result['verdict']} | "
            f"Confidence: {result['confidence']}% | "
            f"Risk: {result['risk_level']}")

        time.sleep(2)

    if results:
        verified = sum(1 for r in results if r["verdict"] == "Verified")
        contradicted = sum(1 for r in results if r["verdict"] == "Contradicted")
        unverified = sum(1 for r in results if r["verdict"] == "Unverified")

        log("\n[DONE] Veritas ESG analysis complete.")
        log(f"   Verified:     {verified}")
        log(f"   Contradicted: {contradicted}")
        log(f"   Unverified:   {unverified}")
    else:
        log("[WARNING] Pipeline completed but no results were generated.")

    return results