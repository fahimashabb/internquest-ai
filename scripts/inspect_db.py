import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("data/applications.db")
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM jobs")
print("Total jobs in applications.db:", c.fetchone()[0])

c.execute("SELECT title, company, url FROM jobs WHERE lower(title) LIKE '%intern%' OR lower(title) LIKE '%placement%'")
rows = c.fetchall()
print(f"Matched 'intern' or 'placement': {len(rows)}")
for r in rows:
    print(" -", r[0], "|", r[1], "|", r[2])
conn.close()
