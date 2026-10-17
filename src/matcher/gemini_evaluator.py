"""Gemini-powered Resume Matcher, Evaluator, and Cover Letter Generator."""
import json
import re
from typing import Optional, Dict, Any
from src.config import AppSettings, load_settings
from src.profile import CandidateProfile
from src.scrapers.base import JobListing

# Gemini prompt template for universal evaluation and tailoring
EVAL_PROMPT = """
You are an expert career advisor and recruitment analyst evaluating internship and entry-level opportunities for a candidate.

Candidate Profile:
Name: {candidate_name}
Degree / Field: {candidate_degree} ({candidate_institution})
Location: {candidate_location}
Email: {candidate_email} | Phone: {candidate_phone}
Key Skills / Competencies: {candidate_skills}
Target Domains: {candidate_domains}

Candidate Resume Details / Experience:
{resume_snippet}

Job Opportunity to Evaluate:
Title: {job_title}
Company: {job_company}
Location: {job_location}
Source: {job_source}
URL: {job_url}
Description:
{job_description}

Instructions:
1. Analyze how well this opportunity matches the candidate's degree, skills, domain interests, and career stage.
2. Assign a match score from 0 to 100:
   - 80-100: High match (strongly aligned domain, skills match, intern/trainee/associate level).
   - 60-79: Moderate match (transferable skills, adjacent business/tech area).
   - 0-59: Low or irrelevant match (senior executive roles requiring 5+ years experience, unrelated fields).
3. Write a concise 2-sentence rationale for the score.
4. If the job is an internship or entry/junior role (or score >= 50), generate:
   - A compelling email subject line for cold outreach or direct application.
   - A highly personalized, 3-paragraph professional cold email / cover letter. Specifically cite relevant real experiences and competencies from the candidate's resume that match this company's needs.
5. Identify the best application channel: "email" if an email is present in the posting or description, otherwise "web". If an email is mentioned in the description, extract it.

Return ONLY a valid JSON object with the following schema:
{{
  "match_score": <int between 0 and 100>,
  "is_internship": <bool>,
  "match_rationale": "<concise explanation>",
  "tailored_email_subject": "<subject line>",
  "tailored_cover_letter": "<personalized email / cover letter text>",
  "application_channel": "<email or web>",
  "extracted_email": "<email or null>"
}}
"""


