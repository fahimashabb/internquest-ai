"""Candidate profile and resume extraction module."""
from pathlib import Path
from typing import Dict, Any, Optional
import pypdf
from src.config import AppSettings, load_settings


class CandidateProfile:
    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or load_settings()
        self._resume_text: Optional[str] = None

    def get_resume_text(self) -> str:
        """Extract text content from the candidate's PDF resume."""
        if self._resume_text:
            return self._resume_text

        resume_path = self.settings.absolute_resume_path
        if not resume_path.exists():
            # Fallback to structured text if PDF is missing
            return self._fallback_summary()

        try:
            reader = pypdf.PdfReader(str(resume_path))
            extracted = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                extracted.append(page_text.strip())
            full_text = "\n\n".join(extracted).strip()
            if full_text:
                self._resume_text = full_text
                return self._resume_text
        except Exception as e:
            print(f"[Warning] Failed to read PDF resume: {e}")

        return self._fallback_summary()

    def _fallback_summary(self) -> str:
        c = self.settings.candidate
        return f"""
Candidate: {c.name}
Contact: {c.email} | {c.phone}
LinkedIn: {c.linkedin}
Location: {c.location}
Degree: {c.degree} - {c.institution}
Interests: {', '.join(c.interests)}
Professional Summary:
Finance & Banking undergraduate with experience in financial modeling, corporate budgeting,
operational planning, and cross-functional leadership (BRAC, Prime Bank, BSEC/BASM).
Key competencies include Advanced MS Excel (XLOOKUP, PivotTables, What-If), Financial Modeling,
and Event Logistics & Operations.
        """.strip()

    def get_structured_profile(self) -> Dict[str, Any]:
        """Return a structured dictionary representing the candidate's background."""
        return {
            "name": self.settings.candidate.name,
            "email": self.settings.candidate.email,
            "phone": self.settings.candidate.phone,
            "linkedin": self.settings.candidate.linkedin,
            "location": self.settings.candidate.location,
            "degree": self.settings.candidate.degree,
            "institution": self.settings.candidate.institution,
            "interests": self.settings.candidate.interests,
            "resume_text": self.get_resume_text()
        }
