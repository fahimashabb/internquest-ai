# 🎯 AI Internship Hunter & Universal CV Matcher

An open-source, AI-powered career assistant platform that automatically discovers daily internship opportunities across **100+ Bangladesh banks, multinational corporations (MNCs), NGOs, FinTechs, conglomerates, and global remote job boards**, scores them against any candidate's uploaded CV, and generates customized outreach pitches.

---

## 🌟 Key Features

1. **📄 Universal Drag-and-Drop CV Uploader**:
   - Any student or job seeker can upload their resume (`.pdf`).
   - Automatically extracts candidate name, degree, institution, detected skills, and target industries.

2. **⚡ Dynamic AI Matching & Scoring**:
   - Real-time match scoring (0–100%) against live positions.
   - Categorizes roles across **Banking & Finance, FinTech, Tech & Software, MNCs & Conglomerates, NGOs & Development, and Remote Global**.
   - Filters out senior executive positions requiring 5+ years of experience to prioritize legitimate student & entry-level openings.

3. **✉️ 1-Click Tailored Cold Outreach Generator**:
   - Generates a customized, 3-paragraph professional cold email and attention-grabbing subject line specifically highlighting the candidate's real coursework, projects, and skills.
   - Built-in **"📋 Copy to Clipboard"** button and direct official application links.

4. **🇧🇩 Deep Bangladesh Job Discovery Engine**:
   - Covers 30+ Commercial & Islamic Banks, 14 FinTechs (bKash, Nagad, Pathao), 7 MNCs (Unilever, BAT, Nestlé), 20 Conglomerates (Square, PRAN, Beximco), 17 NGOs/Development agencies (BRAC, UNDP, World Bank), plus LinkedIn and remote boards (Jobicy, Remotive).

---

## 🚀 How to Run Locally

### Option 1: Standard Web Dashboard (Fast & Lightweight)
Double-click **`Start_Dashboard.bat`** (or run via terminal):
```powershell
python web_server.py
```
Open your browser at **`http://localhost:5000`**.

### Option 2: Streamlit Interactive UI
```powershell
streamlit run streamlit_app.py
```
Open your browser at **`http://localhost:8501`**.

---

## ☁️ How to Host for Free on GitHub & Streamlit Cloud (Live Link for Everyone)

You can share a live web link (`https://your-name-internship-hunter.streamlit.app`) so anyone can access it from their phone or laptop for free!

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com) and sign in.
2. Click the **"+"** button at the top right and select **"New repository"**.
3. Name your repository (e.g., `internship-hunter-webapp`).
4. Keep it **Public** and **do NOT** check "Add README" (we already have one).
5. Click **Create repository**.

### Step 2: Push Your Code to GitHub
In your project folder (`E:\CV hunter Webapp\`), open PowerShell and run:
```powershell
$git = "$env:LOCALAPPDATA\Programs\MinGit\cmd\git.exe"
& $git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
& $git push -u origin main
```
*(Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name).*

### Step 3: Deploy Free on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `YOUR_GITHUB_USERNAME/internship-hunter-webapp`.
4. Set the **Main file path** to: `streamlit_app.py`.
5. Click **"Deploy"**!

Within 60 seconds, your application will be live on the internet with a public link you can share with anyone!

---

## 🔒 Privacy & Safety Guarantee

- **Zero Credential Leaks**: `.env` and all personal passwords/keys are strictly ignored by `.gitignore`.
- **Public Visitor Privacy**: Uploaded CVs are parsed in-memory during the browser session and are not permanently saved or published.
- **No Unsolicited Sending**: Visitors can preview and copy tailored pitches to send from their own inboxes.

---

## 👨‍💻 Author & Maintainer
Created by **Fahim Ashab** (BBA Finance & Banking, Jashore University of Science and Technology).
Open-source under the MIT License.
