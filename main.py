"""Internship Hunter - Main CLI Entry Point."""
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.config import load_settings
from src.scheduler import InternshipBot

console = Console()


def display_banner(settings):
    cand = settings.candidate
    dry_mode = "[bold red]ENABLED (Simulation Only)[/bold red]" if settings.is_dry_run else "[bold green]LIVE SENDING[/bold green]"
    gemini_status = "[bold green]Configured[/bold green]" if settings.gemini_api_key else "[bold yellow]Heuristic Fallback (Set GEMINI_API_KEY in .env)[/bold yellow]"
    
    info = (
        f"[bold]Candidate:[/bold] {cand.name} | {cand.degree}\n"
        f"[bold]Email:[/bold] {cand.email} | [bold]Phone:[/bold] {cand.phone}\n"
        f"[bold]Resume:[/bold] {settings.absolute_resume_path.name} "
        f"({'[green]Found[/green]' if settings.absolute_resume_path.exists() else '[red]Missing[/red]'})\n"
        f"[bold]Gemini AI:[/bold] {gemini_status}\n"
        f"[bold]Safety Dry-Run Mode:[/bold] {dry_mode}\n"
        f"[bold]Daily Email Quota:[/bold] {settings.application.daily_email_limit} emails/day"
    )
    console.print(Panel(info, title="[bold cyan]🚀 Autonomous Internship Hunter & Auto-Applier[/bold cyan]", expand=False))


def cmd_stats(bot):
    stats = bot.tracker.get_stats()
    sent_today = bot.tracker.get_emails_sent_today()
    limit = bot.settings.application.daily_email_limit

    table = Table(title="Application Pipeline Status", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right", style="bold")

    table.add_row("Total Opportunities Tracked", str(stats.get("TOTAL_FOUND", 0)))
    table.add_row("Matched Profile (>= threshold)", str(stats.get("MATCHED", 0)))
    table.add_row("Applications Emailed", str(stats.get("APPLIED_EMAIL", 0)))
    table.add_row("Applications via Web Form", str(stats.get("APPLIED_WEB", 0)))
    table.add_row("Skipped (Low Relevance)", str(stats.get("SKIPPED", 0)))
    table.add_row("Emails Sent Today", f"{sent_today}/{limit}")

    console.print(table)
    console.print(f"\nReport markdown file: [underline]data/applications_report.md[/underline]\n")


def cmd_test_email(bot, to_email: str):
    console.print(f"[bold cyan]Sending test email to: {to_email}...[/bold cyan]")
    cand = bot.settings.candidate
    subject = f"Test Application - {cand.name} (CV Delivery Check)"
    body = (
        f"Hello {cand.name},\n\n"
        f"This is an automated test email from your Internship Hunter agent.\n"
        f"Your resume ({bot.settings.absolute_resume_path.name}) is attached.\n\n"
        f"Best regards,\n{cand.name}"
    )

    force_live = not bot.settings.is_dry_run
    res = bot.email_applier.send_application(
        job_id="",
        to_email=to_email,
        subject=subject,
        body_text=body,
        force_live=force_live
    )
    if res["success"]:
        console.print(f"[bold green]✓ {res['message']}[/bold green]")
    else:
        console.print(f"[bold red]✗ {res['message']}[/bold red]")


def main():
    parser = argparse.ArgumentParser(description="Autonomous Internship Hunter & Auto-Applier")
    parser.add_argument("--find", action="store_true", help="Discover and score today's internship opportunities")
    parser.add_argument("--review", action="store_true", help="Interactively review and apply to matched opportunities")
    parser.add_argument("--auto-apply", action="store_true", help="Automatically apply to high-match opportunities (respecting daily limits)")
    parser.add_argument("--schedule", action="store_true", help="Start background daily scheduler")
    parser.add_argument("--stats", action="store_true", help="Show current application stats and tracking status")
    parser.add_argument("--test-email", type=str, help="Send a test application email with CV to the specified address")

    args = parser.parse_args()
    settings = load_settings()
    display_banner(settings)

    bot = InternshipBot(settings)

    if args.find:
        bot.run_discovery_cycle()
    elif args.review:
        bot.apply_pending(interactive=True)
    elif args.auto_apply:
        bot.apply_pending(interactive=False)
    elif args.schedule:
        bot.start_scheduler()
    elif args.stats:
        cmd_stats(bot)
    elif args.test_email:
        cmd_test_email(bot, args.test_email)
    else:
        # Default: run stats and show available options
        cmd_stats(bot)
        console.print("[dim]Use --find to discover internships, --review to review & apply, or --schedule to run daily.[/dim]")


if __name__ == "__main__":
    main()
