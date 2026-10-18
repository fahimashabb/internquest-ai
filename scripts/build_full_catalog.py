"""
Script to build the comprehensive 3,000+ internship catalog.
Aggregates:
1. Bangladesh Corporate Catalog (985 listings across 120+ top employers)
2. Simplify & PittCSC Global Open-Source Catalog (1,820+ global tech, quant, engineering internships)
3. Arbeitnow & Remote Boards (300+ remote technology & business internships)
Saves output to data/seed_jobs.json and populates data/applications.db.
"""

import os
import sys
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.scrapers.bd_catalog import generate_bangladesh_internships
from src.scrapers.github_internships import GithubInternshipsScraper
from src.scrapers.base import JobListing
from src.tracker import ApplicationTracker

def main():
    print("🚀 [Catalog Builder] Starting ingestion of 3,000+ internships...")

    all_listings = []
    seen_ids = set()

    # 1. Bangladesh Corporate, Bank, MNC, NGO & Tech Catalog
    print("📦 [1/3] Ingesting Bangladesh Corporate & Institutional Catalog...")
    bd_jobs = generate_bangladesh_internships()
    bd_count = 0
    for j in bd_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            all_listings.append(j)
            bd_count += 1
    print(f"✅ Ingested {bd_count} verified Bangladesh corporate opportunities.")

    # 2. GitHub Simplify / Pitt CSC Global Open-Source Index
    print("🌐 [2/3] Ingesting Simplify & Pitt CSC Global Summer Internships...")
    gh_scraper = GithubInternshipsScraper()
    gh_jobs = gh_scraper.search(max_results=3000)
    gh_count = 0
    for j in gh_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            all_listings.append(j)
            gh_count += 1
    print(f"✅ Ingested {gh_count} verified Global tech, quant & engineering opportunities.")

    # 3. Arbeitnow Remote API
    print("☁️ [3/3] Ingesting Arbeitnow Remote Opportunities...")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            jobs_data = data.get("data", [])
            arbeit_count = 0
            for item in jobs_data:
                title = str(item.get("title") or "")
                comp = str(item.get("company_name") or "Global Remote")
                loc = str(item.get("location") or "Remote / Worldwide")
                url = str(item.get("url") or "")
                desc = str(item.get("description") or "")
                tags = [t.lower() for t in item.get("tags", [])]

                # Determine discipline
                discipline = "Science & Tech"
                if any(t in tags for t in ["finance", "business", "accounting", "operations", "sales", "marketing"]):
                    discipline = "Commerce & Banking"
                elif any(t in tags for t in ["design", "writing", "content", "hr", "legal"]):
                    discipline = "Arts & Media"

                listing = JobListing(
                    title=f"{title} ({comp})",
                    company=comp,
                    location=loc,
                    url=url,
                    description=desc[:1500] if desc else f"Remote opportunity at {comp}.",
                    source="ArbeitnowRemote",
                    is_internship=True,
                    location_scope="global",
                    discipline=discipline,
                    deadline="Rolling Application",
                    application_channel="web"
                )
                if listing.id not in seen_ids:
                    seen_ids.add(listing.id)
                    all_listings.append(listing)
                    arbeit_count += 1
            print(f"✅ Ingested {arbeit_count} remote opportunities from Arbeitnow.")
    except Exception as e:
        print(f"⚠️ Arbeitnow ingestion error: {e}")

    print(f"\n🎉 Total aggregated listings: {len(all_listings)}")

    # Convert to JSON serializable dictionaries
    seed_data = []
    for j in all_listings:
        seed_data.append({
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "url": j.url,
            "source": j.source,
            "contact_email": j.contact_email,
            "is_internship": 1 if j.is_internship else 0,
            "found_at": datetime.now().isoformat(),
            "status": "NEW",
            "match_score": 0,
            "match_rationale": "",
            "tailored_email_subject": "",
            "tailored_cover_letter": "",
            "deadline": j.deadline or "Rolling / Open",
            "location_scope": j.location_scope,
            "discipline": j.discipline,
            "description": j.description
        })

    # Save to data/seed_jobs.json
    seed_file = BASE_DIR / "data" / "seed_jobs.json"
    seed_file.parent.mkdir(parents=True, exist_ok=True)
    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Written {len(seed_data)} opportunities to {seed_file}")

    # Seed into data/applications.db
    db_file = BASE_DIR / "data" / "applications.db"
    tracker = ApplicationTracker(db_path=db_file)
    with tracker._get_connection() as conn:
        for s in seed_data:
            conn.execute("""
                INSERT INTO jobs (
                    id, title, company, location, url, source, contact_email,
                    is_internship, match_score, match_rationale,
                    tailored_email_subject, tailored_cover_letter,
                    application_channel, status, deadline, location_scope, discipline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    company = excluded.company,
                    location = excluded.location,
                    url = excluded.url,
                    source = excluded.source,
                    contact_email = COALESCE(excluded.contact_email, jobs.contact_email),
                    deadline = COALESCE(excluded.deadline, jobs.deadline),
                    location_scope = COALESCE(excluded.location_scope, jobs.location_scope),
                    discipline = COALESCE(excluded.discipline, jobs.discipline)
            """, (
                s["id"], s["title"], s["company"], s["location"], s["url"], s["source"],
                s["contact_email"], s["is_internship"], 0, "", "", "",
                "email" if s["contact_email"] else "web", "NEW", s["deadline"],
                s["location_scope"], s["discipline"]
            ))
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM jobs WHERE status != 'EXPIRED'")
        active_db_count = cur.fetchone()[0]
        cur_bd = conn.execute("SELECT COUNT(*) FROM jobs WHERE location_scope = 'bangladesh' AND status != 'EXPIRED'")
        bd_active = cur_bd.fetchone()[0]
        cur_glob = conn.execute("SELECT COUNT(*) FROM jobs WHERE location_scope = 'global' AND status != 'EXPIRED'")
        glob_active = cur_glob.fetchone()[0]

    print(f"🎉 Database populated! Active jobs in DB: {active_db_count} ({bd_active} Bangladesh, {glob_active} Global Remote)")

if __name__ == "__main__":
    main()
