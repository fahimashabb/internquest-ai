"""
Comprehensive Bangladesh Company & Institution Scraper.
Covers: All major banks, MNCs, NGOs, FinTechs, Conglomerates, Pharma,
Telecom, FMCG, Media, Consulting, and promising growth companies in Bangladesh.
"""
import time
import urllib.parse
import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper, JobListing

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

BD_COMPANY_SEARCHES = [
    # ── BANKS & FINANCIAL INSTITUTIONS ──
    "BRAC Bank internship Bangladesh",
    "Dutch Bangla Bank DBBL internship Bangladesh",
    "Prime Bank internship Bangladesh",
    "Standard Chartered Bangladesh internship",
    "HSBC Bangladesh internship",
    "Eastern Bank EBL internship Bangladesh",
    "City Bank Bangladesh internship",
    "Mutual Trust Bank internship Bangladesh",
    "Bank Asia internship Bangladesh",
    "Jamuna Bank internship Bangladesh",
    "Islami Bank Bangladesh internship",
    "Shahjalal Islami Bank internship",
    "One Bank internship Bangladesh",
    "Southeast Bank internship Bangladesh",
    "Social Islami Bank SIBL internship",
    "Mercantile Bank internship Bangladesh",
    "Dhaka Bank internship Bangladesh",
    "Trust Bank internship Bangladesh",
    "IFIC Bank internship Bangladesh",
    "AB Bank internship Bangladesh",
    "United Commercial Bank UCBL internship",
    "Midland Bank internship Bangladesh",
    "Modhumoti Bank internship Bangladesh",
    "Bangladesh Development Bank BDBL internship",
    "Grameen Bank internship Bangladesh",
    "NRB Bank internship Bangladesh",
    "Pubali Bank internship Bangladesh",
    "Rupali Bank internship Bangladesh",
    "Sonali Bank internship Bangladesh",
    # ── FINTECH & MOBILE BANKING ──
    "bKash internship Bangladesh",
    "Nagad internship Bangladesh",
    "iPay internship Bangladesh",
    "ShurjoPay internship Bangladesh",
    "SureCash internship Bangladesh",
    "Pathao internship Bangladesh",
    "Shohoz internship Bangladesh",
    "Chaldal internship Bangladesh",
    "ShopUp internship Bangladesh",
    "10 Minute School internship Bangladesh",
    "Shikho internship Bangladesh",
    "Maya Apps internship Bangladesh",
    "Truck Lagbe internship Bangladesh",
    "Sheba XYZ internship Bangladesh",
    # ── TELECOM ──
    "Grameenphone GP internship Bangladesh",
    "Robi Axiata internship Bangladesh",
    "Banglalink internship Bangladesh",
    "Teletalk internship Bangladesh",
    "Samsung Bangladesh internship",
    "Huawei Bangladesh internship",
    "Ericsson Bangladesh internship",
    "Nokia Bangladesh internship",
    # ── MNCs & FMCG ──
    "Unilever Bangladesh internship",
    "Nestle Bangladesh internship",
    "Marico Bangladesh internship",
    "British American Tobacco BAT Bangladesh internship",
    "Berger Paints Bangladesh internship",
    "Reckitt Bangladesh internship",
    "Johnson Johnson Bangladesh internship",
    # ── CONGLOMERATES ──
    "PRAN RFL Group internship Bangladesh",
    "Square Group internship Bangladesh",
    "ACI Limited internship Bangladesh",
    "Transcom Group internship Bangladesh",
    "Akij Group internship Bangladesh",
    "Bashundhara Group internship Bangladesh",
    "Meghna Group internship Bangladesh",
    "Partex Group internship Bangladesh",
    "PHP Group internship Bangladesh",
    "Ha-Meem Group internship Bangladesh",
    "DBL Group internship Bangladesh",
    "Beximco Group internship Bangladesh",
    "Ananta Group internship Bangladesh",
    "Walton Group internship Bangladesh",
    "Singer Bangladesh internship",
    "Bata Bangladesh internship",
    "Nitol Niloy Group internship Bangladesh",
    "Abul Khair Group internship Bangladesh",
    "City Group Bangladesh internship",
    "Otobi internship Bangladesh",
    # ── PHARMA ──
    "Renata Limited internship Bangladesh",
    "Incepta Pharmaceuticals internship Bangladesh",
    "Square Pharmaceuticals internship Bangladesh",
    "Beximco Pharmaceuticals internship Bangladesh",
    "Drug International internship Bangladesh",
    "Opsonin Pharma internship Bangladesh",
    # ── ENERGY & INDUSTRY ──
    "Chevron Bangladesh internship",
    "Total Energies Bangladesh internship",
    "Lafarge Holcim Bangladesh internship",
    "Heidelberg Cement Bangladesh internship",
    "Summit Power internship Bangladesh",
    # ── NGOs & DEVELOPMENT ──
    "BRAC internship Bangladesh",
    "CARE Bangladesh internship",
    "Save the Children Bangladesh internship",
    "ActionAid Bangladesh internship",
    "World Food Programme WFP Bangladesh internship",
    "UNICEF Bangladesh internship",
    "UNDP Bangladesh internship",
    "World Bank Bangladesh internship",
    "Asian Development Bank ADB Bangladesh internship",
    "IFC Bangladesh internship",
    "Oxfam Bangladesh internship",
    "Plan International Bangladesh internship",
    "World Vision Bangladesh internship",
    "Helen Keller International Bangladesh internship",
    "Population Services PSI Bangladesh internship",
    "Aga Khan Foundation Bangladesh internship",
    "icddr,b internship Bangladesh",
    "BIDS internship Bangladesh",
    # ── PROFESSIONAL SERVICES ──
    "Deloitte Bangladesh internship",
    "PwC Bangladesh internship",
    "KPMG Bangladesh internship",
    "EY Ernst Young Bangladesh internship",
    "Grant Thornton Bangladesh internship",
    "Boston Consulting Group BCG Bangladesh",
    # ── MEDIA & ADVERTISING ──
    "Asiatic JWT Bangladesh internship",
    "Grey Dhaka internship Bangladesh",
    "Magnito Digital internship Bangladesh",
    # ── IT & SOFTWARE ──
    "SSL Wireless internship Bangladesh",
    "BJIT internship Bangladesh",
    "Brain Station 23 internship Bangladesh",
    "Nascenia internship Bangladesh",
    "TigerIT internship Bangladesh",
    "Leads Corporation internship Bangladesh",
    # ── SCIENCE, TECH & ENGINEERING ──
    "software engineer intern Bangladesh 2026",
    "python developer intern Dhaka Bangladesh",
    "data science intern Bangladesh 2026",
    "web development intern Dhaka",
    "IT intern Bangladesh",
    "electrical engineer intern Bangladesh",
    "civil engineering intern Bangladesh",
    "mechanical engineer intern Bangladesh",
    "biotechnology intern Bangladesh",
    "microbiology intern Dhaka Bangladesh",
    "pharmacy intern Dhaka Bangladesh",
    "AI machine learning intern Bangladesh",
    # ── ARTS, HUMANITIES, DESIGN & LAW ──
    "content writer intern Bangladesh 2026",
    "graphic design intern Dhaka Bangladesh",
    "UI UX design intern Bangladesh",
    "digital communications intern Dhaka",
    "journalism media intern Bangladesh",
    "legal intern law intern Dhaka Bangladesh",
    "public relations PR intern Bangladesh",
    "social research intern Dhaka",
    "video editor creative intern Bangladesh",
    # ── COMMERCE & BUSINESS ──
    "finance intern Bangladesh 2026",
    "financial analyst intern Dhaka Bangladesh",
    "business operations intern Bangladesh",
    "banking trainee Bangladesh 2026",
    "management trainee intern Bangladesh",
    "corporate finance intern Bangladesh",
    "accounts intern Dhaka Bangladesh",
    "marketing intern Dhaka Bangladesh",
    "HR human resources intern Bangladesh",
    "supply chain intern Bangladesh",
    "MIS intern Bangladesh operations",
    "cost budgeting intern Bangladesh",
    "credit analyst intern Bangladesh",
    "risk intern Bangladesh",
    "treasury intern Bangladesh",
    "audit intern Bangladesh",
    "compliance intern Bangladesh",
    "microfinance intern Bangladesh",
    "SME banking intern Bangladesh",
    "retail banking intern Bangladesh",
    "trade finance intern Bangladesh",
]


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    if match:
        found = match.group(0).lower().strip(".")
        if not any(found.endswith(x) for x in [".png", ".jpg", ".jpeg", ".svg", ".webp"]):
            return found
    return None


