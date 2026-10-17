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

