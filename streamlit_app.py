"""
🎯 AI Internship Hunter & Tailored Outreach Platform
A universal, multi-user web application where anyone can upload their CV (PDF),
discover matching internships across Bangladesh & global remote boards,
and generate customized outreach pitches.
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

# Page Configuration
st.set_page_config(
    page_title="AI Internship Hunter - Universal Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .job-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .badge-high {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-med {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-low {
        background-color: #f1f5f9;
        color: #475569;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_all_jobs():
    """Load cached internship opportunities from the database."""
    db_path = BASE_DIR / "data" / "applications.db"
    if not db_path.exists():
        return []

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs ORDER BY found_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Failed to load jobs database: {e}")
        return []


def main():
    # Header
    st.markdown('<div class="main-header">🎯 AI Internship Hunter & Application Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload your CV to find tailored internship opportunities across Bangladesh banks, MNCs, NGOs, FinTechs, and remote global boards with custom-tailored outreach pitches.</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Search & Filter")
        sector_filter = st.selectbox(
            "Target Sector",
            ["All Sectors", "Banking & Finance", "FinTech", "Tech & Software", "MNC / Conglomerate", "NGO & Development", "Remote Global"]
        )
        min_score = st.slider("Minimum Match Score (%)", min_value=30, max_value=95, value=60, step=5)
        
        st.divider()
        st.markdown("### 🤖 AI Pitch Engine")
        custom_gemini_key = st.text_input("Gemini API Key (Optional for AI Deep Reasoning)", type="password", help="Leave blank to use built-in smart heuristic matching")

        st.divider()
        st.caption("Developed by **Fahim Ashab** | Open Source on GitHub")

    # Resume Upload Section
    st.markdown("### 📄 Step 1: Upload Your CV / Resume")
    uploaded_file = st.file_uploader("Drop your PDF resume here to analyze skills and discover matching roles:", type=["pdf"])

    all_jobs = load_all_jobs()
    settings = load_settings()
    if custom_gemini_key:
        settings.gemini_api_key = custom_gemini_key

    # Candidate profile handling
    profile_data = None
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        with st.spinner("Extracting skills and profile from your resume..."):
            profile = CandidateProfile.from_pdf_bytes(pdf_bytes, settings=settings)
            profile_data = profile.get_structured_profile()

        # Display Candidate Card
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.success(f"👤 **Candidate**: {profile_data.get('name', 'Candidate')}")
            st.info(f"🎓 **Degree**: {profile_data.get('degree', 'Student')} - {profile_data.get('institution', 'University')}")
        with col2:
            st.info(f"📍 **Location**: {profile_data.get('location', 'Bangladesh')}")
            st.info(f"✉️ **Contact**: {profile_data.get('email', 'Extracted from CV')} | {profile_data.get('phone', '')}")
        with col3:
            skills = profile_data.get('skills', [])
            st.write("**Detected Skills**:")
            if skills:
                st.write(" • " + "\n • ".join(skills[:8]))
            else:
                st.write("General Business & Operations")

    else:
        st.info("💡 Upload your CV above to get personalized match scores and custom-generated pitches. Or browse all available opportunities below:")
        profile = CandidateProfile(settings=settings)
        profile_data = profile.get_structured_profile()

    st.markdown("---")
    st.markdown(f"### 💼 Step 2: Available Opportunities ({len(all_jobs)} in Database)")

    if not all_jobs:
        st.warning("No opportunities currently loaded in the database. Run discovery to scrape fresh postings.")
        return

    # Match evaluation
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

        # Apply sector filter
        category = "Other"
        text_full = f"{job_obj.title} {job_obj.company} {job_obj.description}".lower()
        if any(b in text_full for b in ["bank", "finance", "treasury", "credit", "audit", "accounting"]):
            category = "Banking & Finance"
        elif any(f in text_full for f in ["fintech", "bkash", "nagad", "payment"]):
            category = "FinTech"
        elif any(t in text_full for t in ["software", "developer", "engineer", "python", "tech", "react"]):
            category = "Tech & Software"
        elif any(n in text_full for n in ["ngo", "brac", "un", "foundation", "development"]):
            category = "NGO & Development"
        elif any(m in text_full for m in ["unilever", "bat", "nestle", "square", "pran", "beximco"]):
            category = "MNC / Conglomerate"
        elif "remote" in job_obj.location.lower() or job_obj.source in ("jobicy", "remotive"):
            category = "Remote Global"

        if sector_filter != "All Sectors" and category != sector_filter:
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
                            🏢 {j.company} &nbsp;•&nbsp; 📍 {j.location} &nbsp;•&nbsp; 🏷️ {item['category']}
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
                    st.text_area("Cover Letter / Email Pitch", value=item["cover_letter"], height=200, key=f"pitch_{idx}")
                    if item.get("contact_email"):
                        st.caption(f"📫 Official Contact Email: `{item['contact_email']}`")
            with colB:
                st.link_button(f"🔗 View & Apply on Official Portal", j.url, use_container_width=True)

            st.write("")


if __name__ == "__main__":
    main()
