# ============================================================
# scraper/core/models.py
# Pydantic data models for scraped estate leads
# ============================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class EstateRecord(BaseModel):
    """Single estate/business record scraped from Google Maps."""

    # Identity
    name: str
    place_id: Optional[str] = None
    maps_url: Optional[str] = None

    # Location
    address: Optional[str] = None
    state: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Contact
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None

    # Profile
    category: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    opening_hours: Optional[str] = None
    management_company: Optional[str] = None
    description: Optional[str] = None

    # Lead scoring
    lead_score: Optional[float] = None
    lead_tier: Optional[str] = None  # "HOT", "WARM", "COLD"

    # Meta
    search_query: Optional[str] = None
    search_keyword: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    data_quality: Optional[str] = None  # "complete", "partial", "minimal"

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, v):
        if not v:
            return None
        # Normalise Nigerian phone numbers
        cleaned = re.sub(r"[^\d+\-\s()]", "", str(v)).strip()
        return cleaned if cleaned else None

    @field_validator("website", mode="before")
    @classmethod
    def clean_website(cls, v):
        if not v:
            return None
        v = str(v).strip()
        if v and not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v

    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        if v is None:
            return None
        try:
            return float(str(v).replace(",", "."))
        except (ValueError, TypeError):
            return None

    def compute_data_quality(self) -> str:
        filled = sum([
            bool(self.phone),
            bool(self.website),
            bool(self.address),
            bool(self.rating),
            bool(self.review_count),
            bool(self.maps_url),
        ])
        if filled >= 5:
            return "complete"
        elif filled >= 3:
            return "partial"
        return "minimal"

    def to_export_dict(self) -> dict:
        """Flat dict for CSV/Excel export."""
        return {
            "Estate Name": self.name,
            "Google Maps URL": self.maps_url,
            "Address": self.address,
            "State": self.state,
            "Area / LGA": self.area,
            "Phone": self.phone,
            "Website": self.website,
            "Email": self.email,
            "Category": self.category,
            "Rating": self.rating,
            "Review Count": self.review_count,
            "Opening Hours": self.opening_hours,
            "Management Company": self.management_company,
            "Latitude": self.latitude,
            "Longitude": self.longitude,
            "Lead Score": self.lead_score,
            "Lead Tier": self.lead_tier,
            "Search Query": self.search_query,
            "Data Quality": self.data_quality or self.compute_data_quality(),
            "Scraped At": self.scraped_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
