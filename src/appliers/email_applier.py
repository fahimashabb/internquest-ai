"""Email application engine for sending cold outreach and direct applications with CV."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from src.config import AppSettings, load_settings
from src.tracker import ApplicationTracker


class EmailApplier:
    def __init__(self, settings: Optional[AppSettings] = None, tracker: Optional[ApplicationTracker] = None):
        self.settings = settings or load_settings()
        self.tracker = tracker or ApplicationTracker(self.settings)

    def can_send_more_today(self) -> Tuple[bool, int, int]:
        """Check if daily sending quota is reached."""
        sent_today = self.tracker.get_emails_sent_today()
        limit = self.settings.application.daily_email_limit
        return (sent_today < limit, sent_today, limit)

    def prepare_message(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        resume_path: Optional[Path] = None
    ) -> MIMEMultipart:
        """Construct MIME multipart email with resume attachment."""
        msg = MIMEMultipart()
        msg["From"] = f"{self.settings.application.sender_name} <{self.settings.email_user}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach text body
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach CV
        cv_path = resume_path or self.settings.absolute_resume_path
        if cv_path and cv_path.exists():
            with open(cv_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=cv_path.name
                )
                msg.attach(attachment)

        return msg

    def send_application(
        self,
        job_id: str,
        to_email: str,
        subject: str,
        body_text: str,
        force_live: bool = False
    ) -> Dict[str, Any]:
        """Send an application email to a company or HR contact."""
        is_dry = self.settings.is_dry_run and not force_live

        # Check daily quota
        can_send, sent_count, limit = self.can_send_more_today()
        if not can_send and not is_dry:
            return {
                "success": False,
                "status": "QUOTA_EXCEEDED",
                "message": f"Daily email limit reached ({sent_count}/{limit}). Quota resets tomorrow."
            }

        if is_dry:
            # Simulation / Dry Run
            print(f"[DRY RUN - Simulation] Would send email to: {to_email}")
            print(f"Subject: {subject}")
            print(f"CV Attached: {self.settings.absolute_resume_path.name}")
            return {
                "success": True,
                "status": "SIMULATED",
                "message": f"[DRY RUN] Email drafted and simulated for {to_email}."
            }

        # Live SMTP sending
        if not self.settings.email_password:
            return {
                "success": False,
                "status": "MISSING_CREDENTIALS",
                "message": "EMAIL_PASSWORD not configured in .env. Please set up a Google App Password."
            }

        try:
            msg = self.prepare_message(to_email, subject, body_text)
            server = smtplib.SMTP(self.settings.email_host, self.settings.email_port)
            server.ehlo()
            server.starttls()
            server.login(self.settings.email_user, self.settings.email_password)
            server.sendmail(self.settings.email_user, [to_email], msg.as_string())
            server.quit()

            # Record success in tracker
            if job_id:
                self.tracker.mark_applied(job_id, channel="email", notes=f"Sent to {to_email}")

            return {
                "success": True,
                "status": "SENT",
                "message": f"Application successfully emailed to {to_email} with CV attached."
            }
        except Exception as e:
            return {
                "success": False,
                "status": "ERROR",
                "message": f"SMTP Error sending to {to_email}: {e}"
            }
