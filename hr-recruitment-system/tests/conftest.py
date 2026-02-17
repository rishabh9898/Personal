"""
Shared fixtures for HR Recruitment System tests
"""

import os
import shutil
import tempfile
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Event loop fixture for async tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Mock the AI clients globally so agent constructors never hit real SDKs
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _mock_ai_clients(monkeypatch):
    """Prevent real Anthropic / OpenAI client instantiation in every test."""
    mock_anthropic_cls = MagicMock()
    mock_openai_cls = MagicMock()

    monkeypatch.setattr("anthropic.AsyncAnthropic", mock_anthropic_cls, raising=False)

    # OpenAI may or may not be importable; guard with raising=False
    try:
        import openai  # noqa: F401
        monkeypatch.setattr("openai.AsyncOpenAI", mock_openai_cls, raising=False)
    except ImportError:
        pass

    return mock_anthropic_cls, mock_openai_cls


# ---------------------------------------------------------------------------
# Temp directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_data_dir(tmp_path):
    """Provide a temporary data directory with resumes/ and results/ subdirs."""
    resumes = tmp_path / "resumes"
    results = tmp_path / "results"
    resumes.mkdir()
    results.mkdir()
    return tmp_path


@pytest.fixture
def sample_resume_txt(tmp_path):
    """Create a sample plain-text resume file."""
    content = """John Doe
Email: john.doe@example.com
Phone: (555) 123-4567
Location: New York, NY

PROFESSIONAL SUMMARY
Experienced software engineer with 8 years of experience in Python, JavaScript,
and cloud technologies. Strong background in building scalable web applications.

EXPERIENCE
Senior Software Engineer - TechCorp Inc.
Jan 2020 - Present
- Led a team of 5 engineers to build a microservices platform
- Designed REST APIs serving 10M+ requests/day

Software Engineer - StartupXYZ
Jun 2016 - Dec 2019
- Built full-stack web applications using React and Django
- Implemented CI/CD pipelines with Jenkins and Docker

EDUCATION
B.S. Computer Science - MIT, 2016

SKILLS
Python, JavaScript, React, Django, Docker, Kubernetes, AWS, PostgreSQL, Redis
"""
    file_path = tmp_path / "john_doe_resume.txt"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


@pytest.fixture
def sample_candidates():
    """Return a list of sample candidate dicts for ranking tests."""
    return [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "skills": ["Python", "Django", "AWS", "Docker"],
            "experience": [
                {"company": "BigCo", "title": "Senior Developer", "duration": "3 years"}
            ],
            "education": [{"institution": "Stanford", "degree": "M.S. Computer Science"}],
            "source": "LinkedIn",
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "skills": ["Java", "Spring Boot", "Azure"],
            "experience": [
                {"company": "MediumCo", "title": "Developer", "duration": "2 years"}
            ],
            "education": [{"institution": "State University", "degree": "B.S. CS"}],
            "source": "Indeed",
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Kubernetes"],
            "experience": [
                {"company": "Enterprise Ltd", "title": "Lead Engineer", "duration": "5 years"}
            ],
            "education": [{"institution": "MIT", "degree": "B.S. CS"}],
            "source": "uploaded_resume",
        },
    ]


@pytest.fixture
def sample_job_requirements():
    """Return a sample job requirements dict."""
    return {
        "title": "Senior Python Developer",
        "description": "Looking for a senior Python developer with cloud experience.",
        "required_skills": ["Python", "AWS", "Docker"],
        "preferred_skills": ["Kubernetes", "React", "FastAPI"],
        "min_years_experience": 3,
        "education_requirements": "Bachelor's in Computer Science or equivalent",
        "location": "New York, NY",
    }


# ---------------------------------------------------------------------------
# Agent config fixture (no real API keys)
# ---------------------------------------------------------------------------

@pytest.fixture
def agent_config():
    """Return a mock agent config dict."""
    return {
        "ai_provider": "claude",
        "anthropic_api_key": "test-key-not-real",
        "claude_model": "claude-3-5-sonnet-20241022",
        "openai_api_key": "test-key-not-real",
        "openai_model": "gpt-4-turbo-preview",
        "headless": True,
        "scrape_delay": 0,
        "max_candidates": 10,
    }


# ---------------------------------------------------------------------------
# FastAPI TestClient fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client(tmp_data_dir, monkeypatch):
    """
    Provide a FastAPI TestClient with patched data dirs and orchestrator.
    The orchestrator is NOT initialised (tests that need it should mock it).
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    from starlette.testclient import TestClient
    import backend.api.main as main_module

    main_module.UPLOAD_DIR = tmp_data_dir / "resumes"
    main_module.RESULTS_DIR = tmp_data_dir / "results"
    main_module.orchestrator = None  # reset global

    client = TestClient(main_module.app)
    yield client

    # cleanup
    main_module.orchestrator = None
