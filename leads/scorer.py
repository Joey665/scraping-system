# ============================================================
# leads/scorer.py
# Intelligent lead qualification and scoring engine
# ============================================================

import re
from typing import Optional
from scraper.core.models import EstateRecord
from config.settings import settings

# Keywords that indicate high-value / luxury estate
LUXURY_KEYWORDS = [
    "luxury", "premium", "exclusive", "elite", "high-end", "prestigious",
    "prime", "signature", "grand", "royal", "imperial", "platinum", "diamond",
    "gold", "executive", "deluxe", "sophisticated", "gated", "secured", "serviced",
    "lekki phase 1", "ikoyi", "victoria island", "vi", "maitama", "asokoro",
    "wuse 2", "banana island", "oniru", "osapa london", "ocean view",
    "ocean front", "beachfront", "waterfront", "smart home", "smart estate",
]

# Keywords suggesting mid-tier estates
MID_TIER_KEYWORDS = [
    "estate", "residential", "community", "housing", "gated", "close",
    "court", "crescent", "avenue", "gardens", "park", "heights", "terrace",
    "villas", "manor", "grove", "place", "scheme",
]

# Negative signals — disorganized or low-value
NEGATIVE_SIGNALS = [
    "bungalow", "face me i face you", "tenement", "kiosk", "shop",
    "market", "informal", "temporary",
]

WEBSITE_ABSENCE_OPPORTUNITY_BONUS = 5.0  # No website = opportunity to sell digital infra


def score_lead(record: EstateRecord) -> tuple[float, str]:
    """
    Score a lead 0–100. Returns (score, tier).
    Tier: "HOT" (70+), "WARM" (40–69), "COLD" (<40)
    """
    score = 0.0
    name_lower = (record.name or "").lower()
    address_lower = (record.address or "").lower()
    combined_text = f"{name_lower} {address_lower}"

    # ---- 1. Review count (0–25 pts) ----
    review_count = record.review_count or 0
    if review_count >= 100:
        review_score = 25.0
    elif review_count >= 50:
        review_score = 20.0
    elif review_count >= 20:
        review_score = 15.0
    elif review_count >= 5:
        review_score = 8.0
    elif review_count > 0:
        review_score = 3.0
    else:
        review_score = 0.0
    score += review_score * settings.SCORE_WEIGHT_REVIEWS / 0.25

    # ---- 2. Rating (0–15 pts) ----
    rating = record.rating or 0.0
    if rating >= 4.5:
        rating_score = 15.0
    elif rating >= 4.0:
        rating_score = 12.0
    elif rating >= 3.5:
        rating_score = 8.0
    elif rating > 0:
        rating_score = 4.0
    else:
        rating_score = 0.0
    score += rating_score

    # ---- 3. Website presence (0–20 pts) ----
    if record.website:
        score += 10.0  # Has website = somewhat digital-mature
    else:
        score += WEBSITE_ABSENCE_OPPORTUNITY_BONUS  # No website = BIGGER opportunity for us

    # ---- 4. Luxury keyword match (0–25 pts) ----
    luxury_hits = sum(1 for kw in LUXURY_KEYWORDS if kw in combined_text)
    luxury_score = min(25.0, luxury_hits * 8.0)
    score += luxury_score

    # ---- 5. Has phone number (0–15 pts) ----
    if record.phone:
        score += 15.0

    # ---- 6. Mid-tier keyword bonus (0–10 pts) ----
    mid_hits = sum(1 for kw in MID_TIER_KEYWORDS if kw in combined_text)
    score += min(10.0, mid_hits * 3.0)

    # ---- 7. Negative signal penalty ----
    neg_hits = sum(1 for kw in NEGATIVE_SIGNALS if kw in combined_text)
    score = max(0.0, score - (neg_hits * 10.0))

    # ---- 8. Address quality bonus ----
    if record.address and len(record.address) > 20:
        score += 5.0

    # ---- Normalise to 0–100 ----
    score = min(100.0, round(score, 1))

    # ---- Tier assignment ----
    if score >= 70:
        tier = "HOT"
    elif score >= 40:
        tier = "WARM"
    else:
        tier = "COLD"

    return score, tier


def classify_estate_segment(record: EstateRecord) -> str:
    """
    Returns a sales segment for outreach customisation:
    'luxury', 'mid-tier', 'new-development', 'disorganized'
    """
    name_lower = (record.name or "").lower()
    reviews = record.review_count or 0

    luxury_hits = sum(1 for kw in LUXURY_KEYWORDS if kw in name_lower)
    if luxury_hits >= 2 or any(loc in name_lower for loc in ["ikoyi", "banana island", "maitama", "asokoro"]):
        return "luxury"

    if reviews < 5 and not record.website and not record.phone:
        return "disorganized"

    if reviews == 0 and record.rating is None:
        return "new-development"

    return "mid-tier"


def score_all_records(records: list[EstateRecord]) -> list[EstateRecord]:
    """Apply scoring to a list of records in place."""
    for r in records:
        r.lead_score, r.lead_tier = score_lead(r)
    records.sort(key=lambda x: x.lead_score or 0, reverse=True)
    return records


def get_hot_prospects(records: list[EstateRecord]) -> list[EstateRecord]:
    """Return only HOT tier leads."""
    return [r for r in records if r.lead_tier == "HOT"]
