import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

urls = [
    "https://bd.linkedin.com/jobs/view/finance-intern-at-grameen-healthtech-limited-4458184396",
    "https://bd.linkedin.com/jobs/view/intern-learning-development-at-next-ventures-4477975690",
    "https://bd.linkedin.com/jobs/view/intern-finance-accounts-at-nextjobz-4453864224",
    "https://bd.linkedin.com/jobs/view/research-intern-at-trace-consulting-4454019681",
    "https://bd.linkedin.com/jobs/view/internship-program-at-digibox-4457459901",
    "https://bd.linkedin.com/jobs/view/intern-cost-budgeting-at-nextjobz-4453445421",
    "https://bd.linkedin.com/jobs/view/intern-finance-credit-control-department-at-nextjobz-4467340623",
    "https://bd.linkedin.com/jobs/view/intern-credit-management-dhaka-at-nextjobz-4476047306",
    "https://bd.linkedin.com/jobs/view/intern-hr-operations-bangladesh-at-commure-4475885250",
    "https://bd.linkedin.com/jobs/view/seo-intern-%E2%80%93-sylhet-at-sj-innovation-llc-4456285288"
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=8, allow_redirects=True)
        print(f"Status {r.status_code}: {u}")
        if r.status_code == 200:
            print("  Final URL:", r.url)
    except Exception as e:
        print(f"Error {e}: {u}")
