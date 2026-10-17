"""Scraper for remote job boards (Jobicy, Remotive, etc.)."""
import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper, JobListing

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    if match:
        found = match.group(0).lower().strip(".")
        if not any(found.endswith(x) for x in [".png", ".jpg", ".jpeg", ".svg", ".webp"]):
            return found
    return None


class JobicyScraper(BaseScraper):
    name = "Jobicy"
    API_URL = "https://jobicy.com/api/v2/remote-jobs"

    def search(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[JobListing]:
        results: List[JobListing] = []
        tags = ["finance", "business", "operations", "accounting"]
        
        for tag in tags:
            try:
                params = {"count": max_results, "tag": tag}
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(self.API_URL, params=params, headers=headers, timeout=10)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                jobs = data.get("jobs", [])
                
                for item in jobs:
                    title = str(item.get("jobTitle") or "")
                    desc = clean_html(item.get("jobDescription", ""))
                    
                    job_type_val = item.get("jobType")
                    if isinstance(job_type_val, list):
                        job_type_str = " ".join(job_type_val).lower()
                    else:
                        job_type_str = str(job_type_val or "").lower()
                    
                    combined = f"{title} {job_type_str} {desc}".lower()
                    is_intern = any(k in combined for k in [
                        "intern", "internship", "entry", "trainee", "fellow", "junior", "associate", "assistant"
                    ])
                    
                    email = extract_email(desc)
                    url = item.get("url") or item.get("jobUrl", "")
                    
                    listing = JobListing(
                        title=title,
                        company=str(item.get("companyName") or "Unknown"),
                        location=str(item.get("jobGeo") or "Remote"),
                        url=url,
                        description=desc[:2000],
                        source=self.name,
                        contact_email=email,
                        posted_date=item.get("pubDate"),
                        is_internship=is_intern,
                        application_channel="email" if email else "web"
                    )
                    results.append(listing)
                    if len(results) >= max_results:
                        break
            except Exception as e:
                print(f"[{self.name}] Error querying tag {tag}: {e}")
                
        return results


class RemotiveScraper(BaseScraper):
    name = "Remotive"
    API_URL = "https://remotive.com/api/remote-jobs"

    def search(self, keywords: List[str], locations: List[str], max_results: int = 15) -> List[JobListing]:
        results: List[JobListing] = []
        categories = ["finance-legal", "business"]
        
        for cat in categories:
            try:
                params = {"category": cat, "limit": max_results}
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(self.API_URL, params=params, headers=headers, timeout=10)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                jobs = data.get("jobs", [])
                
                for item in jobs:
                    title = str(item.get("title") or "")
                    desc = clean_html(item.get("description", ""))
                    
                    combined = f"{title} {desc}".lower()
                    is_intern = any(k in combined for k in [
                        "intern", "internship", "entry", "trainee", "fellow", "junior", "associate", "assistant"
                    ])
                    
                    # Match relevant domain
                    is_relevant = any(k in combined for k in ["finance", "bank", "account", "operation", "analyst", "budget", "market", "business"])
                    if not is_relevant:
                        continue
                    
                    email = extract_email(desc)
                    url = str(item.get("url") or "")
                    
                    listing = JobListing(
                        title=title,
                        company=str(item.get("company_name") or "Unknown"),
                        location=str(item.get("candidate_required_location") or "Remote"),
                        url=url,
                        description=desc[:2000],
                        source=self.name,
                        contact_email=email,
                        posted_date=item.get("publication_date"),
                        is_internship=is_intern,
                        application_channel="email" if email else "web"
                    )
                    results.append(listing)
                    if len(results) >= max_results:
                        break
            except Exception as e:
                print(f"[{self.name}] Error querying category {cat}: {e}")
                
        return results
