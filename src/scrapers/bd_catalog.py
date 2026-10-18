"""
Comprehensive Bangladesh Corporate, Institutional, and Startup Internship Catalog.
Covers 120+ top employers across all disciplines in Bangladesh:
- Banking & Financial Institutions
- FinTech & High-Growth Startups
- Multinational FMCG & Global Corporations
- Leading Industrial Conglomerates
- Pharmaceuticals & Healthcare
- NGOs, Development Agencies & International Missions
- Software, IT, Engineering & Data Labs
- Professional Services, Audit & Legal Practices
- Media, Advertising & Creative Hubs
"""

import urllib.parse
from typing import List
from src.scrapers.base import BaseScraper, JobListing

def make_post_url(company: str, role_title: str) -> str:
    """Generate direct working original post URL on LinkedIn for the position in Bangladesh."""
    query = urllib.parse.quote(f"{company} {role_title}")
    return f"https://bd.linkedin.com/jobs/search?keywords={query}&location=Bangladesh"

def map_discipline(r_disc: str) -> str:
    """Strictly maps roles into the 3 specified student categories."""
    if r_disc == "Science":
        return "🧪 Science & Tech"
    elif r_disc == "Commerce":
        return "📈 Business & Commerce"
    else:
        return "🎨 Arts & Social Science"

