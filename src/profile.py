"""
🎯 Internship Hunter AI - Precision CV Scanner, ATS Engine & Profile Intelligence
Performs deep structural analysis of candidate resumes across:
1. 🧪 Science & Tech (Computer Science, Engineering, Data, Biotech, Pharma)
2. 📈 Business & Commerce (Finance, Banking, Accounting, Marketing, Supply Chain)
3. 🎨 Arts & Social Science (Media, Design, Communications, Law, Economics)

Features:
- Latest Institution of Study hierarchy (detects current university over college)
- High-fidelity Applicant Tracking System (ATS) scoring engine (0-100) with category breakdowns
- Strict 10 MB PDF upload limits
"""

import re
import io
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pypdf
from src.config import AppSettings, load_settings

MAX_CV_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes

# Comprehensive Registry of Bangladesh Universities (Public, Tech, Agricultural & Top Private)
BANGLADESH_UNIVERSITIES: List[Tuple[str, List[str]]] = [
    ("Jashore University of Science and Technology (JUST)", [
        r"jashore university of science and technology",
        r"jessore university of science and technology",
        r"\bjust\b"
    ]),
    ("Bangladesh University of Engineering and Technology (BUET)", [
        r"bangladesh university of engineering and technology",
        r"\bbuet\b"
    ]),
    ("University of Dhaka (DU)", [
        r"university of dhaka",
        r"dhaka university",
        r"\bdu\b"
    ]),
    ("Rajshahi University of Engineering & Technology (RUET)", [
        r"rajshahi university of engineering",
        r"\bruet\b"
    ]),
    ("Chittagong University of Engineering & Technology (CUET)", [
        r"chittagong university of engineering",
        r"\bcuet\b"
    ]),
    ("Khulna University of Engineering & Technology (KUET)", [
        r"khulna university of engineering",
        r"\bkuet\b"
    ]),
    ("Shahjalal University of Science and Technology (SUST)", [
        r"shahjalal university of science and technology",
        r"\bsust\b"
    ]),
    ("Jahangirnagar University (JU)", [
        r"jahangirnagar university",
        r"\bju\b"
    ]),
    ("University of Rajshahi (RU)", [
        r"university of rajshahi",
        r"rajshahi university",
        r"\bru\b"
    ]),
    ("University of Chittagong (CU)", [
        r"university of chittagong",
        r"chittagong university",
        r"\bcu\b"
    ]),
    ("Khulna University (KU)", [
        r"khulna university",
        r"\bku\b"
    ]),
    ("Bangladesh University of Professionals (BUP)", [
        r"bangladesh university of professionals",
        r"\bbup\b"
    ]),
    ("Islamic University of Technology (IUT)", [
        r"islamic university of technology",
        r"\biut\b"
    ]),
    ("Jagannath University (JnU)", [
        r"jagannath university",
        r"\bjnu\b"
    ]),
    ("Comilla University (CoU)", [
        r"comilla university",
        r"\bcou\b"
    ]),
    ("Begum Rokeya University, Rangpur (BRUR)", [
        r"begum rokeya university",
        r"\bbrur\b"
    ]),
    ("Haji Mohammad Danesh Science and Technology University (HSTU)", [
        r"haji mohammad danesh science and technology university",
        r"\bhstu\b"
    ]),
    ("Mawlana Bhashani Science and Technology University (MBSTU)", [
        r"mawlana bhashani science and technology university",
        r"\bmbstu\b"
    ]),
    ("Noakhali Science and Technology University (NSTU)", [
        r"noakhali science and technology university",
        r"\bnstu\b"
    ]),
    ("Patuakhali Science and Technology University (PSTU)", [
        r"patuakhali science and technology university",
        r"\bpstu\b"
    ]),
    ("Bangladesh Agricultural University (BAU)", [
        r"bangladesh agricultural university",
        r"\bbau\b"
    ]),
    ("Bangabandhu Sheikh Mujibur Rahman Science and Technology University (BSMRSTU)", [
        r"bangabandhu sheikh mujibur rahman science and technology university",
        r"\bbsmrstu\b"
    ]),
    ("North South University (NSU)", [
        r"north south university",
        r"\bnsu\b"
    ]),
    ("BRAC University (BRACU)", [
        r"brac university",
        r"\bbracu\b"
    ]),
    ("Independent University, Bangladesh (IUB)", [
        r"independent university,? bangladesh",
        r"\biub\b"
    ]),
    ("American International University-Bangladesh (AIUB)", [
        r"american international university[- ]bangladesh",
        r"\baiub\b"
    ]),
    ("Ahsanullah University of Science and Technology (AUST)", [
        r"ahsanullah university of science and technology",
        r"\baust\b"
    ]),
    ("East West University (EWU)", [
        r"east west university",
        r"\bewu\b"
    ]),
    ("United International University (UIU)", [
        r"united international university",
        r"\buiu\b"
    ]),
    ("University of Liberal Arts Bangladesh (ULAB)", [
        r"university of liberal arts bangladesh",
        r"\bulab\b"
    ]),
    ("Daffodil International University (DIU)", [
        r"daffodil international university",
        r"\bdiu\b"
    ]),
    ("Green University of Bangladesh", [
        r"green university of bangladesh",
        r"green university"
    ]),
    ("Southeast University", [
        r"southeast university"
    ]),
    ("University of Asia Pacific (UAP)", [
        r"university of asia pacific",
        r"\buap\b"
    ]),
    ("Stamford University Bangladesh", [
        r"stamford university bangladesh",
        r"stamford university"
    ]),
    ("IBA, University of Dhaka", [
        r"institute of business administration,? du",
        r"iba,? du",
        r"\biba\b"
    ])
]

