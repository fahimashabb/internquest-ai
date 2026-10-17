"""Web application assistant using Playwright to autofill ATS forms and upload CV."""
import time
from pathlib import Path
from typing import Optional, Dict, Any
from src.config import AppSettings, load_settings
from src.tracker import ApplicationTracker


class WebApplier:
    def __init__(self, settings: Optional[AppSettings] = None, tracker: Optional[ApplicationTracker] = None):
        self.settings = settings or load_settings()
        self.tracker = tracker or ApplicationTracker(self.settings)

    def autofill_and_assist(
        self,
        job_id: str,
        application_url: str,
        cover_letter: str = "",
        headless: bool = False
    ) -> Dict[str, Any]:
        """Launch browser, navigate to application page, autofill candidate details and upload CV."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "success": False,
                "status": "MISSING_DEPENDENCY",
                "message": "Playwright is not installed. Please install it or use the email channel."
            }

        cand = self.settings.candidate
        cv_path = self.settings.absolute_resume_path

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context()
                page = context.new_page()

                print(f"[Web Assistant] Navigating to: {application_url}")
                page.goto(application_url, timeout=45000, wait_until="domcontentloaded")
                time.sleep(2)

                # Attempt to fill standard field patterns
                fields_filled = []

                # Full name or First/Last
                name_inputs = page.locator('input[name*="name" i], input[id*="name" i], input[placeholder*="name" i]')
                if name_inputs.count() == 1:
                    name_inputs.first.fill(cand.name)
                    fields_filled.append("Full Name")
                elif name_inputs.count() > 1:
                    first = cand.name.split()[0]
                    last = " ".join(cand.name.split()[1:])
                    page.locator('input[name*="first" i], input[id*="first" i]').fill(first)
                    page.locator('input[name*="last" i], input[id*="last" i]').fill(last)
                    fields_filled.append("First/Last Name")

                # Email
                email_inputs = page.locator('input[type="email"], input[name*="email" i], input[id*="email" i]')
                if email_inputs.count() > 0:
                    email_inputs.first.fill(cand.email)
                    fields_filled.append("Email")

                # Phone
                phone_inputs = page.locator('input[type="tel"], input[name*="phone" i], input[id*="phone" i]')
                if phone_inputs.count() > 0:
                    phone_inputs.first.fill(cand.phone)
                    fields_filled.append("Phone")

                # LinkedIn
                linkedin_inputs = page.locator('input[name*="linkedin" i], input[id*="linkedin" i], input[placeholder*="linkedin" i]')
                if linkedin_inputs.count() > 0:
                    linkedin_inputs.first.fill(cand.linkedin)
                    fields_filled.append("LinkedIn")

                # Resume file upload
                if cv_path.exists():
                    file_inputs = page.locator('input[type="file"]')
                    if file_inputs.count() > 0:
                        file_inputs.first.set_input_files(str(cv_path))
                        fields_filled.append("Resume PDF")

                # Cover letter textarea
                if cover_letter:
                    cl_inputs = page.locator('textarea[name*="cover" i], textarea[id*="cover" i], textarea[placeholder*="cover" i]')
                    if cl_inputs.count() > 0:
                        cl_inputs.first.fill(cover_letter)
                        fields_filled.append("Cover Letter")

                # Save screenshot of the pre-filled form
                screenshot_dir = Path("data/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_file = screenshot_dir / f"{job_id}_form.png"
                page.screenshot(path=str(screenshot_file))

                # In supervised / interactive mode, pause briefly or let user review
                if not headless:
                    print(f"[Web Assistant] Form prefilled ({', '.join(fields_filled)}).")
                    print("[Web Assistant] Reviewing browser window for 15 seconds...")
                    time.sleep(15)

                browser.close()

                if job_id:
                    self.tracker.mark_applied(job_id, channel="web", notes=f"Autofilled: {', '.join(fields_filled)}")

                return {
                    "success": True,
                    "status": "AUTOFILLED",
                    "fields": fields_filled,
                    "screenshot": str(screenshot_file),
                    "message": f"Successfully autofilled {len(fields_filled)} fields for {application_url}"
                }

        except Exception as e:
            return {
                "success": False,
                "status": "ERROR",
                "message": f"Web application error: {e}"
            }
