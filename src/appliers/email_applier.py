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
        resume_path: Optional[Path] = None,
        resume_bytes: Optional[bytes] = None,
        resume_filename: str = "Resume.pdf",
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None
    ) -> MIMEMultipart:
        """Construct MIME multipart email with resume attachment."""
        msg = MIMEMultipart()
        from_name = sender_name or self.settings.application.sender_name or "Applicant"
        from_addr = sender_email or self.settings.email_user
        msg["From"] = f"{from_name} <{from_addr}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach text body
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach CV from user bytes or user file path
        if resume_bytes:
            attachment = MIMEApplication(resume_bytes, _subtype="pdf")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=resume_filename or "Resume.pdf"
            )
            msg.attach(attachment)
        elif resume_path and resume_path.exists():
            with open(resume_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=resume_path.name
                )
                msg.attach(attachment)

        return msg

    def send_application(
        self,
        job_id: str,
        to_email: str,
        subject: str,
        body_text: str,
        resume_path: Optional[Path] = None,
        resume_bytes: Optional[bytes] = None,
        resume_filename: str = "Resume.pdf",
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        force_live: bool = True
    ) -> Dict[str, Any]:
        """Send an application email directly to a company or HR contact using the user's CV."""
        # Check daily quota
        can_send, sent_count, limit = self.can_send_more_today()
        if not can_send:
            return {
                "success": False,
                "status": "QUOTA_EXCEEDED",
                "message": f"Daily email limit reached ({sent_count}/{limit}). Quota resets tomorrow."
            }

        user_email = sender_email or self.settings.email_user
        user_password = sender_password or self.settings.email_password

        # Live SMTP sending requires credentials
        if not user_password:
            return {
                "success": False,
                "status": "MISSING_CREDENTIALS",
                "message": "Gmail App Password not configured. Please enter your 16-character App Password in Settings."
            }

        try:
            msg = self.prepare_message(
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                resume_path=resume_path,
                resume_bytes=resume_bytes,
                resume_filename=resume_filename,
                sender_name=sender_name,
                sender_email=user_email
            )
            server = smtplib.SMTP(self.settings.email_host, self.settings.email_port)
            server.ehlo()
            server.starttls()
            server.login(user_email, user_password)
            server.sendmail(user_email, [to_email], msg.as_string())
            server.quit()

            # Record success in tracker
            if job_id:
                self.tracker.mark_applied(job_id, channel="email", notes=f"Sent to {to_email}")

            return {
                "success": True,
                "status": "SENT",
                "message": f"Application successfully emailed to {to_email} with CV attached."
            }
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "status": "AUTH_ERROR",
                "message": "Authentication failed. Check your Gmail address and 16-character App Password."
            }
        except Exception as e:
            return {
                "success": False,
                "status": "ERROR",
                "message": f"SMTP Error sending to {to_email}: {e}"
            }
