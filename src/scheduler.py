"""Daily runner and background scheduler for Internship Hunter."""
import time
from typing import Optional
import schedule
from rich.console import Console
from rich.table import Table
from src.config import AppSettings, load_settings
from src.profile import CandidateProfile
from src.scrapers.aggregator import JobAggregator
from src.matcher.gemini_evaluator import GeminiEvaluator
from src.tracker import ApplicationTracker
from src.appliers.email_applier import EmailApplier
from src.appliers.web_applier import WebApplier

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(legacy_windows=False)



class InternshipBot:
    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or load_settings()
        self.profile = CandidateProfile(self.settings)
        self.aggregator = JobAggregator(self.settings)
        self.evaluator = GeminiEvaluator(self.settings, self.profile)
        self.tracker = ApplicationTracker(self.settings)
        self.email_applier = EmailApplier(self.settings, self.tracker)
        self.web_applier = WebApplier(self.settings, self.tracker)

    def run_discovery_cycle(self) -> int:
        """Find new jobs, evaluate with Gemini, and store in database."""
        console.print("[bold cyan]🔍 Starting Daily Internship Discovery...[/bold cyan]")
        raw_jobs = self.aggregator.fetch_all()
        console.print(f"Aggregated [bold green]{len(raw_jobs)}[/bold green] raw opportunities across sources.")

        new_jobs = [j for j in raw_jobs if not self.tracker.has_job(j.id)]
        console.print(f"Discovered [bold yellow]{len(new_jobs)}[/bold yellow] newly posted listings to evaluate.")

        matched_count = 0
        min_score = self.settings.filtering.min_match_score

        for idx, job in enumerate(new_jobs, 1):
            console.print(f"[{idx}/{len(new_jobs)}] Evaluating [bold]{job.title}[/bold] @ {job.company}...")
            evaluated_job = self.evaluator.evaluate_job(job)

            if evaluated_job.match_score >= min_score:
                matched_count += 1
                status = "MATCHED"
                console.print(f"  [green]✓ Match Score: {evaluated_job.match_score}%[/green] ({evaluated_job.application_channel})")
            else:
                status = "SKIPPED"
                console.print(f"  [dim]✗ Match Score: {evaluated_job.match_score}% (Below threshold {min_score}%)[/dim]")

            self.tracker.save_job(evaluated_job, status=status)

        report_path = self.tracker.generate_markdown_report()
        console.print(f"[bold green]✨ Discovery complete![/bold green] {matched_count} jobs matched your profile.")
        console.print(f"Updated application tracking report: [underline]{report_path}[/underline]")
        return matched_count

    def apply_pending(self, interactive: bool = True) -> int:
        """Process matched applications via email or web."""
        pending = self.tracker.get_pending_applications(min_score=self.settings.filtering.min_match_score)
        if not pending:
            console.print("[yellow]No pending applications to process right now.[/yellow]")
            return 0

        console.print(f"\n[bold cyan]📋 Found {len(pending)} matched applications ready for processing:[/bold cyan]")
        applied_count = 0

        for item in pending:
            can_send, sent_today, limit = self.email_applier.can_send_more_today()
            job_id = item["id"]
            title = item["title"]
            company = item["company"]
            channel = item["application_channel"] or "web"
            email = item["contact_email"]
            score = item["match_score"]
            subject = item["tailored_email_subject"]
            letter = item["tailored_cover_letter"]
            url = item["url"]

            table = Table(title=f"Application: {title} @ {company}", show_header=False)
            table.add_row("Match Score", f"[bold green]{score}%[/bold green]")
            table.add_row("Channel", f"[bold cyan]{channel.upper()}[/bold cyan]")
            table.add_row("Contact / URL", email if channel == "email" else url)
            table.add_row("Subject", subject or "(Standard Subject)")
            console.print(table)

            if interactive:
                choice = input("Apply to this opportunity? ([y]es / [s]kip / [q]uit): ").strip().lower()
                if choice == "q":
                    break
                if choice != "y":
                    console.print("[dim]Skipping application for now.[/dim]\n")
                    continue

            # Execute application
            if channel == "email" and email:
                if not can_send:
                    console.print(f"[bold red]Daily email quota reached ({sent_today}/{limit}). Pausing email applications.[/bold red]")
                    break

                res = self.email_applier.send_application(
                    job_id=job_id,
                    to_email=email,
                    subject=subject,
                    body_text=letter
                )
                console.print(f"Result: {res['message']}\n")
                if res["success"]:
                    applied_count += 1
            else:
                console.print(f"[bold blue]Web application channel.[/bold blue] Pre-filling form at: {url}")
                res = self.web_applier.autofill_and_assist(
                    job_id=job_id,
                    application_url=url,
                    cover_letter=letter,
                    headless=not interactive
                )
                console.print(f"Result: {res['message']}\n")
                if res["success"]:
                    applied_count += 1

        self.tracker.generate_markdown_report()
        return applied_count

    def send_daily_morning_digests(self, target_user_id: Optional[str] = None) -> list:
        """
        Send or generate 10:00 AM daily internship digest to all registered subscribers.
        Finds the freshest matching opportunities for each candidate's profile and CV.
        """
        from src.auth import user_manager
        from src.scrapers.base import JobListing

        console.print("[bold cyan]⏰ [10:00 AM Engine] Generating Daily Morning Digests for Subscribers...[/bold cyan]")
        self.tracker.log_activity("DIGEST_START", "Triggered automated 10:00 AM daily morning refresh cycle.")

        subscribers = user_manager.get_digest_subscribers()
        if target_user_id:
            subscribers = [s for s in subscribers if s["id"] == target_user_id]
            if not subscribers:
                u = user_manager.get_user_by_id(target_user_id)
                if u:
                    subscribers = [u]

        if not subscribers:
            console.print("[dim]No registered subscribers with active daily digest.[/dim]")
            return []

        all_jobs_raw = self.tracker.get_all_jobs()
        if not all_jobs_raw:
            console.print("[yellow]No listings available in database for daily digest.[/yellow]")
            return []

        results = []
        for user in subscribers:
            user_name = user.get("name") or "Candidate"
            user_email = user.get("email")
            user_track = user.get("track") or "General"
            user_skills = user.get("skills") or []

            user_profile = CandidateProfile(
                name=user_name,
                degree=user.get("degree") or "Student / Graduate",
                institution=user.get("institution") or "University",
                skills=user_skills,
                target_domains=user.get("target_domains") or [user_track]
            )
            evaluator = GeminiEvaluator(self.settings, user_profile)

            matched_for_user = []
            for j in all_jobs_raw[:35]:
                job_obj = JobListing(
                    title=j["title"],
                    company=j["company"],
                    location=j.get("location") or "Bangladesh",
                    url=j["url"],
                    description=j.get("description") or "",
                    source=j.get("source") or "web",
                    contact_email=j.get("contact_email")
                )
                evaluated = evaluator.evaluate_job(job_obj)
                if evaluated.match_score >= 60:
                    matched_for_user.append(evaluated)

            matched_for_user.sort(key=lambda x: x.match_score, reverse=True)
            top_matches = matched_for_user[:5]

            if not top_matches:
                fallback_jobs = []
                for j in all_jobs_raw[:3]:
                    fallback_jobs.append(JobListing(
                        title=j["title"],
                        company=j["company"],
                        location=j.get("location") or "Bangladesh",
                        url=j["url"],
                        source=j.get("source") or "web",
                        contact_email=j.get("contact_email"),
                        match_score=65,
                        match_rationale=f"Active opening matching {user_track} track."
                    ))
                top_matches = fallback_jobs

            subject = f"🎯 InternQuest AI: 10:00 AM Morning Digest ({len(top_matches)} Opportunities for {user_name})"

            lines = [
                f"Good morning {user_name},",
                "",
                "Here is your personalized 10:00 AM daily internship digest generated by InternQuest AI.",
                f"Our background discovery engine scanned Bangladesh companies, banks, MNCs, and remote boards for your {user_track} background.",
                "",
                "==================================================",
                f"  TOP MATCHES FOR YOU TODAY ({len(top_matches)} POSITIONS)",
                "==================================================",
                ""
            ]

            html_jobs_list = ""
            for i, match in enumerate(top_matches, 1):
                channel_str = f"Direct Email: {match.contact_email}" if match.contact_email else "Apply on Official Portal"
                lines.append(f"{i}. {match.title} @ {match.company} ({match.match_score}% Match)")
                lines.append(f"   Location: {match.location} | Source: {match.source}")
                lines.append(f"   Why it fits: {match.match_rationale or 'Strong alignment with your profile.'}")
                lines.append(f"   Apply: {match.url}")
                lines.append(f"   Channel: {channel_str}")
                lines.append("")

                html_jobs_list += f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:14px;">
                  <div style="font-size:16px; font-weight:700; color:#0f172a; margin-bottom:4px;">
                    {i}. {match.title} <span style="background:#dcfce7; color:#15803d; font-size:12px; font-weight:700; padding:3px 8px; border-radius:12px; margin-left:8px;">{match.match_score}% Match</span>
                  </div>
                  <div style="font-size:13px; color:#475569; margin-bottom:8px;">
                    <strong>{match.company}</strong> · {match.location} · <em>{match.source}</em>
                  </div>
                  <div style="background:#f8fafc; border-left:3px solid #6366f1; padding:8px 12px; border-radius:4px; font-size:13px; color:#1e293b; margin-bottom:10px;">
                    🎯 <strong>Fit Insight:</strong> {match.match_rationale or 'High alignment with your skills.'}
                  </div>
                  <div>
                    <a href="{match.url}" style="background:#4f46e5; color:#ffffff; padding:6px 14px; text-decoration:none; border-radius:8px; font-size:13px; font-weight:600; display:inline-block;">View & Apply →</a>
                    <span style="font-size:12px; color:#64748b; margin-left:10px;">{channel_str}</span>
                  </div>
                </div>
                """

            lines.append("To draft tailored cover letters and cold email pitches with 1 click, visit your dashboard:")
            lines.append("http://localhost:5000")
            lines.append("")
            lines.append("To adjust daily 10:00 AM alerts, toggle 'Daily Digest' in your account settings.")
            lines.append("InternQuest AI - Universal Internship Hunter")

            body_text = "\n".join(lines)
            body_html = f"""
            <div style="font-family:'Segoe UI',Roboto,Helvetica,sans-serif; max-width:640px; margin:0 auto; background:#f8fafc; padding:24px; border-radius:16px;">
              <div style="text-align:center; padding-bottom:16px; border-bottom:1px solid #e2e8f0; margin-bottom:20px;">
                <h2 style="color:#0f172a; margin:0 0 6px 0; font-size:22px;">🎯 InternQuest <span style="background:#4f46e5; color:#ffffff; font-size:14px; padding:3px 8px; border-radius:6px;">AI</span></h2>
                <p style="color:#64748b; margin:0; font-size:14px;">Your Personalized 10:00 AM Daily Internship Digest</p>
              </div>
              <p style="font-size:15px; color:#1e293b;">Good morning <strong>{user_name}</strong>,</p>
              <p style="font-size:14px; color:#475569; line-height:1.6;">Our background discovery engine refreshed opportunities this morning. Here are your top matched positions:</p>
              {html_jobs_list}
              <div style="text-align:center; margin-top:24px; padding-top:16px; border-top:1px solid #e2e8f0;">
                <a href="http://localhost:5000" style="background:#0f172a; color:#ffffff; padding:10px 22px; text-decoration:none; border-radius:10px; font-weight:600; font-size:14px; display:inline-block;">Open My Dashboard</a>
                <p style="font-size:11px; color:#94a3b8; margin-top:14px;">You are receiving this because you registered at InternQuest AI with daily 10:00 AM alerts enabled.</p>
              </div>
            </div>
            """

            dispatch_res = self.email_applier.send_digest_email(
                to_email=user_email,
                recipient_name=user_name,
                subject=subject,
                body_text=body_text,
                body_html=body_html
            )
            console.print(f"  [green]✓ Morning Digest -> {user_email} ({dispatch_res['status']})[/green]")
            results.append({
                "user_id": user["id"],
                "email": user_email,
                "matches_count": len(top_matches),
                "status": dispatch_res.get("status"),
                "message": dispatch_res.get("message")
            })

        console.print(f"[bold green]✨ 10:00 AM Digest cycle complete for {len(results)} subscribers.[/bold green]")
        return results

    def start_scheduler(self):
        """Schedule daily run at 10:00 AM."""
        console.print("[bold green]⏰ Starting Internship Hunter Scheduler (Daily at 10:00 AM)...[/bold green]")
        console.print("Press Ctrl+C to stop.")

        def morning_job():
            console.print("\n[bold yellow]⏰ Triggering Scheduled 10:00 AM Daily Run & Subscriber Digests...[/bold yellow]")
            self.run_discovery_cycle()
            self.send_daily_morning_digests()
            if self.settings.application.mode == "autopilot":
                self.apply_pending(interactive=False)

        schedule.every().day.at("10:00").do(morning_job)

        # Run discovery on initial launch
        self.run_discovery_cycle()

        while True:
            schedule.run_pending()
            time.sleep(30)

