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

console = Console()


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
                if not can_send and not self.settings.is_dry_run:
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

    def start_scheduler(self):
        """Schedule daily run at configured time."""
        run_time = self.settings.schedule.run_daily_at
        console.print(f"[bold green]⏰ Starting Internship Hunter Scheduler (Daily at {run_time})...[/bold green]")
        console.print("Press Ctrl+C to stop.")

        def job():
            console.print("\n[bold yellow]🔔 Triggering Scheduled Daily Run...[/bold yellow]")
            self.run_discovery_cycle()
            if self.settings.application.mode == "autopilot":
                self.apply_pending(interactive=False)

        schedule.every().day.at(run_time).do(job)

        # Also run one cycle immediately upon launch
        job()

        while True:
            schedule.run_pending()
            time.sleep(30)
