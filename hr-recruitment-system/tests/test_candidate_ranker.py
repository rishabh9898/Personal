"""
Tests for CandidateRankerAgent (backend/agents/candidate_ranker.py)
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.candidate_ranker import CandidateRankerAgent


def _make_ranker():
    return CandidateRankerAgent(
        agent_id="ranker-test",
        config={
            "ai_provider": "claude",
            "anthropic_api_key": "fake-key",
        },
    )


MOCK_SCORING = {
    "overall_score": 85,
    "match_quality": "Excellent",
    "strengths": ["Strong Python"],
    "weaknesses": [],
    "skill_match": {
        "required_skills_matched": ["Python"],
        "required_skills_missing": [],
        "bonus_skills": ["React"],
    },
    "experience_analysis": {
        "years_match": True,
        "relevant_experience": "5 years backend",
        "experience_score": 80,
    },
    "education_match": {"meets_requirements": True, "details": "BS CS"},
    "recommendation": "Proceed to interview",
}


# ── score_candidate ─────────────────────────────────────────────────────────

class TestScoreCandidate:

    @pytest.mark.asyncio
    async def test_score_returns_dict(self, sample_candidates, sample_job_requirements):
        agent = _make_ranker()

        with patch.object(
            agent, "score_candidate", new_callable=AsyncMock, return_value=MOCK_SCORING
        ):
            result = await agent.score_candidate(
                sample_candidates[0], sample_job_requirements
            )

        assert result["overall_score"] == 85
        assert result["match_quality"] == "Excellent"


# ── rank_candidates ──────────────────────────────────────────────────────────

class TestRankCandidates:

    @pytest.mark.asyncio
    async def test_rank_sorts_descending(self, sample_candidates, sample_job_requirements):
        agent = _make_ranker()

        scores = [
            {**MOCK_SCORING, "overall_score": 70},
            {**MOCK_SCORING, "overall_score": 95},
            {**MOCK_SCORING, "overall_score": 85},
        ]
        call_count = 0

        async def mock_score(candidate, job_req):
            nonlocal call_count
            s = scores[call_count]
            call_count += 1
            return s

        with patch.object(agent, "score_candidate", side_effect=mock_score):
            ranked = await agent.rank_candidates(sample_candidates, sample_job_requirements)

        assert ranked[0]["overall_score"] == 95
        assert ranked[1]["overall_score"] == 85
        assert ranked[2]["overall_score"] == 70

        # Verify ranks are assigned correctly
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2
        assert ranked[2]["rank"] == 3


# ── execute ──────────────────────────────────────────────────────────────────

class TestExecute:

    @pytest.mark.asyncio
    async def test_execute_empty_candidates(self, sample_job_requirements):
        agent = _make_ranker()
        result = await agent.execute(
            candidates=[], job_requirements=sample_job_requirements
        )
        assert result["ranked_candidates"] == []
        assert result["message"] == "No candidates to rank"

    @pytest.mark.asyncio
    async def test_execute_with_candidates(self, sample_candidates, sample_job_requirements):
        agent = _make_ranker()

        async def mock_score(candidate, job_req):
            return {**MOCK_SCORING, "overall_score": 80}

        mock_shortlist = {
            "shortlist": sample_candidates[:2],
            "summary": {"summary": "Good pool"},
            "total_candidates_reviewed": 3,
            "shortlist_size": 2,
        }

        with patch.object(agent, "score_candidate", side_effect=mock_score):
            with patch.object(
                agent, "generate_shortlist", new_callable=AsyncMock, return_value=mock_shortlist
            ):
                result = await agent.execute(
                    candidates=sample_candidates,
                    job_requirements=sample_job_requirements,
                    generate_shortlist=True,
                    shortlist_size=2,
                )

        assert result["total_candidates"] == 3
        assert len(result["ranked_candidates"]) == 3
        assert result["top_score"] == 80
        assert result["average_score"] == 80
        assert "shortlist" in result

    @pytest.mark.asyncio
    async def test_execute_no_shortlist(self, sample_candidates, sample_job_requirements):
        agent = _make_ranker()

        async def mock_score(candidate, job_req):
            return {**MOCK_SCORING, "overall_score": 60}

        with patch.object(agent, "score_candidate", side_effect=mock_score):
            result = await agent.execute(
                candidates=sample_candidates,
                job_requirements=sample_job_requirements,
                generate_shortlist=False,
            )

        assert "shortlist" not in result
        assert result["total_candidates"] == 3


# ── run() wrapper ────────────────────────────────────────────────────────────

class TestRunWrapper:

    @pytest.mark.asyncio
    async def test_run_success(self, sample_candidates, sample_job_requirements):
        agent = _make_ranker()

        async def mock_score(candidate, job_req):
            return {**MOCK_SCORING, "overall_score": 75}

        with patch.object(agent, "score_candidate", side_effect=mock_score):
            with patch.object(
                agent,
                "generate_shortlist",
                new_callable=AsyncMock,
                return_value={"shortlist": [], "total_candidates_reviewed": 3, "shortlist_size": 0},
            ):
                result = await agent.run(
                    candidates=sample_candidates,
                    job_requirements=sample_job_requirements,
                )

        assert result["success"] is True
        assert agent.status == "completed"
