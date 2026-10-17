# 🎯 InternQuest AI - Universal Internship Hunter & Matcher

A modern, multi-user, open-source AI platform designed to help students and graduates across **Science, Commerce, Arts, Engineering, and All Disciplines** discover matching internships and generate tailored outreach pitches.

Users can **register for an account**, **sign in**, **upload their CV**, and have their profile, skills, and resume preserved securely under their personal account.

---

## 🌟 Key Platform Features

1. **🔐 Multi-User Authentication & Profile Storage**:
   - Built-in **Sign In** and **Register Free** system with salted password encryption and session persistence in SQLite.
   - Automatically stores each user's uploaded CV, extracted skills, contact info, and academic track (**Science & Engineering**, **Commerce & Business**, **Arts, Media & Law**, **Health & Pharma**, or **General Studies**).

2. **📄 Dynamic CV Analysis & Alignment**:
   - Drag-and-drop any PDF resume to extract key competencies and educational background in real time.
   - No hardcoded profiles—every analysis is tailored 100% to the specific applicant's resume.

3. **⚡ Universal Multi-Discipline Search & Matching**:
   - Searches across 100+ Bangladesh Banks, MNCs, NGOs, FinTechs, Software Houses, Creative Agencies, and Global Remote boards.
   - Intelligent keyword and level filtering prioritizes student internships and traineeships while filtering out senior executive roles requiring 5+ years of experience.
   - Match scores (0–100%) and instant rationales explain why an opportunity aligns with the applicant.

4. **✉️ 1-Click Tailored Cold Outreach Generator**:
   - Drafts a compelling email subject line and a personalized 3-paragraph cold email / cover letter highlighting the applicant's real coursework, projects, and skills.
   - Includes 1-click **"📋 Copy Pitch"** button and official portal links.

---

## 🚀 Running Locally

### Option 1: Modern Web Dashboard
Double-click **`Start_Dashboard.bat`** (or run via terminal):
```powershell
.\.venv\Scripts\python.exe web_server.py
```
Open your browser at **`http://localhost:5000`**.

### Option 2: Streamlit Public Web UI
Double-click **`Start_Streamlit_Public_App.bat`** (or run via terminal):
```powershell
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```
Open your browser at **`http://localhost:8501`**.

---

## 🌐 How to Host Online with GitHub & Streamlit Cloud (Free Forever)

You can publish this app to GitHub and launch it on **Streamlit Community Cloud** (backed by Snowflake) so anyone with a web link can create an account and upload their CV!

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com) and log in.
2. Click **`+`** at top-right ➔ **New repository**.
3. Name it `internquest-ai` (or your preferred name).
4. Keep it **Public** and leave "Add a README" **unchecked**.
5. Click **Create repository**.

### Step 2: Push Your Code
Open PowerShell in the project directory (`E:\CV hunter Webapp\`) and run:
```powershell
$git = "$env:LOCALAPPDATA\Programs\MinGit\cmd\git.exe"
& $git remote add origin https://github.com/YOUR_GITHUB_USERNAME/internquest-ai.git
& $git push -u origin main
```
*(Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username).*

### Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `YOUR_GITHUB_USERNAME/internquest-ai`.
4. Set **Main file path** to: `streamlit_app.py`.
5. Click **"Deploy"**!

Within 60 seconds, your application is live on the internet with a public link (e.g. `https://internquest-ai.streamlit.app`)!

---

## 🛡️ Security & Data Isolation
- **No Personal CV Bundled**: No candidate resume is bundled in the source code; every user uploads their own CV.
- **Credential Protection**: Private credentials (`.env`, local virtual environments, and personal passwords) are strictly excluded from GitHub by `.gitignore`.
- **User Privacy**: Each user's uploaded CV is tied to their authenticated account.
