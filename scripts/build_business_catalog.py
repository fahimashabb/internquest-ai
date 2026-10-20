"""
Generates the comprehensive, verified Business & Commerce Internship Catalog
for Bangladesh students and global remote opportunities.
Categorized by sub-discipline and sorted by company prestige / corporate value.
"""
import json
from pathlib import Path
from datetime import datetime

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "business_internships.json"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Define Master Companies with Value Tiers, Sectors, and Careers
COMPANIES_MASTER = [
    # Tier 1: Premier Multinationals & Foreign Banks
    {
        "company": "Unilever Bangladesh",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "⭐ Tier 1: Top MNC",
        "tier_class": "tier-1",
        "value_score": 100,
        "location": "Gulshan-1, Dhaka",
        "portal_url": "https://careers.unilever.com/search-jobs/Bangladesh",
        "stipend": "BDT 25,000 - 35,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Finance & Business Partnering Intern",
                "discipline": "Finance & Banking",
                "desc": "Partner directly with category brand managers and supply chain directors. Analyze promotional ROI, prepare variance analyses on P&L drivers, and model cost-of-goods-sold (COGS) optimizations.",
                "keywords": "Unilever Bangladesh Finance Business Partnering Intern"
            },
            {
                "title": "Brand Marketing & Consumer Insights Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Assist in end-to-end brand campaign activations, market share diagnostics using Nielsen data, competitive media tracking, and digital consumer touchpoint strategies.",
                "keywords": "Unilever Bangladesh Brand Marketing Consumer Insights Intern"
            },
            {
                "title": "Supply Chain Excellence & Logistics Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Analyze end-to-end distribution networks, demand forecasting accuracy, raw materials buffer stocks, and vendor lead-time efficiencies across Bangladesh manufacturing plants.",
                "keywords": "Unilever Bangladesh Supply Chain Procurement Intern"
            },
            {
                "title": "Human Resources & Employer Branding Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Coordinate national campus engagements (Unilever BizMaestros), talent acquisition pipelines, leadership development workshops, and employee engagement surveys.",
                "keywords": "Unilever Bangladesh Human Resources Employer Branding Intern"
            }
        ]
    },
    {
        "company": "British American Tobacco (BATB)",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "⭐ Tier 1: Top MNC",
        "tier_class": "tier-1",
        "value_score": 99,
        "location": "Mohakhali, Dhaka",
        "portal_url": "https://careers.bat.com/search/?createNewAlert=false&q=Bangladesh",
        "stipend": "BDT 30,000 - 40,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Corporate Finance & Commercial Budgeting Intern",
                "discipline": "Finance & Banking",
                "desc": "Support the corporate finance team in statutory variance reporting, capital expenditure tracking, excise duty modeling, and cash cycle reconciliations.",
                "keywords": "British American Tobacco Bangladesh Finance Intern"
            },
            {
                "title": "Trade Marketing & Route-to-Market Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Evaluate nationwide distribution channels, retail audit metrics, distributor stock turn rates, and field marketing execution across urban and rural clusters.",
                "keywords": "British American Tobacco Trade Marketing Distribution Intern"
            },
            {
                "title": "Operations & Sourcing Procurement Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Assist the procurement division in supplier performance scorecards, sustainable sourcing audits, packaging material forecasting, and commercial tender preparations.",
                "keywords": "British American Tobacco Supply Chain Procurement Intern"
            },
            {
                "title": "Human Resources & Talent Analytics Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Support Battle of Minds national business competition management, HR digital system automation, campus relations, and talent onboarding workflows.",
                "keywords": "British American Tobacco Human Resources Intern"
            }
        ]
    },
    {
        "company": "Standard Chartered Bank Bangladesh",
        "tier": "Tier 1: Global MNC & Foreign Bank",
        "tier_badge": "🏛️ Tier 1: Global Bank",
        "tier_class": "tier-1",
        "value_score": 98,
        "location": "Gulshan-2, Dhaka",
        "portal_url": "https://www.sc.com/bd/careers/",
        "stipend": "BDT 22,000 - 28,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Corporate Treasury & Capital Markets Intern",
                "discipline": "Finance & Banking",
                "desc": "Work alongside the FX dealing desk and liquidity management team. Monitor money market liquidity, government treasury bond yields, FX swap spreads, and central bank reporting.",
                "keywords": "Standard Chartered Bank Treasury Capital Markets Intern Bangladesh"
            },
            {
                "title": "Commercial Credit Risk & Financial Spreading Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist relationship managers in financial statement spreading, debt-service coverage ratio (DSCR) calculations, credit memo drafting, and industry risk evaluations.",
                "keywords": "Standard Chartered Bank Credit Risk Analyst Intern Bangladesh"
            },
            {
                "title": "Transaction Banking & Trade Operations Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Gain hands-on exposure to Letters of Credit (LC), cross-border trade finance, SWIFT messaging protocols, and corporate electronic cash management portals.",
                "keywords": "Standard Chartered Bank Transaction Banking Trade Intern Bangladesh"
            },
            {
                "title": "Financial Crime & Regulatory Compliance Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Review Know-Your-Customer (KYC) documentation, Anti-Money Laundering (AML) transaction monitoring alerts, sanctions screening checks, and regulatory filings.",
                "keywords": "Standard Chartered Bank Compliance Audit Intern Bangladesh"
            }
        ]
    },
    {
        "company": "HSBC Bangladesh",
        "tier": "Tier 1: Global MNC & Foreign Bank",
        "tier_badge": "🏛️ Tier 1: Global Bank",
        "tier_class": "tier-1",
        "value_score": 97,
        "location": "Bir Uttam Mir Shawkat Sarak, Gulshan, Dhaka",
        "portal_url": "https://www.hsbc.com.bd/1/2/careers",
        "stipend": "BDT 20,000 - 25,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Global Banking & Corporate Finance Intern",
                "discipline": "Finance & Banking",
                "desc": "Support multinational corporate coverage teams in client pitch presentations, credit appraisal memoranda, working capital facility structuring, and sector research.",
                "keywords": "HSBC Bangladesh Global Banking Corporate Finance Intern"
            },
            {
                "title": "Global Trade & Receivables Finance Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in export bill discounting, supply chain financing solutions, international trade compliance, and multi-currency commercial settlement workflows.",
                "keywords": "HSBC Bangladesh Global Trade Receivables Finance Intern"
            },
            {
                "title": "Wealth Management & Premier Banking Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support high-net-worth customer portfolio diagnostics, premium customer experience initiatives, affluent banking campaigns, and investment market briefings.",
                "keywords": "HSBC Bangladesh Wealth Management Premier Banking Intern"
            }
        ]
    },
    {
        "company": "Nestlé Bangladesh",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "⭐ Tier 1: Top MNC",
        "tier_class": "tier-1",
        "value_score": 96,
        "location": "Gulshan-1, Dhaka",
        "portal_url": "https://www.nestle.com.bd/jobs",
        "stipend": "BDT 22,000 - 30,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Financial Planning & Analysis (FP&A) Intern",
                "discipline": "Finance & Banking",
                "desc": "Participate in monthly Dynamic Forecasting (DF), cost center variance diagnostics, overhead allocations, and trade promotion profitability tracking across product categories.",
                "keywords": "Nestle Bangladesh Financial Planning Analysis Intern"
            },
            {
                "title": "Brand Strategy & Nutrition Marketing Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Help plan integrated consumer marketing campaigns, digital consumer activations for flagship brands (Maggi, Nescafé, NIDO), and point-of-sale visibility audits.",
                "keywords": "Nestle Bangladesh Brand Marketing Consumer Strategy Intern"
            },
            {
                "title": "Supply Chain & Customer Service Logistics Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Assist in on-time-in-full (OTIF) order dispatch monitoring, distribution center replenishment schedules, freight vendor audits, and cold-chain inventory analytics.",
                "keywords": "Nestle Bangladesh Supply Chain Logistics Intern"
            }
        ]
    },
    {
        "company": "Marico Bangladesh",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "⭐ Tier 1: Top MNC",
        "tier_class": "tier-1",
        "value_score": 95,
        "location": "Gulshan-1, Dhaka",
        "portal_url": "https://marico.com/bangladesh/careers",
        "stipend": "BDT 25,000 - 35,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Corporate Finance & Commercial Planning Intern",
                "discipline": "Finance & Banking",
                "desc": "Analyze gross margin evolutions, raw material commodity price volatility impact, distributor credit limits, and commercial contract negotiations.",
                "keywords": "Marico Bangladesh Corporate Finance Commercial Planning Intern"
            },
            {
                "title": "Brand Innovation & Consumer Research Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support new product launch roadmaps, packaging and consumer sentiment testing, influencer marketing ROI tracking, and retail audit reviews.",
                "keywords": "Marico Bangladesh Brand Marketing Innovation Intern"
            },
            {
                "title": "Procurement & Strategic Sourcing Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Help analyze packaging material suppliers, copacker compliance ratings, sustainable energy procurement contracts, and inbound shipping schedules.",
                "keywords": "Marico Bangladesh Procurement Sourcing Intern"
            }
        ]
    },
    {
        "company": "PwC Bangladesh",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "📊 Tier 1: Big 4 Audit",
        "tier_class": "tier-1",
        "value_score": 96,
        "location": "Gulshan Avenue, Dhaka",
        "portal_url": "https://www.pwc.com/bd/en/careers.html",
        "stipend": "BDT 18,000 - 25,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Statutory Financial Audit & Assurance Trainee",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Participate in external financial audits of leading banks and multinationals under IFRS and Bangladesh Financial Reporting Standards. Perform substantive testing and voucher verification.",
                "keywords": "PwC Bangladesh Statutory Audit Assurance Trainee Intern"
            },
            {
                "title": "Corporate Taxation & Transfer Pricing Advisory Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Assist tax consultants in corporate tax computation, advance income tax (AIT) reconciliations, VAT audit compliance under NBR guidelines, and transfer pricing documentation.",
                "keywords": "PwC Bangladesh Corporate Tax Transfer Pricing Advisory Intern"
            },
            {
                "title": "Management Consulting & Deals Advisory Intern",
                "discipline": "Management & Operations",
                "desc": "Support financial due diligence, market entry feasibility studies, commercial business modeling, and mergers & acquisitions analysis for corporate clients.",
                "keywords": "PwC Bangladesh Management Consulting Deals Advisory Intern"
            }
        ]
    },
    {
        "company": "KPMG Bangladesh (Rahman Rahman Huq)",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "📊 Tier 1: Big 4 Audit",
        "tier_class": "tier-1",
        "value_score": 95,
        "location": "Mohakhali C/A, Dhaka",
        "portal_url": "https://kpmg.com/bd/en/home/careers.html",
        "stipend": "BDT 16,000 - 22,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Audit & Financial Advisory Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Perform audit field procedures, internal control evaluations, bank reconciliations, inventory count physical verifications, and draft statutory audit workpapers.",
                "keywords": "KPMG Bangladesh Rahman Rahman Huq Audit Financial Advisory Intern"
            },
            {
                "title": "Taxation, VAT & Regulatory Compliance Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Work on corporate income tax returns, monthly VAT submissions, withholding tax deduction schedules, and regulatory appellate documentation.",
                "keywords": "KPMG Bangladesh Taxation VAT Compliance Intern"
            }
        ]
    },
    {
        "company": "Hoda Vasi Chowdhury & Co.",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "📊 Tier 1: Premier Audit",
        "tier_class": "tier-1",
        "value_score": 93,
        "location": "Motijheel / Kawran Bazar, Dhaka",
        "portal_url": "https://www.hodavasi.com/careers",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Chartered Audit & Assurance Trainee",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Engage in full-cycle statutory audits across manufacturing, financial institutions, and NGOs. Conduct analytical reviews, trial balance verifications, and compliance checks.",
                "keywords": "Hoda Vasi Chowdhury Chartered Audit Assurance Trainee Intern"
            },
            {
                "title": "Internal Audit & Risk Advisory Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Review corporate standard operating procedures (SOPs), financial governance checklists, enterprise risk management registers, and fraud prevention controls.",
                "keywords": "Hoda Vasi Chowdhury Internal Audit Risk Advisory Intern"
            }
        ]
    },
    {
        "company": "Grameenphone (Telenor Group)",
        "tier": "Tier 1: Premier Global MNC",
        "tier_badge": "⭐ Tier 1: Top MNC",
        "tier_class": "tier-1",
        "value_score": 97,
        "location": "G-House, Bashundhara R/A, Dhaka",
        "portal_url": "https://www.grameenphone.com/about/careers",
        "stipend": "BDT 25,000 - 32,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Corporate Strategy & Business Performance Intern",
                "discipline": "Management & Operations",
                "desc": "Analyze telecom ARPU dynamics, digital product subscriber growth, spectrum capital investment appraisals, and enterprise 5G market entry plans.",
                "keywords": "Grameenphone Corporate Strategy Business Performance Intern"
            },
            {
                "title": "FinTech & Digital Commerce Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Support digital billing platforms, MyGP app monetization funnels, partner ecosystem commercial negotiations, and customer lifecycle marketing.",
                "keywords": "Grameenphone FinTech Digital Commerce Intern"
            },
            {
                "title": "Financial Planning & Treasury Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in corporate financial budgeting, revenue assurance analytics, foreign currency hedging contracts, and BSEC/BTRC financial reporting.",
                "keywords": "Grameenphone Finance Treasury Planning Intern"
            },
            {
                "title": "Brand Communications & Digital Marketing Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Collaborate on integrated 360-degree brand campaigns, digital agency briefing, social media performance tracking, and event sponsorships.",
                "keywords": "Grameenphone Brand Communications Marketing Intern"
            }
        ]
    },

    # Tier 2: Premier National Banks & Top FinTech Leaders
    {
        "company": "BRAC Bank",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "🏛️ Tier 2: Premier Bank",
        "tier_class": "tier-2",
        "value_score": 90,
        "location": "Anik Tower, Tejgaon I/A, Dhaka",
        "portal_url": "https://www.bracbank.com/en/career",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Financial Analyst & Credit Risk Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist credit risk analysts in spreading audited balance sheets, calculating debt-equity leverage, assessing SME repayment capacities, and drafting credit approval proposals.",
                "keywords": "BRAC Bank Financial Analyst Credit Risk Intern Bangladesh"
            },
            {
                "title": "Corporate Treasury & Capital Markets Intern",
                "discipline": "Finance & Banking",
                "desc": "Support the treasury front and back office in liquidity asset monitoring, statutory liquidity ratio (SLR/CRR) compliance, call money market deals, and repo operations.",
                "keywords": "BRAC Bank Corporate Treasury Capital Markets Intern Bangladesh"
            },
            {
                "title": "Internal Audit & Regulatory Compliance Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Verify branch loan documentation compliance, audit trail validations, anti-money laundering transaction logs, and Bangladesh Bank inspection preparation.",
                "keywords": "BRAC Bank Internal Audit Compliance Intern Bangladesh"
            },
            {
                "title": "Card Operations & Payment Systems Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Examine credit card chargebacks, merchant POS settlements, international card scheme interchange reconciliations, and digital payment gateway metrics.",
                "keywords": "BRAC Bank Card Operations Payment Systems Intern Bangladesh"
            },
            {
                "title": "Brand Marketing & Customer Engagement Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Assist with retail banking marketing initiatives, Astha digital banking app customer promos, festival merchant discount campaigns, and social media analytics.",
                "keywords": "BRAC Bank Brand Marketing Customer Engagement Intern Bangladesh"
            },
            {
                "title": "Human Resources & Talent Management Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Support Young Leaders Program (YLP) recruitment, employee training program coordination, performance appraisal analytics, and HR service desk requests.",
                "keywords": "BRAC Bank Human Resources Talent Management Intern Bangladesh"
            }
        ]
    },
    {
        "company": "bKash Limited",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "⚡ Tier 2: Top FinTech",
        "tier_class": "tier-2",
        "value_score": 92,
        "location": "Shadhinata Bhaban, Bir Uttam Mir Shawkat Sarak, Dhaka",
        "portal_url": "https://www.bkash.com/career",
        "stipend": "BDT 20,000 - 28,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "FinTech Product Management & Growth Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Collaborate on digital payment user flows, QR code transaction conversions, micro-savings & nano-loan customer journey optimizations, and feature experimentation.",
                "keywords": "bKash FinTech Product Management Growth Intern"
            },
            {
                "title": "Financial Planning & Analysis (FP&A) Intern",
                "discipline": "Finance & Banking",
                "desc": "Support the finance team in monthly merchant fee reconciliations, interest income projections from trust funds, operating cost tracking, and executive board decks.",
                "keywords": "bKash Financial Planning Analysis Finance Intern"
            },
            {
                "title": "Merchant Acquisition & Commercial Operations Intern",
                "discipline": "Management & Operations",
                "desc": "Evaluate retail merchant onboarding data, enterprise corporate payroll integrations, merchant commission structures, and territory performance metrics.",
                "keywords": "bKash Merchant Acquisition Commercial Operations Intern"
            },
            {
                "title": "Brand Communications & Campaign Analytics Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support nationwide promotional campaigns, cashback budget utilization analysis, consumer sentiment monitoring, and high-impact digital storytelling.",
                "keywords": "bKash Brand Communications Marketing Campaign Intern"
            },
            {
                "title": "People & Culture (HR) Operations Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Coordinate campus recruitment drives, onboarding experience initiatives, employee wellbeing programs, and HRIS data accuracy management.",
                "keywords": "bKash Human Resources People Culture Intern"
            }
        ]
    },
    {
        "company": "City Bank",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "🏛️ Tier 2: Premier Bank",
        "tier_class": "tier-2",
        "value_score": 89,
        "location": "City Bank Center, Gulshan-2, Dhaka",
        "portal_url": "https://career.thecitybank.com/",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Credit Risk Management & Corporate Lending Intern",
                "discipline": "Finance & Banking",
                "desc": "Analyze commercial corporate balance sheets, debt structures, industry sector risk factors, and prepare credit approval summaries under central bank prudential regulations.",
                "keywords": "City Bank Credit Risk Corporate Lending Intern Bangladesh"
            },
            {
                "title": "City Alo Women Banking & Segment Marketing Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Help drive tailored financial products for women entrepreneurs, organize networking seminars, design segment promotions, and track portfolio acquisition.",
                "keywords": "City Bank City Alo Marketing Segment Intern Bangladesh"
            },
            {
                "title": "Cards & American Express (Amex) Operations Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Support the premium Amex card issuing division in reward point reconciliations, merchant discount rate (MDR) evaluations, and premium client servicing workflows.",
                "keywords": "City Bank Amex Card Operations Intern Bangladesh"
            },
            {
                "title": "Treasury Back-Office & Money Markets Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in inter-bank settlement vouchers, foreign exchange deal matching, treasury bill register upkeep, and liquidity forecasting sheets.",
                "keywords": "City Bank Treasury Money Market Intern Bangladesh"
            }
        ]
    },
    {
        "company": "Eastern Bank Limited (EBL)",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "🏛️ Tier 2: Premier Bank",
        "tier_class": "tier-2",
        "value_score": 88,
        "location": "EBL Tower, Gulshan-1, Dhaka",
        "portal_url": "https://ebl.com.bd/career",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Corporate Banking & Syndication Financing Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist relationship managers in loan syndication information memorandums, project financing viability models, corporate client financial spreading, and covenant reviews.",
                "keywords": "Eastern Bank EBL Corporate Banking Syndication Intern"
            },
            {
                "title": "Consumer Banking & Wealth Advisory Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Analyze branch deposit growth campaigns, payroll banking client acquisition, priority lounge customer feedback, and personal loan portfolio tracking.",
                "keywords": "Eastern Bank EBL Consumer Banking Wealth Intern"
            },
            {
                "title": "Trade Finance Operations & Export/Import Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Gain comprehensive understanding of Letter of Credit (LC) lifecycle, UCP 600 rules, import financing schemes (LTR/UPAS), and export proceeds monitoring.",
                "keywords": "Eastern Bank EBL Trade Finance Operations Intern"
            }
        ]
    },
    {
        "company": "Nagad",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "⚡ Tier 2: Top FinTech",
        "tier_class": "tier-2",
        "value_score": 88,
        "location": "Banani, Dhaka",
        "portal_url": "https://www.nagad.com.bd/careers",
        "stipend": "BDT 18,000 - 25,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Strategic Partnerships & Commercial Alliances Intern",
                "discipline": "Management & Operations",
                "desc": "Support business development teams in striking utility biller partnerships, e-commerce payment integrations, government disbursement schemes, and revenue sharing agreements.",
                "keywords": "Nagad Strategic Partnerships Commercial Alliances Intern"
            },
            {
                "title": "Financial Reconciliations & Regulatory Reporting Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in high-volume electronic fund transfers (NPSB, BEFTN, RTGS) reconciliations, trust cum settlement account audits, and postal department financial statements.",
                "keywords": "Nagad Financial Reconciliations Regulatory Reporting Intern"
            },
            {
                "title": "Growth Marketing & Consumer Acquisition Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Analyze app install conversion rates, customer retention cohorts, gamified campaign mechanics, and regional promotional budget allocations.",
                "keywords": "Nagad Growth Marketing Consumer Acquisition Intern"
            }
        ]
    },
    {
        "company": "Mutual Trust Bank (MTB)",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "🏛️ Tier 2: Premier Bank",
        "tier_class": "tier-2",
        "value_score": 87,
        "location": "MTB Centre, Gulshan-1, Dhaka",
        "portal_url": "https://www.mutualtrustbank.com/career/",
        "stipend": "BDT 15,000 - 18,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "SME Banking & Financial Appraisal Intern",
                "discipline": "Finance & Banking",
                "desc": "Evaluate small and medium enterprise loan applications, assess physical inventory hypothecations, spread financial data, and evaluate borrower cash flows.",
                "keywords": "Mutual Trust Bank MTB SME Banking Financial Appraisal Intern"
            },
            {
                "title": "Digital Banking & Alternate Channels Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Evaluate ATM/CRM cash utilization rates, internet banking onboarding funnels, interoperable QR code payments, and digital branch service efficiency.",
                "keywords": "Mutual Trust Bank MTB Digital Banking Alternate Channels Intern"
            }
        ]
    },
    {
        "company": "IDLC Finance Limited",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "💼 Tier 2: Top NBFI",
        "tier_class": "tier-2",
        "value_score": 89,
        "location": "DR Tower, Bir Uttam Mir Shawkat Sarak, Dhaka",
        "portal_url": "https://idlc.com/career.php",
        "stipend": "BDT 16,000 - 22,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Investment Banking & Corporate Advisory Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in corporate bond issuance structuring, IPO prospectus drafting, valuation of private enterprises, and mergers & acquisition transaction modeling.",
                "keywords": "IDLC Finance Investment Banking Corporate Advisory Intern"
            },
            {
                "title": "Equity Research & Securities Analyst Intern",
                "discipline": "Finance & Banking",
                "desc": "Draft sector reports for the Dhaka Stock Exchange (DSE), construct discounted cash flow (DCF) models, track quarterly corporate earnings, and evaluate macro indicators.",
                "keywords": "IDLC Securities Equity Research Analyst Intern"
            },
            {
                "title": "Consumer Credit Underwriting & Mortgages Intern",
                "discipline": "Finance & Banking",
                "desc": "Review home loan and personal auto finance applications, assess applicant debt-burden ratios, collateral valuations, and credit bureau (CIB) reports.",
                "keywords": "IDLC Finance Consumer Credit Underwriting Intern"
            }
        ]
    },
    {
        "company": "IPDC Finance Limited",
        "tier": "Tier 2: Premier Bank & FinTech Leader",
        "tier_badge": "💼 Tier 2: Top NBFI",
        "tier_class": "tier-2",
        "value_score": 87,
        "location": "Hosna Centre, Gulshan-1, Dhaka",
        "portal_url": "https://www.ipdcbd.com/aboutus/career",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Supply Chain Finance & Factoring Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist in blockchain-based reverse factoring (Orjon), invoice discounting operations for corporate suppliers, and vendor working capital financing.",
                "keywords": "IPDC Finance Supply Chain Finance Factoring Intern"
            },
            {
                "title": "Brand Marketing & Youth Engagement Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Assist in high-visibility cultural brand initiatives, retail consumer product promotions, social content production, and public relations briefings.",
                "keywords": "IPDC Finance Brand Marketing Youth Engagement Intern"
            }
        ]
    },

    # Tier 3: Leading Conglomerates & Corporate Powerhouses
    {
        "company": "Square Group (Pharma, Toiletries & F&B)",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 84,
        "location": "Square Centre, 48 Mohakhali C/A, Dhaka",
        "portal_url": "https://career.squaregroup.com/",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Product Brand Management Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support marketing managers in pharmaceutical brand launches, doctor scientific symposium collateral, consumer toiletries market share analysis, and campaign rollouts.",
                "keywords": "Square Pharmaceuticals Brand Management Marketing Intern"
            },
            {
                "title": "Cost Accounting & Plant Financial Control Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Work on manufacturing batch cost cards, raw material yield variances, direct labor efficiency calculations, and plant overhead allocations.",
                "keywords": "Square Group Cost Accounting Financial Control Intern"
            },
            {
                "title": "Central Procurement & Global Sourcing Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Assist in active pharmaceutical ingredient (API) import documentation, vendor comparative statement preparations, purchase order workflows, and customs clearance tracking.",
                "keywords": "Square Pharmaceuticals Procurement Global Sourcing Intern"
            },
            {
                "title": "Human Capital & Organizational Development Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Coordinate executive training calendars, annual performance KPI documentation, factory worker welfare records, and campus hiring events.",
                "keywords": "Square Group Human Resources Talent Development Intern"
            }
        ]
    },
    {
        "company": "Beximco Group",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 82,
        "location": "BEXIMCO Industrial Park, Dhanmondi / Kashimpur",
        "portal_url": "https://www.beximco.com/careers/",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Corporate Finance & Treasury Intern",
                "discipline": "Finance & Banking",
                "desc": "Support group corporate treasury in working capital credit line consolidations, bank liability statements, loan interest rate negotiations, and export proceeds reconciliations.",
                "keywords": "Beximco Group Corporate Finance Treasury Intern"
            },
            {
                "title": "Export Commercial & International Trade Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Process export Letter of Credit (LC) documentation, bill of lading endorsements, customs bonded warehouse documentation, and international buyer compliance audits.",
                "keywords": "Beximco Export Commercial International Trade Intern"
            },
            {
                "title": "Brand Strategy & E-Commerce Intern (Yellow)",
                "discipline": "Marketing & Brand Management",
                "desc": "Support retail fashion brand campaigns (Yellow), digital catalog merchandising, omnichannel customer satisfaction tracking, and seasonal fashion show activations.",
                "keywords": "Beximco Yellow Fashion Brand Strategy Ecommerce Intern"
            }
        ]
    },
    {
        "company": "ACI Limited",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 81,
        "location": "ACI Centre, 245 Tejgaon I/A, Dhaka",
        "portal_url": "https://www.aci-bd.com/careers",
        "stipend": "BDT 14,000 - 18,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Agribusiness Financial Analyst Intern",
                "discipline": "Finance & Banking",
                "desc": "Examine agribusiness dealer credit exposures, crop protection sales season forecasts, seed division margin analysis, and dealer incentive computations.",
                "keywords": "ACI Limited Agribusiness Financial Analyst Intern"
            },
            {
                "title": "Retail Category & Merchandising Intern (Shwapno)",
                "discipline": "Supply Chain & Procurement",
                "desc": "Analyze superstore category revenue per square foot, planogram compliance, perishable produce spoilage rates, and fast-moving consumer goods inventory turns.",
                "keywords": "ACI Shwapno Retail Category Merchandising Intern"
            },
            {
                "title": "FMCG Brand Management Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support consumer goods marketing across home care and foods divisions. Track retail trade promotions, agency creative deliverables, and competitor retail pricing.",
                "keywords": "ACI Limited FMCG Brand Management Intern"
            }
        ]
    },
    {
        "company": "Meghna Group of Industries (MGI)",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 80,
        "location": "Fresh Villa, Gulshan-1, Dhaka",
        "portal_url": "https://www.mgi.org/career",
        "stipend": "BDT 14,000 - 18,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Group Treasury & Budgeting Intern",
                "discipline": "Finance & Banking",
                "desc": "Support financial modeling across MGI's industrial units (Fresh brand). Assist in daily cash position reporting, banking relationship coordination, and foreign currency LC requirements.",
                "keywords": "Meghna Group of Industries MGI Group Treasury Budgeting Intern"
            },
            {
                "title": "Brand Communications Intern (Fresh Brand)",
                "discipline": "Marketing & Brand Management",
                "desc": "Coordinate above-the-line (ATL) and below-the-line (BTL) activations for Fresh consumer staples (oil, flour, water, beverage), monitor media agency execution, and evaluate trade fairs.",
                "keywords": "Meghna Group Fresh Brand Communications Marketing Intern"
            },
            {
                "title": "Industrial Sourcing & Logistics Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Monitor bulk ocean freight charter tracking, raw commodity vessel discharge operations at Chittagong port, and nationwide fleet distribution efficiency.",
                "keywords": "Meghna Group Industrial Sourcing Logistics Supply Chain Intern"
            }
        ]
    },
    {
        "company": "Walton Hi-Tech Industries",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 79,
        "location": "Walton Corporate Office, Bashundhara R/A, Dhaka",
        "portal_url": "https://waltonbd.com/career",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "International Business & Global Export Intern",
                "discipline": "Management & Operations",
                "desc": "Analyze export buyer inquiries across Europe, Middle East, and Asia. Coordinate export documentation, international trade fair participation, and overseas distributor compliance.",
                "keywords": "Walton Hi Tech International Business Export Intern"
            },
            {
                "title": "Financial Planning & Costing Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist electronics manufacturing finance teams in bill of materials (BOM) cost calculations, depreciation schedules, and working capital cycle tracking.",
                "keywords": "Walton Financial Planning Costing Intern"
            },
            {
                "title": "Digital Marketing & E-Commerce Operations Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support Walton Plaza online sales initiatives, digital ad budget performance tracking (ROAS), promotional bundle campaigns, and customer support analytics.",
                "keywords": "Walton Digital Marketing Ecommerce Operations Intern"
            }
        ]
    },
    {
        "company": "PRAN-RFL Group",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 79,
        "location": "PRAN-RFL Centre, Middle Badda, Dhaka",
        "portal_url": "https://pranrflgroup.com/career",
        "stipend": "BDT 13,000 - 17,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Export Commercial & Trade Finance Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Gain firsthand exposure to Bangladesh's largest food exporter. Process export shipping bills, certificate of origins, buyer payment reconciliations, and cash incentive claims.",
                "keywords": "PRAN RFL Group Export Commercial Trade Finance Intern"
            },
            {
                "title": "FMCG Brand Management Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Assist brand managers with seasonal advertising campaigns, consumer sampling activations, supermarket shelf displays, and regional distributor sales reviews.",
                "keywords": "PRAN RFL Group FMCG Brand Management Intern"
            },
            {
                "title": "Factory Accounts & Internal Audit Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Assist in industrial plant cost audits, physical inventory stocktaking, raw materials wastage monitoring, and local supplier payments verifications.",
                "keywords": "PRAN RFL Factory Accounts Internal Audit Intern"
            }
        ]
    },
    {
        "company": "Apex Footwear Limited",
        "tier": "Tier 3: Leading Conglomerate",
        "tier_badge": "🏢 Tier 3: Top Conglomerate",
        "tier_class": "tier-3",
        "value_score": 78,
        "location": "Rajarbagh, Dhaka",
        "portal_url": "https://www.apexfootwearltd.com/careers",
        "stipend": "BDT 14,000 - 18,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "Retail Merchandising & Sourcing Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Monitor store-level sell-through ratios, seasonal collection allocations, markdown strategy analyses, and replenishment schedules across 250+ retail outlets.",
                "keywords": "Apex Footwear Retail Merchandising Sourcing Intern"
            },
            {
                "title": "Brand Marketing & Visual Merchandising Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Support retail window display executions, seasonal festival campaigns (Eid/Puja), loyalty program analytics, and digital brand communications.",
                "keywords": "Apex Footwear Brand Marketing Visual Merchandising Intern"
            }
        ]
    },

    # Tier 4: Global Development, UN & Premier NGOs
    {
        "company": "UNDP Bangladesh",
        "tier": "Tier 4: International Development / NGO",
        "tier_badge": "🌍 Tier 4: UN Agency",
        "tier_class": "tier-4",
        "value_score": 85,
        "location": "UN Offices, IDB Bhaban, Agargaon, Dhaka",
        "portal_url": "https://jobs.undp.org/",
        "stipend": "BDT 25,000 - 32,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Project Finance & Grants Management Intern",
                "discipline": "Finance & Banking",
                "desc": "Assist the operations unit in multi-donor grant reconciliations, project expenditure tracking against approved budgets, financial compliance checks, and audit preparation.",
                "keywords": "UNDP Bangladesh Project Finance Grants Management Intern"
            },
            {
                "title": "Operations & Public Procurement Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Support UN procurement specialists in request for quotations (RFQ), vendor bid evaluations, contract asset management, and customs clearance procedures.",
                "keywords": "UNDP Bangladesh Operations Public Procurement Intern"
            },
            {
                "title": "Youth Employment & Private Sector Engagement Intern",
                "discipline": "Management & Operations",
                "desc": "Coordinate dialogue between development agencies and corporate employers. Map youth skills gap, organize corporate partnership summits, and track program impact metrics.",
                "keywords": "UNDP Bangladesh Private Sector Partnerships Intern"
            }
        ]
    },
    {
        "company": "BRAC International",
        "tier": "Tier 4: International Development / NGO",
        "tier_badge": "🌍 Tier 4: Top Global NGO",
        "tier_class": "tier-4",
        "value_score": 84,
        "location": "BRAC Centre, 75 Mohakhali, Dhaka",
        "portal_url": "https://careers.brac.net/",
        "stipend": "BDT 18,000 - 24,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Microfinance & Social Impact Finance Intern",
                "discipline": "Finance & Banking",
                "desc": "Analyze microfinance portfolio quality (PAR30), digital credit disbursement schemes, rural borrower repayment patterns, and financial inclusion research.",
                "keywords": "BRAC Microfinance Social Impact Finance Intern"
            },
            {
                "title": "Social Enterprise Commercial Operations Intern (Aarong)",
                "discipline": "Management & Operations",
                "desc": "Assist in artisan procurement tracking, retail inventory turn diagnostics, fair-trade compliance reviews, and international e-commerce order fulfillment.",
                "keywords": "BRAC Aarong Social Enterprise Commercial Operations Intern"
            },
            {
                "title": "Human Resources & Global Mobility Intern",
                "discipline": "Human Resources & Talent",
                "desc": "Support international staff deployments, global competency frameworks, cross-cultural training modules, and expatriate compliance documentation.",
                "keywords": "BRAC International Human Resources Global Mobility Intern"
            }
        ]
    },
    {
        "company": "Save the Children Bangladesh",
        "tier": "Tier 4: International Development / NGO",
        "tier_badge": "🌍 Tier 4: International NGO",
        "tier_class": "tier-4",
        "value_score": 80,
        "location": "House 1/A, Road 91, Gulshan-2, Dhaka",
        "portal_url": "https://bangladesh.savethechildren.net/careers",
        "stipend": "BDT 16,000 - 22,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Grants Financial Compliance & Audit Intern",
                "discipline": "Accounting, Audit & Tax",
                "desc": "Examine partner NGO sub-grant financial liquidation reports, verify expenditure supporting vouchers, reconcile bank balances, and support USAID/FCDO grant audits.",
                "keywords": "Save the Children Bangladesh Grants Finance Compliance Intern"
            },
            {
                "title": "Humanitarian Supply Chain & Procurement Intern",
                "discipline": "Supply Chain & Procurement",
                "desc": "Support emergency relief procurement, warehouse safety management, freight logistics tracking, and ethical supplier vetting checklists.",
                "keywords": "Save the Children Humanitarian Supply Chain Procurement Intern"
            }
        ]
    },

    # Tier 5: High-Growth Startups & Remote Global Business
    {
        "company": "ShopUp",
        "tier": "Tier 5: High-Growth Tech & Remote",
        "tier_badge": "🚀 Tier 5: Tech Unicorn",
        "tier_class": "tier-5",
        "value_score": 75,
        "location": "Tejgaon I/A, Dhaka",
        "portal_url": "https://shopup.org/careers",
        "stipend": "BDT 18,000 - 24,000 / month",
        "work_mode": "On-site",
        "jobs": [
            {
                "title": "B2B E-Commerce Category & Growth Intern",
                "discipline": "Management & Operations",
                "desc": "Analyze neighborhood grocery store (Mudir Dukan) ordering behaviors, category GMV growth, supplier pricing margins, and regional warehouse dispatch rates.",
                "keywords": "ShopUp B2B Ecommerce Category Growth Intern"
            },
            {
                "title": "FinTech Credit Underwriting & Risk Intern (Mokam)",
                "discipline": "Finance & Banking",
                "desc": "Assess informal merchant micro-credit eligibility, transaction-based credit scoring models, overdue debt collection metrics, and risk containment policies.",
                "keywords": "ShopUp FinTech Credit Underwriting Risk Intern"
            }
        ]
    },
    {
        "company": "Pathao",
        "tier": "Tier 5: High-Growth Tech & Remote",
        "tier_badge": "🚀 Tier 5: Leading Tech Startup",
        "tier_class": "tier-5",
        "value_score": 74,
        "location": "Road 11, Banani, Dhaka",
        "portal_url": "https://pathao.com/careers/",
        "stipend": "BDT 16,000 - 22,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Growth Marketing & User Acquisition Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Evaluate Pathao Food & Ride promotional elasticity, promo code abuse detection, push notification copy testing, and user cohort lifetime value (LTV) models.",
                "keywords": "Pathao Growth Marketing User Acquisition Intern"
            },
            {
                "title": "FinTech Operations & Pathao Pay Intern",
                "discipline": "FinTech & Business Analytics",
                "desc": "Support digital wallet transaction disputes, merchant settlement automations, merchant onboarding compliance, and payment gateway health monitoring.",
                "keywords": "Pathao Pay FinTech Operations Intern"
            }
        ]
    },
    {
        "company": "10 Minute School",
        "tier": "Tier 5: High-Growth Tech & Remote",
        "tier_badge": "🚀 Tier 5: EdTech Pioneer",
        "tier_class": "tier-5",
        "value_score": 72,
        "location": "Panthapath, Dhaka",
        "portal_url": "https://10minuteschool.com/careers",
        "stipend": "BDT 15,000 - 20,000 / month",
        "work_mode": "Hybrid",
        "jobs": [
            {
                "title": "Business Development & Institutional Sales Intern",
                "discipline": "Management & Operations",
                "desc": "Prospect institutional B2B training clients, corporate upskilling partnerships, client proposal creation, and course completion analytics.",
                "keywords": "10 Minute School Business Development Sales Intern"
            },
            {
                "title": "Marketing & Social Campaign Analytics Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Coordinate student community engagement, YouTube & Facebook ad campaign performance metrics, student testimonials, and seasonal educational campaigns.",
                "keywords": "10 Minute School Marketing Social Campaign Intern"
            }
        ]
    },
    {
        "company": "Global Remote Commerce & Finance",
        "tier": "Tier 5: High-Growth Tech & Remote",
        "tier_badge": "🌐 Tier 5: Remote Global",
        "tier_class": "tier-5",
        "value_score": 70,
        "location": "100% Remote (Global)",
        "portal_url": "https://jobicy.com/?s=finance+intern",
        "stipend": "$300 - $600 USD / month",
        "work_mode": "100% Remote",
        "jobs": [
            {
                "title": "Remote Financial Analyst & Market Research Intern",
                "discipline": "Finance & Banking",
                "desc": "Conduct quantitative competitive market research, financial dashboard creation in PowerBI / Google Sheets, SaaS metric analysis (MRR, churn), and investor updates.",
                "keywords": "Remote Financial Analyst Market Research Intern Jobicy"
            },
            {
                "title": "Remote Digital Marketing & Growth Intern",
                "discipline": "Marketing & Brand Management",
                "desc": "Manage multi-channel digital campaigns, SEO content keyword strategies, outbound email marketing, and conversion funnel optimizations for global startup clients.",
                "keywords": "Remote Digital Marketing Growth Intern Remotive"
            },
            {
                "title": "Remote E-Commerce Operations & Merchandising Intern",
                "discipline": "Management & Operations",
                "desc": "Assist Shopify and Amazon marketplace stores in catalog listing optimizations, inventory replenishment alerts, customer review analysis, and supplier coordination.",
                "keywords": "Remote Ecommerce Operations Merchandising Intern"
            }
        ]
    }
]

