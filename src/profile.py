"""Candidate profile and resume extraction module supporting universal multi-user CV uploads."""
import re
import io
from pathlib import Path
from typing import Dict, Any, Optional, List
import pypdf
from src.config import AppSettings, load_settings

# Common skill keywords across multiple disciplines
KNOWN_SKILLS = {
    "Finance & Banking": [
        "financial modeling", "financial analysis", "corporate finance", "accounting",
        "banking", "budgeting", "valuation", "investment banking", "portfolio management",
        "working capital", "credit analysis", "auditing", "taxation", "treasury", "fintech",
        "ms excel", "excel", "xlookup", "pivottables", "financial statements", "trade finance"
    ],
    "Software & Tech": [
        "python", "javascript", "typescript", "java", "c++", "c#", "php", "golang",
        "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot",
        "sql", "postgresql", "mysql", "mongodb", "docker", "kubernetes", "aws", "git",
        "machine learning", "data science", "data analysis", "html", "css", "rest api"
    ],
    "Marketing & Growth": [
        "digital marketing", "seo", "sem", "content marketing", "social media", "copywriting",
        "market research", "google analytics", "brand management", "advertising", "lead generation",
        "email marketing", "public relations", "growth hacking", "campaign management"
    ],
    "Operations & HR": [
        "human resources", "recruitment", "talent acquisition", "operations management",
        "project management", "supply chain", "logistics", "procurement", "event management",
        "business development", "team leadership", "scrum", "agile", "strategic planning"
    ],
    "Design & Creative": [
        "ui/ux", "figma", "adobe photoshop", "illustrator", "graphic design",
        "video editing", "wireframing", "prototyping", "motion graphics"
    ]
}


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                extracted.append(t.strip())
        return "\n\n".join(extracted).strip()
    except Exception as e:
        print(f"[Warning] Failed to parse PDF bytes: {e}")
        return ""


def parse_resume_content(text: str) -> Dict[str, Any]:
    """Parse raw resume text into a structured profile with heuristics."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # 1. Candidate Name (usually in first 3 lines)
    name = "Candidate"
    for line in lines[:5]:
        # Ignore lines with email, phone, or url
        if "@" in line or "http" in line.lower() or any(c.isdigit() for c in line if len(line) > 15):
            continue
        cleaned = re.sub(r'[^a-zA-Z\s\.]', '', line).strip()
        if 2 <= len(cleaned.split()) <= 4 and len(cleaned) < 40:
            name = cleaned.title()
            break

    # 2. Email detection
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    # 3. Phone detection (Bangladesh & international)
    phone_match = re.search(r'(?:\+?880|0)?1[3-9]\d{8}|\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,9}', text)
    phone = phone_match.group(0) if phone_match else ""

    # 4. LinkedIn detection
    li_match = re.search(r'linkedin\.com/in/[\w\-]+', text)
    linkedin = f"https://www.{li_match.group(0)}" if li_match else ""

    # 5. Detect Degree & Institution
    degree = "Undergraduate Student"
    institution = ""
    lower_text = text.lower()

    degree_patterns = [
        r'(bba|b\.b\.a|bachelor of business administration|b\.sc|bsc|bachelor of science|b\.a|ba|bachelor of arts|b\.com|mba|master of business administration|m\.sc|msc)',
        r'(computer science|software engineering|finance|banking|accounting|marketing|economics|management|electrical engineering|human resource)',
    ]
    for pattern in degree_patterns:
        m = re.search(pattern, lower_text)
        if m:
            degree = m.group(0).upper() if len(m.group(0)) <= 4 else m.group(0).title()
            break

    inst_patterns = [
        r'([A-Za-z\s]+(university|college|institute|academy|school of business))',
        r'(dhaka university|du|buet|nsu|brac university|just|iut|ewu|aiub|aust|ru|cu)',
    ]
    for pattern in inst_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            institution = m.group(0).strip()
            break

    # 6. Detect Skills
    detected_skills: List[str] = []
    detected_domains: List[str] = []
    for domain, skill_list in KNOWN_SKILLS.items():
        domain_hits = 0
        for skill in skill_list:
            if re.search(rf'\b{re.escape(skill)}\b', lower_text):
                if skill.title() not in detected_skills:
                    detected_skills.append(skill.title())
                domain_hits += 1
        if domain_hits >= 2:
            detected_domains.append(domain)

    # 7. Location
    loc_match = re.search(r'(dhaka|chittagong|sylhet|rajshahi|khulna|jashore|barishal|bangladesh)', lower_text)
    location = loc_match.group(0).title() if loc_match else "Bangladesh"

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "location": location,
        "degree": degree,
        "institution": institution or "University",
        "skills": detected_skills[:15],
        "target_domains": detected_domains or ["General Business"],
        "resume_text": text
    }


class CandidateProfile:
    def __init__(self, settings: Optional[AppSettings] = None, profile_data: Optional[Dict[str, Any]] = None):
        self.settings = settings or load_settings()
        self._profile_data = profile_data
        self._resume_text: Optional[str] = None

    @classmethod
    def from_pdf_bytes(cls, pdf_bytes: bytes, settings: Optional[AppSettings] = None) -> "CandidateProfile":
        """Instantiate a profile from uploaded PDF file bytes."""
        text = extract_text_from_pdf_bytes(pdf_bytes)
        profile_data = parse_resume_content(text)
        inst = cls(settings=settings, profile_data=profile_data)
        inst._resume_text = text
        return inst

    @classmethod
    def from_dict(cls, data: Dict[str, Any], settings: Optional[AppSettings] = None) -> "CandidateProfile":
        """Instantiate a profile from pre-parsed profile dictionary."""
        return cls(settings=settings, profile_data=data)

    def get_resume_text(self) -> str:
        """Extract text content from the candidate's PDF resume."""
        if self._resume_text:
            return self._resume_text

        if self._profile_data and self._profile_data.get("resume_text"):
            self._resume_text = self._profile_data["resume_text"]
            return self._resume_text

        resume_path = self.settings.absolute_resume_path
        if not resume_path or not resume_path.exists():
            return self._fallback_summary()

        try:
            reader = pypdf.PdfReader(str(resume_path))
            extracted = []
            for page in reader.pages:
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
operational planning, and cross-functional leadership.
        """.strip()

    def get_structured_profile(self) -> Dict[str, Any]:
        """Return a structured dictionary representing the candidate's background."""
        if self._profile_data:
            return {
                "name": self._profile_data.get("name", "Candidate"),
                "email": self._profile_data.get("email", ""),
                "phone": self._profile_data.get("phone", ""),
                "linkedin": self._profile_data.get("linkedin", ""),
                "location": self._profile_data.get("location", "Bangladesh"),
                "degree": self._profile_data.get("degree", "Undergraduate"),
                "institution": self._profile_data.get("institution", "University"),
                "skills": self._profile_data.get("skills", []),
                "target_domains": self._profile_data.get("target_domains", ["General"]),
                "resume_text": self._profile_data.get("resume_text", "")
            }


        return {
            "name": self.settings.candidate.name,
            "email": self.settings.candidate.email,
            "phone": self.settings.candidate.phone,
            "linkedin": self.settings.candidate.linkedin,
            "location": self.settings.candidate.location,
            "degree": self.settings.candidate.degree,
            "institution": self.settings.candidate.institution,
            "skills": [
                "Financial Modeling", "Corporate Budgeting", "MS Excel",
                "Working Capital", "Credit Analysis", "Logistics"
            ],
            "target_domains": ["Finance & Banking", "FinTech", "Operations"],
            "resume_text": self.get_resume_text()
        }

