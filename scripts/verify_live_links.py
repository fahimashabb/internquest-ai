import json
import re
import requests
import time

with open("data/business_internships.json", encoding="utf-8") as f:
    jobs = json.load(f)

pattern = re.compile(r"\b(intern|interns|internship|internships|placement|freshstart)\b", re.IGNORECASE)
matched = [j for j in jobs if pattern.search(j["title"])]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

print(f"Testing HTTP status of {len(matched)} matched jobs...")
ok_count = 0
fail_count = 0

for i, j in enumerate(matched):
    url = j["post_url"]
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            final_u = r.url.lower()
            if "404" in final_u or "page-not-found" in final_u or "error" in final_u:
                print(f"❌ {i+1}. [Soft 404] {j['title']} -> {url}")
                fail_count += 1
            else:
                ok_count += 1
        else:
            print(f"❌ {i+1}. [{r.status_code}] {j['title']} -> {url}")
            fail_count += 1
    except Exception as e:
        print(f"❌ {i+1}. [Exception {e}] {j['title']} -> {url}")
        fail_count += 1
    time.sleep(0.05)

print(f"\nResults: {ok_count} OK (200), {fail_count} Failed.")
