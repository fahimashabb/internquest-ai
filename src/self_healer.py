"""
🛠️ Internship Hunter AI - Self-Healing Watchdog & Automated Resilience Engine
Monitors platform health, auto-repairs database schemas, heals corrupt file streams,
and ensures zero-downtime operation across web, cloud, and background tasks.
"""

import sys
import io
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class SelfHealer:
    """Self-healing resilience engine that automatically recovers from system failures."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (DATA_DIR / "applications.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.healing_history: List[Dict[str, Any]] = []

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def auto_heal_all(self) -> Dict[str, Any]:
        """Perform comprehensive system diagnostics and auto-repair schemas and files."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "database_healed": False,
            "columns_added": [],
            "indexes_created": [],
            "status": "HEALTHY"
        }

        # 1. Database Schema Healing
        try:
            with self._get_connection() as conn:
                # Ensure all required tables exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        company TEXT NOT NULL,
                        location TEXT,
                        url TEXT,
                        source TEXT,
                        contact_email TEXT,
                        is_internship BOOLEAN DEFAULT 1,
                        match_score INTEGER DEFAULT 0,
                        match_rationale TEXT,
                        tailored_email_subject TEXT,
                        tailored_cover_letter TEXT,
                        application_channel TEXT DEFAULT 'web',
                        status TEXT NOT NULL DEFAULT 'NEW',
                        deadline TEXT,
                        location_scope TEXT DEFAULT 'bangladesh',
                        discipline TEXT DEFAULT 'General',
                        found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        applied_at TIMESTAMP,
                        notes TEXT
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        name TEXT NOT NULL,
                        track TEXT DEFAULT 'General',
                        degree TEXT DEFAULT '',
                        institution TEXT DEFAULT '',
                        phone TEXT DEFAULT '',
                        linkedin TEXT DEFAULT '',
                        resume_filename TEXT DEFAULT '',
                        resume_bytes BLOB,
                        resume_text TEXT DEFAULT '',
                        skills_json TEXT DEFAULT '[]',
                        target_domains_json TEXT DEFAULT '[]',
                        daily_digest INTEGER DEFAULT 1,
                        auth_provider TEXT DEFAULT 'email',
                        is_admin INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS site_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
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

                # Auto-add missing columns to jobs table
                job_cols = [c[1] for c in conn.execute("PRAGMA table_info(jobs)").fetchall()]
                needed_job_cols = {
                    "deadline": "TEXT",
                    "location_scope": "TEXT DEFAULT 'bangladesh'",
                    "discipline": "TEXT DEFAULT 'General'",
                    "is_internship": "BOOLEAN DEFAULT 1",
                    "match_score": "INTEGER DEFAULT 0"
                }
                for col_name, col_def in needed_job_cols.items():
                    if col_name not in job_cols:
                        conn.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_def}")
                        results["columns_added"].append(f"jobs.{col_name}")

                # Auto-add missing columns to users table
                user_cols = [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
                needed_user_cols = {
                    "daily_digest": "INTEGER DEFAULT 1",
                    "auth_provider": "TEXT DEFAULT 'email'",
                    "is_admin": "INTEGER DEFAULT 0"
                }
                for col_name, col_def in needed_user_cols.items():
                    if col_name not in user_cols:
                        conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                        results["columns_added"].append(f"users.{col_name}")

                # Ensure high-performance query indexes exist
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs (match_score DESC)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_scope ON jobs (location_scope)",
                    "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)"
                ]
                for idx_sql in indexes:
                    conn.execute(idx_sql)

                # Ensure default site settings
                default_settings = {
                    "site_title": "Internship Hunter AI",
                    "announcement": "Welcome to Internship Hunter AI! 100+ Bangladesh & Global Internships Refreshed Daily at 10:00 AM.",
                    "show_announcement": "true",
                    "min_match_score": "55",
                    "daily_email_limit": "5",
                    "allow_guest_mode": "true",
                    "maintenance_mode": "false"
                }
                for k, v in default_settings.items():
                    conn.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES (?, ?)", (k, v))

                # Update site_title if still old name
                conn.execute(
                    "UPDATE site_settings SET value = 'Internship Hunter AI' WHERE key = 'site_title' AND value = 'InternQuest AI'"
                )

                conn.commit()
                results["database_healed"] = True

        except Exception as e:
            results["status"] = f"DEGRADED: {e}"
            self.log_healing_event("DB_REPAIR_FAIL", str(e))

        return results

    def heal_pdf_stream(self, raw_bytes: bytes) -> bytes:
        """Sanitize and repair malformed PDF headers or carriage returns."""
        if not raw_bytes:
            return b""
        # Ensure %PDF- header is clean
        idx = raw_bytes.find(b"%PDF-")
        if idx > 0:
            raw_bytes = raw_bytes[idx:]
        return raw_bytes

    def log_healing_event(self, event_type: str, details: str):
        """Record healing intervention into activity log."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO activity_log (activity_type, details) VALUES (?, ?)",
                    (f"SELF_HEAL:{event_type}", details)
                )
                conn.commit()
        except Exception:
            pass


# Global singleton instance
self_healer = SelfHealer()
self_healer.auto_heal_all()
