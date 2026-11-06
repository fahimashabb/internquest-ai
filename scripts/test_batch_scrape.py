import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path("E:/CV hunter Webapp")
sys.path.insert(0, str(BASE_DIR))

# Let's test the search logic on 15 company queries with multi-threading
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

INTERN_REGEX = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)

def scrape(query_tuple):
    query, start = query_tuple
    api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    results = []
    try:
        params = {"keywords": query, "location": "Bangladesh", "start": start}
        resp = requests.get(api_url, params=params, headers=HEADERS, timeout=8)
        if resp.status_code == 200 and resp.text.strip():
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("div", class_="base-card")
            for card in cards:
                title_elem = card.find("h3", class_="base-search-card__title")
                comp_elem = card.find("h4", class_="base-search-card__subtitle")
                link_elem = card.find("a", class_="base-card__full-link")
                if title_elem and link_elem:
                    t = title_elem.get_text(strip=True)
                    c = comp_elem.get_text(strip=True) if comp_elem else "Corporate"
                    u = link_elem.get("href", "").split("?")[0]
                    if "linkedin.com/jobs/view" in u and INTERN_REGEX.search(t):
                        results.append((t, c, u))
    except Exception:
        pass
    return results

sample_queries = [
    ("internship Bangladesh", 0),
    ("internship Bangladesh", 25),
    ("finance intern Bangladesh", 0),
    ("finance intern Bangladesh", 25),
    ("marketing intern Bangladesh", 0),
    ("hr intern Bangladesh", 0),
    ("supply chain intern Bangladesh", 0),
    ("LafargeHolcim internship Bangladesh", 0),
    ("Marico internship Bangladesh", 0),
    ("Nestle internship Bangladesh", 0),
    ("City Bank internship Bangladesh", 0),
    ("BRAC Bank internship Bangladesh", 0),
    ("bKash internship Bangladesh", 0),
    ("Square internship Bangladesh", 0),
    ("PRAN internship Bangladesh", 0),
]

with ThreadPoolExecutor(max_workers=5) as ex:
    all_res = list(ex.map(scrape, sample_queries))

flattened = [item for sublist in all_res for item in sublist]
print(f"Sample run yielded {len(flattened)} candidate internships.")
unique_urls = set(item[2] for item in flattened)
print(f"Unique URLs: {len(unique_urls)}")
for t, c, u in flattened[:10]:
    print(f" + [{c}] {t}")
