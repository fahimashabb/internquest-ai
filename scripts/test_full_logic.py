import re
import json

# Let's inspect data/business_internships.json
with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Current jobs: {len(jobs)}")
