import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total Placements in Catalog: {len(jobs)}")
for i, j in enumerate(jobs):
    print(f"{i+1}. [{j['tier_class']}] {j['title']} @ {j['company']}")
    print(f"   Discipline: {j['discipline']} | Stipend: {j['stipend']}")
    print(f"   URL: {j['post_url']}")
