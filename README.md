# 💼 BizIntern BD — Premier Business & Commerce Internship Hub

[![GitHub Pages](https://img.shields.io/badge/Live_Website-GitHub_Pages-indigo?style=for-the-badge&logo=github)](https://fahimashabb.github.io/internquest-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)](LICENSE)
[![Target Audience](https://img.shields.io/badge/Audience-BBA_%26_Commerce_Students-blue?style=for-the-badge)](#)

> **Live Website**: [https://fahimashabb.github.io/internquest-ai/](https://fahimashabb.github.io/internquest-ai/)

**BizIntern BD** is a free, open-access internship discovery platform curated specifically for **Business and Commerce students** across Bangladesh and global remote channels.

It aggregates and curates verified corporate internships from **130+ premier institutions**—including top multinationals, commercial banks, industrial conglomerates, FinTech leaders, audit firms, and international development agencies.

---

## 🌟 Key Features

1. **Ranked by Corporate Prestige & Market Value**:
   - ⭐ **Tier 1**: Premier Multinationals & Foreign Banks (*Unilever, BAT, Nestlé, Standard Chartered, HSBC, Marico, Grameenphone, Big 4 Audit*)
   - 🏛️ **Tier 2**: Leading Commercial Banks & FinTechs (*BRAC Bank, City Bank, Eastern Bank, bKash, Nagad, IDLC, IPDC*)
   - 🏢 **Tier 3**: Top Industrial Conglomerates & FMCG Giants (*Square, Beximco, ACI, Meghna, Walton, PRAN-RFL, Apex*)
   - 🌍 **Tier 4**: International Development & UN Agencies (*UNDP, BRAC International, Save the Children, CARE*)
   - 🚀 **Tier 5**: High-Growth Startups & Remote Global Commerce (*ShopUp, Pathao, 10 Minute School, Jobicy/Remotive*)

2. **Direct Official Postings**:
   - Every role includes a direct **"See Original Post ↗"** button that opens the verified listing on LinkedIn, BDJobs, or the company's official career portal.

3. **Curated Across All Business Sub-Disciplines**:
   - 💼 **Finance & Banking**: Credit Analysis, Treasury Operations, Financial Modeling, Corporate Lending
   - 📊 **Accounting, Audit & Tax**: Statutory Assurance, Tax/VAT Compliance, Cost Accounting
   - 📢 **Marketing & Brand Management**: FMCG Brand Strategy, Consumer Insights, Trade Marketing
   - 🚚 **Supply Chain & Procurement**: Sourcing, Inventory Control, Export/Import & Commercial LC
   - 👥 **Human Resources & Talent**: People Operations, Campus Recruitment, Talent Analytics
   - ⚡ **FinTech & Digital Business**: Payment Systems, Card Operations, Product Operations
   - 🎯 **Management & Operations**: Business Development, Strategic Planning, Project Management

4. **Fresh, Eye-Pleasing UI**:
   - Modern, distraction-free aesthetic with instant live search and filtering
   - One-click Dark / Light mode toggle
   - Save & Bookmark favorite positions directly in your browser (`localStorage`)
   - Built-in Commerce Student Career Guide with cold-email templates and resume tips

---

## 🚀 How to Run Locally

If you wish to run the platform locally or contribute:

```bash
# Clone the repository
git clone https://github.com/fahimashabb/internquest-ai.git
cd internquest-ai

# Open directly in browser (works 100% offline)
start index.html

# OR run with Python's built-in server
python -m http.server 5000
```
Then visit `http://localhost:5000` in your browser.

---

## 📂 Project Architecture

```
internquest-ai/
├── index.html                   ← Root static web application (served by GitHub Pages)
├── data/
│   └── business_internships.json← Verified master catalog of 500+ business internships
├── scripts/
│   └── build_business_catalog.py← Automation script to rebuild/update catalog
├── .github/
│   └── workflows/
│       └── deploy-pages.yml     ← GitHub Actions automatic deployment to GitHub Pages
├── web/
│   └── index.html               ← Synced UI interface for local server runs
├── web_server.py                ← Local Python web server
└── README.md                    ← Documentation
```

---

## 📄 License & Community

This project is an open-source, community-driven initiative for business and commerce students in Bangladesh. Distributed under the MIT License.
