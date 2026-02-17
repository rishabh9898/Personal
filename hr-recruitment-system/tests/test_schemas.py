"""
Tests for Pydantic schemas (backend/models/schemas.py)
"""

import pytest
from pydantic import ValidationError
from backend.models.schemas import (
    JobRequirements,
    SearchRequest,
    ResumeUploadRequest,
    OrchestrationRequest,
    CandidateResponse,
    RankingResponse,
    AgentStatusResponse,
    OrchestrationResponse,
    ErrorResponse,
)


# ── JobRequirements ──────────────────────────────────────────────────────────

class TestJobRequirements:

    def test_minimal_valid(self):
        jr = JobRequirements(title="SWE", description="Build stuff")
        assert jr.title == "SWE"
        assert jr.required_skills == []
        assert jr.min_years_experience is None

    def test_full_valid(self):
        jr = JobRequirements(
            title="Senior Python Dev",
            description="Backend role",
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"],
            min_years_experience=5,
            education_requirements="BS CS",
            location="NYC",
            salary_range="$120k-$160k",
            additional_requirements={"clearance": True},
        )
        assert jr.min_years_experience == 5
        assert "Docker" in jr.preferred_skills

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            JobRequirements()  # title & description are required

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            JobRequirements(description="desc only")

    def test_missing_description(self):
        with pytest.raises(ValidationError):
            JobRequirements(title="title only")


# ── SearchRequest ────────────────────────────────────────────────────────────

class TestSearchRequest:

    def test_minimal_valid(self):
        sr = SearchRequest(job_title="Data Scientist")
        assert sr.job_title == "Data Scientist"
        assert sr.search_linkedin is True
        assert sr.search_indeed is True
        assert sr.max_candidates == 50

    def test_with_credentials(self):
        sr = SearchRequest(
            job_title="SWE",
            linkedin_email="user@example.com",
            linkedin_password="secret",
        )
        assert sr.linkedin_email == "user@example.com"

    def test_missing_job_title(self):
        with pytest.raises(ValidationError):
            SearchRequest()


# ── ResumeUploadRequest ─────────────────────────────────────────────────────

class TestResumeUploadRequest:

    def test_valid(self):
        r = ResumeUploadRequest(file_paths=["/tmp/resume.pdf"])
        assert r.include_raw_text is False

    def test_missing_file_paths(self):
        with pytest.raises(ValidationError):
            ResumeUploadRequest()


# ── OrchestrationRequest ────────────────────────────────────────────────────

class TestOrchestrationRequest:

    def test_defaults(self):
        req = OrchestrationRequest()
        assert req.mode == "full_search"
        assert req.rank_candidates is True
        assert req.shortlist_size == 10

    def test_parse_only_mode(self):
        req = OrchestrationRequest(
            mode="parse_only",
            resume_files=["/resumes/a.pdf", "/resumes/b.docx"],
        )
        assert req.mode == "parse_only"
        assert len(req.resume_files) == 2

    def test_with_job_requirements(self):
        jr = JobRequirements(title="SWE", description="Build")
        req = OrchestrationRequest(
            mode="full_search",
            job_requirements=jr,
            job_title="SWE",
        )
        assert req.job_requirements.title == "SWE"


# ── CandidateResponse ───────────────────────────────────────────────────────

class TestCandidateResponse:

    def test_empty(self):
        c = CandidateResponse()
        assert c.name is None
        assert c.skills is None

    def test_full(self):
        c = CandidateResponse(
            name="Jane",
            email="jane@example.com",
            skills=["Python"],
            overall_score=92.5,
            rank=1,
        )
        assert c.overall_score == 92.5


# ── RankingResponse ──────────────────────────────────────────────────────────

class TestRankingResponse:

    def test_valid(self):
        r = RankingResponse(
            total_candidates=3,
            ranked_candidates=[{"name": "A", "score": 90}],
            top_score=90.0,
            average_score=75.0,
        )
        assert r.total_candidates == 3

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            RankingResponse()


# ── OrchestrationResponse ───────────────────────────────────────────────────

class TestOrchestrationResponse:

    def test_valid(self):
        r = OrchestrationResponse(
            mode="full_search",
            total_candidates_found=5,
            candidates=[],
            sources={"linkedin": 3, "indeed": 2},
        )
        assert r.total_candidates_found == 5
        assert r.timestamp  # auto-generated


# ── ErrorResponse ────────────────────────────────────────────────────────────

class TestErrorResponse:

    def test_valid(self):
        e = ErrorResponse(error="Something broke")
        assert e.error == "Something broke"
        assert e.timestamp
