"""Configuration manager for Internship Hunter."""
from pathlib import Path
from typing import List, Optional
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.yaml"
ENV_FILE = BASE_DIR / ".env"

# Load .env
load_dotenv(dotenv_path=ENV_FILE)


class CandidateConfig(BaseModel):
    name: str = "Fahim Ashab"
    email: str = "fahimashabofficial@gmail.com"
    phone: str = "+880 1832-383642"
    linkedin: str = "https://linkedin.com/in/fahim-ashab-0473542b6"
    location: str = "Rajshahi / Jashore, Bangladesh"
    degree: str = "Bachelor of Business Administration (BBA) in Finance & Banking"
    institution: str = "Jashore University of Science and Technology (JUST)"
    resume_path: str = "data/Fahim_Ashab_Resume.pdf"
    interests: List[str] = Field(default_factory=list)


class SearchConfig(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    max_results_per_source: int = 15


class FilteringConfig(BaseModel):
    min_match_score: int = 65
    require_internship: bool = True


class ApplicationConfig(BaseModel):
    mode: str = "supervised"
    dry_run: bool = False
    daily_email_limit: int = 5
    email_subject_template: str = "Application for {role} - {candidate_name}"
    sender_name: str = "Fahim Ashab"


class ScheduleConfig(BaseModel):
    run_daily_at: str = "08:30"


class AppSettings(BaseModel):
    candidate: CandidateConfig = Field(default_factory=CandidateConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    filtering: FilteringConfig = Field(default_factory=FilteringConfig)
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)

    # Secrets from .env
    gemini_api_key: Optional[str] = None
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_user: str = "fahimashabofficial@gmail.com"
    email_password: str = ""
    dry_run_override: Optional[bool] = None

    @property
    def is_dry_run(self) -> bool:
        if self.dry_run_override is not None:
            return self.dry_run_override
        return self.application.dry_run

    @property
    def absolute_resume_path(self) -> Path:
        rel = Path(self.candidate.resume_path)
        if rel.is_absolute():
            return rel
        return BASE_DIR / rel


def load_settings() -> AppSettings:
    """Load configuration from config.yaml and environment variables."""
    raw_config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f) or {}

    settings = AppSettings(**raw_config)

    # Inject env vars
    settings.gemini_api_key = os.getenv("GEMINI_API_KEY") or None
    settings.email_host = os.getenv("EMAIL_HOST", settings.email_host)
    settings.email_port = int(os.getenv("EMAIL_PORT", str(settings.email_port)))
    settings.email_user = os.getenv("EMAIL_USER", settings.candidate.email)
    settings.email_password = os.getenv("EMAIL_PASSWORD", "")

    env_dry_run = os.getenv("DRY_RUN")
    if env_dry_run is not None:
        settings.dry_run_override = env_dry_run.lower() in ("true", "1", "yes")

    return settings
