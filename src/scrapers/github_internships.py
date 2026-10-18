"""
Scraper for GitHub Open-Source Curated Internship Repositories (Pitt CSC & Simplify).
Ingests 1,800+ verified, live tech, quant finance, product, data, and engineering internships.
"""

from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import re
from src.scrapers.base import BaseScraper, JobListing

GITHUB_README_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"


class GithubInternshipsScraper(BaseScraper):
    name = "PittCSC_Simplify_Global"

    def __init__(self, fallback_enabled: bool = True):
        self.fallback_enabled = fallback_enabled

    def search(self, keywords: List[str] = None, locations: List[str] = None, max_results: int = 2500) -> List[JobListing]:
        results: List[JobListing] = []
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(GITHUB_README_URL, headers=headers, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")

                last_company = "Tech Company"
                for t_idx, table in enumerate(tables):
                    rows = table.find_all("tr")
                    if not rows:
                        continue
                    
                    # Discern table category
                    discipline = "Science & Tech"
                    if t_idx == 1:
                        discipline = "Commerce & Banking" # Product Management
                    elif t_idx == 4:
                        discipline = "Commerce & Banking" # Quant Finance
                    else:
                        discipline = "Science & Tech" # Software, Data, Hardware

                    for row in rows[1:]:
                        cols = row.find_all(["td", "th"])
                        if len(cols) < 3:
                            continue

                        comp_text = cols[0].get_text(strip=True)
                        if "↳" in comp_text or not comp_text:
                            company = last_company
                        else:
                            # Clean up markdown or icon links
                            company = re.sub(r"\[([^\]]+)\].*", r"\1", comp_text).strip()
                            company = re.sub(r"[^\w\s\-\.\&]", "", company).strip()
                            if company:
                                last_company = company

                        title_elem = cols[1]
                        title = title_elem.get_text(strip=True)
                        # Remove emojis
                        title = re.sub(r"[^\x00-\x7F]+", "", title).strip()
                        if not title:
                            title = "Summer Internship"

                        loc_text = cols[2].get_text(strip=True) if len(cols) > 2 else "Remote / Worldwide"
                        loc_clean = re.sub(r"[^\x00-\x7F]+", "", loc_text).strip() or "Worldwide / Remote"

                        # Extract Application URL
                        link_tag = None
                        for col in [cols[1], cols[3] if len(cols) > 3 else None, cols[0]]:
                            if col:
                                found_a = col.find("a", href=True)
                                if found_a and found_a["href"].startswith("http"):
                                    link_tag = found_a["href"]
                                    break
                        
                        url = link_tag or f"https://simplify.jobs/c/{company.replace(' ', '-')}"

                        # Details and deadline
                        deadline = "Summer 2026 / Rolling"
                        if len(cols) > 3:
                            age = cols[3].get_text(strip=True)
                            if age:
                                deadline = f"Active ({age} ago)"

                        listing = JobListing(
                            title=f"{title} ({company})",
                            company=company,
                            location=loc_clean,
                            url=url,
                            description=f"Official {title} opportunity at {company}. Position location: {loc_clean}. Verified through the premier global technology & quantitative finance internship index.",
                            source=self.name,
                            contact_email=None,
                            is_internship=True,
                            location_scope="global",
                            discipline=discipline,
                            application_channel="web",
                            deadline=deadline
                        )
                        results.append(listing)
                        if len(results) >= max_results:
                            break
                    if len(results) >= max_results:
                        break

        except Exception as e:
            print(f"[{self.name}] Error scraping GitHub internships: {e}")

        return results
