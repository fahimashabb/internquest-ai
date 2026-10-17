"""
🎯 Internship Hunter AI - Universal Internship Hunter & Precision Matcher
Cloud Web Application for Science, Commerce, Arts, Engineering & All Majors.
Includes:
- Dark & Light Theme Switcher
- WordPress-Style Admin Control Hub (Exclusively for Platform Admin)
- Candidate CV Matcher & Multi-Discipline Search
- Bespoke 4-Paragraph Tailored Cover Letter Generator
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import streamlit as st

# Setup base paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.profile import CandidateProfile, extract_text_from_pdf_bytes, parse_resume_content
from src.matcher.gemini_evaluator import GeminiEvaluator, generate_custom_cover_letter
from src.scrapers.base import JobListing
from src.config import load_settings
from src.auth import user_manager
from src.tracker import ApplicationTracker

st.set_page_config(
    page_title="Internship Hunter AI - Universal Internship Hunter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "user" not in st.session_state:
    st.session_state.user = None
if "admin_unlocked" not in st.session_state:
    st.session_state.admin_unlocked = False

# Fetch Site Settings from DB
site_settings = user_manager.get_site_settings()
site_title = site_settings.get("site_title", "Internship Hunter AI")
announcement = site_settings.get("announcement", "")
show_announcement = site_settings.get("show_announcement", "true") == "true"
default_min_score = int(site_settings.get("min_match_score", "55"))

# Theme Toggle in Sidebar
with st.sidebar:
    st.markdown("### 🎨 Display Theme")
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("☀️ Light", use_container_width=True, type="primary" if st.session_state.theme == "light" else "secondary"):
            st.session_state.theme = "light"
            st.rerun()
    with theme_col2:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if st.session_state.theme == "dark" else "secondary"):
            st.session_state.theme = "dark"
            st.rerun()
    st.divider()

# Inject Dynamic CSS Based on Theme
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp {
            background-color: #090d16;
            color: #f1f5f9;
        }
        div[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        .brand-title {
            font-size: 2.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.1rem;
        }
        .brand-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            margin-bottom: 1.5rem;
        }
        .job-card {
            background-color: #131b2e;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        .job-card h4 {
            color: #f8fafc !important;
        }
        .badge-high {
            background-color: #064e3b;
            color: #a7f3d0;
            padding: 5px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
            border: 1px solid #059669;
        }
        .badge-med {
            background-color: #713f12;
            color: #fef08a;
            padding: 5px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
            border: 1px solid #ca8a04;
        }
        .badge-low {
            background-color: #1e293b;
            color: #94a3b8;
            padding: 5px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            border: 1px solid #334155;
        }
        .track-pill {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 8px;
            background: #312e81;
            color: #c7d2fe;
        }
        .admin-banner {
            background: linear-gradient(135deg, #1e1b4b, #312e81);
            border: 1px solid #6366f1;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            color: #e0e7ff;
            margin-bottom: 1.5rem;
        }
        .announcement-box {
            background: rgba(99, 102, 241, 0.12);
            border-left: 4px solid #6366f1;
            padding: 0.85rem 1.2rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 1.5rem;
            color: #e0e7ff;
        }
        div[data-testid="stExpander"] {
            background-color: #131b2e;
            border: 1px solid #1e293b;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
        }
        div[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
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
        .job-card h4 {
            color: #0f172a !important;
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
        .admin-banner {
            background: linear-gradient(135deg, #e0e7ff, #ede9fe);
            border: 1px solid #a5b4fc;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            color: #1e1b4b;
            margin-bottom: 1.5rem;
        }
        .announcement-box {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 0.85rem 1.2rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 1.5rem;
            color: #1e3a8a;
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=120)
def load_all_jobs():
    """Load cached internship opportunities from the database."""
    try:
        tracker = ApplicationTracker()
        return tracker.get_all_jobs()
    except Exception as e:
        st.error(f"Failed to load jobs database: {e}")
        return []


def is_super_admin() -> bool:
    """Verify if the current session has verified admin privileges."""
    if st.session_state.admin_unlocked:
        return True
    if st.session_state.user:
        return user_manager.is_admin(st.session_state.user)
    return False


# ─────────────────────────────────────────────────────────────
# 👑 WORDPRESS-STYLE ADMIN PANEL
# ─────────────────────────────────────────────────────────────
def render_admin_panel():
    st.markdown("""
    <div class="admin-banner">
        <h2 style="margin: 0 0 6px 0;">👑 Internship Hunter AI Control Hub (WordPress-Style Admin)</h2>
        <div>Super Administrator: <strong>Fahim Ashab</strong> &nbsp;•&nbsp; Full Platform Access & Settings</div>
    </div>
    """, unsafe_allow_html=True)

    tracker = ApplicationTracker()
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
        "📊 Dashboard Overview",
        "👥 Users & Resumes",
        "💼 Job Listings Manager",
        "⚙️ Site Settings",
        "📜 System Activity Logs"
    ])

    # ── Tab 1: Dashboard Overview ──
    with admin_tab1:
        st.markdown("### 📈 Platform Analytics & Quick Health")
        all_users = user_manager.get_all_users_admin()
        all_jobs = tracker.get_all_jobs()
        resumes_count = sum(1 for u in all_users if u.get("has_resume"))
        subscribers_count = sum(1 for u in all_users if u.get("daily_digest"))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Registered Users", len(all_users))
        m2.metric("Stored Resumes", resumes_count)
        m3.metric("Active Opportunities", len(all_jobs))
        m4.metric("10 AM Subscribers", subscribers_count)

        st.divider()
        st.markdown("#### ⚡ Quick Actions")
        qa_col1, qa_col2 = st.columns(2)
        with qa_col1:
            if st.button("🚀 Trigger Live Scraper Cycle", use_container_width=True):
                with st.spinner("Scraping fresh opportunities across boards..."):
                    try:
                        from src.scheduler import InternshipBot
                        bot = InternshipBot()
                        count = bot.run_discovery_cycle()
                        st.success(f"Scraper complete! Discovered and added {count} matching positions.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Scraper error: {e}")
        with qa_col2:
            if st.button("⏰ Dispatch Test 10:00 AM Morning Digest", use_container_width=True):
                with st.spinner("Generating and dispatching test digests..."):
                    try:
                        from src.scheduler import InternshipBot
                        bot = InternshipBot()
                        bot.send_daily_morning_digests()
                        st.success("Test Morning Digest executed successfully!")
                    except Exception as e:
                        st.error(f"Digest error: {e}")

    # ── Tab 2: Users & Resumes Manager ──
    with admin_tab2:
        st.markdown("### 👥 Manage Candidates & Resumes")
        all_users = user_manager.get_all_users_admin()

        if not all_users:
            st.info("No registered users yet. Guests are actively using the platform.")
        else:
            # Table summary
            user_table_data = []
            for u in all_users:
                user_table_data.append({
                    "Name": u.get("name", "N/A"),
                    "Email": u.get("email", "N/A"),
                    "Track": u.get("track", "General"),
                    "Degree": u.get("degree", "-"),
                    "Has CV": "✅ Yes" if u.get("has_resume") else "❌ No",
                    "Alerts": "🔔 10 AM Active" if u.get("daily_digest") else "🔕 Muted",
                    "Joined": str(u.get("created_at", ""))[:10]
                })
            st.dataframe(pd.DataFrame(user_table_data), use_container_width=True)

            st.divider()
            st.markdown("#### 🔍 Candidate Dossiers & CV Downloads")
            for u in all_users:
                with st.expander(f"👤 {u['name']} ({u['email']}) - Track: {u.get('track', 'General')}"):
                    uc1, uc2 = st.columns([2, 1])
                    with uc1:
                        st.write(f"**Institution:** {u.get('institution') or 'Not specified'}")
                        st.write(f"**Degree:** {u.get('degree') or 'Not specified'}")
                        st.write(f"**Phone:** {u.get('phone') or 'Not specified'}")
                        st.write(f"**Skills:** {', '.join(u.get('skills', [])) if u.get('skills') else 'Not extracted'}")
                    with uc2:
                        if u.get("has_resume"):
                            cv_data = user_manager.get_user_resume_bytes(u["id"])
                            if cv_data:
                                st.download_button(
                                    label=f"📥 Download {cv_data['filename']}",
                                    data=cv_data["bytes"],
                                    file_name=cv_data["filename"],
                                    mime="application/pdf",
                                    key=f"dl_{u['id']}",
                                    use_container_width=True
                                )
                        else:
                            st.caption("No resume attached.")

                        if st.button("🗑️ Delete User Account", key=f"del_{u['id']}", type="secondary", use_container_width=True):
                            user_manager.delete_user_admin(u["id"])
                            st.warning(f"Deleted user {u['name']}.")
                            st.rerun()

    # ── Tab 3: Job Listings Manager ──
    with admin_tab3:
        st.markdown("### 💼 Manage Internship Vacancies")

        with st.expander("➕ Post New Internship Listing (WordPress Style)", expanded=False):
            with st.form("new_job_form", clear_on_submit=True):
                nf_col1, nf_col2 = st.columns(2)
                with nf_col1:
                    new_title = st.text_input("Job Title *", placeholder="e.g. Summer Finance Intern 2026")
                    new_comp = st.text_input("Company Name *", placeholder="e.g. Standard Chartered Bank")
                    new_loc = st.text_input("Location", value="Dhaka, Bangladesh")
                with nf_col2:
                    new_url = st.text_input("Application Portal URL *", placeholder="https://company.com/apply")
                    new_email = st.text_input("Contact HR Email (Optional)", placeholder="hr@company.com")
                    new_score = st.slider("Initial Match Score (%)", 50, 95, 80)

                submitted = st.form_submit_button("Publish Internship Opportunity", use_container_width=True)
                if submitted:
                    if not new_title or not new_comp or not new_url:
                        st.error("Please fill in Job Title, Company, and URL.")
                    else:
                        tracker.add_job_admin(
                            title=new_title,
                            company=new_comp,
                            location=new_loc,
                            url=new_url,
                            contact_email=new_email,
                            match_score=new_score
                        )
                        st.success(f"Successfully published '{new_title}' at '{new_comp}'!")
                        st.cache_data.clear()
                        st.rerun()

        st.markdown("#### Active Listings Database")
        all_jobs = tracker.get_all_jobs()
        job_search = st.text_input("Search listings by title or company:", "")
        filtered = [j for j in all_jobs if job_search.lower() in f"{j['title']} {j['company']} {j.get('location', '')}".lower()]

        st.caption(f"Showing {len(filtered)} of {len(all_jobs)} opportunities:")
        for j in filtered[:40]:
            with st.container():
                jc1, jc2, jc3 = st.columns([0.65, 0.2, 0.15])
                with jc1:
                    st.markdown(f"**{j['title']}** — {j['company']} ({j.get('location', 'Dhaka')})")
                    st.caption(f"Source: {j.get('source', 'web')} • Link: [{j['url']}]({j['url']})")
                with jc2:
                    st.write(f"Score: **{j.get('match_score', 0)}%**")
                with jc3:
                    if st.button("🗑️ Delete", key=f"del_job_{j['id']}", use_container_width=True):
                        tracker.delete_job_admin(j["id"])
                        st.success(f"Removed listing {j['id']}.")
                        st.cache_data.clear()
                        st.rerun()
                st.divider()

    # ── Tab 4: Site Settings ──
    with admin_tab4:
        st.markdown("### ⚙️ WordPress-Style General Site Settings")
        with st.form("site_settings_form"):
            curr_title = st.text_input("Site / Brand Name", value=site_settings.get("site_title", "InternQuest AI"))
            curr_announcement = st.text_area("Public Announcement Banner", value=site_settings.get("announcement", ""))
            curr_show_announcement = st.checkbox("Show Announcement Banner to Visitors", value=site_settings.get("show_announcement", "true") == "true")
            curr_min_score = st.slider("Default Minimum Match Score Filter (%)", 30, 90, int(site_settings.get("min_match_score", "55")), step=5)
            curr_guest = st.checkbox("Allow Guest CV Uploads Without Registration", value=site_settings.get("allow_guest_mode", "true") == "true")
            curr_daily_limit = st.number_input("Max Auto-Email Applications Per Day", min_value=1, max_value=50, value=int(site_settings.get("daily_email_limit", "5")))

            save_settings = st.form_submit_button("💾 Save All Site Settings", use_container_width=True)
            if save_settings:
                user_manager.update_site_settings({
                    "site_title": curr_title,
                    "announcement": curr_announcement,
                    "show_announcement": "true" if curr_show_announcement else "false",
                    "min_match_score": str(curr_min_score),
                    "allow_guest_mode": "true" if curr_guest else "false",
                    "daily_email_limit": str(curr_daily_limit)
                })
                st.success("Platform settings saved and applied successfully!")
                st.rerun()

    # ── Tab 5: Activity Logs ──
    with admin_tab5:
        st.markdown("### 📜 System Activity & Audit Trail")
        logs = tracker.get_recent_activity(limit=60)
        if not logs:
            st.info("No activity records yet.")
        else:
            log_table = []
            for l in logs:
                log_table.append({
                    "Timestamp": l.get("timestamp", ""),
                    "Event Type": l.get("activity_type", ""),
                    "Details": l.get("details", "")
                })
            st.dataframe(pd.DataFrame(log_table), use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 🌐 PUBLIC CANDIDATE INTERFACE
# ─────────────────────────────────────────────────────────────
def main():
    # Public Announcement Banner if configured by Admin
    if show_announcement and announcement.strip():
        st.markdown(f'<div class="announcement-box">📢 <strong>Announcement:</strong> {announcement}</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="brand-title">{site_title}</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-subtitle">Universal AI Internship Hunter & Matcher for <strong>Science, Commerce, Arts, Tech & All Majors</strong></div>', unsafe_allow_html=True)

    # Sidebar: Account & Search Filters
    with st.sidebar:
        st.markdown("### 👤 User Account")
        if st.session_state.user:
            u = st.session_state.user
            admin_badge = " 👑 (Super Admin)" if user_manager.is_admin(u) else ""
            st.success(f"Signed in as **{u['name']}**{admin_badge}")
            st.caption(f"Track: {u.get('track', 'General')} | {u.get('degree', '')}")
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.user = None
                st.session_state.admin_unlocked = False
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

        # Super Admin Access Expander (Protected for Fahim only)
        if not is_super_admin():
            with st.expander("🔐 Admin Access (Fahim Only)"):
                admin_key = st.text_input("Admin Passkey", type="password", key="admin_key_input")
                if st.button("Verify Admin Key", use_container_width=True):
                    if admin_key in ("fahim@admin", "admin2026"):
                        st.session_state.admin_unlocked = True
                        st.success("Admin Hub Unlocked!")
                        st.rerun()
                    else:
                        st.error("Invalid Admin Passkey.")

        st.divider()

        # View Mode Toggle if Admin is Verified
        if is_super_admin():
            st.markdown("### 👑 Admin Navigation")
            active_view = st.radio("Select View:", ["💼 Public Internship Portal", "👑 WordPress Admin Panel"], index=0)
            st.divider()
        else:
            active_view = "💼 Public Internship Portal"

        st.markdown("### 🎯 Discipline & Sector Filters")
        scope_choice = st.radio(
            "Location Scope",
            ["All Locations", "🇧🇩 Bangladesh Only", "🌐 Global Remote"],
            index=0,
            horizontal=True
        )
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
        min_score = st.slider("Minimum Match Threshold (%)", min_value=30, max_value=95, value=default_min_score, step=5)

        st.divider()
        st.caption("Internship Hunter AI • Developed by Fahim Ashab")

    # If Admin selected the WordPress Admin Panel, route directly to it
    if is_super_admin() and active_view == "👑 WordPress Admin Panel":
        render_admin_panel()
        return

    # ── CANDIDATE PORTAL VIEW ──
    # Step 1: Resume Upload / Active Profile
    st.markdown("### 📄 Step 1: Upload or Connect Your CV")
    st.caption("Drop your resume in PDF format (Science, Commerce, Arts, or Tech; Max 10 MB) to unlock instant AI matching:")
    uploaded_file = st.file_uploader("Upload PDF Resume (< 10 MB):", type=["pdf"], label_visibility="collapsed")

    settings = load_settings()
    profile_data = None
    profile = None

    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("⚠️ Uploaded CV exceeds the maximum 10 MB limit. Please upload a PDF under 10 MB.")
            st.stop()
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
            major_text = f" - {profile_data.get('major')}" if profile_data.get('major') else ""
            st.info(f"🎓 **Degree**: {profile_data.get('degree', 'Student')}{major_text}")
            if profile_data.get('career_archetype'):
                st.caption(f"⚡ **Archetype**: `{profile_data.get('career_archetype')}`")
        with col2:
            st.info(f"🏛️ **Institution**: {profile_data.get('institution', 'University')}")
            st.info(f"📍 **Location**: {profile_data.get('location', 'Bangladesh')}")
            if profile_data.get('cgpa'):
                st.caption(f"📊 **CGPA**: {profile_data.get('cgpa')}")
        with col3:
            skills = profile_data.get("skills", [])
            st.write("**Detected Skills & Alignment**:")
            if skills:
                st.write(" • " + "\n • ".join(skills[:8]))
            else:
                st.write("Multi-disciplinary skillset")
            if profile_data.get("strengths"):
                st.caption("💪 Strengths: " + ", ".join(profile_data["strengths"][:3]))
    elif st.session_state.user and st.session_state.user.get("has_resume"):
        # Load from saved profile
        u = st.session_state.user
        cv_obj = user_manager.get_user_resume_bytes(u["id"])
        if cv_obj and cv_obj.get("bytes"):
            profile = CandidateProfile.from_pdf_bytes(cv_obj["bytes"], settings=settings)
            profile_data = profile.get_structured_profile()
            st.success(f"📁 Loaded your saved CV: **{u.get('resume_filename', 'Resume.pdf')}** ({u.get('name')})")
    else:
        st.info("💡 You can upload a CV above for 1-click tailored match scores, or explore all live opportunities below:")
        profile = CandidateProfile(settings=settings)
        profile_data = profile.get_structured_profile()

    st.markdown("---")
    st.markdown("### 💼 Step 2: Live Opportunities Across Bangladesh & Global Boards")

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

        # Scope filtering
        is_global = (rj.get("location_scope") == "global") or any(k in f"{job_obj.location} {job_obj.source}".lower() for k in ["remote", "worldwide", "global", "apac", "usa", "canada", "europe", "uk", "singapore"])
        if scope_choice == "🇧🇩 Bangladesh Only" and is_global:
            continue
        if scope_choice == "🌐 Global Remote" and not is_global:
            continue

        if sector_filter != "All Disciplines" and category != sector_filter:
            continue

        if score >= min_score:
            evaluated_jobs.append({
                "job": job_obj,
                "score": score,
                "category": category,
                "is_global": is_global,
                "deadline": rj.get("deadline"),
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
        scope_pill = "🌐 Global Remote" if item["is_global"] else "🇧🇩 Bangladesh"
        deadline_info = f" &nbsp;•&nbsp; ⏳ <strong>Deadline:</strong> {item['deadline']}" if item.get('deadline') else ""

        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0 0 4px 0;">{j.title}</h4>
                        <div style="font-weight: 600; margin-bottom: 6px; opacity: 0.85;">
                            🏢 {j.company} &nbsp;•&nbsp; 📍 {j.location} &nbsp;•&nbsp; <span class="track-pill">{scope_pill}</span> &nbsp;•&nbsp; <span class="track-pill">{item['category']}</span>{deadline_info}
                        </div>
                    </div>
                    <div>
                        <span class="{badge_class}">{score}% Match</span>
                    </div>
                </div>
                <p style="font-size: 0.9rem; margin: 8px 0; opacity: 0.8;">{item['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)

            colA, colB = st.columns([1.1, 0.9])
            with colA:
                with st.expander(f"✉️ Quick Pitch for {j.company}"):
                    st.text_input("Subject Line", value=item["subject"], key=f"subj_{idx}")
                    st.text_area("Tailored Outreach Pitch", value=item["cover_letter"], height=160, key=f"pitch_{idx}")
                    if item.get("contact_email"):
                        st.caption(f"📫 Official Contact Email: `{item['contact_email']}`")

                with st.expander(f"✍️ Tailored Cover Letter Generator (Formal 4-Paragraph)"):
                    cl_data = generate_custom_cover_letter(j, profile_data or {})
                    cl_text = st.text_area(
                        "Formal Application Cover Letter (Live Editable)",
                        value=cl_data.get("formal_letter") or cl_data.get("cover_letter", ""),
                        height=260,
                        key=f"cl_body_{idx}"
                    )
                    st.text_area(
                        "LinkedIn / Cold InMail Pitch",
                        value=cl_data.get("email_pitch") or cl_data.get("cold_email_pitch", ""),
                        height=90,
                        key=f"cl_cold_{idx}"
                    )
                    st.download_button(
                        label=f"💾 Download Cover Letter ({j.company}.txt)",
                        data=cl_text,
                        file_name=f"Cover_Letter_{j.company.replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"dl_cl_{idx}"
                    )
            with colB:
                st.link_button("🔗 View & Apply on Official Portal", j.url, use_container_width=True)

            st.write("")


if __name__ == "__main__":
    main()
