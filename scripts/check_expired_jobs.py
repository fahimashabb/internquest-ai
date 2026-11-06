import json
import requests
from bs4 import BeautifulSoup
import re
import time
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Checking {len(jobs)} jobs for expiration / closed status...")

closed_indicators = [
    "no longer accepting applications",
    "this job is closed",
    "this job is no longer open",
    "this position is closed",
    "application closed",
    "this job has expired",
    "job closed",
    "no longer available"
]

results = []

for i, job in enumerate(jobs):
    url = job["post_url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            text = r.text.lower()
            soup = BeautifulSoup(r.text, "html.parser")
            
            is_closed = False
            reason = ""

            # Check text indicators
            for ind in closed_indicators:
                if ind in text:
                    is_closed = True
                    reason = ind
                    break
            
            # Check specific LinkedIn closed banners
            if not is_closed:
                closed_banner = soup.find(class_=lambda x: x and ("closed" in x.lower() or "expired" in x.lower()))
                if closed_banner:
                    banner_text = closed_banner.get_text(strip=True).lower()
                    for ind in closed_indicators:
                        if ind in banner_text:
                            is_closed = True
                            reason = f"banner: {banner_text[:40]}"
                            break

            results.append({
                "job": job,
                "is_closed": is_closed,
                "reason": reason,
                "status_code": r.status_code
            })
            if is_closed:
                print(f"[CLOSED] ({reason}): [{job['company']}] {job['title']} -> {url}")
            else:
                print(f"[OPEN]: [{job['company']}] {job['title']}")
        else:
            results.append({
                "job": job,
                "is_closed": True,
                "reason": f"HTTP {r.status_code}",
                "status_code": r.status_code
            })
            print(f"[CLOSED - STATUS {r.status_code}]: [{job['company']}] {job['title']}")
    except Exception as e:
        results.append({
            "job": job,
            "is_closed": True,
            "reason": str(e),
            "status_code": 0
        })
        print(f"[ERR]: {e}")
    time.sleep(0.06)

open_jobs = [r for r in results if not r["is_closed"]]
closed_jobs = [r for r in results if r["is_closed"]]

print(f"\nSummary:")
print(f"Total: {len(jobs)}")
print(f"Open & Applyable: {len(open_jobs)}")
print(f"Closed / Expired: {len(closed_jobs)}")

# Save to check_results.json
with open("data/expiration_check_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "open_count": len(open_jobs),
        "closed_count": len(closed_jobs),
        "closed_jobs": [{
            "title": r["job"]["title"],
            "company": r["job"]["company"],
            "url": r["job"]["post_url"],
            "reason": r["reason"]
        } for r in closed_jobs]
    }, f, indent=2, ensure_ascii=False)
