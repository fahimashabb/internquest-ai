import requests
import time
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

# Let's inspect the ones from raw_candidates before filtering
with open("scripts/test_dedup.py", "r", encoding="utf-8") as f:
    pass
