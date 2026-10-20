import requests
import time
import json
import re
import sys
from filter_db_jobs import valid, is_valid_internship

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def norm_title(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9]", "", t)
    return t

dedup = {}
for title, comp, url in valid:
    nt = norm_title(title)
    if nt not in dedup:
        dedup[nt] = (title, comp, url)
    else:
        existing = dedup[nt]
        if any(agg in existing[1].lower() for agg in ["nextjobz", "skill jobs", "urban job", "bdjobs"]):
            if not any(agg in comp.lower() for agg in ["nextjobz", "skill jobs", "urban job", "bdjobs"]):
                dedup[nt] = (title, comp, url)

unique_jobs = list(dedup.values())
print(f"Total Unique Business Internships to test: {len(unique_jobs)}")

verified = []
for i, (title, comp, url) in enumerate(unique_jobs):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            final_u = r.url.lower()
            if not ("404" in final_u or "page-not-found" in final_u or "error" in final_u):
                verified.append((title, comp, url))
                print(f"[{i+1}/{len(unique_jobs)}] OK (200): {title} @ {comp}")
            else:
                print(f"[{i+1}/{len(unique_jobs)}] SOFT 404: {title}")
        else:
            print(f"[{i+1}/{len(unique_jobs)}] STATUS {r.status_code}: {title}")
    except Exception as e:
        print(f"[{i+1}/{len(unique_jobs)}] ERR: {e}")
    time.sleep(0.06)

print(f"\nFinal Verified Count: {len(verified)} out of {len(unique_jobs)}")
