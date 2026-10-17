# 🚀 Fahim's Autonomous Internship Hunter & Web Application

An intelligent, scheduled AI agent system designed to find daily internship opportunities tailored to **Fahim Ashab's** background (Finance & Banking, Financial Analysis, Corporate Budgeting, Business Operations, FinTech) and execute applications through official channels—including cold emails with CV attachment and web ATS form autofill.

---

## 📂 Project Organization (`E:\CV hunter Webapp\`)

```
E:\CV hunter Webapp\
├── Start_Dashboard.bat          ← Double-click to launch the Web Dashboard
├── run_daily_now.bat            ← Double-click to manually run today's 10:00 AM scan immediately
├── run_silent_scan.vbs          ← Silent runner used by Windows Task Scheduler (runs hidden at 10 AM)
├── web_server.py                ← Local web dashboard server & API
├── daily_runner.py              ← Daily scan & scoring runner with desktop notifications
├── main.py                      ← CLI interface for custom tasks
├── config.yaml                  ← Configuration for search keywords, locations, score threshold
├── .env                         ← Your credentials (Gmail App Password, Gemini API Key, Safe Mode toggle)
├── notify.ps1                   ← Windows toast notification script
├── data/                        ← Your persistent database & resume
│   ├── Fahim_Ashab_Resume.pdf   ← Your resume (automatically attached to applications)
│   ├── applications.db          ← SQLite database storing all discovered jobs & application status
│   └── applications_report.md  ← Markdown report of all matched opportunities
├── web/
│   └── index.html               ← Visual interactive web dashboard
├── src/                         ← Core AI engine & automation logic
│   ├── appliers/                ← Email and Web application automation
│   ├── matcher/                 ← Gemini AI evaluation & tailored cover letter generator
│   ├── scrapers/                ← 130+ Bangladesh company & bank scrapers + LinkedIn + Remote boards
│   ├── config.py                ← Configuration loader
│   ├── notifier.py              ← Windows notification trigger
│   ├── profile.py               ← Resume parser
│   ├── scheduler.py             ← Workflow orchestrator
│   └── tracker.py               ← SQLite database tracker
└── .venv/                       ← Isolated Python virtual environment
```

---

## 🌟 How To Use (Non-Technical / 1-Click)

### 1. Launch the Web Dashboard
- **From your Desktop**: Double-click **`Start_Internship_Assistant.bat`** on your Desktop.
- **Or from this folder**: Double-click **`Start_Dashboard.bat`**.
- Your browser will open automatically at **`http://localhost:5000`**.

### 2. Automated Daily Scan at 10:00 AM
- Windows Task Scheduler automatically runs `run_silent_scan.vbs` every morning at **10:00 AM**.
- It checks 100+ Bangladesh banks, multinational companies, NGOs, FinTechs, and remote boards.
- It calculates match scores with your CV and shows a Windows notification with results.

### 3. Activating Live Sending (Turning Off Safe Mode)
- In the dashboard, click **Settings**.
- Enter your **Gmail App Password** (16 characters from [Google App Passwords](https://myaccount.google.com/apppasswords)).
- Turn **Safe Test Mode** to **Inactive (Live)**.
- Click **Save Settings**.
- Safe daily limit is set to 5 emails/day to keep your email reputation 100% clean.
