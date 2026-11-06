import json
import re

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Current catalog size: {len(jobs)}")
titles = [j['title'] for j in jobs]
print(f"Unique titles: {len(set(titles))}")