# High-Yield Action Verbs for ATS Analysis
ACTION_VERBS = [
    "developed", "engineered", "implemented", "optimized", "designed",
    "analyzed", "collaborated", "built", "managed", "deployed",
    "created", "led", "architected", "spearheaded", "researched",
    "automated", "integrated", "delivered", "formulated", "streamlined",
    "executed", "modeled", "coordinated", "evaluated", "resolved"
]

# Multidisciplinary Skill Taxonomy across the 3 Tracks
KNOWN_SKILLS = {
    "Technical & Engineering": [
        "python", "javascript", "typescript", "java", "c++", "c#", "php", "golang", "rust",
        "react", "angular", "vue", "next.js", "node.js", "django", "flask", "fastapi", "spring boot",
        "sql", "postgresql", "mysql", "mongodb", "sqlite", "redis", "docker", "kubernetes", "aws", "gcp",
        "machine learning", "deep learning", "nlp", "data science", "data analysis", "html", "css",
        "rest api", "graphql", "git", "linux", "embedded systems", "matlab", "verilog", "biotech", "microbiology"
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


def extract_latest_institution(text: str) -> str:
    """
    Intelligently extracts the candidate's LATEST institution of study.
    Prioritizes current university over higher secondary/intermediate college (e.g. JUST over Degree College).
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    lower_text = text.lower()
    found_candidates: List[Tuple[int, str]] = []

    # 1. Check known Bangladesh universities with chronological and status weighting
    for official_name, patterns in BANGLADESH_UNIVERSITIES:
        for p in patterns:
            match = re.search(p, lower_text)
            if match:
                start_pos = match.start()
                # Examine surrounding window for active enrollment indicators
                surround = lower_text[max(0, start_pos - 160): min(len(lower_text), start_pos + 160)]
                weight = 100  # Base priority for recognized universities

                if any(w in surround for w in ["present", "current", "ongoing", "enrolled", "expected", "pursuing", "2026", "2025", "2024", "2027", "2028"]):
                    weight += 50
                if any(w in surround for w in ["b.sc", "bachelor", "bba", "undergraduate", "honours", "masters", "mba", "cse", "eee", "ce"]):
                    weight += 30

                found_candidates.append((weight, official_name))
                break

    if found_candidates:
        found_candidates.sort(key=lambda x: x[0], reverse=True)
        return found_candidates[0][1]

    # 2. Heuristic check: lines containing 'university' (excluding colleges)
    for line in lines:
        l_low = line.lower()
        if "university" in l_low and not any(neg in l_low for neg in ["college", "school", "board", "curriculum"]):
            if len(line) < 70 and not any(c in line for c in ["@", "http", ".com"]):
                clean = re.sub(r'[^a-zA-Z\s\(\)\,\-\&]', '', line).strip()
                if clean:
                    return clean.title()

    # 3. Fallback: Check for other tertiary institutes or colleges
    for line in lines:
        l_low = line.lower()
        if any(w in l_low for w in ["university", "institute", "college"]) and len(line) < 70:
            if not any(c in line for c in ["@", "http", ".com"]):
                clean = re.sub(r'[^a-zA-Z\s\(\)\,\-\&]', '', line).strip()
                if clean:
                    return clean.title()

    return "University of Study"


def calculate_ats_evaluation(text: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-fidelity Applicant Tracking System (ATS) Evaluator.
    Produces a 0-100 ATS Score, component breakdowns, action verbs, and actionable feedback.
    """
    lower = text.lower()
    scores: Dict[str, int] = {}
    suggestions: List[str] = []

    # 1. Contact & Identity Clarity (Max: 20 pts)
    c_score = 0
    if profile.get("name") and profile["name"] not in ("Candidate", "Unknown"):
        c_score += 4
    if profile.get("email"):
        c_score += 4
    else:
        suggestions.append("Add a professional personal email address at the top of your resume.")
    if profile.get("phone"):
        c_score += 4
    else:
        suggestions.append("Include your primary phone number for fast HR phone screens.")
    if profile.get("linkedin"):
        c_score += 4
    else:
        suggestions.append("Include a customized LinkedIn profile URL to verify your professional presence.")
    if profile.get("github") or "portfolio" in lower:
        c_score += 4
    else:
        if profile.get("discipline") == "🧪 Science & Tech":
            suggestions.append("Add your GitHub or project portfolio URL to validate code capabilities.")
    scores["contact"] = min(20, c_score)

    # 2. Education & Degree Hierarchy (Max: 20 pts)
    e_score = 0
    inst = profile.get("institution", "")
    if inst and "University" in inst:
        e_score += 8
    elif inst:
        e_score += 5
    else:
        suggestions.append("Ensure your latest university is explicitly stated with your expected graduation year.")

    deg = profile.get("degree", "")
    if deg and deg != "Undergraduate Student":
        e_score += 6
    if profile.get("cgpa"):
        e_score += 3
    if re.search(r'\b(202[0-9]|present|ongoing|enrolled)\b', lower):
        e_score += 3
    scores["education"] = min(20, e_score)

    # 3. Core Skills & Domain Keywords (Max: 20 pts)
    s_score = 0
    skills = profile.get("skills", [])
    if len(skills) >= 10:
        s_score = 20
    elif len(skills) >= 6:
        s_score = 15
    elif len(skills) >= 3:
        s_score = 10
    else:
        s_score = 5
        suggestions.append("Expand your skills section with 8-12 industry-standard technical and operational keywords.")
    scores["skills"] = min(20, s_score)

    # 4. Action Verbs & Quantified Results (Max: 20 pts)
    a_score = 0
    found_verbs = [v for v in ACTION_VERBS if re.search(rf'\b{v}\b', lower)]
    if len(found_verbs) >= 5:
        a_score += 10
    elif len(found_verbs) >= 2:
        a_score += 6
    else:
        a_score += 3
        suggestions.append("Begin project and work bullets with strong action verbs (e.g., Developed, Engineered, Analyzed).")

    metrics = re.findall(r'\b(\d+[\%xX\+]?|\d+\s*(?:users|clients|percent|days|months|records|million|thousand))\b', text)
    if len(metrics) >= 3:
        a_score += 10
    elif len(metrics) >= 1:
        a_score += 5
    else:
        suggestions.append("Include quantified impact metrics (e.g., 'Boosted efficiency by 25%', 'Handled 1,000+ records').")
    scores["action_verbs"] = min(20, a_score)

    # 5. Format, Headings & Readability (Max: 20 pts)
    f_score = 0
    sections = 0
    if re.search(r'\b(education|academic)\b', lower):
        sections += 1
    if re.search(r'\b(skills|technical proficiencies|competencies)\b', lower):
        sections += 1
    if re.search(r'\b(projects|experience|work|internships)\b', lower):
        sections += 1
    if re.search(r'\b(certifications|activities|achievements|leadership)\b', lower):
        sections += 1

    if sections >= 3:
        f_score += 10
    else:
        f_score += 5

    words = len(text.split())
    if 250 <= words <= 900:
        f_score += 10
    elif 150 <= words <= 1200:
        f_score += 6
    else:
        f_score += 3

    scores["readability"] = min(20, f_score)

    total_score = sum(scores.values())

    if total_score >= 85:
        grade = "A+ (Highly ATS-Optimized)"
    elif total_score >= 75:
        grade = "A (Strong Competitive Match)"
    elif total_score >= 60:
        grade = "B (Good - Minor Tweaks Recommended)"
    else:
        grade = "C (Needs ATS Optimization)"

    return {
        "total": total_score,
        "grade": grade,
        "scores": scores,
        "found_verbs": [v.title() for v in found_verbs[:6]],
        "metrics_count": len(metrics),
        "suggestions": suggestions[:4]
    }


def parse_resume_content(text: str) -> Dict[str, Any]:
    """Perform comprehensive structural parsing and ATS analysis on resume text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lower_text = text.lower()

    # 1. Candidate Name (clean headers like "Curriculum Vitae", "Resume", etc.)
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

    # 4. Social Links (LinkedIn, GitHub)
    li_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)', text)
    linkedin = f"https://www.linkedin.com/in/{li_match.group(1)}" if li_match else ""

    gh_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-_]+)', text)
    github = f"https://github.com/{gh_match.group(1)}" if gh_match else ""

    # 5. Degree Analysis (Specific Majors Checked First)
    degree = "Undergraduate Student"
    degree_patterns = [
        # Engineering & Tech
        (r'\b(computer science and engineering|cse|software engineering)\b', 'B.Sc. in Computer Science & Engineering'),
        (r'\b(electrical and electronic engineering|eee)\b', 'B.Sc. in Electrical & Electronic Engineering'),
        (r'\b(civil engineering|ce)\b', 'B.Sc. in Civil Engineering'),
        (r'\b(mechanical engineering|me)\b', 'B.Sc. in Mechanical Engineering'),
        (r'\b(biotechnology|genetic engineering|bge)\b', 'B.Sc. in Biotechnology & Genetic Engineering'),
        (r'\b(pharmacy|b\.pharm|m\.pharm)\b', 'Bachelor of Pharmacy (B.Pharm)'),
        (r'\b(information technology|it)\b', 'B.Sc. in Information Technology'),
        # Business & Commerce
        (r'\b(bachelor of business administration|bba)\b', 'Bachelor of Business Administration (BBA)'),
        (r'\b(finance|banking and insurance)\b', 'BBA in Finance & Banking'),
        (r'\b(accounting and information systems|accounting|ais)\b', 'BBA in Accounting'),
        (r'\b(marketing)\b', 'BBA in Marketing'),
        (r'\b(master of business administration|mba)\b', 'Master of Business Administration (MBA)'),
        # Arts & Social Science
        (r'\b(economics)\b', 'B.S.S. in Economics'),
        (r'\b(law|llb|ll\.b)\b', 'Bachelor of Laws (LL.B.)'),
        (r'\b(english|english literature)\b', 'B.A. in English Language & Literature'),
        (r'\b(journalism|mass communication)\b', 'B.S.S. in Mass Communication & Journalism'),
        (r'\b(bachelor of arts|b\.a|ba)\b', 'Bachelor of Arts (B.A.)'),
        # General fallbacks
        (r'\b(bachelor of science|b\.sc|bsc)\b', 'Bachelor of Science (B.Sc.)'),
        (r'\b(master of science|m\.sc|msc)\b', 'Master of Science (M.Sc.)')
    ]
    for pattern, title in degree_patterns:
        if re.search(pattern, lower_text):
            degree = title
            break

    # 6. Latest Institution of Study
    institution = extract_latest_institution(text)

    # 7. GPA / CGPA
    cgpa_match = re.search(r'(?:cgpa|gpa)[\s:]*([0-4]\.\d{1,2}|5\.00)', lower_text)
    cgpa = cgpa_match.group(1) if cgpa_match else ""

    # 8. Detailed Skill Taxonomy Categorization
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

    # 9. Strictly Enforce the 3 Student Categories
    tech_count = len(categorized_skills.get("Technical & Engineering", []))
    biz_count = len(categorized_skills.get("Business, Finance & Commerce", []))
    arts_count = len(categorized_skills.get("Creative, Media & Arts", []))

    deg_lower = degree.lower()
    if any(k in deg_lower for k in ["computer", "engineering", "b.sc", "bsc", "tech", "science", "eee", "civil", "mechanical", "biotech", "pharm"]):
        tech_count += 4
    if any(k in deg_lower for k in ["business", "bba", "mba", "finance", "accounting", "marketing", "commerce", "management"]):
        biz_count += 4
    if any(k in deg_lower for k in ["arts", "b.a", "ba", "social", "journalism", "media", "english", "law", "economics", "sociology"]):
        arts_count += 4

    if tech_count >= max(biz_count, arts_count, 1):
        discipline = "🧪 Science & Tech"
        archetype = "Software & Engineering Trainee"
    elif biz_count >= max(tech_count, arts_count, 1):
        discipline = "📈 Business & Commerce"
        archetype = "Corporate Commercial & Finance Trainee"
    else:
        discipline = "🎨 Arts & Social Science"
        archetype = "Creative Communications & Media Trainee"

    # Executive Strengths
    strengths = []
    if flat_skills:
        strengths.append(f"Demonstrated domain capability in {', '.join(flat_skills[:4])}.")
    if institution:
        strengths.append(f"Strong academic foundation from {institution}{' with CGPA ' + cgpa if cgpa else ''}.")
    strengths.append("High agility with readiness for rigorous internship and corporate project execution.")

    # Location Detection
    loc_match = re.search(r'\b(dhaka|chittagong|jashore|jessore|sylhet|rajshahi|khulna|barishal|rangpur|cumilla|mymensingh|bangladesh)\b', lower_text)
    location = loc_match.group(0).title() if loc_match else "Bangladesh"

    # Base profile dictionary
    profile_dict = {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "location": location,
        "degree": degree,
        "institution": institution,
        "cgpa": cgpa,
        "discipline": discipline,
        "archetype": archetype,
        "strengths": strengths,
        "skills": flat_skills[:20],
        "categorized_skills": categorized_skills,
        "resume_text": text
    }

    # Run comprehensive ATS evaluation
    ats_report = calculate_ats_evaluation(text, profile_dict)
    profile_dict["ats_score"] = ats_report["total"]
    profile_dict["ats_grade"] = ats_report["grade"]
    profile_dict["ats_breakdown"] = ats_report["scores"]
    profile_dict["ats_verbs"] = ats_report["found_verbs"]
    profile_dict["ats_suggestions"] = ats_report["suggestions"]

    return profile_dict


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
        """Return high-fidelity structured profile with ATS scoring."""
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
            "resume_text": "",
            "ats_score": 78,
            "ats_grade": "A (Strong Competitive Match)",
            "ats_breakdown": {"contact": 16, "education": 16, "skills": 16, "action_verbs": 14, "readability": 16},
            "ats_verbs": ["Developed", "Analyzed", "Engineered"],
            "ats_suggestions": ["Upload your PDF resume to generate an instant real-time ATS compatibility audit."]
        }
