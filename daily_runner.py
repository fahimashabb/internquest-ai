"""
Daily automated search runner executed by Windows Task Scheduler at 10:00 AM.
Scrapes, filters authentic student business internships, cross-checks all URLs (HTTP 200),
updates the JSON & website, syncs to GitHub Pages, and triggers a desktop notification.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix working directory to project root regardless of where Task Scheduler launches from
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.internship_auto_updater import run_daily_update
from src.notifier import show_desktop_notification


def main():
    log_file = BASE_DIR / "data" / "daily_runs.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] 🚀 Running 10:00 AM Daily Internship Placement Discovery..."
    print(header)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{header}\n")

    try:
        # Run autonomous daily discovery, verification & GitHub deployment
        verified_count = run_daily_update()

        msg = f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Completed 10:00 AM scan: {verified_count} verified authentic internship placements active."
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")

        # Desktop toast notification
        if verified_count > 0:
            show_desktop_notification(
                title="🎯 Internship Hunter (10:00 AM Scan)",
                message=f"Daily scan complete! {verified_count} verified business internships active & published."
            )
        else:
            show_desktop_notification(
                title="🎯 Internship Hunter (10:00 AM Scan)",
                message="Daily search complete! All existing links verified."
            )

    except Exception as e:
        err = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ERROR during daily run: {e}"
        print(err)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{err}\n")


if __name__ == "__main__":
    main()
