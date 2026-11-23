# Master Memory & Core Operating Rules: InternQuest AI

## 1. Zero Expired, Closed, or Past-Deadline Postings (Unbreakable Directive)
On **every single catalog refresh and scan**, the discovery and verification engine must cross-check **every candidate and existing posting** across all companies, conglomerates, banks, MNCs, and NGOs without exception:

1. **Active Application Check**:
   - The posting URL must return a live `HTTP 200 OK` (strictly zero 404, 410, or soft-404 error pages).
   - The posting must NOT display any job closure notice, banner, or CSS class (`closed-job`, `no longer accepting applications`, `আর আবেদনপত্র গ্রহণ করা হচ্ছে না`, `this job is closed`, `this position is closed`, `this job has expired`, `applications are closed`, `application closed`, `job is no longer available`, etc.).
   - For LinkedIn postings: The posting **MUST** have an active, clickable Apply CTA button or link (`apply-button` or `top-card-layout__cta` with "Apply" or "আবেদন করুন"). If the position has been filled or the apply button removed, the posting is considered closed and **must be removed immediately**.

2. **Application Deadline & Time Verification**:
   - If an application deadline, closing date, or last date of application is stated anywhere in the post description (e.g., `Deadline: DD Month YYYY`, `Apply before: ...`, `Last date of application: ...`), it must be parsed and compared against `datetime.now()`.
   - If the deadline is **over or passed**, the post **must be removed immediately** from the catalog.

3. **No Blind Fallback or Stale Retention**:
   - Never give a blind pass to previously existing jobs (`is_existing` must never bypass live verification, rate limits, or exceptions).
   - If a listing fails live verification or has expired, it must be removed from `data/business_internships.json`, purged from `index.html` and `web/index.html`, and permanently pruned from `data/applications.db`.

---

## 2. Business & Commerce Student Exclusivity
- Only verified internships, attachments, and work placements suitable for undergraduate and postgraduate Business, BBA, B.Com, and MBA students.
- Disciplines: Finance & Banking; Accounting, Audit & Tax; Marketing & Brand Management; Supply Chain & Procurement; Human Resources & Talent; FinTech & Business Analytics; Management & Operations.
- Strictly exclude technical/engineering roles (software development, devops, SQA, electrical, civil, mechanical, architecture, IT support, graphics, video editing, legal counsel, lab testing).

---

## 3. Comprehensive Institutional Coverage
- Continuous coverage across all sectors in Bangladesh: Global MNCs, Premier Private & Islamic Banks, Financial Institutions (NBFIs), National Conglomerates (Akij, Square, Beximco, PRAN-RFL, ACI, Meghna, Bashundhara, Walton, SSG, etc.), Footwear & Retail Giants (Apex, Bata, Aarong, Shwapno), RMG/Apparel Merchandising (Ha-Meem, DBL, Pacific Jeans, Envoy, Mohammadi, Epyllion, Youngone, Centric Brands), Pharmaceuticals (Renata, Square, Incepta, Beximco, Roche), Telecoms & FinTech (Grameenphone, Robi, Banglalink, bKash, Nagad), and Global NGOs (BRAC, NRC, UNDP, UNICEF).

---

## 4. Direct Original Postings Requirement ("See Original Post" Integrity)
- Every single "See Original Post" button MUST land directly on an individual, original internship post page (strictly zero generic company homepages or root career landing pages like `/career` where students cannot find the specific internship).
- Maximize direct, verified LinkedIn job postings (`https://bd.linkedin.com/jobs/view/...` or `https://www.linkedin.com/jobs/view/...`) across Bangladesh, as LinkedIn postings provide the exact role requirements, authentic company metadata, and a direct "Apply" / "Easy Apply" / "আবেদন করুন" button right on the page.
- Any non-LinkedIn listing must be an official dedicated program portal that features the direct active application intake (e.g. BRAC BRIDGE).
- Every link in the catalog must be live-tested and cross-verified to be 100% fault-free, active, and open.

---

## 5. Multi-Platform Deployment & Synchronization
- Every refresh must update:
  1. `data/business_internships.json`
  2. `index.html` (`EMBEDDED_JOBS`)
  3. `web/index.html` (`EMBEDDED_JOBS`)
- Git commits and pushes must synchronize both `origin main` and `origin gh-pages`.
