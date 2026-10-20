"""Gemini-powered Resume Matcher, Evaluator, and Cover Letter Generator."""
import json
import re
from typing import Optional, Dict, Any
from src.config import AppSettings, load_settings
from src.profile import CandidateProfile
from src.scrapers.base import JobListing

# Gemini prompt template for evaluation and tailoring
EVAL_PROMPT = """
You are an expert career advisor and recruitment analyst assisting an ambitious Finance & Banking student named Fahim Ashab.

Candidate Profile & Resume Data:
Name: {candidate_name}
Degree: {candidate_degree} ({candidate_institution})
Location: {candidate_location}
Email: {candidate_email} | Phone: {candidate_phone}
Key Competencies: Advanced MS Excel (XLOOKUP, PivotTables, Financial Modeling), Operating Budgeting, Working Capital, Cross-Functional Leadership, Event Logistics.
Experience & Achievements:
- Youth Fellow at Amra Notun Network (ANN) - CAP Project on youth leadership & economic empowerment.
- Lead Program Coordinator for Career Expo & Job Fair 2026 (BRAC & JUST Career Club) - managed logistics connecting corporate recruiters with candidates.
- Program Organizer & Participant - Prime Bank & JUST Banking Seminar (retail banking & financial inclusion).
- Program Organizer - Capital Market Workshop (BSEC & BASM - Bangladesh Securities & Exchange Commission).
- Program Convener - Corporate Excel Workshop for 100+ business undergraduates.
- Operations & Marketing Lead - Agribusiness venture managing budgeting & procurement.

Job Opportunity to Evaluate:
Title: {job_title}
Company: {job_company}
Location: {job_location}
Source: {job_source}
URL: {job_url}
Description:
{job_description}

Instructions:
1. Analyze how well this opportunity matches Fahim Ashab's background (Finance & Banking, Financial Analysis, Operations, FinTech, Banking, Budgeting, Excel).
2. Assign a match score from 0 to 100:
   - 80-100: High match (Finance/Banking/Operations Intern, Trainee, Analyst role).
   - 60-79: Moderate match (General Business, Management Trainee, Project Assistant).
   - 0-59: Low or irrelevant match (Senior executive, unrelated engineering, senior legal, etc.).
3. Write a concise 2-sentence rationale for the score.
4. If the job is an internship or entry/junior role (or score >= 60), generate:
   - A compelling email subject line for cold outreach or direct application.
   - A highly personalized, 3-paragraph professional cold email / cover letter. Specifically cite relevant real experiences from Fahim's resume (e.g. BRAC Career Expo coordination, Prime Bank seminar, BSEC Capital Market workshop, or advanced Excel modeling) that match this company's needs.
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

        prompt = EVAL_PROMPT.format(
            candidate_name=prof["name"],
            candidate_degree=prof["degree"],
            candidate_institution=prof["institution"],
            candidate_location=prof["location"],
            candidate_email=prof["email"],
            candidate_phone=prof["phone"],
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
        text = f"{job.title} {job.description}".lower()
        score = 40

        # Keywords scoring
        if any(k in job.title.lower() for k in ["intern", "internship", "trainee", "fellow"]):
            score += 25
            job.is_internship = True

        finance_matches = sum(1 for k in ["finance", "banking", "financial", "analyst", "accounts", "budget", "valuation"] if k in text)
        score += min(20, finance_matches * 5)

        ops_matches = sum(1 for k in ["operations", "excel", "modeling", "logistics", "fintech"] if k in text)
        score += min(15, ops_matches * 5)

        # Penalize senior roles
        if any(k in job.title.lower() for k in ["senior", "lead", "director", "head of", "principal", "vp"]):
            score = max(20, score - 30)

        job.match_score = min(98, max(10, score))
        job.match_rationale = f"Evaluated via profile heuristics: Found finance/ops overlap and level alignment ({job.match_score}% match)."

        # Generate cover letter draft
        candidate = self.settings.candidate
        job.tailored_email_subject = f"Application for {job.title} - {candidate.name} ({candidate.degree.split('(')[0].strip()})"
        job.tailored_cover_letter = f"""Dear Hiring Team at {job.company},

I am writing to express my strong interest in the {job.title} position. As an undergraduate pursuing a {candidate.degree} at {candidate.institution}, I have developed rigorous analytical capabilities in financial modeling, corporate budgeting, and operational planning.

Through leadership experiences such as coordinating logistics for the BRAC & JUST Career Expo, organizing banking seminars with Prime Bank, and training in capital markets with BSEC/BASM, I have cultivated a practical understanding of financial ecosystems and cross-functional execution. My technical toolkit includes advanced MS Excel (nested lookups, financial statements, dynamic modeling) and quantitative problem-solving.

I am eager to contribute this combination of financial discipline and operational agility to {job.company}. My resume is attached for your review, and I would welcome the opportunity to discuss how I can add immediate value to your team.

Thank you for your time and consideration.

Warm regards,
{candidate.name}
{candidate.phone} | {candidate.email}
{candidate.linkedin}
"""
        return job
