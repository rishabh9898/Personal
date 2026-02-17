"""
Tests for AgentOrchestrator (backend/agents/orchestrator.py)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.agents.orchestrator import AgentOrchestrator


def _make_orchestrator():
    config = {
        "ai_provider": "claude",
        "anthropic_api_key": "fake-key",
        "claude_model": "claude-3-5-sonnet-20241022",
        "headless": True,
        "scrape_delay": 0,
        "max_candidates": 10,
    }
    return AgentOrchestrator(config=config)


# ── Initialization ───────────────────────────────────────────────────────────

class TestInit:

    def test_sub_agents_created(self):
        orch = _make_orchestrator()
        assert orch.resume_parser is not None
        assert orch.linkedin_scraper is not None
        assert orch.indeed_scraper is not None
        assert orch.candidate_ranker is not None

    def test_agent_ids(self):
        orch = _make_orchestrator()
        assert orch.agent_id == "orchestrator"
        assert orch.resume_parser.agent_id == "resume_parser_1"


# ── get_agents_status ────────────────────────────────────────────────────────

class TestGetAgentsStatus:

    def test_returns_all_agents(self):
        orch = _make_orchestrator()
        status = orch.get_agents_status()
        assert "orchestrator" in status
        assert "resume_parser" in status
        assert "linkedin_scraper" in status
        assert "indeed_scraper" in status
        assert "candidate_ranker" in status

    def test_status_fields(self):
        orch = _make_orchestrator()
        status = orch.get_agents_status()
        for key in status:
            agent_summary = status[key]
            assert "agent_id" in agent_summary
            assert "status" in agent_summary
            assert "results_count" in agent_summary


# ── parse_resumes ────────────────────────────────────────────────────────────

class TestParseResumes:

    @pytest.mark.asyncio
    async def test_parse_resumes_success(self, sample_resume_txt):
        orch = _make_orchestrator()

        mock_result = {
            "success": True,
            "data": {
                "parsed_data": {
                    "name": "John Doe",
                    "skills": ["Python"],
                }
            },
        }

        with patch.object(
            orch.resume_parser, "run", new_callable=AsyncMock, return_value=mock_result
        ):
            parsed = await orch.parse_resumes([sample_resume_txt])

        assert len(parsed) == 1
        assert parsed[0]["name"] == "John Doe"
        assert parsed[0]["source"] == "uploaded_resume"

    @pytest.mark.asyncio
    async def test_parse_resumes_partial_failure(self, sample_resume_txt):
        """If one resume fails, others should still be returned."""
        orch = _make_orchestrator()

        good_result = {
            "success": True,
            "data": {"parsed_data": {"name": "Good Candidate"}},
        }
        bad_result = {"success": False, "error": "parse error"}

        with patch.object(
            orch.resume_parser,
            "run",
            new_callable=AsyncMock,
            side_effect=[good_result, bad_result],
        ):
            parsed = await orch.parse_resumes([sample_resume_txt, "/bad/file.pdf"])

        assert len(parsed) == 1
        assert parsed[0]["name"] == "Good Candidate"


# ── search_candidates ───────────────────────────────────────────────────────

class TestSearchCandidates:

    @pytest.mark.asyncio
    async def test_search_both_sources(self):
        orch = _make_orchestrator()

        linkedin_result = {
            "success": True,
            "data": {"candidates": [{"name": "L1", "source": "LinkedIn"}]},
        }
        indeed_result = {
            "success": True,
            "data": {"results": [{"name": "I1", "source": "Indeed"}]},
        }

        with patch.object(
            orch.linkedin_scraper, "run", new_callable=AsyncMock, return_value=linkedin_result
        ):
            with patch.object(
                orch.indeed_scraper, "run", new_callable=AsyncMock, return_value=indeed_result
            ):
                candidates = await orch.search_candidates(
                    job_title="SWE",
                    search_linkedin=True,
                    search_indeed=True,
                )

        assert len(candidates) == 2

    @pytest.mark.asyncio
    async def test_search_linkedin_only(self):
        orch = _make_orchestrator()

        linkedin_result = {
            "success": True,
            "data": {"candidates": [{"name": "L1"}]},
        }

        with patch.object(
            orch.linkedin_scraper, "run", new_callable=AsyncMock, return_value=linkedin_result
        ):
            candidates = await orch.search_candidates(
                job_title="SWE",
                search_linkedin=True,
                search_indeed=False,
            )

        assert len(candidates) == 1

    @pytest.mark.asyncio
    async def test_search_handles_failure(self):
        orch = _make_orchestrator()

        with patch.object(
            orch.linkedin_scraper, "run", new_callable=AsyncMock, side_effect=Exception("timeout")
        ):
            candidates = await orch.search_candidates(
                job_title="SWE",
                search_linkedin=True,
                search_indeed=False,
            )

        assert candidates == []


# ── execute (full workflow) ──────────────────────────────────────────────────

class TestExecute:

    @pytest.mark.asyncio
    async def test_parse_only_mode(self):
        orch = _make_orchestrator()

        with patch.object(
            orch,
            "parse_resumes",
            new_callable=AsyncMock,
            return_value=[{"name": "A", "source": "uploaded_resume"}],
        ):
            result = await orch.execute(
                mode="parse_only",
                resume_files=["/resume.pdf"],
                rank_candidates=False,
            )

        assert result["mode"] == "parse_only"
        assert result["total_candidates_found"] == 1

    @pytest.mark.asyncio
    async def test_search_only_mode(self):
        orch = _make_orchestrator()

        with patch.object(
            orch,
            "search_candidates",
            new_callable=AsyncMock,
            return_value=[{"name": "B", "source": "LinkedIn"}],
        ):
            result = await orch.execute(
                mode="search_only",
                job_title="SWE",
                rank_candidates=False,
            )

        assert result["mode"] == "search_only"
        assert result["total_candidates_found"] == 1

    @pytest.mark.asyncio
    async def test_full_search_with_ranking(self, sample_job_requirements):
        orch = _make_orchestrator()

        with patch.object(
            orch,
            "search_candidates",
            new_callable=AsyncMock,
            return_value=[{"name": "C", "source": "LinkedIn"}],
        ):
            ranking_result = {
                "success": True,
                "data": {
                    "ranked_candidates": [{"name": "C", "overall_score": 90}],
                    "top_score": 90,
                },
            }
            with patch.object(
                orch.candidate_ranker, "run", new_callable=AsyncMock, return_value=ranking_result
            ):
                result = await orch.execute(
                    mode="full_search",
                    job_title="SWE",
                    job_requirements=sample_job_requirements,
                    rank_candidates=True,
                )

        assert result["ranked_results"] is not None
        assert result["ranked_results"]["top_score"] == 90

    @pytest.mark.asyncio
    async def test_sources_count(self):
        orch = _make_orchestrator()

        candidates = [
            {"name": "A", "source": "uploaded_resume"},
            {"name": "B", "source": "LinkedIn"},
            {"name": "C", "source": "LinkedIn"},
            {"name": "D", "source": "Indeed"},
        ]

        with patch.object(
            orch, "parse_resumes", new_callable=AsyncMock, return_value=[candidates[0]]
        ):
            with patch.object(
                orch,
                "search_candidates",
                new_callable=AsyncMock,
                return_value=candidates[1:],
            ):
                result = await orch.execute(
                    mode="full_search",
                    job_title="SWE",
                    resume_files=["/r.pdf"],
                    rank_candidates=False,
                )

        assert result["sources"]["uploaded_resumes"] == 1
        assert result["sources"]["linkedin"] == 2
        assert result["sources"]["indeed"] == 1
