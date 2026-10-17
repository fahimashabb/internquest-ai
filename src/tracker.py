"""Database storage, application state tracker, and report generator."""
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.config import AppSettings, load_settings, DATA_DIR
from src.scrapers.base import JobListing


class ApplicationTracker:
    def __init__(self, settings: Optional[AppSettings] = None, db_path: Optional[Path] = None):
        self.settings = settings or load_settings()
        self.db_path = db_path or (DATA_DIR / "applications.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    url TEXT,
                    source TEXT,
                    contact_email TEXT,
                    is_internship BOOLEAN,
                    match_score INTEGER,
                    match_rationale TEXT,
                    tailored_email_subject TEXT,
                    tailored_cover_letter TEXT,
                    application_channel TEXT,
                    status TEXT NOT NULL,
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_at TIMESTAMP,
                    notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def log_activity(self, activity_type: str, details: str) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO activity_log (activity_type, details) VALUES (?, ?)",
                    (activity_type, details)
                )
                conn.commit()
        except Exception:
            pass

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM jobs ORDER BY found_at DESC")
            return [dict(r) for r in cur.fetchall()]

    def has_job(self, job_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,))
            return cursor.fetchone() is not None

    def save_job(self, job: JobListing, status: str = "FOUND", notes: str = "") -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (
                    id, title, company, location, url, source, contact_email,
                    is_internship, match_score, match_rationale,
                    tailored_email_subject, tailored_cover_letter,
                    application_channel, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    match_score = excluded.match_score,
                    match_rationale = excluded.match_rationale,
                    tailored_email_subject = excluded.tailored_email_subject,
                    tailored_cover_letter = excluded.tailored_cover_letter,
                    status = CASE WHEN jobs.status = 'FOUND' THEN excluded.status ELSE jobs.status END,
                    contact_email = COALESCE(excluded.contact_email, jobs.contact_email),
                    notes = COALESCE(excluded.notes, jobs.notes)
            """, (
                job.id, job.title, job.company, job.location, job.url, job.source,
                job.contact_email, job.is_internship, job.match_score, job.match_rationale,
                job.tailored_email_subject, job.tailored_cover_letter,
                job.application_channel, status, notes
            ))
            conn.commit()

    def get_pending_applications(self, min_score: int = 65) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM jobs 
                WHERE status IN ('FOUND', 'MATCHED', 'APPROVED')
                  AND match_score >= ?
                ORDER BY match_score DESC, found_at DESC
            """, (min_score,))
            return [dict(row) for row in cursor.fetchall()]

    def mark_applied(self, job_id: str, channel: str, notes: str = "") -> None:
        now_str = datetime.now().isoformat()
        status = f"APPLIED_{channel.upper()}"
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE jobs 
                SET status = ?, applied_at = ?, notes = ?
                WHERE id = ?
            """, (status, now_str, notes, job_id))
            conn.commit()

    def get_emails_sent_today(self) -> int:
        today_str = date.today().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM jobs 
                WHERE status = 'APPLIED_EMAIL' 
                  AND date(applied_at) = ?
            """, (today_str,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_stats(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            stats = {row[0]: row[1] for row in cursor.fetchall()}
            cursor = conn.execute("SELECT COUNT(*) FROM jobs")
            stats["TOTAL_FOUND"] = cursor.fetchone()[0]
            return stats

    def generate_markdown_report(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (DATA_DIR / "applications_report.md")
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM jobs ORDER BY match_score DESC, found_at DESC")
            all_jobs = [dict(row) for row in cursor.fetchall()]

        stats = self.get_stats()
        lines = [
            "# Internship Hunting & Application Report",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Candidate:** {self.settings.candidate.name} ({self.settings.candidate.degree})  ",
            "",
            "## Summary Statistics",
            f"- **Total Opportunities Tracked:** {stats.get('TOTAL_FOUND', 0)}",
            f"- **Applied via Email:** {stats.get('APPLIED_EMAIL', 0)}",
            f"- **Applied via Web:** {stats.get('APPLIED_WEB', 0)}",
            f"- **Pending / Ready for Review:** {stats.get('MATCHED', 0) + stats.get('FOUND', 0)}",
            f"- **Skipped / Filtered:** {stats.get('SKIPPED', 0)}",
            "",
            "## Applications & Tracked Jobs Table",
            "| Score | Role | Company | Channel | Status | Contact / Link | Applied Date |",
            "| :---: | :--- | :--- | :---: | :---: | :--- | :---: |"
        ]

        for j in all_jobs:
            score = j.get('match_score') or 0
            title = j.get('title', 'N/A')
            comp = j.get('company', 'N/A')
            chan = j.get('application_channel', 'web')
            status = j.get('status', 'FOUND')
            link = j.get('url', '#')
            email = j.get('contact_email') or ''
            applied = (j.get('applied_at') or '')[:10]
            
            contact_str = f"[{email}](mailto:{email})" if email else f"[View Job]({link})"
            lines.append(f"| {score}% | **{title}** | {comp} | `{chan}` | `{status}` | {contact_str} | {applied or '-'} |")

        target.write_text("\n".join(lines), encoding="utf-8")
        return target
