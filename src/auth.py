"""
User authentication, registration, session management, and personal CV storage.
Supports candidates from Science, Commerce, Arts, Engineering, and all academic backgrounds.
"""

import sqlite3
import hashlib
import secrets
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import DATA_DIR
from src.profile import extract_text_from_pdf_bytes, parse_resume_content

DB_PATH = DATA_DIR / "applications.db"


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password with SHA256 and a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{hashed}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt:hash."""
    try:
        salt, _ = stored_hash.split(":", 1)
        expected = _hash_password(password, salt)
        return secrets.compare_digest(expected, stored_hash)
    except Exception:
        return False


ADMIN_EMAILS = ["fahimashabofficial@gmail.com"]


class UserManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create users, sessions, and site_settings tables if they don't exist."""
        with self._get_connection() as conn:
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
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS site_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            try:
                conn.execute("ALTER TABLE users ADD COLUMN daily_digest INTEGER DEFAULT 1")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'email'")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            except Exception:
                pass

            # Default site settings
            defaults = {
                "site_title": "InternQuest AI",
                "announcement": "Welcome to InternQuest AI! New opportunities updated daily at 10:00 AM.",
                "show_announcement": "true",
                "min_match_score": "55",
                "daily_email_limit": "5",
                "allow_guest_mode": "true",
                "maintenance_mode": "false"
            }
            for k, v in defaults.items():
                conn.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES (?, ?)", (k, v))

            conn.commit()

    def register_user(
        self,
        email: str,
        password: str,
        name: str,
        track: str = "General",
        degree: str = "",
        institution: str = "",
        phone: str = "",
        linkedin: str = "",
        resume_bytes: Optional[bytes] = None,
        resume_filename: str = ""
    ) -> Dict[str, Any]:
        """Register a new user with optional initial CV."""
        email_clean = email.strip().lower()
        if not email_clean or "@" not in email_clean:
            return {"success": False, "message": "Please enter a valid email address."}
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters long."}

        # Check existing
        with self._get_connection() as conn:
            cur = conn.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
            if cur.fetchone():
                return {"success": False, "message": "An account with this email already exists. Please log in."}

        user_id = str(uuid.uuid4())
        pwd_hash = _hash_password(password)

        resume_text = ""
        skills = []
        target_domains = [track]

        if resume_bytes:
            resume_text = extract_text_from_pdf_bytes(resume_bytes)
            parsed = parse_resume_content(resume_text)
            if not name or name == "Candidate":
                name = parsed.get("name") or name
            if not degree or degree == "Undergraduate":
                degree = parsed.get("degree") or degree
            if not institution or institution == "University":
                institution = parsed.get("institution") or institution
            phone = phone or parsed.get("phone", "")
            linkedin = linkedin or parsed.get("linkedin", "")
            skills = parsed.get("skills", [])
            target_domains = parsed.get("target_domains", [track])

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO users (
                    id, email, password_hash, name, track, degree, institution,
                    phone, linkedin, resume_filename, resume_bytes, resume_text,
                    skills_json, target_domains_json, daily_digest, auth_provider, created_at, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'email', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                user_id, email_clean, pwd_hash, name, track, degree, institution,
                phone, linkedin, resume_filename, resume_bytes, resume_text,
                json.dumps(skills), json.dumps(target_domains)
            ))
            conn.commit()

        token = self.create_session(user_id)
        user_info = self.get_user_by_id(user_id)
        return {"success": True, "token": token, "user": user_info, "message": f"Welcome, {name}! Your account is active."}

    def social_login(
        self,
        provider: str,
        email: str,
        name: str = "",
        avatar: str = ""
    ) -> Dict[str, Any]:
        """Automatic one-click registration & sign-in with Google or Facebook."""
        email_clean = email.strip().lower()
        if not email_clean or "@" not in email_clean:
            return {"success": False, "message": "Valid email address is required for social authentication."}

        provider_name = provider.lower().strip()
        if provider_name not in ("google", "facebook"):
            provider_name = "social"

        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
            row = cur.fetchone()
            if row:
                user_data = dict(row)
                conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_data["id"],))
                conn.commit()
                token = self.create_session(user_data["id"])
                user_info = self._sanitize_user(user_data)
                return {
                    "success": True,
                    "token": token,
                    "user": user_info,
                    "message": f"Welcome back, {user_info['name']}! Signed in with {provider_name.title()}."
                }

        # Auto-create user without password
        user_id = str(uuid.uuid4())
        display_name = name.strip() if name and name.strip() else email_clean.split("@")[0].title()
        social_pwd = _hash_password(f"{provider_name}_{secrets.token_hex(16)}")

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO users (
                    id, email, password_hash, name, track, degree, institution,
                    daily_digest, auth_provider, created_at, last_login
                ) VALUES (?, ?, ?, ?, 'General', '', '', 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, email_clean, social_pwd, display_name, provider_name))
            conn.commit()

        token = self.create_session(user_id)
        user_info = self.get_user_by_id(user_id)
        return {
            "success": True,
            "token": token,
            "user": user_info,
            "message": f"Welcome to InternQuest AI, {display_name}! Successfully registered via {provider_name.title()}."
        }

    def toggle_daily_digest(self, user_id: str, enabled: bool) -> bool:
        """Enable or disable daily 10:00 AM email digest for user."""
        val = 1 if enabled else 0
        with self._get_connection() as conn:
            conn.execute("UPDATE users SET daily_digest = ? WHERE id = ?", (val, user_id))
            conn.commit()
        return True

    def get_digest_subscribers(self) -> List[Dict[str, Any]]:
        """Return all users with active daily 10:00 AM digests."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM users WHERE daily_digest = 1 AND email IS NOT NULL AND email != ''")
            return [self._sanitize_user(dict(r)) for r in cur.fetchall()]

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user by email and password, returning session token."""
        email_clean = email.strip().lower()
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
            row = cur.fetchone()
            if not row:
                return {"success": False, "message": "Account not found with this email."}

            user_data = dict(row)
            if not _verify_password(password, user_data["password_hash"]):
                return {"success": False, "message": "Incorrect password. Please try again."}

            # Update last login
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_data["id"],))
            conn.commit()

        token = self.create_session(user_data["id"])
        sanitized = self._sanitize_user(user_data)
        return {"success": True, "token": token, "user": sanitized, "message": f"Welcome back, {sanitized['name']}!"}

    def create_session(self, user_id: str) -> str:
        """Create a new session token for the user."""
        token = secrets.token_hex(24)
        with self._get_connection() as conn:
            conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
            conn.commit()
        return token

    def get_user_by_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile by active session token."""
        if not token:
            return None
        with self._get_connection() as conn:
            cur = conn.execute("""
                SELECT u.* FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.token = ?
            """, (token,))
            row = cur.fetchone()
            if row:
                return self._sanitize_user(dict(row))
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if row:
                return self._sanitize_user(dict(row))
        return None

    def get_user_resume_bytes(self, user_id: str) -> Optional[bytes]:
        """Get raw PDF bytes for user's uploaded CV."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT resume_bytes FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if row and row["resume_bytes"]:
                return row["resume_bytes"]
        return None

    def update_user_cv(self, user_id: str, resume_bytes: bytes, resume_filename: str) -> Dict[str, Any]:
        """Upload or update CV for an authenticated user."""
        resume_text = extract_text_from_pdf_bytes(resume_bytes)
        parsed = parse_resume_content(resume_text)

        skills = parsed.get("skills", [])
        domains = parsed.get("target_domains", [])

        with self._get_connection() as conn:
            # Check what fields need updating if empty
            cur = conn.execute("SELECT name, degree, institution, phone, linkedin, track FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                return {"success": False, "message": "User not found."}

            curr = dict(row)
            name = curr["name"] if curr["name"] and curr["name"] != "Candidate" else parsed.get("name", curr["name"])
            degree = curr["degree"] if curr["degree"] and curr["degree"] != "Undergraduate" else parsed.get("degree", curr["degree"])
            institution = curr["institution"] if curr["institution"] and curr["institution"] != "University" else parsed.get("institution", curr["institution"])
            phone = curr["phone"] or parsed.get("phone", "")
            linkedin = curr["linkedin"] or parsed.get("linkedin", "")

            conn.execute("""
                UPDATE users SET
                    resume_filename = ?,
                    resume_bytes = ?,
                    resume_text = ?,
                    skills_json = ?,
                    target_domains_json = ?,
                    name = ?,
                    degree = ?,
                    institution = ?,
                    phone = ?,
                    linkedin = ?
                WHERE id = ?
            """, (
                resume_filename, resume_bytes, resume_text,
                json.dumps(skills), json.dumps(domains),
                name, degree, institution, phone, linkedin,
                user_id
            ))
            conn.commit()

        updated_user = self.get_user_by_id(user_id)
        return {"success": True, "user": updated_user, "message": f"CV '{resume_filename}' successfully uploaded and analyzed!"}

    def logout_session(self, token: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()

    def _sanitize_user(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Strip sensitive fields before returning user dictionary."""
        skills = []
        try:
            skills = json.loads(d.get("skills_json") or "[]")
        except Exception:
            pass

        domains = []
        try:
            domains = json.loads(d.get("target_domains_json") or "[]")
        except Exception:
            pass

        is_admin_flag = bool(d.get("is_admin", 0)) or (d.get("email", "").lower() in [e.lower() for e in ADMIN_EMAILS])

        return {
            "id": d["id"],
            "email": d["email"],
            "name": d["name"],
            "track": d.get("track", "General"),
            "degree": d.get("degree", ""),
            "institution": d.get("institution", ""),
            "phone": d.get("phone", ""),
            "linkedin": d.get("linkedin", ""),
            "has_resume": bool(d.get("resume_bytes")),
            "resume_filename": d.get("resume_filename", ""),
            "skills": skills,
            "target_domains": domains,
            "resume_text": d.get("resume_text", ""),
            "daily_digest": bool(d.get("daily_digest", 1)),
            "auth_provider": d.get("auth_provider", "email"),
            "is_admin": is_admin_flag,
            "created_at": d.get("created_at")
        }

    # ==========================================
    # WordPress-Style Admin Panel Helpers
    # ==========================================
    def is_admin(self, user_or_email: Any) -> bool:
        """Check if a given user object or email has Super Admin privileges."""
        if not user_or_email:
            return False
        if isinstance(user_or_email, str):
            return user_or_email.strip().lower() in [e.lower() for e in ADMIN_EMAILS]
        if isinstance(user_or_email, dict):
            email = user_or_email.get("email", "").strip().lower()
            return bool(user_or_email.get("is_admin")) or (email in [e.lower() for e in ADMIN_EMAILS])
        return False

    def get_site_settings(self) -> Dict[str, str]:
        """Fetch all site configuration key-value pairs."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT key, value FROM site_settings")
            return {r[0]: r[1] for r in cur.fetchall()}

    def update_site_settings(self, settings_dict: Dict[str, Any]) -> Dict[str, str]:
        """Update or insert site settings from admin panel."""
        with self._get_connection() as conn:
            for k, v in settings_dict.items():
                conn.execute(
                    "INSERT INTO site_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (str(k), str(v))
                )
            conn.commit()
        return self.get_site_settings()

    def get_all_users_admin(self) -> List[Dict[str, Any]]:
        """Return all registered users with CV metadata for Admin Panel."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [self._sanitize_user(dict(row)) for row in cur.fetchall()]

    def get_user_resume_bytes(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored PDF resume bytes and filename for Admin download."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT resume_filename, resume_bytes, name FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if row and row["resume_bytes"]:
                return {
                    "filename": row["resume_filename"] or f"{row['name'].replace(' ', '_')}_Resume.pdf",
                    "bytes": row["resume_bytes"]
                }
            return None

    def delete_user_admin(self, user_id: str) -> bool:
        """Permanently delete a user account and associated sessions."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        return True


# Global singleton
user_manager = UserManager()
