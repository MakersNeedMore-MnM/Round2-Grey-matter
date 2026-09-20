import re
from typing import List, Tuple, Dict, Any

# Generic challenge question templates that prompt without leaking details
TEMPLATES = [
    "Can you describe any marks, damage, stickers, or distinguishing details on the item?",
    "Does this item have any specific markings, initials, tags, or internal contents you can identify?",
    "Please describe any unique identifying features, repairs, or tags present on your item.",
]

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "of",
    "by", "is", "it", "its", "has", "have", "with", "small", "very", "there", "some"
}


def generate_challenge_question(hidden_attribute: str, item_description: str = "") -> str:
    """
    Generate a deterministic, template-based challenge question
    that prompts the claimant without leaking the hidden attribute.
    """
    # Deterministic choice based on description or hidden_attribute length
    idx = (len(hidden_attribute) + len(item_description)) % len(TEMPLATES)
    return TEMPLATES[idx]


def extract_key_terms(hidden_attribute: str, pre_tagged_terms: str = None) -> List[str]:
    """
    Extract 2-4 key terms from the hidden attribute or use pre-tagged terms.
    """
    if pre_tagged_terms and pre_tagged_terms.strip():
        terms = [t.strip().lower() for t in pre_tagged_terms.split(",") if t.strip()]
        if terms:
            return terms

    # Extract words, remove stopwords and short tokens
    cleaned = re.sub(r"[^\w\s]", " ", (hidden_attribute or "").lower())
    words = [w for w in cleaned.split() if len(w) > 2 and w not in STOPWORDS]

    # Deduplicate while preserving order
    unique_words = []
    for w in words:
        if w not in unique_words:
            unique_words.append(w)

    return unique_words[:4] if unique_words else ["verified"]


def verify_claim_answer(claimant_answer: str, hidden_attribute: str, pre_tagged_terms: str = None) -> Dict[str, Any]:
    """
    Verify claimant's answer using reliable keyword-presence matching.
    Returns match status, matched terms, and missing terms.
    """
    expected_terms = extract_key_terms(hidden_attribute, pre_tagged_terms)
    answer_clean = (claimant_answer or "").strip().lower()

    if not answer_clean:
        return {
            "is_match": False,
            "matched_keywords": [],
            "expected_keywords": expected_terms,
            "message": "No answer provided by claimant."
        }

    matched = []
    for term in expected_terms:
        # Check if term appears as substring or whole word
        if term in answer_clean:
            matched.append(term)

    is_match = len(matched) > 0

    if is_match:
        message = f"Verified: Found matching key details ({', '.join(matched)})."
    else:
        message = "Verification failed: None of the required distinctive key details were mentioned."

    return {
        "is_match": is_match,
        "matched_keywords": matched,
        "expected_keywords": expected_terms,
        "message": message
    }
