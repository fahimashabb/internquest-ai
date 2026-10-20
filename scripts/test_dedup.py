import json
import re

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

pattern = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)
matched = [j for j in jobs if pattern.search(j["title"])]

def norm_title(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9]", "", t)
    return t

seen = {}
for j in matched:
    t = j["title"]
    comp = j["company"]
    nt = norm_title(t)
    
    # Check if we already have this normalized title
    if nt in seen:
        existing = seen[nt]
        # Prefer direct employer over nextjobz/distributor
        if "nextjobz" in existing["company"].lower() and "nextjobz" not in comp.lower():
            seen[nt] = j
    else:
        seen[nt] = j

deduped = list(seen.values())
print(f"Original matched: {len(matched)}")
print(f"Deduplicated: {len(deduped)}")
for i, d in enumerate(deduped):
    print(f"{i+1}. [{d['company']}] {d['title']}")
