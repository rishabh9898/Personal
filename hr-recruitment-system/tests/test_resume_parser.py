"""
Tests for ResumeParserAgent (backend/agents/resume_parser.py)
"""

import os
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.agents.resume_parser import ResumeParserAgent


# ── Text extraction ──────────────────────────────────────────────────────────

class TestTextExtraction:

    def _make_agent(self):
        return ResumeParserAgent(
            agent_id="parser-test",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )

    def test_extract_text_from_txt(self, sample_resume_txt):
        agent = self._make_agent()
        text = agent.extract_text_from_file(sample_resume_txt)
        assert "John Doe" in text
        assert "john.doe@example.com" in text
        assert "Python" in text

    def test_extract_text_unsupported_format(self, tmp_path):
        agent = self._make_agent()
        bad_file = tmp_path / "resume.xyz"
        bad_file.write_text("content")
        with pytest.raises(ValueError, match="Unsupported file format"):
            agent.extract_text_from_file(str(bad_file))

    def test_extract_text_from_txt_encoding(self, tmp_path):
        """Ensure UTF-8 content is read correctly."""
        agent = self._make_agent()
        content = "Résumé of José García — Senior Développeur"
        f = tmp_path / "utf8_resume.txt"
        f.write_text(content, encoding="utf-8")
        result = agent.extract_text_from_file(str(f))
        assert "José García" in result


# ── execute() ────────────────────────────────────────────────────────────────

class TestExecute:

    @pytest.mark.asyncio
    async def test_execute_with_file_path(self, sample_resume_txt):
        """execute() should extract text and call AI, returning parsed data."""
        agent = ResumeParserAgent(
            agent_id="parser-exec",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )

        mock_parsed = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "skills": ["Python", "JavaScript"],
        }

        with patch.object(
            agent, "parse_resume_with_ai", new_callable=AsyncMock, return_value=mock_parsed
        ):
            result = await agent.execute(file_path=sample_resume_txt)

        assert result["parsed_data"]["name"] == "John Doe"
        assert result["source_file"] == sample_resume_txt
        assert result["text_length"] > 0

    @pytest.mark.asyncio
    async def test_execute_with_raw_text(self):
        agent = ResumeParserAgent(
            agent_id="parser-text",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )

        mock_parsed = {"name": "Jane", "skills": ["Go"]}

        with patch.object(
            agent, "parse_resume_with_ai", new_callable=AsyncMock, return_value=mock_parsed
        ):
            result = await agent.execute(resume_text="Jane Doe resume text here")

        assert result["parsed_data"]["name"] == "Jane"
        assert result["source_file"] is None

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self):
        agent = ResumeParserAgent(
            agent_id="parser-fnf",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )
        with pytest.raises(FileNotFoundError):
            await agent.execute(file_path="/nonexistent/resume.pdf")

    @pytest.mark.asyncio
    async def test_execute_no_input(self):
        agent = ResumeParserAgent(
            agent_id="parser-noinput",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )
        with pytest.raises(ValueError, match="Either file_path or resume_text"):
            await agent.execute()


# ── run() integration (via BaseAgent wrapper) ────────────────────────────────

class TestRunWrapper:

    @pytest.mark.asyncio
    async def test_run_success(self, sample_resume_txt):
        agent = ResumeParserAgent(
            agent_id="parser-run",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )

        mock_parsed = {"name": "John Doe", "skills": ["Python"]}

        with patch.object(
            agent, "parse_resume_with_ai", new_callable=AsyncMock, return_value=mock_parsed
        ):
            result = await agent.run(file_path=sample_resume_txt)

        assert result["success"] is True
        assert result["data"]["parsed_data"]["name"] == "John Doe"
        assert agent.status == "completed"

    @pytest.mark.asyncio
    async def test_run_failure(self):
        agent = ResumeParserAgent(
            agent_id="parser-fail",
            config={
                "ai_provider": "claude",
                "anthropic_api_key": "fake-key",
            },
        )

        result = await agent.run(file_path="/does/not/exist.pdf")
        assert result["success"] is False
        assert agent.status == "failed"
