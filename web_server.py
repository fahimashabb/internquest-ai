"""
Universal Multi-User Web Server for AI Internship Hunter Platform.
Features:
- General user registration, login, and session persistence in SQLite
- Personal CV storage (PDF bytes) attached to registered user ID
- Multi-disciplinary support: Science, Commerce, Arts, Engineering, Law, Healthcare
- Personalized AI job matching & customized cold email pitch generation
- Secure live email applications using user's uploaded CV
"""

import json
import os
import sys
import webbrowser
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Fix working directory
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import load_settings, ENV_FILE
from src.scheduler import InternshipBot
from src.profile import CandidateProfile
from src.matcher.gemini_evaluator import GeminiEvaluator
from src.scrapers.base import JobListing
from src.auth import user_manager

WEB_DIR = BASE_DIR / "web"


class DashboardHandler(BaseHTTPRequestHandler):
    bot: InternshipBot = None

    def log_message(self, format, *args):
        pass  # Silent logging

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write((WEB_DIR / "index.html").read_bytes())
            return

        if path == "/api/auth/me":
            auth_header = self.headers.get("Authorization", "")
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
            if not token:
                qs = parse_qs(parsed.query)
                token = qs.get("token", [""])[0]

            user = user_manager.get_user_by_session(token)
            if user:
                self._send_json({"success": True, "user": user})
            else:
                self._send_json({"success": False, "message": "Not authenticated."})
            return

        if path == "/api/jobs":
            with self.bot.tracker._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM jobs ORDER BY match_score DESC, found_at DESC")
                all_jobs = [dict(row) for row in cursor.fetchall()]
            self._send_json(all_jobs)
            return

        if path == "/api/stats":
            stats = self.bot.tracker.get_stats()
            stats["sent_today"] = self.bot.tracker.get_emails_sent_today()
            stats["limit"] = self.bot.settings.application.daily_email_limit
            self._send_json(stats)
            return

        if path == "/api/config":
            s = self.bot.settings
            data = {
                "is_dry_run": False,
                "email_user": s.email_user,
                "email_password": "SET" if s.email_password else "",
                "has_gemini": bool(s.gemini_api_key),
                "sender_name": s.application.sender_name,
                "mode": s.application.mode,
            }
            self._send_json(data)
            return

        if path == "/api/log":
            log_path = BASE_DIR / "data" / "daily_runs.log"
            if log_path.exists():
                content = log_path.read_text(encoding="utf-8", errors="replace")
                lines = content.strip().split("\n")[-30:]
                self._send_json({"lines": lines})
            else:
                self._send_json({"lines": ["Discovery engine active."]})
        if path == "/api/settings":
            self._send_json(user_manager.get_site_settings())
            return

        if path == "/api/admin/verify":
            user = self._get_user_from_req(parsed)
            if user and user_manager.is_admin(user):
                self._send_json({"success": True, "admin": True, "user": user})
            else:
                self._send_json({"success": False, "admin": False, "message": "Unauthorized."}, status=403)
            return

        if path == "/api/admin/users":
            user = self._get_user_from_req(parsed)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized. Admin privileges required."}, status=403)
                return
            self._send_json({"success": True, "users": user_manager.get_all_users_admin()})
            return

        if path == "/api/admin/cv":
            user = self._get_user_from_req(parsed)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            qs = parse_qs(parsed.query)
            target_id = qs.get("user_id", [""])[0]
            cv_obj = user_manager.get_user_resume_bytes(target_id)
            if cv_obj and cv_obj.get("bytes"):
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", f'attachment; filename="{cv_obj["filename"]}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(cv_obj["bytes"])
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path == "/api/admin/activity":
            user = self._get_user_from_req(parsed)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            self._send_json({"success": True, "activity": self.bot.tracker.get_recent_activity(50)})
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body) if body.strip() else {}
        except Exception:
            payload = {}

        # ── AUTHENTICATION ROUTES ──
        if path == "/api/auth/register":
            email = payload.get("email", "").strip()
            password = payload.get("password", "").strip()
            name = payload.get("name", "").strip()
            track = payload.get("track", "Commerce & Business").strip()
            degree = payload.get("degree", "Undergraduate").strip()
            institution = payload.get("institution", "University").strip()
            phone = payload.get("phone", "").strip()
            linkedin = payload.get("linkedin", "").strip()
            file_base64 = payload.get("file_base64", "")
            filename = payload.get("filename", "")

            resume_bytes = None
            if file_base64:
                try:
                    resume_bytes = base64.b64decode(file_base64)
                except Exception:
                    pass

            result = user_manager.register_user(
                email=email,
                password=password,
                name=name,
                track=track,
                degree=degree,
                institution=institution,
                phone=phone,
                linkedin=linkedin,
                resume_bytes=resume_bytes,
                resume_filename=filename
            )
            self._send_json(result)
            return

        if path == "/api/auth/login":
            email = payload.get("email", "").strip()
            password = payload.get("password", "").strip()
            result = user_manager.authenticate_user(email, password)
            self._send_json(result)
            return

        if path == "/api/auth/logout":
            token = payload.get("token", "").strip()
            if token:
                user_manager.logout_session(token)
            self._send_json({"success": True, "message": "Logged out."})
            return

        if path == "/api/auth/social-login":
            provider = payload.get("provider", "google")
            email = payload.get("email", "").strip()
            name = payload.get("name", "").strip()
            avatar = payload.get("avatar", "").strip()
            result = user_manager.social_login(provider=provider, email=email, name=name, avatar=avatar)
            self._send_json(result)
            return

        if path == "/api/auth/toggle-digest":
            token = payload.get("token", "").strip()
            enabled = bool(payload.get("enabled", True))
            user = user_manager.get_user_by_session(token)
            if not user:
                self._send_json({"success": False, "message": "Authentication required."})
                return
            user_manager.toggle_daily_digest(user["id"], enabled)
            self._send_json({
                "success": True,
                "daily_digest": enabled,
                "message": f"10:00 AM Daily Email Digest {'activated' if enabled else 'paused'}."
            })
            return

        if path == "/api/test-digest":
            token = payload.get("token", "").strip()
            target_user_id = None
            if token:
                user = user_manager.get_user_by_session(token)
                if user:
                    target_user_id = user["id"]

            def run_digest():
                self.bot.send_daily_morning_digests(target_user_id=target_user_id)

            threading.Thread(target=run_digest, daemon=True).start()
            self._send_json({"success": True, "message": "10:00 AM Morning Digest triggered! Check your inbox or engine logs."})
            return


        if path == "/api/auth/upload-cv":
            token = payload.get("token", "").strip()
            user = user_manager.get_user_by_session(token)
            if not user:
                self._send_json({"success": False, "message": "Please log in to save your CV."})
                return

            file_base64 = payload.get("file_base64", "")
            filename = payload.get("filename", "Resume.pdf")
            if not file_base64:
                self._send_json({"success": False, "message": "No file received."})
                return

            try:
                resume_bytes = base64.b64decode(file_base64)
                res = user_manager.update_user_cv(user["id"], resume_bytes, filename)
                self._send_json(res)
            except Exception as e:
                self._send_json({"success": False, "message": f"Upload failed: {e}"})
            return

        # ── CV PARSING & MATCHING ROUTES ──
        if path == "/api/upload-cv":
            file_base64 = payload.get("file_base64", "")
            if not file_base64:
                self._send_json({"success": False, "message": "No file received."})
                return
            try:
                pdf_bytes = base64.b64decode(file_base64)
                profile = CandidateProfile.from_pdf_bytes(pdf_bytes, settings=self.bot.settings)
                data = profile.get_structured_profile()
                self._send_json({"success": True, "profile": data})
            except Exception as e:
                self._send_json({"success": False, "message": f"Failed to parse resume: {e}"})
            return

        if path == "/api/match-cv":
            profile_data = payload.get("profile", {})
            profile = CandidateProfile.from_dict(profile_data, settings=self.bot.settings)
            evaluator = GeminiEvaluator(settings=self.bot.settings, profile=profile)

            with self.bot.tracker._get_connection() as conn:
                cur = conn.execute("SELECT * FROM jobs")
                raw_jobs = [dict(row) for row in cur.fetchall()]

            matched_jobs = []
            for rj in raw_jobs:
                job_obj = JobListing(
                    title=rj["title"],
                    company=rj["company"],
                    location=rj.get("location") or "Bangladesh",
                    url=rj["url"],
                    description=rj.get("description") or "",
                    source=rj.get("source") or "web",
                    contact_email=rj.get("contact_email")
                )
                evaluated = evaluator._evaluate_with_heuristics(job_obj)
                item = dict(rj)
                item["match_score"] = evaluated.match_score
                item["match_rationale"] = evaluated.match_rationale
                item["tailored_email_subject"] = evaluated.tailored_email_subject
                item["tailored_cover_letter"] = evaluated.tailored_cover_letter
                matched_jobs.append(item)

            matched_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            self._send_json({"success": True, "jobs": matched_jobs})
            return

        if path == "/api/generate-pitch":
            job_id = payload.get("job_id")
            profile_data = payload.get("profile", {})
            profile = CandidateProfile.from_dict(profile_data, settings=self.bot.settings)
            evaluator = GeminiEvaluator(settings=self.bot.settings, profile=profile)

            with self.bot.tracker._get_connection() as conn:
                cur = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"success": False, "message": "Job not found."})
                    return
                rj = dict(row)

            job_obj = JobListing(
                title=rj["title"],
                company=rj["company"],
                location=rj.get("location") or "Bangladesh",
                url=rj["url"],
                description=rj.get("description") or "",
                source=rj.get("source") or "web",
                contact_email=rj.get("contact_email")
            )
            evaluated = evaluator.evaluate_job(job_obj)
            self._send_json({
                "success": True,
                "subject": evaluated.tailored_email_subject,
                "pitch": evaluated.tailored_cover_letter,
                "contact_email": evaluated.contact_email or rj.get("contact_email") or ""
            })
            return

        if path == "/api/scan":
            def run_scan():
                self.bot.run_discovery_cycle()
            threading.Thread(target=run_scan, daemon=True).start()
            self._send_json({"success": True, "message": "Scan started! Scraping fresh postings across all disciplines..."})
            return

        if path == "/api/apply-email":
            job_id = payload.get("job_id")
            token = payload.get("token", "")
            user = user_manager.get_user_by_session(token) if token else None

            with self.bot.tracker._get_connection() as conn:
                cur = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"success": False, "message": "Job not found."})
                    return
                job = dict(row)

            # Retrieve user's CV if authenticated
            resume_bytes = None
            resume_filename = "Resume.pdf"
            candidate_name = "Candidate"
            if user:
                candidate_name = user.get("name") or "Candidate"
                resume_bytes = user_manager.get_user_resume_bytes(user["id"])
                resume_filename = user.get("resume_filename") or "Resume.pdf"
            elif payload.get("file_base64"):
                try:
                    resume_bytes = base64.b64decode(payload["file_base64"])
                    resume_filename = payload.get("filename", "Resume.pdf")
                except Exception:
                    pass

            res = self.bot.email_applier.send_application(
                job_id=job["id"],
                to_email=job["contact_email"],
                subject=job["tailored_email_subject"] or f"Application for {job['title']} - {candidate_name}",
                body_text=job["tailored_cover_letter"] or f"Dear Hiring Team,\nPlease find my CV attached for the {job['title']} role.\n\nBest regards,\n{candidate_name}",
                resume_bytes=resume_bytes,
                resume_filename=resume_filename,
                sender_name=candidate_name
            )
            if res.get("success"):
                self.bot.tracker.mark_applied(job["id"], channel="email")
            self._send_json(res)
            return

        if path == "/api/config":
            self.bot.settings.dry_run_override = False

            email_user = payload.get("email_user", "").strip()
            if email_user:
                self.bot.settings.email_user = email_user

            email_pass = payload.get("email_password", "").strip()
            if email_pass and email_pass not in ("SET", "***"):
                self.bot.settings.email_password = email_pass

            gemini_key = payload.get("gemini_api_key", "").strip()
            if gemini_key:
                self.bot.settings.gemini_api_key = gemini_key
                self.bot.evaluator._init_client()

            env_content = "\n".join([
                f"GEMINI_API_KEY={self.bot.settings.gemini_api_key or ''}",
                f"EMAIL_HOST={self.bot.settings.email_host}",
                f"EMAIL_PORT={self.bot.settings.email_port}",
                f"EMAIL_USER={self.bot.settings.email_user}",
                f"EMAIL_PASSWORD={self.bot.settings.email_password}",
                f"DRY_RUN=False",
            ])
            ENV_FILE.write_text(env_content, encoding="utf-8")
            self._send_json({"success": True, "message": "Settings updated."})
            return

        # ── WORDPRESS-STYLE ADMIN POST ROUTES ──
        if path == "/api/admin/settings":
            user = self._get_user_from_req(parsed, payload)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            settings_data = payload.get("settings", {})
            updated = user_manager.update_site_settings(settings_data)
            self._send_json({"success": True, "settings": updated})
            return

        if path == "/api/admin/users/delete":
            user = self._get_user_from_req(parsed, payload)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            target_id = payload.get("user_id", "")
            user_manager.delete_user_admin(target_id)
            self._send_json({"success": True, "message": "User deleted successfully."})
            return

        if path == "/api/admin/jobs/add":
            user = self._get_user_from_req(parsed, payload)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            job_id = self.bot.tracker.add_job_admin(
                title=payload.get("title", ""),
                company=payload.get("company", ""),
                location=payload.get("location", "Dhaka"),
                url=payload.get("url", "#"),
                contact_email=payload.get("contact_email", ""),
                match_score=int(payload.get("match_score", 75))
            )
            self._send_json({"success": True, "job_id": job_id})
            return

        if path == "/api/admin/jobs/delete":
            user = self._get_user_from_req(parsed, payload)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            job_id = payload.get("job_id", "")
            self.bot.tracker.delete_job_admin(job_id)
            self._send_json({"success": True, "message": "Job deleted."})
            return

        if path == "/api/admin/trigger-scrape":
            user = self._get_user_from_req(parsed, payload)
            if not user or not user_manager.is_admin(user):
                self._send_json({"success": False, "message": "Unauthorized."}, status=403)
                return
            threading.Thread(target=self.bot.run_discovery_cycle, daemon=True).start()
            self._send_json({"success": True, "message": "Scraper started in background."})
            return

        self.send_response(404)
        self.end_headers()

    def _get_user_from_req(self, parsed, payload=None):
        token = ""
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        if not token and payload and isinstance(payload, dict):
            token = payload.get("token", "").strip()
        if not token:
            qs = parse_qs(parsed.query)
            token = qs.get("token", [""])[0]

        # Admin master key bypass (Fahim Ashab)
        if payload and isinstance(payload, dict) and payload.get("admin_key") in ("fahim@admin", "admin2026"):
            return {"id": "admin", "name": "Fahim Ashab (Admin)", "email": "fahimashabofficial@gmail.com", "is_admin": True}
        qs = parse_qs(parsed.query)
        if qs.get("admin_key", [""])[0] in ("fahim@admin", "admin2026"):
            return {"id": "admin", "name": "Fahim Ashab (Admin)", "email": "fahimashabofficial@gmail.com", "is_admin": True}

        if token:
            return user_manager.get_user_by_session(token)
        return None

    def _send_json(self, data, status=200):
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server(port=5000):
    import schedule
    import time

    settings = load_settings()
    bot = InternshipBot(settings)
    DashboardHandler.bot = bot

    # 10:00 AM Daily Morning Refresh & Subscriber Digest Job
    def background_scheduler():
        schedule.every().day.at("10:00").do(lambda: (bot.run_discovery_cycle(), bot.send_daily_morning_digests()))
        while True:
            try:
                schedule.run_pending()
            except Exception:
                pass
            time.sleep(30)

    threading.Thread(target=background_scheduler, daemon=True).start()

    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://localhost:{port}"
    print(f"\n========================================================")
    print(f"  InternQuest AI - Universal Internship Platform LIVE!")
    print(f"  Open: {url}")
    print(f"  Auto-Refresh: Daily at 10:00 AM with Email Digests")
    print(f"  Press Ctrl+C to stop.")
    print(f"========================================================\n")

    threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    run_server()
