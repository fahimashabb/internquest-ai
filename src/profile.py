"""
🎯 Internship Hunter AI - Precision CV Scanner & Profile Intelligence Engine
Performs deep structural analysis of candidate resumes across Science, Commerce, Arts,
Engineering, Healthcare, and all academic backgrounds. Enforces strict 10 MB size limit.
"""

import re
import io
from pathlib import Path
from typing import Dict, Any, Optional, List
import pypdf
from src.config import AppSettings, load_settings

MAX_CV_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes


# Deep Multidisciplinary Skill Taxonomy
KNOWN_SKILLS = {
    "Technical & Engineering": [
        "python", "javascript", "typescript", "java", "c++", "c#", "php", "golang", "rust",
        "react", "angular", "vue", "next.js", "node.js", "django", "flask", "fastapi", "spring boot",
        "sql", "postgresql", "mysql", "mongodb", "sqlite", "redis", "docker", "kubernetes", "aws", "gcp",
        "machine learning", "deep learning", "nlp", "data science", "data analysis", "html", "css",
        "rest api", "graphql", "git", "linux", "embedded systems", "matlab", "verilog", "biotech"
    ],
    "Business, Finance & Commerce": [
        "financial modeling", "financial analysis", "corporate finance", "accounting",
        "banking", "budgeting", "valuation", "dcf", "investment banking", "portfolio management",
        "working capital", "credit analysis", "auditing", "taxation", "treasury", "fintech",
        "ms excel", "excel", "xlookup", "pivottables", "financial statements", "trade finance",
        "market research", "brand management", "digital marketing", "seo", "sem", "lead generation",
        "supply chain", "logistics", "procurement", "talent acquisition", "human resources"
    ],
    "Creative, Media & Arts": [
        "ui/ux", "figma", "adobe photoshop", "illustrator", "premiere pro", "after effects",
        "graphic design", "video editing", "wireframing", "prototyping", "motion graphics",
        "copywriting", "content writing", "creative writing", "journalism", "public relations",
        "social media management", "brand storytelling", "legal research", "contract drafting"
    ],
    "Tools & Analytics": [
        "power bi", "tableau", "spss", "stata", "jira", "confluence", "trello", "notion",
        "salesforce", "hubspot", "google analytics", "metatrader", "bloomberg", "sap"
    ],
    "Professional & Soft Skills": [
        "team leadership", "cross-functional collaboration", "critical thinking",
        "problem solving", "public speaking", "project management", "agile", "scrum",
        "stakeholder management", "strategic planning", "negotiation", "time management"
    ]
}


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes with multi-layer error healing."""
    if len(pdf_bytes) > MAX_CV_SIZE_BYTES:
        raise ValueError(f"File size ({len(pdf_bytes) / (1024*1024):.2f} MB) exceeds the 10 MB limit.")

    # Heal stream header if necessary
    idx = pdf_bytes.find(b"%PDF-")
    if idx > 0:
        pdf_bytes = pdf_bytes[idx:]

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                extracted.append(t.strip())
        text = "\n\n".join(extracted).strip()
        if text:
            return text
    except Exception as e:
        print(f"[Self-Healing Warning] pypdf reader encountered an issue: {e}")

    # Fallback heuristic string extractor
    try:
        raw_text = pdf_bytes.decode("latin-1", errors="ignore")
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', raw_text)
        matches = re.findall(r'[A-Za-z0-9\s.,;:()\-/@]{4,}', cleaned)
        return " ".join(matches[:500]).strip()
    except Exception:
        return ""


def parse_resume_content(text: str) -> Dict[str, Any]:
    """Perform comprehensive structural parsing on resume text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lower_text = text.lower()

    # 1. Candidate Name (cleaning headers like "Curriculum Vitae", "Resume", etc.)
    name = "Candidate"
    invalid_name_keywords = ["curriculum", "vitae", "resume", "page", "profile", "contact", "summary", "education"]
    for line in lines[:8]:
        if any(kw in line.lower() for kw in invalid_name_keywords):
            continue
        if "@" in line or "http" in line.lower() or any(c.isdigit() for c in line if len(line) > 10):
            continue
        cleaned = re.sub(r'[^a-zA-Z\s\.]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and len(cleaned) < 35:
            name = cleaned.title()
            break

    # 2. Email Detection
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    # 3. Phone Detection (Bangladesh +880 & International)
    phone_match = re.search(r'(?:\+?880|0)?1[3-9]\d{8}|\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,9}', text)
    phone = phone_match.group(0) if phone_match else ""

    # 4. Social Links (LinkedIn, GitHub, Portfolio)
    li_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)', text)
    linkedin = f"https://www.linkedin.com/in/{li_match.group(1)}" if li_match else ""

    gh_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-_]+)', text)
    github = f"https://github.com/{gh_match.group(1)}" if gh_match else ""

    # 5. Education Analysis
    degree = "Undergraduate Student"
    degree_patterns = [
        (r'\b(bachelor of business administration|bba)\b', 'Bachelor of Business Administration (BBA)'),
        (r'\b(bachelor of science|b\.sc|bsc)\b', 'Bachelor of Science (B.Sc.)'),
        (r'\b(bachelor of arts|b\.a|ba)\b', 'Bachelor of Arts (B.A.)'),
        (r'\b(master of business administration|mba)\b', 'Master of Business Administration (MBA)'),
        (r'\b(master of science|m\.sc|msc)\b', 'Master of Science (M.Sc.)'),
        (r'\b(computer science and engineering|cse|software engineering)\b', 'B.Sc. in Computer Science & Engineering'),
        (r'\b(electrical and electronic engineering|eee)\b', 'B.Sc. in Electrical & Electronic Engineering'),
        (r'\b(finance|accounting|marketing|economics|management)\b', 'Business Major (Finance & Commerce)')
    ]
    for pattern, title in degree_patterns:
        if re.search(pattern, lower_text):
            degree = title
            break

    # Institution
    institution = ""
    inst_patterns = [
        r'\b(university of dhaka|dhaka university|du|buet|north south university|nsu|brac university|bracu|iba|iut|jahangirnagar university|ju|rajshahi university|chittagong university|aust|aiub|ewu|bup|sust|ulab)\b',
        r'([A-Za-z\s]+(university|college|institute|academy|school of business))'
    ]
    for pattern in inst_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            institution = m.group(0).strip().title()
            break

    # GPA / CGPA
    cgpa_match = re.search(r'(?:cgpa|gpa)[\s:]*([0-4]\.\d{1,2}|5\.00)', lower_text)
    cgpa = cgpa_match.group(1) if cgpa_match else ""

    # 6. Detailed Skill Taxonomy Categorization
    categorized_skills: Dict[str, List[str]] = {}
    flat_skills: List[str] = []

    for category, skill_list in KNOWN_SKILLS.items():
        matched = []
        for skill in skill_list:
            if re.search(rf'\b{re.escape(skill)}\b', lower_text):
                matched.append(skill.title())
                if skill.title() not in flat_skills:
                    flat_skills.append(skill.title())
        if matched:
            categorized_skills[category] = matched

    # 7. Discipline Determination
    discipline = "General Studies"
    tech_count = len(categorized_skills.get("Technical & Engineering", []))
    biz_count = len(categorized_skills.get("Business, Finance & Commerce", []))
    arts_count = len(categorized_skills.get("Creative, Media & Arts", []))

    if tech_count >= max(biz_count, arts_count, 1):
        discipline = "🧪 Science & Tech"
    elif biz_count >= max(tech_count, arts_count, 1):
        discipline = "📈 Business & Commerce"
    elif arts_count >= 1:
        discipline = "🎨 Arts, Media & Design"

    # 8. Career Archetype & Tailored Synthesis
    archetype = f"{discipline.split()[-1]} Intern"
    if "Computer" in degree or tech_count >= 3:
        archetype = "Software Engineering & Data Trainee"
    elif "Finance" in degree or "Financial Modeling" in flat_skills:
        archetype = "Corporate Finance & Valuation Trainee"
    elif "Marketing" in degree or "Digital Marketing" in flat_skills:
        archetype = "Brand Strategy & Growth Marketing Trainee"
    elif arts_count >= 2:
        archetype = "Creative Design & Communications Trainee"

    # Executive Strengths Matrix
    strengths = []
    if flat_skills:
        strengths.append(f"Demonstrated domain capability in {', '.join(flat_skills[:4])}.")
    if institution:
        strengths.append(f"Strong academic foundation from {institution}{' with CGPA ' + cgpa if cgpa else ''}.")
    strengths.append("High agility with readiness for rigorous internship and corporate project execution.")

    # 9. Location Detection
    loc_match = re.search(r'\b(dhaka|chittagong|sylhet|rajshahi|khulna|barishal|bangladesh)\b', lower_text)
    location = loc_match.group(0).title() if loc_match else "Dhaka, Bangladesh"

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "location": location,
        "degree": degree,
        "institution": institution or "University",
        "cgpa": cgpa,
        "discipline": discipline,
        "archetype": archetype,
        "strengths": strengths,
        "skills": flat_skills[:20],
        "categorized_skills": categorized_skills,
        "resume_text": text
    }


