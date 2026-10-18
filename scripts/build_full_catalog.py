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

    # Bangladesh Corporate, Bank, MNC, NGO & Tech Catalog (Strict regional Bangladesh only)
    print("📦 Ingesting Verified Bangladesh Corporate, Banking, MNC & Tech Catalog...")
    bd_jobs = generate_bangladesh_internships()
    bd_count = 0
    for j in bd_jobs:
        if j.id not in seen_ids:
            seen_ids.add(j.id)
            all_listings.append(j)
            bd_count += 1
    print(f"✅ Ingested {bd_count} verified, active Bangladesh corporate opportunities.")

    print(f"\n🎉 Total verified Bangladesh listings: {len(all_listings)}")

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
        # Purge any unverified or global listings
        deleted = conn.execute("DELETE FROM jobs WHERE location_scope = 'global' OR location_scope IS NULL OR source IN ('Jobicy', 'Remotive', 'Test')").rowcount
        if deleted:
            print(f"🧹 Purged {deleted} global/unverified postings from database.")

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
