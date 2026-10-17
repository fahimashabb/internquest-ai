"""LinkedIn Public Guest Job Search Scraper (No login or credentials required)."""
import re
import urllib.parse
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper, JobListing

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    if match:
        found = match.group(0).lower().strip(".")
        if not any(found.endswith(x) for x in [".png", ".jpg", ".jpeg", ".svg"]):
            return found
    return None


class LinkedInGuestScraper(BaseScraper):
    name = "LinkedInGuest"
    BASE_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def search(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[JobListing]:
        results: List[JobListing] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Select top keywords and locations
        active_keywords = keywords[:3] if keywords else ["Finance Intern", "Banking Intern"]
        active_locations = locations[:2] if locations else ["Bangladesh", "Remote"]

        for kw in active_keywords:
            for loc in active_locations:
                try:
                    params = {
                        "keywords": kw,
                        "location": loc,
                        "start": 0,
                    }
                    resp = requests.get(self.BASE_API, params=params, headers=headers, timeout=12)
                    if resp.status_code != 200 or not resp.text.strip():
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")
                    cards = soup.find_all("div", class_="base-card")

                    for card in cards:
                        title_elem = card.find("h3", class_="base-search-card__title")
                        comp_elem = card.find("h4", class_="base-search-card__subtitle")
                        loc_elem = card.find("span", class_="job-search-card__location")
                        link_elem = card.find("a", class_="base-card__full-link")
                        time_elem = card.find("time")

                        if not title_elem or not link_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = comp_elem.get_text(strip=True) if comp_elem else "Unknown"
                        location_str = loc_elem.get_text(strip=True) if loc_elem else loc
                        raw_link = link_elem.get("href", "")
                        clean_link = raw_link.split("?")[0]
                        posted_date = time_elem.get_text(strip=True) if time_elem else "Recent"

                        # Check description if available or fetch brief description
                        desc = f"{title} at {company} located in {location_str}."
                        contact_email = None

                        try:
                            detail_resp = requests.get(clean_link, headers=headers, timeout=8)
                            if detail_resp.status_code == 200:
                                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                                desc_elem = detail_soup.find("div", class_="show-more-less-html__markup")
                                if desc_elem:
                                    full_desc = desc_elem.get_text(separator=" ", strip=True)
                                    desc = full_desc[:2500]
                                    contact_email = extract_email(desc)
                        except Exception:
                            pass

                        is_intern = any(k in title.lower() or k in desc.lower() for k in [
                            "intern", "internship", "trainee", "entry", "fellow", "junior", "assistant"
                        ])

                        listing = JobListing(
                            title=title,
                            company=company,
                            location=location_str,
                            url=clean_link,
                            description=desc,
                            source=self.name,
                            contact_email=contact_email,
                            posted_date=posted_date,
                            is_internship=is_intern,
                            application_channel="email" if contact_email else "web"
                        )
                        results.append(listing)
                        if len(results) >= max_results:
                            return results

                except Exception as e:
                    print(f"[{self.name}] Error searching {kw} in {loc}: {e}")

        return results
