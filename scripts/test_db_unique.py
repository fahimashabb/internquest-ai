import sqlite3
import re
import json

INTERN_REGEX = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)

NON_COMMERCE_EXCLUSIONS = [
    "developer", "software", "frontend", "backend", "laravel", "react", "flutter",
    "sqa", "qa engineer", "full stack", "devops", "civil engineer", "electrical",
    "mechanical", "chemical engineer", "lab testing", "textile lab", "textile engineer",
    "ui/ux", "graphic designer", "graphics intern", "video editor", "videographer", "photographer",
    "salesforce technical", "pharmacist", "microbiolog", "lawyer", "counsel",
    "test engineer", "motion design", "artificial intelligence", "data science",
    "it -", "it intern", "ai intern", "engineer intern", "architect intern", "designer intern",
    "engineering internship", "ai builders", "competitive programming"
]

SENIOR_FULLTIME_EXCLUSIONS = [
    "general manager", "senior manager", "agm", "dgm", "assistant accountant",
    "accounts assistant", "accounting specialist", "commercial executive",
    "junior executive", "officer,", "specialist,", "associate, customer",
    "finance assistant bangladesh", "accountant, accounts", "managerial trainee officer",
    "junior accounts executive", "accounts & finance executive", "executive - revenue",
    "supply chain associate", "inventory management specialist"
]

def is_valid_internship(title: str) -> bool:
    tl = title.strip().lower()
    if tl in ("intern", "internship", "trainee", "student"):
        return False
    if not INTERN_REGEX.search(title):
        return False
    if any(ex in tl for ex in NON_COMMERCE_EXCLUSIONS):
        return False
    for s in SENIOR_FULLTIME_EXCLUSIONS:
        if s in tl and not ("intern" in tl or "internship" in tl or "placement" in tl):
            return False
    return True

conn = sqlite3.connect("data/applications.db")
c = conn.cursor()
c.execute("SELECT title, company, url FROM jobs WHERE url LIKE '%linkedin.com/jobs/view%'")
rows = c.fetchall()
conn.close()

# Deduplicate by (norm_title, company) or by URL
by_url = {}
for t, comp, u in rows:
    if is_valid_internship(t):
        clean_u = u.split("?")[0]
        by_url[clean_u] = (t, comp, clean_u)

print(f"Total valid unique URL postings in db: {len(by_url)}")
