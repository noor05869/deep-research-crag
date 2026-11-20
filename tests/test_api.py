"""
tests/test_api.py
-----------------
Integration tests for FastAPI REST API endpoints.
"""

from fastapi.testclient import TestClient
from deep_research.api import api

client = TestClient(api)


def test_health_check_endpoint():
    """Verify GET /api/health returns 200 OK and valid engine statuses."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "engine" in data
    assert "vector_store" in data


def test_list_documents_endpoint():
    """Verify GET /api/documents returns a list of indexed knowledge sources."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) > 0


def test_upload_text_document_endpoint():
    """Verify POST /api/upload indexes uploaded text file into active Qdrant store."""
    file_content = b"Policy update: All research grants require peer review within 14 days."
    files = {"file": ("research_grant_policy.txt", file_content, "text/plain")}

    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "research_grant_policy.txt"
    assert data["chunks_indexed"] >= 1
    assert "Successfully indexed" in data["message"]


def test_research_stream_handshake():
    """Verify POST /api/research/stream initiates SSE stream with text/event-stream content-type."""
    payload = {"query": "What is the standard fossil loan period?"}
    response = client.post("/api/research/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "data: " in response.text
    assert '"event": "start"' in response.text
