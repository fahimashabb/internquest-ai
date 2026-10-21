import json
import subprocess

content_prev = subprocess.check_output(['git', 'show', 'HEAD~1:data/business_internships.json'], encoding='utf-8')
jobs_prev = json.loads(content_prev)

with open('data/business_internships.json', encoding='utf-8') as f:
    jobs_now = json.load(f)

urls_now = {j['post_url'] for j in jobs_now}
print(f"Previous count: {len(jobs_prev)}, Now: {len(jobs_now)}")
print("Jobs that were removed / not in current:")
for j in jobs_prev:
    if j['post_url'] not in urls_now:
        print(" -", j['title'], "|", j['company'], "|", j['post_url'])