class BangladeshCompanyScraper(BaseScraper):
    """Comprehensive scraper: 100+ Bangladesh companies, banks, NGOs via LinkedIn."""
    name = "BangladeshCompanyScraper"
    BASE_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def search(self, keywords: List[str], locations: List[str], max_results: int = 150) -> List[JobListing]:
        results: List[JobListing] = []
        seen_urls = set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        for search_query in BD_COMPANY_SEARCHES:
            if len(results) >= max_results:
                break
            try:
                params = {"keywords": search_query, "location": "Bangladesh", "start": 0}
                resp = requests.get(self.BASE_API, params=params, headers=headers, timeout=12)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.find_all("div", class_="base-card")

                for card in cards:
                    if len(results) >= max_results:
                        break

                    title_elem = card.find("h3", class_="base-search-card__title")
                    comp_elem = card.find("h4", class_="base-search-card__subtitle")
                    loc_elem = card.find("span", class_="job-search-card__location")
                    link_elem = card.find("a", class_="base-card__full-link")
                    time_elem = card.find("time")

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    company = comp_elem.get_text(strip=True) if comp_elem else "Unknown"
                    location_str = loc_elem.get_text(strip=True) if loc_elem else "Bangladesh"
                    clean_link = link_elem.get("href", "").split("?")[0]
                    posted_date = time_elem.get_text(strip=True) if time_elem else "Recent"

                    if clean_link in seen_urls:
                        continue
                    seen_urls.add(clean_link)

                    # Fetch job description
                    desc = f"{title} at {company} in {location_str}."
                    contact_email = None
                    try:
                        detail_resp = requests.get(clean_link, headers=headers, timeout=8)
                        if detail_resp.status_code == 200:
                            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                            desc_elem = detail_soup.find("div", class_="show-more-less-html__markup")
                            if desc_elem:
                                desc = desc_elem.get_text(separator=" ", strip=True)[:2500]
                                contact_email = extract_email(desc)
                    except Exception:
                        pass

                    combined = f"{title} {desc}".lower()
                    is_intern = any(k in combined for k in [
                        "intern", "internship", "trainee", "entry", "fellow",
                        "junior", "associate", "assistant", "placement", "attachment", "apprentice"
                    ])

                    listing = JobListing(
                        title=title,
                        company=company,
                        location=location_str,
                        url=clean_link,
                        description=desc,
                        source=self.name,
                        contact_email=contact_email,
                        posted_date=posted_date,
                        is_internship=is_intern,
                        application_channel="email" if contact_email else "web"
                    )
                    results.append(listing)
                    time.sleep(0.25)

            except Exception as e:
                print(f"[{self.name}] Error on '{search_query}': {e}")

        return results
