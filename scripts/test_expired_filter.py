import json
import requests
from bs4 import BeautifulSoup
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

print(f"Total jobs in business_internships.json: {len(jobs)}")

EXPIRED_INDICATORS = [
    "no longer accepting applications",
    "আর আবেদনপত্র গ্রহণ করা হচ্ছে না",
    "this job is closed",
    "this position is closed",
    "this job has expired",
    "applications are closed",
    "application closed"
]

def check_job_status(job):
    url = job["post_url"]
    for attempt in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                final_u = r.url.lower()
                if "404" in final_u or "page-not-found" in final_u or "error" in final_u:
                    return False, "404 redirect"
                
                soup = BeautifulSoup(r.text, "html.parser")
                # 1. Closed CSS class
                if soup.find(class_=lambda x: x and ("closed-job" in x.lower() or "closed_job" in x.lower())):
                    return False, "closed-job class"
                
                # 2. Text indicator
                text = r.text.lower()
                for ind in EXPIRED_INDICATORS:
                    if ind in text:
                        return False, f"text: {ind}"
                
                return True, "open"
            elif r.status_code in (404, 410):
                return False, f"HTTP {r.status_code}"
            elif r.status_code in (429, 999):
                time.sleep(1.2)
                continue
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            if attempt == 0:
                time.sleep(1.0)
                continue
            return False, str(e)
    return False, "timeout / rate limit"

open_list = []
expired_list = []

for i, j in enumerate(jobs):
    is_open, reason = check_job_status(j)
    if is_open:
        open_list.append(j)
        print(f"[{i+1}/{len(jobs)}] OPEN: [{j['company']}] {j['title']}")
    else:
        expired_list.append((j, reason))
        print(f"[{i+1}/{len(jobs)}] EXPIRED/CLOSED ({reason}): [{j['company']}] {j['title']}")
    time.sleep(0.06)

print(f"\n==============================")
print(f"Total checked: {len(jobs)}")
print(f"Active & Open: {len(open_list)}")
print(f"Expired/Closed to remove: {len(expired_list)}")
print(f"==============================")
for j, r in expired_list:
    print(f" - REMOVE: [{j['company']}] {j['title']} ({r})")
