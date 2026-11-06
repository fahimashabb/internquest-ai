import requests
from bs4 import BeautifulSoup
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

url = "https://bd.linkedin.com/jobs/view/hsbc-bangladesh-student-work-placement-programme-at-hsbc-4469880348"
r = requests.get(url, headers=HEADERS, timeout=10)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "html.parser")
closed_el = soup.find(class_=lambda x: x and "closed-job" in x.lower())
print("Found closed-job class?:", closed_el is not None)

# Check for apply button
apply_btn = soup.find(class_=lambda x: x and "apply" in x.lower())
print("Found apply button?:", apply_btn is not None)
