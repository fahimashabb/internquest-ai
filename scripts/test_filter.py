import json
import re
import requests

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

pattern = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)
matched = [j for j in jobs if pattern.search(j["title"])]

print(f"Total matched: {len(matched)}")
for i, j in enumerate(matched):
    print(f"{i+1}. [{j.get('company')}] {j.get('title')}")
    print(f"    URL: {j.get('post_url')}")
