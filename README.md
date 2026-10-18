# 🎯 Internship Hunter AI - Bangladesh's #1 Verified Internship Discovery & ATS CV Scanner

A modern, multi-user AI platform designed to help students and graduates in Bangladesh discover genuine, active corporate internships and generate tailored outreach materials.

Features:
- **100% Verified Bangladesh Internships**: Purged of junk, expired, and broken links. 1,000+ active positions across Bangladesh banks, fintechs, conglomerates, pharmaceuticals, MNCs, and tech firms.
- **Strict 3 Student Categories**:
  1. `🧪 Science & Tech` (CSE, EEE, Biotech, Pharmacy, Software Engineering, IT)
  2. `📈 Business & Commerce` (Finance, Banking, Accounting, Marketing, Supply Chain, BBA)
  3. `🎨 Arts & Social Science` (Media, Communications, English, Design, Law, Economics)
- **High-Precision ATS Resume Compatibility Scorer (0-100)**: Evaluates resumes against automated HR applicant tracking systems with a 5-factor breakdown and actionable tips.
- **Latest Institution Hierarchy**: Chronologically prioritizes university of study (e.g., Jashore University of Science and Technology (JUST)) over secondary/intermediate colleges.
- **Custom 4-Paragraph Tailored Cover Letter Generator**: Generates formal letters and LinkedIn/email pitches aligned with job requirements.
- **10:00 AM Daily Morning Auto-Refresh & Alerts**: Registered profiles are refreshed every morning at 10:00 AM with customized digests.
- **Frictionless Guest Mode (< 10 MB)**: Anyone can scan their CV (under 10 MB) without mandatory registration.

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
