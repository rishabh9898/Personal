"""
Tests for configuration management (backend/utils/config.py)
"""

import pytest
from unittest.mock import patch
from backend.utils.config import Settings, get_settings


class TestSettings:

    def test_defaults(self):
        s = Settings(
            _env_file=None,  # don't read .env during tests
        )
        assert s.ai_provider == "claude"
        assert s.app_port == 8000
        assert s.headless_browser is True
        assert s.max_candidates_per_search == 50
        assert s.debug_mode is True
        assert s.scrape_delay == 2

    def test_custom_values(self):
        s = Settings(
            ai_provider="openai",
            app_port=9000,
            max_candidates_per_search=100,
            debug_mode=False,
            _env_file=None,
        )
        assert s.ai_provider == "openai"
        assert s.app_port == 9000
        assert s.max_candidates_per_search == 100
        assert s.debug_mode is False

    def test_database_url_default(self):
        s = Settings(_env_file=None)
        assert "sqlite" in s.database_url

    def test_api_keys_optional(self):
        s = Settings(_env_file=None)
        assert s.anthropic_api_key is None
        assert s.openai_api_key is None
        assert s.indeed_api_key is None


class TestGetSettings:

    def test_returns_settings_instance(self):
        get_settings.cache_clear()
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
            s = get_settings()
            assert isinstance(s, Settings)
        get_settings.cache_clear()

    def test_cached(self):
        get_settings.cache_clear()
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
            s1 = get_settings()
            s2 = get_settings()
            assert s1 is s2
        get_settings.cache_clear()
