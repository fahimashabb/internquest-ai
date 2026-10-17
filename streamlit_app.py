"""
🎯 InternQuest AI - Universal Internship Hunter & Matcher
Cloud Web Application for Science, Commerce, Arts, Engineering & All Majors.
"""

import os
import sys
import sqlite3
from pathlib import Path
import streamlit as st

# Setup base paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.profile import CandidateProfile, extract_text_from_pdf_bytes, parse_resume_content
from src.matcher.gemini_evaluator import GeminiEvaluator
from src.scrapers.base import JobListing
from src.config import load_settings
from src.auth import user_manager

st.set_page_config(
    page_title="InternQuest AI - Universal Internship Hunter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme & Styling
st.markdown("""
<style>
    .brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .job-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }
    .badge-high {
        background-color: #dcfce7;
        color: #166534;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-med {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-low {
        background-color: #f1f5f9;
        color: #475569;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .track-pill {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 8px;
        background: #e0e7ff;
        color: #3730a3;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_all_jobs():
    """Load cached internship opportunities from the database."""
    try:
        from src.tracker import ApplicationTracker
        tracker = ApplicationTracker()
        return tracker.get_all_jobs()
    except Exception as e:
        st.error(f"Failed to load jobs database: {e}")
        return []


def main():
    # Brand Header with Logo
    col_logo, col_text = st.columns([0.08, 0.92])
    with col_logo:
        st.markdown("""
        <svg width="56" height="56" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="100" height="100" rx="24" fill="url(#bgGrad)"/>
            <path d="M50 22L80 37L50 52L20 37L50 22Z" fill="#FFFFFF"/>
            <path d="M30 46V64C30 73 50 78 50 78C50 78 70 73 70 64V46L50 56L30 46Z" fill="#E0E7FF" fill-opacity="0.85"/>
            <circle cx="50" cy="50" r="7" fill="#38BDF8"/>
            <defs>
              <linearGradient id="bgGrad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                <stop stop-color="#4F46E5"/>
                <stop offset="0.5" stop-color="#7C3AED"/>
                <stop offset="1" stop-color="#06B6D4"/>
              </linearGradient>
            </defs>
        </svg>
        """, unsafe_allow_html=True)
    with col_text:
        st.markdown('<div class="brand-title">InternQuest AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Universal AI Internship Hunter & Matcher for <strong>Science, Commerce, Arts, Tech & All Majors</strong></div>', unsafe_allow_html=True)

    # Authentication & User State in Streamlit Session
    if "user" not in st.session_state:
        st.session_state.user = None

    # Sidebar: Account & Search Filters
    with st.sidebar:
        st.markdown("### 👤 User Account")
        if st.session_state.user:
            u = st.session_state.user
            st.success(f"Signed in as **{u['name']}**")
            st.caption(f"Track: {u.get('track', 'General')} | {u.get('degree', '')}")
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            auth_choice = st.radio("Access Your Account", ["Sign In", "Register Free"], horizontal=True)
            if auth_choice == "Sign In":
                login_email = st.text_input("Email", key="l_email")
                login_pass = st.text_input("Password", type="password", key="l_pass")
                if st.button("Sign In", use_container_width=True):
                    res = user_manager.authenticate_user(login_email, login_pass)
                    if res.get("success"):
                        st.session_state.user = res["user"]
                        st.success(res["message"])
                        st.rerun()
                    else:
                        st.error(res.get("message", "Login failed"))
            else:
                reg_name = st.text_input("Full Name", key="r_name")
                reg_email = st.text_input("Email", key="r_email")
                reg_pass = st.text_input("Password (min 6 chars)", type="password", key="r_pass")
                reg_track = st.selectbox(
                    "Academic Track",
                    [
                        "🧪 Science & Engineering (CS, Data, Biotech, EEE)",
                        "📈 Commerce & Business (Finance, Banking, Marketing)",
                        "🎨 Arts, Media & Law (Content, UI/UX, Legal)",
                        "🏥 Health, Pharma & Life Sciences",
                        "🌐 General / Other Majors"
                    ]
                )
                if st.button("Create Account", use_container_width=True):
                    res = user_manager.register_user(
                        email=reg_email,
                        password=reg_pass,
                        name=reg_name,
                        track=reg_track
                    )
                    if res.get("success"):
                        st.session_state.user = res["user"]
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(res.get("message", "Registration failed"))

        st.divider()
        st.markdown("### 🎯 Discipline & Sector Filters")
        sector_filter = st.selectbox(
            "Target Discipline",
            [
                "All Disciplines",
                "🧪 Science, Tech & Engineering",
                "📈 Commerce, Banking & Finance",
                "🎨 Arts, Media, Design & Law",
                "🏢 MNCs & Conglomerates",
                "🌍 NGOs & Development",
                "🌐 Global Remote"
            ]
        )
        min_score = st.slider("Minimum Match Threshold (%)", min_value=30, max_value=95, value=55, step=5)

        st.divider()
        st.caption("InternQuest AI • Open-Source Career Platform")

    # Step 1: Resume Upload / Active Profile
    st.markdown("### 📄 Step 1: Upload or Connect Your CV")
    uploaded_file = st.file_uploader("Upload your resume in PDF format (Science, Commerce, Arts, or Tech):", type=["pdf"])

    settings = load_settings()
    profile_data = None
    profile = None

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        profile = CandidateProfile.from_pdf_bytes(pdf_bytes, settings=settings)
        profile_data = profile.get_structured_profile()

        # If user is logged in, automatically save CV to their profile
        if st.session_state.user:
            user_manager.update_user_cv(st.session_state.user["id"], pdf_bytes, uploaded_file.name)
            st.session_state.user = user_manager.get_user_by_id(st.session_state.user["id"])

        # Display Candidate Overview Card
        col1, col2, col3 = st.columns([1, 1, 1.2])
        with col1:
            st.success(f"👤 **Candidate**: {profile_data.get('name', 'Candidate')}")
            st.info(f"🎓 **Degree**: {profile_data.get('degree', 'Student')}")
        with col2:
            st.info(f"🏛️ **Institution**: {profile_data.get('institution', 'University')}")
            st.info(f"📍 **Location**: {profile_data.get('location', 'Bangladesh')}")
        with col3:
            skills = profile_data.get("skills", [])
            st.write("**Detected Skills & Alignment**:")
            if skills:
                st.write(" • " + "\n • ".join(skills[:8]))
            else:
                st.write("Multi-disciplinary skillset")
    elif st.session_state.user and st.session_state.user.get("has_resume"):
        # Load from saved profile
        u = st.session_state.user
        pdf_bytes = user_manager.get_user_resume_bytes(u["id"])
        if pdf_bytes:
            profile = CandidateProfile.from_pdf_bytes(pdf_bytes, settings=settings)
            profile_data = profile.get_structured_profile()
            st.success(f"📁 Loaded your saved CV: **{u.get('resume_filename', 'Resume.pdf')}** ({u.get('name')})")
    else:
        st.info("💡 Drop your CV above to get custom match scores and tailored pitches. You can also explore all opportunities below:")
        profile = CandidateProfile(settings=settings)
        profile_data = profile.get_structured_profile()

    st.markdown("---")
    st.markdown(f"### 💼 Step 2: Live Opportunities Across Bangladesh & Global Boards")

    all_jobs = load_all_jobs()
    if not all_jobs:
        st.warning("No opportunities currently loaded. The discovery engine will populate them.")
        return

    evaluator = GeminiEvaluator(settings=settings, profile=profile)
    evaluated_jobs = []

    for rj in all_jobs:
        job_obj = JobListing(
            title=rj["title"],
            company=rj["company"],
            location=rj.get("location") or "Bangladesh",
            url=rj["url"],
            description=rj.get("description") or "",
            source=rj.get("source") or "web",
            contact_email=rj.get("contact_email")
        )
        evaluated = evaluator._evaluate_with_heuristics(job_obj)
        score = evaluated.match_score or 50

        # Discipline categorization
        category = "Other"
        text_full = f"{job_obj.title} {job_obj.company} {job_obj.description}".lower()
        if any(s in text_full for s in ["software", "developer", "engineer", "python", "tech", "data", "ai", "machine learning", "biotech", "microbiology", "pharmacy", "civil", "electrical"]):
            category = "🧪 Science, Tech & Engineering"
        elif any(c in text_full for c in ["bank", "finance", "treasury", "credit", "audit", "accounting", "marketing", "hr", "supply chain", "budget", "fintech"]):
            category = "📈 Commerce, Banking & Finance"
        elif any(a in text_full for a in ["content", "writing", "graphic", "design", "ui", "ux", "media", "journalism", "communications", "legal", "law", "social"]):
            category = "🎨 Arts, Media, Design & Law"
        elif any(m in text_full for m in ["unilever", "bat", "nestle", "square", "pran", "beximco", "marico", "walton"]):
            category = "🏢 MNCs & Conglomerates"
        elif any(n in text_full for n in ["ngo", "brac", "un", "foundation", "development", "undp", "world bank", "usaid", "care", "unicef"]):
            category = "🌍 NGOs & Development"
        elif "remote" in job_obj.location.lower() or job_obj.source in ("jobicy", "remotive"):
            category = "🌐 Global Remote"

        if sector_filter != "All Disciplines" and category != sector_filter:
            continue

        if score >= min_score:
            evaluated_jobs.append({
                "job": job_obj,
                "score": score,
                "category": category,
                "rationale": evaluated.match_rationale,
                "subject": evaluated.tailored_email_subject,
                "cover_letter": evaluated.tailored_cover_letter,
                "contact_email": evaluated.contact_email or rj.get("contact_email")
            })

    evaluated_jobs.sort(key=lambda x: x["score"], reverse=True)

    st.write(f"Showing **{len(evaluated_jobs)}** internships matching your criteria:")

    for idx, item in enumerate(evaluated_jobs):
        j = item["job"]
        score = item["score"]
        badge_class = "badge-high" if score >= 80 else ("badge-med" if score >= 65 else "badge-low")

        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0 0 4px 0; color: #0f172a;">{j.title}</h4>
                        <div style="color: #475569; font-weight: 600; margin-bottom: 6px;">
                            🏢 {j.company} &nbsp;•&nbsp; 📍 {j.location} &nbsp;•&nbsp; <span class="track-pill">{item['category']}</span>
                        </div>
                    </div>
                    <div>
                        <span class="{badge_class}">{score}% Match</span>
                    </div>
                </div>
                <p style="color: #64748b; font-size: 0.9rem; margin: 8px 0;">{item['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)

            colA, colB = st.columns([1, 1])
            with colA:
                with st.expander(f"✉️ View Tailored Pitch for {j.company}"):
                    st.text_input("Subject Line", value=item["subject"], key=f"subj_{idx}")
                    st.text_area("Tailored Outreach Pitch", value=item["cover_letter"], height=200, key=f"pitch_{idx}")
                    if item.get("contact_email"):
                        st.caption(f"📫 Official Contact Email: `{item['contact_email']}`")
            with colB:
                st.link_button(f"🔗 View & Apply on Official Portal", j.url, use_container_width=True)

            st.write("")


if __name__ == "__main__":
    main()
