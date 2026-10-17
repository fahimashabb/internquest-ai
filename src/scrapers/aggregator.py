"""Job Aggregator combining ALL scrapers — Bangladesh-focused + remote boards."""
from typing import List
from src.config import AppSettings, load_settings
from src.scrapers.base import JobListing
from src.scrapers.remote_boards import JobicyScraper, RemotiveScraper
from src.scrapers.linkedin_guest import LinkedInGuestScraper
from src.scrapers.bangladesh_companies import BangladeshCompanyScraper


class JobAggregator:
    def __init__(self, settings: AppSettings = None):
        self.settings = settings or load_settings()
        self.scrapers = [
            BangladeshCompanyScraper(),   # Priority 1: Every major BD company/bank/NGO
            LinkedInGuestScraper(),        # Priority 2: General LinkedIn Bangladesh search
            JobicyScraper(),               # Priority 3: Remote finance boards
            RemotiveScraper(),             # Priority 4: Remote business/finance boards
        ]

    def fetch_all(self) -> List[JobListing]:
        """Query all scrapers and return deduplicated list of internship listings."""
        all_jobs: List[JobListing] = []
        seen_ids = set()
        seen_urls = set()

        keywords = self.settings.search.keywords
        locations = self.settings.search.locations
        max_per_source = self.settings.search.max_results_per_source

        for scraper in self.scrapers:
            try:
                print(f"[Aggregator] Running {scraper.name}...")
                jobs = scraper.search(keywords, locations, max_results=max_per_source)
                added = 0
                for job in jobs:
                    if self.settings.filtering.require_internship and not job.is_internship:
                        continue
                    clean_url = job.url.split("?")[0].rstrip("/")
                    if job.id in seen_ids or clean_url in seen_urls:
                        continue
                    seen_ids.add(job.id)
                    seen_urls.add(clean_url)
                    all_jobs.append(job)
                    added += 1
                print(f"[Aggregator] {scraper.name}: +{added} new unique listings")
            except Exception as e:
                print(f"[Aggregator] Error running {scraper.name}: {e}")

        return all_jobs