class GeminiEvaluator:
    def __init__(self, settings: Optional[AppSettings] = None, profile: Optional[CandidateProfile] = None):
        self.settings = settings or load_settings()
        self.profile = profile or CandidateProfile(self.settings)
        self._client = None
        self._init_client()

    def _init_client(self):
        api_key = self.settings.gemini_api_key
        if api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[GeminiEvaluator] Failed to initialize genai Client: {e}")

    def evaluate_job(self, job: JobListing) -> JobListing:
        """Score job listing, generate personalized outreach pitch, and update job metadata."""
        if self._client:
            return self._evaluate_with_gemini(job)
        else:
            return self._evaluate_with_heuristics(job)

    def _evaluate_with_gemini(self, job: JobListing) -> JobListing:
        from google.genai import types
        prof = self.profile.get_structured_profile()

        resume_snippet = prof.get("resume_text", "")[:2500]
        skills_str = ", ".join(prof.get("skills", [])) or "Business, Operations, Communication"
        domains_str = ", ".join(prof.get("target_domains", [])) or "All"

        prompt = EVAL_PROMPT.format(
            candidate_name=prof["name"],
            candidate_degree=prof["degree"],
            candidate_institution=prof["institution"],
            candidate_location=prof["location"],
            candidate_email=prof["email"],
            candidate_phone=prof["phone"],
            candidate_skills=skills_str,
            candidate_domains=domains_str,
            resume_snippet=resume_snippet,
            job_title=job.title,
            job_company=job.company,
            job_location=job.location,
            job_source=job.source,
            job_url=job.url,
            job_description=job.description[:3000]
        )

        try:
            response = self._client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip()
            # Clean possible markdown blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            data = json.loads(raw_text.strip())
            job.match_score = int(data.get("match_score", 50))
            job.is_internship = bool(data.get("is_internship", job.is_internship))
            job.match_rationale = data.get("match_rationale", "")
            job.tailored_email_subject = data.get("tailored_email_subject", "")
            job.tailored_cover_letter = data.get("tailored_cover_letter", "")
            
            chan = data.get("application_channel", job.application_channel).lower()
            if chan in ("email", "web"):
                job.application_channel = chan
                
            extracted_email = data.get("extracted_email")
            if extracted_email and not job.contact_email:
                job.contact_email = extracted_email
                job.application_channel = "email"

            return job
        except Exception as e:
            print(f"[GeminiEvaluator] Gemini evaluation failed for '{job.title}': {e}. Using heuristic fallback.")
            return self._evaluate_with_heuristics(job)

    def _evaluate_with_heuristics(self, job: JobListing) -> JobListing:
        """Deterministic rule-based scoring and template generator when API key is not present."""
        prof = self.profile.get_structured_profile()
        candidate_name = prof.get("name", "Candidate")
        candidate_degree = prof.get("degree", "Undergraduate")
        candidate_institution = prof.get("institution", "University")
        skills = [s.lower() for s in prof.get("skills", [])]

        text = f"{job.title} {job.description}".lower()
        score = 40

        # Keywords scoring
        if any(k in job.title.lower() for k in ["intern", "internship", "trainee", "fellow", "junior", "assistant"]):
            score += 25
            job.is_internship = True

        # Candidate skills matching
        matched_skills = [s for s in skills if s in text]
        score += min(30, len(matched_skills) * 8)

        # Penalize senior roles
        if any(k in job.title.lower() for k in ["senior", "lead", "director", "head of", "principal", "vp"]):
            score = max(15, score - 35)

        job.match_score = min(98, max(10, score))
        job.match_rationale = f"Evaluated via profile skills: matched {len(matched_skills)} core competencies ({', '.join(matched_skills[:3]) or 'foundational skills'})."

        # Generate cover letter draft
        job.tailored_email_subject = f"Application for {job.title} - {candidate_name} ({candidate_degree})"
        skills_summary = ", ".join(prof.get("skills", [])[:4]) or "analytical and communication skills"
        job.tailored_cover_letter = f"""Dear Hiring Team at {job.company},

I am writing to express my enthusiastic interest in the {job.title} position. As a {candidate_degree} student at {candidate_institution}, I have developed hands-on capabilities across {skills_summary}.

My background and coursework have equipped me with practical problem-solving experience and the agility to adapt quickly to dynamic corporate environments. I am impressed by {job.company}'s impactful work and would love the opportunity to contribute my dedication and technical toolkit to your ongoing initiatives.

My resume is attached for your review, and I would welcome the opportunity to discuss how I can add immediate value as an intern.

Thank you very much for your time and consideration.

Warm regards,
{candidate_name}
{prof.get('phone', '')} | {prof.get('email', '')}
{prof.get('linkedin', '')}
"""
        return job

    def generate_custom_cover_letter(
        self,
        job: JobListing,
        candidate_profile: Optional[Dict[str, Any]] = None,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """Generate a bespoke, formal 4-paragraph cover letter and email pitch tailored to this opportunity."""
        prof = candidate_profile or self.profile.get_structured_profile()
        c_name = prof.get("name", "Candidate")
        c_degree = prof.get("degree", "Undergraduate Student")
        c_inst = prof.get("institution", "University")
        c_email = prof.get("email", "")
        c_phone = prof.get("phone", "")
        c_li = prof.get("linkedin", "")
        c_skills = prof.get("skills", [])
        skills_str = ", ".join(c_skills[:5]) or "critical thinking, analytics, and cross-functional communication"

        # Try with Gemini if available
        if self._client:
            try:
                from google.genai import types
                cover_prompt = f"""
Write a high-caliber, tailored formal cover letter for an internship applicant.

Applicant Information:
Name: {c_name}
Degree & Major: {c_degree}
Institution: {c_inst}
Contact: {c_email} | {c_phone}
Skills: {skills_str}
Strengths: {', '.join(prof.get('strengths', []))}

Target Company & Position:
Role: {job.title}
Company: {job.company}
Location: {job.location}
Job Details: {job.description[:1500]}

Format Requirements:
1. Include formal applicant header and date.
2. Address to 'Hiring Team / Internship Selection Committee at {job.company}'.
3. Four clear, compelling paragraphs:
   - Paragraph 1: Enthusiastic opening with specific mention of {job.company} and the role.
   - Paragraph 2: Core competencies, projects, and academic coursework that prepare the candidate for this exact role.
   - Paragraph 3: Passion for {job.company}'s market impact and why the candidate is eager to learn and contribute.
   - Paragraph 4: Confident sign-off requesting an interview.
4. Professional sign-off.

Return ONLY a JSON object:
{{
  "subject": "Application for {job.title} - {c_name}",
  "formal_letter": "<Full formatted text of the letter>",
  "email_pitch": "<Concise 3-paragraph executive cold email pitch>"
}}
"""
                resp = self._client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=cover_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                res_data = json.loads(resp.text.strip())
                return {
                    "subject": res_data.get("subject", f"Application for {job.title} - {c_name}"),
                    "formal_letter": res_data.get("formal_letter", ""),
                    "email_pitch": res_data.get("email_pitch", "")
                }
            except Exception as e:
                print(f"[CoverLetter Generator] Gemini generation fallback: {e}")

        # Deterministic High-Quality Heuristic Cover Letter
        from datetime import date
        today_str = date.today().strftime("%B %d, %Y")
        
        formal_letter = f"""{c_name}
{c_email} | {c_phone}
{prof.get('location', 'Dhaka, Bangladesh')}
{c_li}

{today_str}

To:
The Internship Selection Committee / Hiring Team
{job.company}
{job.location}

Subject: Formal Application for {job.title}

Dear Hiring Team at {job.company},

I am writing to express my strong enthusiasm and formal application for the {job.title} opportunity at {job.company}. As a dedicated student pursuing {c_degree} at {c_inst}, I have actively followed {job.company}'s impactful work in the sector. I am keen to channel my academic rigor and practical skillset into supporting your team's ongoing operational and strategic initiatives.

Throughout my academic coursework and hands-on projects, I have developed solid foundational competencies in {skills_str}. I take pride in my analytical discipline, capacity for fast learning, and ability to translate project briefs into actionable outcomes. Whether collaborating cross-functionally or executing self-directed assignments, I ensure accuracy, proactive communication, and high attention to detail.

What particularly draws me to {job.company} is your commitment to excellence, innovation, and cultivating emerging talent. I am eager to contribute fresh perspectives, absorb practical industry mentorship, and deliver tangible value across day-to-day deliverables.

Thank you very much for reviewing my credentials. My complete resume is attached for your consideration, and I welcome the opportunity to discuss my candidacy during an interview at your earliest convenience.

Sincerely,

{c_name}
{c_email} | {c_phone}
"""

        email_pitch = f"""Subject: Application for {job.title} - {c_name}

Dear Hiring Team at {job.company},

I hope this email finds you well. I am reaching out to formally apply for the {job.title} position at {job.company}. As a {c_degree} candidate at {c_inst}, I have built strong hands-on capabilities in {skills_str}.

I am passionate about {job.company}'s work and confident that my strong work ethic, problem-solving mindset, and dedication will make me a productive addition to your team.

My resume is attached for your review. I would welcome a brief conversation to discuss how I can contribute to {job.company} this term.

Warm regards,
{c_name}
{c_email} | {c_phone}
{c_li}
"""

        return {
            "subject": f"Application for {job.title} - {c_name}",
            "formal_letter": formal_letter.strip(),
            "email_pitch": email_pitch.strip()
        }


def generate_custom_cover_letter(
    job: JobListing,
    candidate_profile: Optional[Dict[str, Any]] = None,
    tone: str = "professional",
    settings: Optional[AppSettings] = None
) -> Dict[str, str]:
    """Top-level convenience function to generate a tailored cover letter and email pitch."""
    evaluator = GeminiEvaluator(settings=settings)
    return evaluator.generate_custom_cover_letter(job, candidate_profile=candidate_profile, tone=tone)


