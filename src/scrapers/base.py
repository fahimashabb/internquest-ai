"""Base models and abstract scraper for internship hunting."""
from abc import ABC, abstractmethod
from typing import List, Optional
import hashlib
from datetime import datetime
from pydantic import BaseModel, Field


class JobListing(BaseModel):
    id: str = ""
    title: str
    company: str
    location: str = "Worldwide / Remote"
    url: str
    description: str = ""
    source: str
    contact_email: Optional[str] = None
    posted_date: Optional[str] = None
    is_internship: bool = True
    match_score: Optional[int] = None
    match_rationale: Optional[str] = None
    tailored_email_subject: Optional[str] = None
    tailored_cover_letter: Optional[str] = None
    application_channel: str = "web"  # "email" or "web"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    def model_post_init(self, __context):
        if not self.id:
            # Generate deterministic hash from title, company, and url
            raw = f"{self.company.lower()}:{self.title.lower()}:{self.url.strip()}"
            self.id = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class BaseScraper(ABC):
    name: str = "BaseScraper"

    @abstractmethod
    def search(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[JobListing]:
        """Fetch and return matching internship job listings."""
        pass