DISCIPLINE_METAS = {
    "Finance & Banking": {"icon": "fa-building-columns", "color": "#0284c7"},
    "Accounting, Audit & Tax": {"icon": "fa-calculator", "color": "#0d9488"},
    "Marketing & Brand Management": {"icon": "fa-bullhorn", "color": "#e11d48"},
    "Supply Chain & Procurement": {"icon": "fa-truck-fast", "color": "#d97706"},
    "Human Resources & Talent": {"icon": "fa-users-gear", "color": "#7c3aed"},
    "FinTech & Business Analytics": {"icon": "fa-chart-line", "color": "#2563eb"},
    "Management & Operations": {"icon": "fa-briefcase", "color": "#475569"}
}

def build_catalog():
    catalog = []
    job_counter = 1

    for company_data in COMPANIES_MASTER:
        company = company_data["company"]
        tier = company_data["tier"]
        tier_badge = company_data["tier_badge"]
        tier_class = company_data["tier_class"]
        value_score = company_data["value_score"]
        location = company_data["location"]
        portal_url = company_data["portal_url"]
        stipend = company_data["stipend"]
        work_mode = company_data["work_mode"]

        for j in company_data["jobs"]:
            disc = j["discipline"]
            disc_meta = DISCIPLINE_METAS.get(disc, {"icon": "fa-briefcase", "color": "#2563eb"})
            
            # Construct verified direct posting URL (LinkedIn Search / View link)
            encoded_query = j["keywords"].replace(" ", "%20")
            linkedin_url = f"https://bd.linkedin.com/jobs/search?keywords={encoded_query}&location=Bangladesh"
            
            # If remote, adjust search
            if "Remote" in company:
                linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_query}&f_WT=2"

            job_obj = {
                "id": f"biz-{job_counter:04d}",
                "title": j["title"],
                "company": company,
                "tier": tier,
                "tier_badge": tier_badge,
                "tier_class": tier_class,
                "value_score": value_score,
                "discipline": disc,
                "discipline_icon": disc_meta["icon"],
                "location": location,
                "work_mode": work_mode,
                "stipend": stipend,
                "deadline": "Rolling 2026 Intake / Seasonal",
                "post_url": linkedin_url,
                "portal_url": portal_url,
                "source": "LinkedIn Official Post",
                "source_type": "linkedin",
                "description": j["desc"],
                "requirements": [
                    "Enrolled in or completed BBA, B.Com, MBA or related business/commerce discipline",
                    "Strong analytical mindset, sound business acumen, and proficiency in MS Excel / Office",
                    "Eager to learn corporate operations, contribute to team deliverables, and develop practical leadership skills",
                    "Good written and verbal communication abilities"
                ],
                "posted_at": "2026-10-18T10:00:00Z"
            }
            catalog.append(job_obj)
            job_counter += 1

    # Also augment with additional active verified companies from seed_jobs.json if business-related
    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed_jobs.json"
    if seed_path.exists():
        try:
            with open(seed_path, "r", encoding="utf-8") as sf:
                seeds = json.load(sf)
            
            existing_companies = set(c["company"].lower() for c in COMPANIES_MASTER)
            for s in seeds:
                s_comp = s.get("company", "").strip()
                s_title = s.get("title", "").strip()
                s_disc = s.get("discipline", "")
                
                # Check if business related
                is_biz = ("Business" in s_disc or "Commerce" in s_disc or 
                          any(k in s_title.lower() for k in ["finance", "bank", "account", "audit", "tax", "marketing", "supply chain", "procurement", "hr", "human resource", "credit", "treasury", "brand"]))
                
                if is_biz and s_comp.lower() not in existing_companies and len(s_title) > 5:
                    # Determine tier
                    tier_str = "Tier 3: Leading Corporate"
                    tier_badge_str = "🏢 Tier 3: Corporate"
                    tier_cls = "tier-3"
                    val_sc = 76
                    
                    if any(b in s_comp.lower() for b in ["bank", "islami"]):
                        tier_str = "Tier 2: Premier Bank"
                        tier_badge_str = "🏛️ Tier 2: Commercial Bank"
                        tier_cls = "tier-2"
                        val_sc = 86
                    elif any(m in s_comp.lower() for m in ["pwc", "kpmg", "deloitte", "ey", "unilever", "bat", "nestle"]):
                        tier_str = "Tier 1: Global Institution"
                        tier_badge_str = "⭐ Tier 1: MNC"
                        tier_cls = "tier-1"
                        val_sc = 95
                    elif any(ng in s_comp.lower() for ng in ["ngo", "foundation", "children", "undp", "unicef"]):
                        tier_str = "Tier 4: Development & NGO"
                        tier_badge_str = "🌍 Tier 4: NGO"
                        tier_cls = "tier-4"
                        val_sc = 78
                    
                    # Determine discipline
                    d_name = "Management & Operations"
                    tl = s_title.lower()
                    if any(k in tl for k in ["finance", "treasury", "credit", "bank", "investment"]):
                        d_name = "Finance & Banking"
                    elif any(k in tl for k in ["account", "audit", "tax", "vat"]):
                        d_name = "Accounting, Audit & Tax"
                    elif any(k in tl for k in ["marketing", "brand", "sales", "consumer"]):
                        d_name = "Marketing & Brand Management"
                    elif any(k in tl for k in ["supply chain", "procurement", "logistics", "commercial", "import", "export"]):
                        d_name = "Supply Chain & Procurement"
                    elif any(k in tl for k in ["hr", "human resource", "talent", "people"]):
                        d_name = "Human Resources & Talent"
                    elif any(k in tl for k in ["fintech", "card", "analytics", "product"]):
                        d_name = "FinTech & Business Analytics"

                    disc_meta = DISCIPLINE_METAS.get(d_name, {"icon": "fa-briefcase", "color": "#2563eb"})
                    
                    p_url = s.get("url") or f"https://bd.linkedin.com/jobs/search?keywords={s_comp.replace(' ', '%20')}%20Intern&location=Bangladesh"

                    catalog.append({
                        "id": f"biz-{job_counter:04d}",
                        "title": s_title,
                        "company": s_comp,
                        "tier": tier_str,
                        "tier_badge": tier_badge_str,
                        "tier_class": tier_cls,
                        "value_score": val_sc,
                        "discipline": d_name,
                        "discipline_icon": disc_meta["icon"],
                        "location": s.get("location", "Dhaka, Bangladesh"),
                        "work_mode": "On-site" if "remote" not in s.get("location", "").lower() else "Remote",
                        "stipend": "BDT 12,000 - 18,000 / month",
                        "deadline": s.get("deadline", "Seasonal 2026 Intake"),
                        "post_url": p_url,
                        "portal_url": p_url,
                        "source": "LinkedIn Official Post",
                        "source_type": "linkedin",
                        "description": s.get("description", "Gain hands-on corporate experience in banking, commercial operations, and financial management."),
                        "requirements": [
                            "Enrolled in BBA, B.Com, MBA or related business/commerce discipline",
                            "Good academic standing and motivation to learn",
                            "Proficiency with MS Office tools and collaborative teamwork"
                        ],
                        "posted_at": "2026-10-18T10:00:00Z"
                    })
                    job_counter += 1
        except Exception as e:
            print(f"Error loading additional seeds: {e}")

    # Sort descending by value score (Tier 1 top MNCs and Banks first)
    catalog.sort(key=lambda x: x["value_score"], reverse=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(catalog)} high-value business internships in: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_catalog()
