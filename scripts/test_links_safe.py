import requests
import time
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Load the 43 jobs from test_dedup
from test_dedup import deduped

print(f"Testing {len(deduped)} jobs with gentle pacing...")
success = 0
failed = 0
for i, j in enumerate(deduped):
    url = j["post_url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            success += 1
        else:
            print(f"Status {r.status_code}: {j['title']} -> {url}")
            failed += 1
    except Exception as e:
        print(f"Error {e}: {j['title']}")
        failed += 1
    time.sleep(0.08)

print(f"Done: {success} passed, {failed} failed.")