class CandidateProfile:
    def __init__(self, settings: Optional[AppSettings] = None, profile_data: Optional[Dict[str, Any]] = None):
        self.settings = settings or load_settings()
        self._profile_data = profile_data
        self._resume_text: Optional[str] = None

    @classmethod
    def from_pdf_bytes(cls, pdf_bytes: bytes, settings: Optional[AppSettings] = None) -> "CandidateProfile":
        """Instantiate a profile from uploaded PDF file bytes with 10MB limit validation."""
        text = extract_text_from_pdf_bytes(pdf_bytes)
        profile_data = parse_resume_content(text)
        inst = cls(settings=settings, profile_data=profile_data)
        inst._resume_text = text
        return inst

    @classmethod
    def from_dict(cls, data: Dict[str, Any], settings: Optional[AppSettings] = None) -> "CandidateProfile":
        return cls(settings=settings, profile_data=data)

    def get_structured_profile(self) -> Dict[str, Any]:
        """Return high-fidelity structured profile."""
        if self._profile_data:
            return self._profile_data

        return {
            "name": self.settings.candidate.name,
            "email": self.settings.candidate.email,
            "phone": self.settings.candidate.phone,
            "linkedin": self.settings.candidate.linkedin,
            "github": "",
            "location": self.settings.candidate.location,
            "degree": self.settings.candidate.degree,
            "institution": self.settings.candidate.institution,
            "cgpa": "",
            "discipline": "📈 Business & Commerce",
            "archetype": "Finance & Operations Trainee",
            "strengths": [
                "Proficiency in Financial Analysis & Corporate Modeling",
                "Advanced spreadsheet and quantitative analytics"
            ],
            "skills": [
                "Financial Modeling", "Corporate Budgeting", "MS Excel",
                "Working Capital", "Credit Analysis", "Logistics"
            ],
            "categorized_skills": {
                "Business, Finance & Commerce": ["Financial Modeling", "Corporate Budgeting", "Credit Analysis"],
                "Tools & Analytics": ["MS Excel", "Power BI"]
            },
            "resume_text": ""
        }
