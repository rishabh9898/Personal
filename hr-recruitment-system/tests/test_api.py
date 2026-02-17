"""
Tests for FastAPI endpoints (backend/api/main.py)
"""

import io
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path


# ── Health check ─────────────────────────────────────────────────────────────

class TestHealthCheck:

    def test_health_returns_200(self, api_client):
        resp = api_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "resume_parser" in data["agents"]


# ── Upload resumes ───────────────────────────────────────────────────────────

class TestUploadResumes:

    def test_upload_txt_file(self, api_client, tmp_data_dir):
        content = b"John Doe\nPython Developer"
        files = [("files", ("resume.txt", io.BytesIO(content), "text/plain"))]
        resp = api_client.post("/api/upload-resumes", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["files_uploaded"] == 1

    def test_upload_pdf_file(self, api_client):
        content = b"%PDF-1.4 fake pdf content"
        files = [("files", ("resume.pdf", io.BytesIO(content), "application/pdf"))]
        resp = api_client.post("/api/upload-resumes", files=files)
        assert resp.status_code == 200

    def test_upload_unsupported_type(self, api_client):
        content = b"some content"
        files = [("files", ("resume.jpg", io.BytesIO(content), "image/jpeg"))]
        resp = api_client.post("/api/upload-resumes", files=files)
        assert resp.status_code == 500  # wrapped HTTPException

    def test_upload_multiple_files(self, api_client):
        files = [
            ("files", ("a.txt", io.BytesIO(b"A"), "text/plain")),
            ("files", ("b.txt", io.BytesIO(b"B"), "text/plain")),
        ]
        resp = api_client.post("/api/upload-resumes", files=files)
        assert resp.status_code == 200
        assert resp.json()["files_uploaded"] == 2


# ── List resumes ─────────────────────────────────────────────────────────────

class TestListResumes:

    def test_list_empty(self, api_client):
        resp = api_client.get("/api/resumes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["count"] == 0

    def test_list_after_upload(self, api_client):
        files = [("files", ("test.txt", io.BytesIO(b"data"), "text/plain"))]
        api_client.post("/api/upload-resumes", files=files)

        resp = api_client.get("/api/resumes")
        data = resp.json()
        assert data["count"] == 1
        assert "test.txt" in data["files"]


# ── Delete resume ────────────────────────────────────────────────────────────

class TestDeleteResume:

    def test_delete_existing(self, api_client):
        # Upload first
        files = [("files", ("delete_me.txt", io.BytesIO(b"data"), "text/plain"))]
        api_client.post("/api/upload-resumes", files=files)

        resp = api_client.delete("/api/resumes/delete_me.txt")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_delete_nonexistent(self, api_client):
        resp = api_client.delete("/api/resumes/no_such_file.pdf")
        # The endpoint's broad except catches HTTPException(404) and re-raises
        # as 500. This test documents the current behaviour.
        assert resp.status_code == 500


# ── Search candidates ───────────────────────────────────────────────────────

class TestSearchCandidates:

    def test_search_calls_orchestrator(self, api_client):
        import backend.api.main as main_module

        mock_orch = MagicMock()
        mock_orch.run = AsyncMock(
            return_value={
                "success": True,
                "data": [{"name": "Found Candidate"}],
            }
        )
        main_module.orchestrator = mock_orch

        resp = api_client.post(
            "/api/search-candidates",
            json={"job_title": "Python Developer"},
        )
        assert resp.status_code == 200


# ── Agents status ────────────────────────────────────────────────────────────

class TestAgentsStatus:

    def test_status_with_mock_orchestrator(self, api_client):
        import backend.api.main as main_module

        mock_orch = MagicMock()
        mock_orch.get_agents_status.return_value = {
            "orchestrator": {"status": "initialized"},
            "resume_parser": {"status": "initialized"},
        }
        main_module.orchestrator = mock_orch

        resp = api_client.get("/api/agents/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "orchestrator" in data
