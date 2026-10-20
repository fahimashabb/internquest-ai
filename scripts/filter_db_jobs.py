import sqlite3
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INTERN_REGEX = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)

NON_COMMERCE_EXCLUSIONS = [
    "developer", "software", "frontend", "backend", "laravel", "react", "flutter",
    "sqa", "qa engineer", "full stack", "devops", "civil engineer", "electrical",
    "mechanical", "chemical engineer", "lab testing", "textile lab", "textile engineer",
    "ui/ux", "graphic designer", "graphics intern", "video editor", "videographer", "photographer",
    "salesforce technical", "pharmacist", "microbiolog", "lawyer", "counsel",
    "test engineer", "motion design", "artificial intelligence", "data science",
    "it -", "it intern", "ai intern", "engineer intern", "architect intern", "designer intern"
]

SENIOR_FULLTIME_EXCLUSIONS = [
    "general manager", "senior manager", "agm", "dgm", "assistant accountant",
    "accounts assistant", "accounting specialist", "commercial executive",
    "junior executive", "officer,", "specialist,", "associate, customer",
    "finance assistant bangladesh", "accountant, accounts", "managerial trainee officer",
    "junior accounts executive", "accounts & finance executive", "executive - revenue",
    "supply chain associate", "inventory management specialist"
]

def is_valid_internship(title):
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

valid = []
for title, comp, url in rows:
    if is_valid_internship(title):
        clean_u = url.split("?")[0]
        valid.append((title, comp, clean_u))

print(f"Total view jobs in db matching valid internship criteria: {len(valid)}")
for v in valid[:25]:
    print(" +", v[0], "|", v[1], "|", v[2])
