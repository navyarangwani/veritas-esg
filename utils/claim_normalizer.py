def normalize_claims(claims: list) -> list:
    """
    Removes duplicate claims from the extracted list.

    Why duplicates happen:
    Remember we use 300-character overlap between chunks.
    That means the same claim can appear at the end of chunk 4
    and the beginning of chunk 5 -- extracted twice.
    This function catches and removes those duplicates.

    How we detect duplicates:
    We don't check for exact string matches because the same claim
    might be worded slightly differently across two chunks.
    Instead we check word overlap ratio.
    If 80% of words in claim A exist in claim B -- they are the same claim.

    Why 80% and not 100%:
    100% would miss near-duplicates with minor wording differences.
    80% is tight enough to avoid false positives but loose enough
    to catch real duplicates. This threshold is a tunable parameter --
    something good to mention in your interview.
    """
    if not claims:
        print("[Brain 2 - Normalizer] No claims to normalize")
        return []

    unique_claims = []
    seen_texts = []

    for claim in claims:
        claim_text = claim.get("claim_text", "").lower().strip()
        if not claim_text:
            continue

        claim_words = set(claim_text.split())
        is_duplicate = False

        for seen in seen_texts:
            seen_words = set(seen.lower().split())

            # avoid division by zero
            if len(claim_words) == 0:
                continue

            # calculate what percentage of this claim's words
            # appear in an already-seen claim
            overlap = len(claim_words & seen_words) / len(claim_words)

            if overlap > 0.8:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_claims.append(claim)
            seen_texts.append(claim_text)

    print(f"[Brain 2 - Normalizer] Reduced {len(claims)} raw claims -> {len(unique_claims)} unique claims")
    return unique_claims