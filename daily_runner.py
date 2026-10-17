"""Daily automated search runner executed by Windows Task Scheduler."""
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix working directory to project root regardless of where Task Scheduler launches from
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import load_settings
from src.scheduler import InternshipBot
from src.notifier import show_desktop_notification


def main():
    log_file = BASE_DIR / "data" / "daily_runs.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] Running 10:00 AM Daily Internship Search..."
    print(header)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{header}\n")

    try:
        settings = load_settings()
        bot = InternshipBot(settings)
        matched_count = bot.run_discovery_cycle()

        msg = f"Completed 10:00 AM scan. {matched_count} new matching opportunities found."
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

        # Desktop notification
        if matched_count > 0:
            show_desktop_notification(
                title="🎯 Internship Hunter (10:00 AM Scan)",
                message=f"Found {matched_count} new finance/banking internships matching your CV!"
            )
        else:
            show_desktop_notification(
                title="🎯 Internship Hunter (10:00 AM Scan)",
                message="Daily search complete! No new postings today. Existing matches are saved."
            )

        # Autopilot processing if enabled
        if settings.application.mode == "autopilot":
            applied = bot.apply_pending(interactive=False)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Autopilot applied to {applied} opportunities.\n")

    except Exception as e:
        err = f"Error during daily run: {e}"
        print(err)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {err}\n")


if __name__ == "__main__":
    main()
