"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"

    # LinkedIn Credentials (optional)
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None

    # Indeed Configuration
    indeed_api_key: Optional[str] = None

    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug_mode: bool = True

    # Database
    database_url: str = "sqlite:///./hr_recruitment.db"

    # Scraping Settings
    headless_browser: bool = True
    scrape_delay: int = 2
    max_candidates_per_search: int = 50

    # Agent Settings
    max_concurrent_agents: int = 3
    agent_timeout: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Returns:
        Settings instance
    """
    return Settings()
