import requests
from bs4 import BeautifulSoup
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

url = "https://bd.linkedin.com/jobs/view/fresh-start-internship-program-at-singer-bangladesh-ltd-4474035821"
r = requests.get(url, headers=HEADERS, timeout=10)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "html.parser")
closed_el = soup.find(class_=lambda x: x and "closed" in x.lower())
if closed_el:
    print("Found closed class element tag:", closed_el.name, "classes:", closed_el.get("class"))
    print("Content:", closed_el.get_text(strip=True))

for line in soup.get_text().split("\n"):
    line_s = line.strip()
    if any(k in line_s.lower() for k in ["no longer accepting", "job is closed", "expired", "closed"]):
        print("  Text line:", line_s)
