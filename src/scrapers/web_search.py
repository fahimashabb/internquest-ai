"""Web search scraper for targeted regional and global internship opportunities."""
import re
import urllib.parse
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper, JobListing

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def unwrap_ddg_url(raw_url: str) -> str:
    """Extract destination URL from DuckDuckGo redirect wrapper."""
    if "duckduckgo.com/l/?" in raw_url:
        parsed = urllib.parse.urlparse(raw_url)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params:
            return params["uddg"][0]
    return raw_url


class WebSearchScraper(BaseScraper):
    name = "WebSearch"
    SEARCH_URL = "https://html.duckduckgo.com/html/"

    def search(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[JobListing]:
        results: List[JobListing] = []
        queries = [
            'internship ("finance" OR "banking" OR "operations") Bangladesh 2026 OR 2025',
            '("finance intern" OR "financial analyst intern") ("Bangladesh" OR "Dhaka" OR "Remote")',
            '("BRAC" OR "Prime Bank" OR "bKash" OR "Standard Chartered") internship 2026',
            '("operations intern" OR "corporate finance intern") remote paid 2026'
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        for q in queries:
            try:
                resp = requests.post(
                    self.SEARCH_URL,
                    data={"q": q},
                    headers=headers,
                    timeout=12
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                result_blocks = soup.find_all("div", class_="result")

                for block in result_blocks:
                    title_elem = block.find("a", class_="result__a")
                    snippet_elem = block.find("a", class_="result__snippet")

                    if not title_elem:
                        continue

                    title_text = title_elem.get_text(strip=True)
                    snippet_text = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    raw_link = title_elem.get("href", "")
                    link = unwrap_ddg_url(raw_link)

                    # Simple heuristic to extract company name
                    company = "Target Organization"
                    if " - " in title_text:
                        parts = title_text.split(" - ")
                        company = parts[-1].strip()
                        title_text = " - ".join(parts[:-1]).strip()
                    elif " | " in title_text:
                        parts = title_text.split(" | ")
                        company = parts[-1].strip()
                        title_text = " | ".join(parts[:-1]).strip()

                    # Check for emails
                    email_match = EMAIL_REGEX.search(snippet_text)
                    contact_email = None
                    if email_match:
                        found = email_match.group(0).lower().strip(".")
                        if not any(found.endswith(x) for x in [".png", ".jpg", ".jpeg"]):
                            contact_email = found

                    listing = JobListing(
                        title=title_text,
                        company=company,
                        location="Bangladesh / Remote" if "bangladesh" in q.lower() else "Global / Remote",
                        url=link,
                        description=snippet_text,
                        source=self.name,
                        contact_email=contact_email,
                        is_internship=True,
                        application_channel="email" if contact_email else "web"
                    )
                    results.append(listing)
                    if len(results) >= max_results:
                        break

            except Exception as e:
                print(f"[{self.name}] Error searching '{q}': {e}")

            if len(results) >= max_results:
                break

        return results