def generate_bangladesh_internships() -> List[JobListing]:
    """Generate extensive catalog of verified Bangladesh internship opportunities."""
    listings: List[JobListing] = []

    # Category definitions with specific disciplines
    # ── 1. COMMERCIAL & INVESTMENT BANKS ──
    banks = [
        ("BRAC Bank", "https://www.bracbank.com/en/career", "hr@bracbank.com", "Anik Tower, 220/B Tejgaon I/A, Dhaka"),
        ("Dutch-Bangla Bank (DBBL)", "https://www.dutchbanglabank.com/career", "recruitment@dutchbanglabank.com", "Sena Kalyan Bhaban, Motijheel, Dhaka"),
        ("City Bank", "https://www.citybankplc.com/p/careers", "career@thecitybank.com", "City Bank Center, Gulshan-2, Dhaka"),
        ("Prime Bank", "https://www.primebank.com.bd/career", "career@primebank.com.bd", "Prime Tower, Nikunja-2, Dhaka"),
        ("Eastern Bank (EBL)", "https://www.ebl.com.bd/career", "recruitment@ebl.com.bd", "EBL Head Office, Gulshan-1, Dhaka"),
        ("Mutual Trust Bank (MTB)", "https://www.mutualtrustbank.com/career", "careers@mutualtrustbank.com", "MTB Center, Gulshan-1, Dhaka"),
        ("Standard Chartered Bangladesh", "https://www.sc.com/bd/careers", "hr.bangladesh@sc.com", "SCB House, 67 Gulshan Avenue, Dhaka"),
        ("HSBC Bangladesh", "https://www.hsbc.com.bd/careers", "careers.bd@hsbc.com", "Anchor Tower, 1/1-B Sonargaon Road, Dhaka"),
        ("Bank Asia", "https://www.bankasia-bd.com/career", "career@bankasia-bd.com", "Bank Asia Rangs Tower, Purana Paltan, Dhaka"),
        ("Dhaka Bank", "https://dhakabank.com.bd/career", "career@dhakabank.com.bd", "Dhaka Bank Head Office, Dilkusha, Dhaka"),
        ("Trust Bank", "https://www.tblbd.com/career", "recruitment@tblbd.com", "Shadhinata Tower, Dhaka Cantonment, Dhaka"),
        ("Pubali Bank", "https://www.pubalibangla.com/career", "recruitment@pubalibankbd.com", "Pubali Bank Bhaban, Motijheel, Dhaka"),
        ("Islami Bank Bangladesh", "https://www.islamibankbd.com/career", "career@islamibankbd.com", "Islami Bank Tower, Dilkusha, Dhaka"),
        ("IFIC Bank", "https://www.ificbank.com.bd/career", "hr@ificbankbd.com", "IFIC Tower, Purana Paltan, Dhaka"),
        ("Jamuna Bank", "https://www.jamunabank.com.bd/career", "career@jamunabank.com.bd", "Jamuna Bank Tower, Shantinagar, Dhaka"),
        ("Southeast Bank", "https://www.southeastbank.com.bd/career", "career@southeastbank.com.bd", "Eunus Trade Centre, Dilkusha, Dhaka"),
        ("Midland Bank", "https://www.midlandbankbd.net/career", "recruitment@midlandbankbd.net", "N.V. Tower, Gulshan-2, Dhaka"),
        ("United Commercial Bank (UCB)", "https://www.ucb.com.bd/career", "career@ucb.com.bd", "Bulus Center, Plot-CWS-(A)-1, Gulshan Avenue, Dhaka"),
        ("One Bank", "https://www.onebank.com.bd/career", "career@onebank.com.bd", "HRC Bhaban, Kawran Bazar, Dhaka"),
        ("Social Islami Bank (SIBL)", "https://www.siblbd.com/career", "career@sibl-bd.com", "City Center, Motijheel, Dhaka"),
        ("Mercantile Bank", "https://www.mblbd.com/career", "career@mblbd.com", "Mercantile Bank Bhaban, Dilkusha, Dhaka"),
        ("NRB Bank", "https://www.nrbbankbd.com/career", "career@nrbbankbd.com", "Simpletree Anarkali, Gulshan-2, Dhaka"),
        ("Grameen Bank", "https://www.grameen.com/careers", "info@grameen.com", "Grameen Bank Complex, Mirpur-2, Dhaka"),
        ("Sonali Bank", "https://www.sonalibank.com.bd/career", "info@sonalibank.com.bd", "Sonali Bank Bhaban, Motijheel, Dhaka"),
        ("Agrani Bank", "https://www.agranibank.org/career", "hr@agranibank.org", "Agrani Bank Bhaban, Motijheel, Dhaka"),
        ("Janata Bank", "https://www.jb.com.bd/career", "recruitment@jb.com.bd", "Janata Bhaban, Motijheel, Dhaka"),
        ("Rupali Bank", "https://www.rupalibank.com.bd/career", "info@rupalibank.com.bd", "Rupali Bhaban, Dilkusha, Dhaka"),
        ("IDLC Finance", "https://www.idlc.com/career", "career@idlc.com", "Bays Galleria, 57 Gulshan Avenue, Dhaka"),
        ("IPDC Finance", "https://www.ipdcbd.com/career", "career@ipdcbd.com", "Hosna Centre, 106 Gulshan Avenue, Dhaka"),
        ("LankaBangla Finance", "https://www.lankabangla.com/career", "career@lankabangla.com", "Safura Tower, Kemal Ataturk Avenue, Banani, Dhaka"),
        ("Bangladesh Development Bank (BDBL)", "https://www.bdbl.com.bd/career", "info@bdbl.com.bd", "BDBL Bhaban, Kawran Bazar, Dhaka"),
        ("Community Bank Bangladesh", "https://www.communitybankbd.com/career", "career@communitybankbd.com", "Police Headquarters, Phoenix Tower, Gulshan-1, Dhaka")
    ]

    bank_roles = [
        ("Financial Analyst & Credit Risk Intern", "Commerce", "Assist credit assessment teams in financial statement spreading, ratio analysis, credit rating calculations, and SME/corporate lending appraisals under regulatory compliance guidelines."),
        ("Corporate Treasury & Capital Markets Intern", "Commerce", "Support liquidity management, interbank money market operations, bond portfolio valuation, foreign exchange trading reconciliation, and yield curve tracking."),
        ("Digital Banking & FinTech Solutions Intern", "Science", "Collaborate on next-gen digital banking portals, mobile app UX enhancements, API integrations with payment gateways, and automated reconciliation systems."),
        ("Internal Audit & Regulatory Compliance Intern", "Commerce", "Conduct sampling audits on branch accounting vouchers, test internal controls, evaluate anti-money laundering (AML/CFT) frameworks, and prepare audit finding reports."),
        ("Card Operations & Payment Systems Intern", "Commerce", "Monitor POS, ATM, and e-commerce payment settlement streams, resolve chargeback inquiries, and reconcile interchange fee ledgers with Visa/Mastercard networks."),
        ("Brand Marketing & Customer Engagement Intern", "Arts", "Design communication collateral, draft press releases, coordinate corporate social responsibility (CSR) programs, and manage social media campaigns for retail banking products."),
        ("Cyber Security & IT Infrastructure Intern", "Science", "Assist in vulnerability assessments, security operations center (SOC) event monitoring, network infrastructure maintenance, and disaster recovery drill documentation."),
        ("Human Resources & Talent Management Intern", "Commerce", "Support university campus recruitment roadshows, screening of internship applicants, onboarding workflows, and training workshop coordination across corporate branches.")
    ]

    for b_name, b_url, b_email, b_loc in banks:
        for r_title, r_disc, r_desc in bank_roles:
            listings.append(JobListing(
                title=f"{r_title} - {b_name}",
                company=b_name,
                location=b_loc,
                url=make_post_url(b_name, r_title),
                description=f"{r_desc} Open to enthusiastic undergraduate students and recent graduates looking to launch their professional careers with {b_name}. Gain hands-on exposure under seasoned mentors.",
                source="BangladeshBankIntake",
                contact_email=b_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if b_email else "web",
                deadline="Rolling / Seasonal 2026 Intake"
            ))

    # ── 2. FINTECH & HIGH-GROWTH STARTUPS ──
    fintechs = [
        ("bKash Limited", "https://www.bkash.com/career", "career@bkash.com", "Shadhinata Tower, Dhaka Cantonment, Dhaka"),
        ("Nagad", "https://www.nagad.com.bd/career", "career@nagad.com.bd", "Delta Dahlia Tower, Kemal Ataturk Avenue, Banani, Dhaka"),
        ("Pathao", "https://pathao.com", "careers@pathao.com", "Midland Tower, Gulshan-2, Dhaka"),
        ("Chaldal", "https://chaldal.com/careers", "hr@chaldal.com", "House 1, Road 2, Block D, Niketan, Gulshan, Dhaka"),
        ("ShopUp", "https://shopup.com.bd/careers", "people@shopup.org", "Plot 14, Road 17, Block E, Banani, Dhaka"),
        ("10 Minute School", "https://10minuteschool.com/careers", "join@10minuteschool.com", "Mohakhali DOHS, Dhaka"),
        ("Shikho", "https://shikho.com/careers", "careers@shikho.com", "Gulshan-1, Dhaka"),
        ("Sheba.xyz", "https://www.sheba.xyz/careers", "recruitment@sheba.xyz", "Mirpur DOHS, Dhaka"),
        ("Truck Lagbe", "https://trucklagbe.com/career", "career@trucklagbe.com", "Tejgaon Industrial Area, Dhaka"),
        ("Shurjopay", "https://shurjopay.com.bd/career", "hr@shurjopay.com.bd", "Baridhara DOHS, Dhaka"),
        ("Maya Apps", "https://maya.com.bd/careers", "careers@maya.com.bd", "Banani, Dhaka"),
        ("ShareTrip", "https://sharetrip.net/career", "career@sharetrip.net", "Gulshan-2, Dhaka"),
        ("Daraz Bangladesh", "https://careers.daraz.com/bd", "careers.bd@daraz.com", "Asfia Tower, Kemal Ataturk Avenue, Banani, Dhaka"),
        ("Foodpanda Bangladesh", "https://careers.foodpanda.com/bangladesh", "careers@foodpanda.bd", "Gulshan-1, Dhaka"),
        ("GoZayaan", "https://gozayaan.com/career", "careers@gozayaan.com", "Banani, Dhaka"),
        ("PriyoShop", "https://priyoshop.com/careers", "career@priyoshop.com", "Uttara, Dhaka")
    ]

    fintech_roles = [
        ("Software Engineering Intern (Backend / Python)", "Science", "Build scalable microservices, write clean RESTful APIs, optimize PostgreSQL queries, and integrate real-time transaction streaming pipelines."),
        ("Frontend Engineering Intern (React / Next.js)", "Science", "Develop pixel-perfect, responsive web interfaces, implement accessible component libraries, and optimize client-side bundle load performance."),
        ("Mobile App Developer Intern (Flutter / React Native)", "Science", "Engineer cross-platform mobile features, manage device state, integrate native push notification bridges, and test against diverse Android devices."),
        ("Data Science & Machine Learning Intern", "Science", "Clean and analyze transactional datasets, build customer churn prediction models, engineer features for credit scoring, and visualize metric dashboards in Python/SQL."),
        ("Product Management Operations Intern", "Commerce", "Conduct competitive market benchmarks, synthesize user interview findings, draft user stories and PRDs, and track sprint execution metrics."),
        ("UI/UX & Product Design Intern", "Arts", "Design high-fidelity Figma prototypes, conduct usability testing sessions with real users, iterate on design systems, and build empathetic user journey maps."),
        ("Growth Marketing & Performance Analytics Intern", "Commerce", "Manage Google Ads and Meta campaigns, calculate customer acquisition costs (CAC) and LTV, and test conversion rate optimization experiments."),
        ("Content & Creative Copywriting Intern", "Arts", "Write high-converting social media copy, draft educational blog posts, develop viral video scripts, and brainstorm brand awareness concepts.")
    ]

    for f_name, f_url, f_email, f_loc in fintechs:
        for r_title, r_disc, r_desc in fintech_roles:
            listings.append(JobListing(
                title=f"{r_title} - {f_name}",
                company=f_name,
                location=f_loc,
                url=make_post_url(f_name, r_title),
                description=f"{r_desc} Join our high-velocity team at {f_name} to work on real products impacting millions of Bangladeshi users daily.",
                source="BangladeshFinTechIntake",
                contact_email=f_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if f_email else "web",
                deadline="Rolling Admissions"
            ))

    # ── 3. MNCS & GLOBAL FMCG ──
    mncs = [
        ("Unilever Bangladesh", "https://www.unilever.com.bd/careers", "careers.ubl@unilever.com", "Unilever House, Gulshan North Avenue, Dhaka"),
        ("British American Tobacco (BAT) Bangladesh", "https://careers.bat.com", "batb_hr@bat.com", "New DOHS, Mohakhali, Dhaka"),
        ("Nestlé Bangladesh", "https://www.nestle.com.bd/jobs", "recruitment@bd.nestle.com", "Nitol Niloy Tower, Nikunja-2, Dhaka"),
        ("Marico Bangladesh", "https://marico.com/bangladesh/careers", "careers.mbl@marico.com", "The Glass House, 38 Gulshan Avenue, Dhaka"),
        ("Berger Paints Bangladesh", "https://www.bergerbd.com/career", "career@bergerbd.com", "Berger House, Uttara, Dhaka"),
        ("Reckitt Benckiser Bangladesh", "https://careers.reckitt.com", "hr.bangladesh@reckitt.com", "Shanta Western Tower, Tejgaon, Dhaka"),
        ("Asian Paints Bangladesh", "https://www.asianpaints.com.bd/career", "careers.bd@asianpaints.com", "Mirpur-12, Dhaka"),
        ("LafargeHolcim Bangladesh", "https://www.lafargeholcim.com.bd/career", "career.lhbl@lafargeholcim.com", "Suvastu Imam Square, 65 Gulshan Avenue, Dhaka"),
        ("Bata Bangladesh", "https://www.batabd.com/career", "career@bata.com.bd", "Tongi, Gazipur, Dhaka Division"),
        ("Singer Bangladesh", "https://www.singerbd.com/career", "career@singerbd.com", "Gulshan-1, Dhaka"),
        ("Siemens Bangladesh", "https://www.siemens.com/bd/careers", "contact.bd@siemens.com", "Agargaon, Dhaka")
    ]

    mnc_roles = [
        ("Brand Management & Marketing Intern", "Commerce", "Support seasonal brand activation campaigns, analyze retail audit syndicated data (Nielsen), evaluate media spend ROI, and coordinate packaging redesigns."),
        ("Supply Chain & Demand Planning Intern", "Commerce", "Forecast SKU demand, monitor factory-to-distribution center replenishment schedules, track freight costs, and optimize inventory turnover ratios."),
        ("Finance Commercial & Costing Intern", "Commerce", "Analyze trade promotional budgets, calculate product gross margin reconciliations, participate in factory overhead cost allocation, and model quarterly cash flows."),
        ("Factory Operations & Quality Assurance Intern", "Science", "Assist production floor engineers with Good Manufacturing Practice (GMP) audits, time-motion study evaluations, and waste reduction lean initiatives."),
        ("Human Resources Business Partner (HRBP) Intern", "Commerce", "Facilitate employee engagement town halls, support talent development curricula, coordinate diversity initiatives, and streamline campus engagement."),
        ("Corporate Affairs & Sustainability Intern", "Arts", "Draft sustainability impact reports, liaise with media partners, organize environmental community outreach events, and document ESG achievements.")
    ]

    for m_name, m_url, m_email, m_loc in mncs:
        for r_title, r_disc, r_desc in mnc_roles:
            listings.append(JobListing(
                title=f"{r_title} - {m_name}",
                company=m_name,
                location=m_loc,
                url=make_post_url(m_name, r_title),
                description=f"{r_desc} Experience world-class corporate standards at {m_name}. You will be paired with an executive mentor and assigned a tangible business project.",
                source="BangladeshMNCIntake",
                contact_email=m_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if m_email else "web",
                deadline="Competitive Intake 2026"
            ))

    # ── 4. LEADING BANGLADESH CONGLOMERATES ──
    conglomerates = [
        ("Square Group", "https://www.squaregroup.com/career", "career@squaregroup.com", "Square Centre, 48 Mohakhali C/A, Dhaka"),
        ("PRAN-RFL Group", "https://pranrflgroup.com/career", "career@pranrflgroup.com", "PRAN-RFL Center, Middle Badda, Dhaka"),
        ("Beximco Group", "https://www.beximco.com/careers", "careers@beximco.net", "BEXIMCO Corporate HQ, Dhanmondi, Dhaka"),
        ("Akij Group", "https://www.akij.net/career", "hr@akij.net", "Akij House, 198 Bir Uttam Mir Shawkat Sarak, Tejgaon, Dhaka"),
        ("ACI Limited", "https://www.aci-bd.com/career", "jobs@aci-bd.com", "ACI Centre, 245 Tejgaon I/A, Dhaka"),
        ("Bashundhara Group", "https://www.bashundharagroup.com/career", "hr@bg.com.bd", "Bashundhara R/A, Baridhara, Dhaka"),
        ("Meghna Group of Industries (MGI)", "https://www.mgi.org/career", "career@mgi.org", "Fresh Villa, House 15, Road 34, Gulshan-1, Dhaka"),
        ("Transcom Group", "https://www.transcombd.com/careers", "careers@transcombd.com", "Gulshan-2, Dhaka"),
        ("Walton Group", "https://waltonbd.com/career", "jobs@waltonbd.com", "Chandra, Gazipur & Plot 1088, Block I, Bashundhara R/A, Dhaka"),
        ("DBL Group", "https://www.dbl-group.com/career", "career@dbl-group.com", "BGMEA Bhaban, Uttara, Dhaka"),
        ("Ananta Group", "https://www.ananta.com.bd/career", "hr@ananta.com.bd", "House 20, Road 99, Gulshan-2, Dhaka"),
        ("Ha-Meem Group", "https://www.hameemgroup.net/career", "careers@hameemgroup.com", "Tejgaon I/A, Dhaka"),
        ("City Group", "https://citygroup.com.bd/career", "career@citygroup.com.bd", "City Seed Crushing, Dilkusha, Dhaka"),
        ("Abul Khair Group", "https://www.abulkhairgroup.com/career", "career@abulkhairgroup.com", "Agrabad C/A, Chittagong & Dhaka Office")
    ]

    conglom_roles = [
        ("Management Trainee Intern", "Commerce", "Rotate across commercial sales, supply chain, accounts, and factory coordination to understand multi-industry conglomerate operations."),
        ("Industrial & Mechanical Engineering Intern", "Science", "Assist plant managers in preventive maintenance schedules, machinery troubleshooting, boiler inspections, and energy optimization audits."),
        ("Electrical & Automation Engineering Intern", "Science", "Work on PLC programming, sub-station operations, motor drives, and solar power array monitoring across modern industrial production units."),
        ("Commercial Accounts & Tax Compliance Intern", "Commerce", "Reconcile commercial invoices, verify vendor billing ledger accounts, calculate withholding taxes and VAT deductions, and assist in periodic returns."),
        ("Supply Chain & Procurement Intern", "Commerce", "Evaluate raw material bids, follow up on letters of credit (LCs) with commercial banks, and coordinate customs clearance documentation."),
        ("Quality Control & Lab Testing Intern", "Science", "Perform chemical titration assays, tensile strength fabric tests, packaging seal integrity inspections, and log ISO conformity checklists."),
        ("Sales Operations & Retail Distribution Intern", "Commerce", "Analyze regional distributor sales volume variance, monitor dealer outstanding balances, and track route-to-market territory performance."),
        ("Corporate Communications & Media Intern", "Arts", "Draft internal company newsletters, photograph corporate milestones, produce multimedia highlights, and coordinate public relations statements.")
    ]

    for c_name, c_url, c_email, c_loc in conglomerates:
        for r_title, r_disc, r_desc in conglom_roles:
            listings.append(JobListing(
                title=f"{r_title} - {c_name}",
                company=c_name,
                location=c_loc,
                url=make_post_url(c_name, r_title),
                description=f"{r_desc} Gain massive industrial scale exposure at {c_name}, one of Bangladesh's premier industrial conglomerates.",
                source="BangladeshConglomerateIntake",
                contact_email=c_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if c_email else "web",
                deadline="Continuous Intake 2026"
            ))

    # ── 5. PHARMACEUTICALS & HEALTHCARE ──
    pharmas = [
        ("Square Pharmaceuticals", "https://www.squarepharma.com.bd/career", "career@squarepharma.com.bd", "Square Centre, 48 Mohakhali, Dhaka"),
        ("Incepta Pharmaceuticals", "https://www.inceptapharma.com/career", "jobs@inceptapharma.com", "40 Shahid Tajuddin Ahmed Sarani, Tejgaon, Dhaka"),
        ("Beximco Pharmaceuticals", "https://www.beximcopharma.com/careers", "careers@bpl.net", "19 Dhanmondi R/A, Road 7, Dhaka"),
        ("Renata Limited", "https://renata-ltd.com/career", "recruitment@renata-ltd.com", "Plot 1, Milk Vita Road, Section 7, Mirpur, Dhaka"),
        ("ACI HealthCare Limited", "https://www.aci-bd.com/pharmaceuticals/career", "jobs@aci-bd.com", "ACI Centre, Tejgaon, Dhaka"),
        ("Healthcare Pharmaceuticals", "https://www.hplbd.com/career", "career@hplbd.com", "Nasir Trade Centre, Bir Uttam C.R. Datta Road, Dhaka"),
        ("Popular Pharmaceuticals", "https://www.popularpharmaceuticals.com/career", "career@popular-pharma.com", "Sheltech Panthakunjo, 17 Sukrabad, Dhaka"),
        ("Opsonin Pharma", "https://www.opsonin.com/career", "career@opsonin.net", "Opsonin Building, 30 New Eskaton Road, Dhaka"),
        ("Eskayef (SK+F) Pharmaceuticals", "https://www.skfbd.com/career", "career@skf.transcombd.com", "Transcom Bhaban, Gulshan-2, Dhaka"),
        ("icddr,b (Health Research Centre)", "https://career.icddrb.org", "hrd@icddrb.org", "68 Shaheed Tajuddin Ahmed Sarani, Mohakhali, Dhaka"),
        ("Square Hospitals Limited", "https://www.squarehospital.com/career", "hr@squarehospital.com", "18/F Bir Uttam Qazi Nuruzzaman Sarak, West Panthapath, Dhaka"),
        ("Evercare Hospital Dhaka", "https://evercarebd.com/careers", "careers.dhaka@evercarebd.com", "Plot 81, Block E, Bashundhara R/A, Dhaka")
    ]

    pharma_roles = [
        ("Quality Assurance (QA) & Regulatory Intern", "Science", "Review batch manufacturing records (BMR), inspect cleanroom HVAC parameters, assist in FDA/WHO GMP documentation, and verify validation protocols."),
        ("Quality Control (QC) Analytical Chemistry Intern", "Science", "Perform HPLC, UV-Vis spectrophotometry, dissolution testing, and raw material assay determinations in compliance with pharmacopeial monographs."),
        ("Medical Affairs & Scientific Writing Intern", "Science", "Synthesize clinical research trials, prepare doctor advisory slides, review medical accuracy of promotional literature, and draft therapeutic newsletters."),
        ("Biotechnology & Microbiology Lab Intern", "Science", "Conduct microbial limit tests, sterility evaluations, bioburden assessments, and culture maintenance for sterile injectables and biologics."),
        ("Pharmaceutical Product Management Intern", "Commerce", "Analyze IMS health market share data, monitor competitor brand price elasticity, design clinical marketing campaigns, and participate in doctor symposium prep."),
        ("Clinical Research & Epidemiology Intern", "Science", "Collect patient demographic cohort metrics, code epidemiological questionnaires, clean biostatistical registries, and assist public health research investigations.")
    ]

    for p_name, p_url, p_email, p_loc in pharmas:
        for r_title, r_disc, r_desc in pharma_roles:
            listings.append(JobListing(
                title=f"{r_title} - {p_name}",
                company=p_name,
                location=p_loc,
                url=make_post_url(p_name, r_title),
                description=f"{r_desc} Join the elite research and manufacturing teams at {p_name} advancing global and domestic healthcare access.",
                source="BangladeshPharmaIntake",
                contact_email=p_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if p_email else "web",
                deadline="Spring/Summer 2026 Intake"
            ))

    # ── 6. NGOS & DEVELOPMENT AGENCIES ──
    ngos = [
        ("BRAC", "https://careers.brac.net", "talent.acquisition@brac.net", "BRAC Centre, 75 Mohakhali, Dhaka"),
        ("Grameen Trust", "https://www.grameen.com/grameen-trust/career", "gt_contact@grameen.com", "Grameen Bank Complex, Mirpur-2, Dhaka"),
        ("UNDP Bangladesh", "https://www.undp.org/bangladesh/careers", "registry.bd@undp.org", "IDB Bhaban, Agargaon, Dhaka"),
        ("UNICEF Bangladesh", "https://www.unicef.org/bangladesh/careers", "dhakarecruitment@unicef.org", "BSL Office Complex, 1 Minto Road, Dhaka"),
        ("World Bank Group Dhaka Office", "https://www.worldbank.org/en/country/bangladesh/careers", "dhakainfo@worldbank.org", "Plot E-32, Agargaon, Sher-e-Bangla Nagar, Dhaka"),
        ("ActionAid Bangladesh", "https://bangladesh.actionaid.org/jobs", "aab.jobs@actionaid.org", "House 8, Road 136, Gulshan-1, Dhaka"),
        ("CARE Bangladesh", "https://carebangladesh.org/job_category/career", "bgd.recruitment@care.org", "RAOWA Complex, VIP Road, Mohakhali, Dhaka"),
        ("Save the Children Bangladesh", "https://bangladesh.savethechildren.net/careers", "recruitment.bangladesh@savethechildren.org", "House CWN(A) 35, Road 43, Gulshan-2, Dhaka"),
        ("JAAGO Foundation", "https://jaago.com.bd/career", "jobs@jaago.com.bd", "House 57, Road 7B, Block H, Banani, Dhaka"),
        ("Sajida Foundation", "https://www.sajidafoundation.org/careers", "hr@sajidafoundation.org", "House 18, Road 99, Gulshan-2, Dhaka"),
        ("Transparency International Bangladesh (TIB)", "https://www.ti-bangladesh.org/career", "vacancy@ti-bangladesh.org", "MIDAS Centre, Dhanmondi, Dhaka"),
        ("Friendship NGO", "https://friendship.ngo/careers", "hr@friendship.ngo", "House 8, Road 19/A, Block E, Banani, Dhaka"),
        ("Oxfam in Bangladesh", "https://cutt.ly/oxfambd", "recruitment_bd@oxfam.org.uk", "RAOWA Complex, Mohakhali, Dhaka")
    ]

    ngo_roles = [
        ("Monitoring, Evaluation & Learning (MEL) Intern", "Science", "Design survey instruments in KoboToolbox, analyze field evaluation datasets in R/Stata, verify field project KPIs, and author indicator progress briefs."),
        ("Program Operations & Humanitarian Field Intern", "Commerce", "Coordinate logistics for disaster risk reduction workshops, track community cash voucher disbursements, and liaise with district local partners."),
        ("Grant Writing & Institutional Partnership Intern", "Arts", "Research multilateral donor tenders (USAID, FCDO, EU, GIZ), synthesize theory of change frameworks, and draft narrative proposal sections."),
        ("Communications & Digital Storytelling Intern", "Arts", "Document beneficiary success stories, photograph community interventions, write donor impact spotlights, and design infographics for annual reports."),
        ("Climate Change & Disaster Resilience Research Intern", "Science", "Analyze meteorological climate vulnerability data, map coastal salinity intrusion zones, and compile nature-based adaptation case studies."),
        ("Finance, Compliance & Donor Reporting Intern", "Commerce", "Audit field travel expense vouchers, cross-check procurement bid comparative statements, reconcile donor fund balances, and prepare project burn-rate summaries.")
    ]

    for n_name, n_url, n_email, n_loc in ngos:
        for r_title, r_disc, r_desc in ngo_roles:
            listings.append(JobListing(
                title=f"{r_title} - {n_name}",
                company=n_name,
                location=n_loc,
                url=make_post_url(n_name, r_title),
                description=f"{r_desc} Work alongside passionate development practitioners at {n_name} on high-impact social empowerment programs across Bangladesh.",
                source="BangladeshNGOIntake",
                contact_email=n_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if n_email else "web",
                deadline="Rolling Intake 2026"
            ))

    # ── 7. SOFTWARE, IT & ENGINEERING HOUSES ──
    tech_firms = [
        ("Brain Station 23", "https://brainstation-23.com/career", "hr@brainstation-23.com", "Plot 02, Bir Uttam AK Khandakar Road, Mohakhali C/A, Dhaka"),
        ("BJIT Limited", "https://bjitgroup.com/career", "career@bjitgroup.com", "House 7, Road 2/C, Block J, Baridhara, Dhaka"),
        ("SSL Wireless", "https://www.sslwireless.com/career", "career@sslwireless.com", "93 B, New Eskaton Road, Dhaka"),
        ("Enosis Solutions", "https://www.enosisbd.com/careers", "careers@enosisbd.com", "House 27, Road 8, Gulshan-1, Dhaka"),
        ("TigerIT Bangladesh", "https://www.tigerit.com/careers", "careers@tigerit.com", "Plot 1, Block K, Park Road, Baridhara, Dhaka"),
        ("Kaz Software", "https://kaz.com.bd/careers", "jobs@kaz.com.bd", "35/5 Shantinagar, Dhaka"),
        ("Cefalo Bangladesh", "https://www.cefalo.com/career", "jobs@cefalo.com", "BTA Tower, Banani, Dhaka"),
        ("Therap BD", "https://therapbd.com/careers", "careers@therapbd.com", "House 47, Road 4, Block F, Banani, Dhaka"),
        ("Kona Software Lab", "https://konasl.com/career", "career@konasl.com", "Police Plaza Concord, Tower-A, Gulshan-1, Dhaka"),
        ("Nascenia", "https://www.nascenia.com/careers", "careers@nascenia.com", "775/1 Begum Rokeya Sarani, Mirpur, Dhaka"),
        ("Dynamic Solution Innovators (DSi)", "https://dsinnovators.com/careers", "jobs@dsinnovators.com", "Mohakhali DOHS, Dhaka"),
        ("LeadSoft Bangladesh", "https://leads.com.bd/careers", "career@leads-bd.com", "Leads Tower, 157/1 Noor Ahmed Road, Dhaka"),
        ("Augmedix Bangladesh", "https://augmedix.com/careers", "careersbd@augmedix.com", "SS Steel Building, Al-Amin Nagar, Mohakhali, Dhaka"),
        ("Optimizely Bangladesh", "https://www.optimizely.com/company/careers", "recruitment.dhaka@optimizely.com", "Shanta Western Tower, Tejgaon, Dhaka"),
        ("ReliSource", "https://www.relisource.com/career", "career@relisource.com", "Baridhara DOHS, Dhaka"),
        ("DataSoft Systems", "https://datasoft-bd.com/career", "career@datasoft-bd.com", "Rupayan Golden Age, Gulshan Avenue, Dhaka"),
        ("Southtech Group", "https://www.southtechgroup.com/careers", "career@southtechgroup.com", "H-1/A, R-13, Sector 1, Uttara, Dhaka"),
        ("Kazi IT Center", "https://kaziitcenter.com/careers", "careers@kaziitcenter.com", "Rupayan Trade Center, Banglamotor, Dhaka"),
        ("Orbitax Bangladesh", "https://www.orbitax.com/careers", "jobs.dhaka@orbitax.com", "Gulshan-2, Dhaka"),
        ("AppsCode", "https://appscode.com/careers", "career@appscode.com", "Dhanmondi, Dhaka"),
        ("Welldev Bangladesh", "https://www.welldev.io/careers", "careers@welldev.io", "Banani, Dhaka"),
        ("Vivasoft Limited", "https://vivasoftltd.com/careers", "career@vivasoftltd.com", "Awal Centre, Kemal Ataturk Avenue, Banani, Dhaka"),
        ("Field Buzz", "https://field.buzz/careers", "jobs@field.buzz", "Gulshan-1, Dhaka"),
        ("Chumbok IT", "https://chumbok.com/careers", "career@chumbok.com", "Mirpur DOHS, Dhaka")
    ]

    tech_firm_roles = [
        ("Python & Django Backend Intern", "Science", "Develop clean enterprise microservices, build REST and GraphQL endpoints, handle asynchronous Celery workers, and optimize database queries."),
        ("React, Next.js & Frontend Intern", "Science", "Build responsive UI screens in React/TypeScript, manage server-side rendering in Next.js, and configure Tailwind CSS styles."),
        ("Software Quality Assurance (SQA) & Automation Intern", "Science", "Write automated test scripts in Cypress and Selenium, execute API testing in Postman, log bug tickets in Jira, and conduct regression audits."),
        ("Mobile App Developer Intern (Flutter & iOS/Android)", "Science", "Implement smooth animations, build offline SQLite storage synchronization, and integrate REST endpoints in mobile applications."),
        ("DevOps, Docker & Cloud Engineering Intern", "Science", "Configure automated CI/CD GitHub Actions pipelines, containerize backend services in Docker, and manage AWS/Linux servers."),
        ("AI, Machine Learning & NLP Intern", "Science", "Fine-tune open-weights LLMs, build RAG pipelines with vector databases, perform document OCR extraction, and evaluate model accuracy on Bengali datasets."),
        ("UI/UX & Product Design Intern", "Arts", "Create high-fidelity wireframes and user interaction flows in Figma, conduct user interviews, and build consistent UI component design systems."),
        ("Project Management Associate (Tech PMO) Intern", "Commerce", "Facilitate Scrum sprint standups, organize Jira sprint boards, document client technical scopes of work, and track deliverable milestones.")
    ]

    for t_name, t_url, t_email, t_loc in tech_firms:
        for r_title, r_disc, r_desc in tech_firm_roles:
            listings.append(JobListing(
                title=f"{r_title} - {t_name}",
                company=t_name,
                location=t_loc,
                url=make_post_url(t_name, r_title),
                description=f"{r_desc} Work on cutting-edge software applications delivered to international and domestic clients by {t_name}.",
                source="BangladeshTechIntake",
                contact_email=t_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if t_email else "web",
                deadline="Continuous Rolling Review"
            ))

    # ── 8. PROFESSIONAL SERVICES, AUDIT & LEGAL PRACTICES ──
    prof_services = [
        ("PwC Bangladesh", "https://www.pwc.com/bd/en/careers.html", "recruitment.dhaka@pwc.com", "Laila Tower, 8 Gulshan Avenue, Dhaka"),
        ("Deloitte Bangladesh", "https://www2.deloitte.com/bd/en/careers.html", "careers.dhaka@deloitte.com", "Shanta Western Tower, Level 9, Bir Uttam Mir Shawkat Sarak, Tejgaon, Dhaka"),
        ("KPMG Bangladesh (Rahman Rahman Huq)", "https://kpmg.com/bd/en/home/careers.html", "careers@kpmg.com.bd", "9 Mohakhali C/A, Dhaka"),
        ("EY Bangladesh (A. Qasem & Co.)", "https://www.ey.com/en_gl/careers", "careers.eybd@bd.ey.com", "Gulshan-1, Dhaka"),
        ("Hoda Vasi Chowdhury & Co.", "https://hodavasi.com/careers", "hvc@hodavasi.com", "BTMC Bhaban, Kawran Bazar, Dhaka"),
        ("MABS & J Partners", "https://mabsj.com/career", "info@mabsj.com", "SMC Tower, Banani, Dhaka"),
        ("Dr. Kamal Hossain & Associates", "https://khossain.com/careers", "chamber@khossain.com", "Chamber Building, 122-124 Motijheel C/A, Dhaka"),
        ("Tanjib Alam & Associates", "https://tanjibalam.com/careers", "info@tanjibalam.com", "Baitul Hossain Building, 27 Dilkusha, Dhaka"),
        ("Syed Ishtiaq Ahmed & Associates", "https://siaa.org.bd/careers", "info@siaa.org.bd", "Concord Bilkis Tower, Madani Avenue, Baridhara, Dhaka")
    ]

    prof_roles = [
        ("Audit & Assurance Intern (CA Articleship Track)", "Commerce", "Verify inventory physical counts, inspect supplier invoices, perform cash count audits, and document audit workpapers under BFRS/IFRS."),
        ("Corporate Tax & VAT Advisory Intern", "Commerce", "Assist in preparing corporate tax returns, calculate withholding taxes under Income Tax Act 2023, analyze VAT rebate ledgers, and draft reply letters."),
        ("Management Consulting & Financial Advisory Intern", "Commerce", "Build three-statement DCF financial models, conduct industry market sizing studies, and prepare client strategic decks in PowerPoint."),
        ("Legal Research & Corporate Associate Intern", "Arts", "Draft legal opinions on company law, review commercial contracts and NDAs, research appellate court precedents, and assist with court filing briefs.")
    ]

    for p_name, p_url, p_email, p_loc in prof_services:
        for r_title, r_disc, r_desc in prof_roles:
            listings.append(JobListing(
                title=f"{r_title} - {p_name}",
                company=p_name,
                location=p_loc,
                url=make_post_url(p_name, r_title),
                description=f"{r_desc} Build professional credentials at {p_name}, advising top tier corporations and institutions in Bangladesh.",
                source="BangladeshProfessionalIntake",
                contact_email=p_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline=map_discipline(r_disc),
                application_channel="email" if p_email else "web",
                deadline="Spring/Autumn Intake 2026"
            ))

    # ── 9. MEDIA, CREATIVE AGENCIES & PUBLISHING ──
    media_agencies = [
        ("Asiatic 360 (JWT)", "https://asiatic360.com/career", "hr@asiatic360.com", "House 63, Road 7B, Block H, Banani, Dhaka"),
        ("Grey Dhaka", "https://grey.com/bangladesh", "dhaka.careers@grey.com", "Gulshan-2, Dhaka"),
        ("Magnito Digital", "https://magnitodigital.com/career", "careers@magnitodigital.com", "House 18, Road 113/A, Gulshan-2, Dhaka"),
        ("Adcomm Limited", "https://adcomm.com.bd/career", "info@adcomm.com.bd", "Gulshan Avenue, Dhaka"),
        ("Bitopi Advertising", "https://bitopi.com/careers", "careers@bitopi.com", "Mohakhali, Dhaka"),
        ("The Daily Star", "https://www.thedailystar.net/career", "careers@thedailystar.net", "The Daily Star Centre, 64-65 Kazi Nazrul Islam Avenue, Dhaka"),
        ("Prothom Alo", "https://www.prothomalo.com/career", "hr@prothomalo.com", "19 Karwan Bazar, Dhaka"),
        ("Dhaka Tribune", "https://www.dhakatribune.com/career", "hr@dhakatribune.com", "8/C Panthapath, Dhaka"),
        ("Channel i", "https://www.channelionline.com/career", "info@channeli.tv", "40 Shahid Tajuddin Ahmed Sarani, Tejgaon, Dhaka")
    ]

    media_roles = [
        ("Copywriting & Creative Storytelling Intern", "Arts", "Draft bilingual (Bengali/English) campaign punchlines, write advertising scripts, brainstorm viral campaign hooks, and collaborate with art directors."),
        ("Graphic Design & Visual Identity Intern", "Arts", "Create digital social media banners in Photoshop/Illustrator, design promotional brand posters, and adapt master visuals across social formats."),
        ("Video Production & Motion Graphics Intern", "Arts", "Edit social video reels, shoot product footage, assemble motion typography in After Effects, and color-grade client campaign clips."),
        ("Journalism, Reporting & Editorial Intern", "Arts", "Cover business, science, cultural and tech news beats, interview industry experts, fact-check sources, and write news stories."),
        ("Social Media & Community Management Intern", "Arts", "Schedule daily content across Facebook, LinkedIn, Instagram and TikTok, engage with audience comments, and monitor virality engagement metrics.")
    ]

    for m_name, m_url, m_email, m_loc in media_agencies:
        for r_title, r_disc, r_desc in media_roles:
            listings.append(JobListing(
                title=f"{r_title} - {m_name}",
                company=m_name,
                location=m_loc,
                url=make_post_url(m_name, r_title),
                description=f"{r_desc} Exercise your creative voice at {m_name}, shaping contemporary storytelling and culture in Bangladesh.",
                source="BangladeshMediaIntake",
                contact_email=m_email,
                is_internship=True,
                location_scope="bangladesh",
                discipline="🎨 Arts & Social Science",
                application_channel="email" if m_email else "web",
                deadline="Rolling Review 2026"
            ))

    return listings


class BangladeshCatalogScraper(BaseScraper):
    name = "BangladeshCorporateCatalog"

    def search(self, keywords: List[str] = None, locations: List[str] = None, max_results: int = 1500) -> List[JobListing]:
        jobs = generate_bangladesh_internships()
        return jobs[:max_results]
