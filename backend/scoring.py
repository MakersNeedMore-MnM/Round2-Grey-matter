import re
from datetime import datetime
from typing import Optional, Dict, Tuple
import numpy as np

from backend.embeddings import (
    get_text_embedding,
    get_image_embedding,
    cosine_similarity,
)


def compute_keyword_match_score(found_description: str, lost_description: str) -> float:
    """
    Standard legacy keyword matching (exact word / token overlap).
    Returns 0.0 for mismatched wording (e.g. 'navy backpack' vs 'black rucksack').
    """
    generic_words = {
        "with", "and", "or", "in", "on", "at", "to", "for", "a", "an", "the", "of", "by", "is", "it",
        "inside", "near", "side", "dual", "padded", "bottom", "straps", "top", "small", "dark", "light"
    }
    words_found = set(w.lower() for w in re.findall(r"\w+", found_description or "") if len(w) > 2 and w.lower() not in generic_words)
    words_lost = set(w.lower() for w in re.findall(r"\w+", lost_description or "") if len(w) > 2 and w.lower() not in generic_words)
    
    if not words_found or not words_lost:
        return 0.0
    
    overlap = words_found.intersection(words_lost)
    if not overlap:
        return 0.0
    return round(len(overlap) / max(len(words_found), len(words_lost)), 4)


def generate_plain_language_driver(
    visual_score: float,
    text_score: float,
    location_score: float,
    time_score: float,
    has_photo: bool,
) -> str:
    """
    Generate plain-language line explaining which signal drove the match decision (Priority 3):
    - If visual_score is the highest component: "Matched primarily on photo similarity, despite different wording."
    - If text_score is highest: "Matched primarily on description similarity."
    - If location_score + time_score together dominate: "Matched primarily on where and when it was found."
    """
    if has_photo and visual_score >= 0.65 and visual_score >= text_score:
        if text_score < 0.60:
            return "Matched primarily on photo similarity, despite different wording."
        return "Matched primarily on strong visual and semantic similarity."
    elif (location_score + time_score) / 2.0 > max(visual_score, text_score) and location_score >= 0.80:
        return "Matched primarily on where and when it was found."
    elif text_score >= visual_score:
        return "Matched primarily on description similarity."
    else:
        return "Matched primarily on photo similarity, despite different wording."


# Location similarity zone classification
def compute_location_similarity(loc1: str, loc2: str) -> float:
    """
    Calculate location similarity using station zone adjacency rules.
    """
    l1 = (loc1 or "").strip().lower()
    l2 = (loc2 or "").strip().lower()

    if not l1 or not l2:
        return 0.3

    if l1 == l2:
        return 1.0

    # Define station zone groupings
    zones = {
        "platform_central": ["platform 1", "platform 2", "platform 3", "platform 4", "platform 5", "near track"],
        "concourse": ["ticket counter", "main concourse", "waiting hall", "enquiry counter", "vip lounge", "near ticket counter", "central hall"],
        "commercial": ["food court", "cafeteria", "refreshment stall", "book stall", "tea stall"],
        "train": ["coach b4", "coach a1", "coach s2", "berth", "train compartment", "ac coach"],
        "exit_parking": ["parking lot", "auto stand", "east entry", "west entry", "taxi stand", "main gate"],
    }

    # Find matching zones
    zone1 = None
    zone2 = None

    for z_name, keywords in zones.items():
        if any(kw in l1 for kw in keywords):
            zone1 = z_name
        if any(kw in l2 for kw in keywords):
            zone2 = z_name

    # Same zone
    if zone1 and zone2 and zone1 == zone2:
        return 0.90

    # Adjacent / highly related zones
    adjacent_pairs = {
        ("platform_central", "concourse"): 0.80,
        ("concourse", "platform_central"): 0.80,
        ("concourse", "commercial"): 0.85,
        ("commercial", "concourse"): 0.85,
        ("platform_central", "train"): 0.85,
        ("train", "platform_central"): 0.85,
        ("platform_central", "commercial"): 0.70,
        ("commercial", "platform_central"): 0.70,
        ("concourse", "exit_parking"): 0.75,
        ("exit_parking", "concourse"): 0.75,
    }

    if (zone1, zone2) in adjacent_pairs:
        return adjacent_pairs[(zone1, zone2)]

    # Substring / keyword overlap heuristic
    words1 = set(l1.replace(",", " ").replace("-", " ").split())
    words2 = set(l2.replace(",", " ").replace("-", " ").split())
    common = words1.intersection(words2)
    if common:
        return 0.75

    # Default baseline for same general facility
    return 0.40


