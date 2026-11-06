import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

INTERN_REGEX = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)

api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

queries = [
    "internship Bangladesh",
    "intern Bangladesh",
    "business intern Bangladesh",
    "Marico internship Bangladesh",
    "Nestle internship Bangladesh",
    "City Bank internship Bangladesh",
    "IDLC internship Bangladesh",
    "EBL internship Bangladesh"
]

for q in queries:
    for start in [0, 25]:
        params = {"keywords": q, "location": "Bangladesh", "start": start}
        try:
            r = requests.get(api_url, params=params, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                cards = soup.find_all("div", class_="base-card")
                print(f"Query: '{q}' (start={start}) -> found {len(cards)} cards")
                for c in cards[:3]:
                    t = c.find("h3", class_="base-search-card__title")
                    comp = c.find("h4", class_="base-search-card__subtitle")
                    if t:
                        print("   -", t.get_text(strip=True), "|", comp.get_text(strip=True) if comp else "")
        except Exception as e:
            print("Err:", e)
