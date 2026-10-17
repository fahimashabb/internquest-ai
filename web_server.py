"""
Improved web server with full API support — all dashboard buttons functional.
"""
import json
import os
import sys
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Fix working directory
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import base64
from src.config import load_settings, ENV_FILE
from src.scheduler import InternshipBot
from src.profile import CandidateProfile
from src.matcher.gemini_evaluator import GeminiEvaluator
from src.scrapers.base import JobListing

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
                "is_dry_run": s.is_dry_run,
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
                lines = content.strip().split("\n")[-30:]  # Last 30 lines
                self._send_json({"lines": lines})
            else:
                self._send_json({"lines": ["No scan logs yet."]})
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
            self._send_json({"success": True, "message": "Scan started! Refresh in ~30 seconds for new results."})
            return

        if path == "/api/apply-email":
            job_id = payload.get("job_id")
            with self.bot.tracker._get_connection() as conn:
                cur = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"success": False, "message": "Job not found."})
                    return
                job = dict(row)
            res = self.bot.email_applier.send_application(
                job_id=job["id"],
                to_email=job["contact_email"],
                subject=job["tailored_email_subject"] or f"Application for {job['title']} - Fahim Ashab",
                body_text=job["tailored_cover_letter"] or f"Dear Hiring Team,\nPlease find my CV attached for the {job['title']} role.\n\nBest regards,\nFahim Ashab"
            )
            if res.get("success") and not self.bot.settings.is_dry_run:
                self.bot.tracker.mark_applied(job["id"], channel="email")
            self._send_json(res)
            return

        if path == "/api/apply-all-email":
            results = []
            pending = self.bot.tracker.get_pending_applications(min_score=self.bot.settings.filtering.min_match_score)
            email_jobs = [j for j in pending if j.get("application_channel") == "email" and j.get("contact_email")]
            for job in email_jobs[:self.bot.settings.application.daily_email_limit]:
                can_send, sent, limit = self.bot.email_applier.can_send_more_today()
                if not can_send and not self.bot.settings.is_dry_run:
                    break
                res = self.bot.email_applier.send_application(
                    job_id=job["id"],
                    to_email=job["contact_email"],
                    subject=job.get("tailored_email_subject") or f"Application for {job['title']} - Fahim Ashab",
                    body_text=job.get("tailored_cover_letter") or f"Dear Hiring Team,\nPlease find my CV attached.\n\nBest regards,\nFahim Ashab"
                )
                if res.get("success") and not self.bot.settings.is_dry_run:
                    self.bot.tracker.mark_applied(job["id"], channel="email")
                results.append({"company": job["company"], "result": res["status"]})
            self._send_json({"success": True, "applied": results, "count": len(results)})
            return

        if path == "/api/test-email":
            cand = self.bot.settings.candidate
            res = self.bot.email_applier.send_application(
                job_id="",
                to_email=cand.email,
                subject=f"Test Application Email - {cand.name} (CV Check)",
                body_text=f"Dear {cand.name},\n\nThis is a test email from your Internship Hunter.\nYour CV is attached. Everything looks great!\n\nBest,\n{cand.name}"
            )
            self._send_json(res)
            return

        if path == "/api/config":
            dry_run = payload.get("is_dry_run")
            if dry_run is not None:
                self.bot.settings.dry_run_override = bool(dry_run)

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

            # Persist to .env
            env_content = "\n".join([
                f"GEMINI_API_KEY={self.bot.settings.gemini_api_key or ''}",
                f"EMAIL_HOST={self.bot.settings.email_host}",
                f"EMAIL_PORT={self.bot.settings.email_port}",
                f"EMAIL_USER={self.bot.settings.email_user}",
                f"EMAIL_PASSWORD={self.bot.settings.email_password}",
                f"DRY_RUN={self.bot.settings.is_dry_run}",
            ])
            ENV_FILE.write_text(env_content, encoding="utf-8")
            self._send_json({"success": True, "message": "Settings saved."})
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, data):
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_server(port=5000):
    settings = load_settings()
    bot = InternshipBot(settings)
    DashboardHandler.bot = bot

    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://localhost:{port}"
    print(f"\n========================================================")
    print(f"  Fahim's Internship Assistant is LIVE!")
    print(f"  Open: {url}")
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
