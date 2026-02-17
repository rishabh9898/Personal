"""
Tests for BaseAgent (backend/agents/base_agent.py)
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch
from backend.agents.base_agent import BaseAgent


# Concrete subclass for testing the abstract base
class DummyAgent(BaseAgent):
    """Minimal concrete agent for testing."""

    async def execute(self, **kwargs):
        return {"result": "ok", **kwargs}


class FailingAgent(BaseAgent):
    """Agent whose execute always raises."""

    async def execute(self, **kwargs):
        raise RuntimeError("intentional failure")


# ── Initialization ───────────────────────────────────────────────────────────

class TestBaseAgentInit:

    def test_defaults(self):
        agent = DummyAgent(agent_id="test-1")
        assert agent.agent_id == "test-1"
        assert agent.status == "initialized"
        assert agent.config == {}
        assert agent.results == []
        assert agent.errors == []
        assert isinstance(agent.created_at, datetime)
        assert agent.last_run is None

    def test_with_config(self):
        cfg = {"key": "value"}
        agent = DummyAgent(agent_id="test-2", config=cfg)
        assert agent.config == cfg


# ── Status management ────────────────────────────────────────────────────────

class TestStatusManagement:

    def test_update_status(self):
        agent = DummyAgent(agent_id="s1")
        agent.update_status("running")
        assert agent.status == "running"

    def test_update_status_multiple_times(self):
        agent = DummyAgent(agent_id="s2")
        for s in ("running", "completed", "idle"):
            agent.update_status(s)
        assert agent.status == "idle"


# ── Results & errors ─────────────────────────────────────────────────────────

class TestResultsAndErrors:

    def test_add_result(self):
        agent = DummyAgent(agent_id="r1")
        agent.add_result({"data": 42})
        assert len(agent.results) == 1
        assert agent.results[0]["data"] == 42
        assert "timestamp" in agent.results[0]

    def test_add_error_without_exception(self):
        agent = DummyAgent(agent_id="e1")
        agent.add_error("something went wrong")
        assert len(agent.errors) == 1
        assert agent.errors[0]["message"] == "something went wrong"
        assert agent.errors[0]["exception"] is None

    def test_add_error_with_exception(self):
        agent = DummyAgent(agent_id="e2")
        agent.add_error("boom", ValueError("bad value"))
        assert "bad value" in agent.errors[0]["exception"]


# ── get_summary ──────────────────────────────────────────────────────────────

class TestGetSummary:

    def test_summary_fields(self):
        agent = DummyAgent(agent_id="sum1", config={"x": 1})
        summary = agent.get_summary()
        assert summary["agent_id"] == "sum1"
        assert summary["agent_type"] == "DummyAgent"
        assert summary["status"] == "initialized"
        assert summary["results_count"] == 0
        assert summary["errors_count"] == 0
        assert summary["config"] == {"x": 1}
        assert summary["last_run"] is None


# ── run() wrapper ────────────────────────────────────────────────────────────

class TestRunWrapper:

    @pytest.mark.asyncio
    async def test_successful_run(self):
        agent = DummyAgent(agent_id="run1")
        result = await agent.run(foo="bar")
        assert result["success"] is True
        assert result["agent_id"] == "run1"
        assert result["data"]["result"] == "ok"
        assert result["data"]["foo"] == "bar"
        assert agent.status == "completed"
        assert agent.last_run is not None

    @pytest.mark.asyncio
    async def test_failed_run(self):
        agent = FailingAgent(agent_id="fail1")
        result = await agent.run()
        assert result["success"] is False
        assert "intentional failure" in result["error"]
        assert agent.status == "failed"
        assert len(agent.errors) == 1


# ── Logging ──────────────────────────────────────────────────────────────────

class TestLogging:

    def test_log_levels(self):
        agent = DummyAgent(agent_id="log1")
        # Should not raise for any valid level
        for level in ("info", "warning", "error", "debug"):
            agent.log(f"test {level}", level=level)