def compute_time_similarity(found_at: datetime, lost_at: datetime) -> float:
    """
    Calculate time similarity: max(0, 1 - (days_between / 14))
    Linear 14-day decay window floored at 0.
    """
    if not found_at or not lost_at:
        return 0.5

    delta_seconds = abs((found_at - lost_at).total_seconds())
    days_between = delta_seconds / 86400.0

    score = max(0.0, 1.0 - (days_between / 14.0))
    return round(score, 4)


def compute_fused_score(
    found_description: str,
    found_location: str,
    found_at: datetime,
    found_photo_path: Optional[str],
    lost_description: str,
    lost_location: str,
    lost_at: datetime,
    lost_photo_path: Optional[str],
) -> Dict[str, any]:
    """
    Calculate fused similarity score across Visual, Text, Location, and Time.
    Handles weight re-normalization when lost report lacks a photo.
    Also computes legacy keyword score (Priority 1) and plain-language driver (Priority 3).
    """
    # 1. Text Similarity (Semantic)
    v_text_found = get_text_embedding(found_description)
    v_text_lost = get_text_embedding(lost_description)
    text_score = cosine_similarity(v_text_found, v_text_lost)

    # Legacy Keyword Score
    keyword_score = compute_keyword_match_score(found_description, lost_description)

    # 2. Location Similarity
    location_score = compute_location_similarity(found_location, lost_location)

    # 3. Time Similarity
    time_score = compute_time_similarity(found_at, lost_at)

    # 4. Visual Similarity
    has_photo = bool(lost_photo_path and lost_photo_path.strip())
    visual_score = 0.0

    if has_photo and found_photo_path:
        v_img_found = get_image_embedding(found_photo_path)
        v_img_lost = get_image_embedding(lost_photo_path)
        if v_img_found is not None and v_img_lost is not None:
            visual_score = cosine_similarity(v_img_found, v_img_lost)
        else:
            has_photo = False

    # Fusion calculation
    if has_photo:
        fused = (
            (0.40 * visual_score)
            + (0.30 * text_score)
            + (0.15 * location_score)
            + (0.15 * time_score)
        )
        explanation = (
            f"Full 4-way fusion: Visual (40% * {visual_score:.2f}) + "
            f"Text (30% * {text_score:.2f}) + "
            f"Location (15% * {location_score:.2f}) + "
            f"Time (15% * {time_score:.2f})"
        )
    else:
        # Re-normalized weights: Text (50%), Location (25%), Time (25%)
        fused = (
            (0.50 * text_score)
            + (0.25 * location_score)
            + (0.25 * time_score)
        )
        explanation = (
            f"Re-normalized fusion (no photo on lost report): "
            f"Text (50% * {text_score:.2f}) + "
            f"Location (25% * {location_score:.2f}) + "
            f"Time (25% * {time_score:.2f})"
        )

    # Generate plain language driver (Priority 3)
    driver_explanation = generate_plain_language_driver(
        visual_score=visual_score,
        text_score=text_score,
        location_score=location_score,
        time_score=time_score,
        has_photo=has_photo,
    )

    return {
        "visual_score": round(visual_score, 4),
        "text_score": round(text_score, 4),
        "location_score": round(location_score, 4),
        "time_score": round(time_score, 4),
        "fused_score": round(fused, 4),
        "keyword_score": round(keyword_score, 4),
        "has_photo": has_photo,
        "explanation": explanation,
        "driver_explanation": driver_explanation,
    }
