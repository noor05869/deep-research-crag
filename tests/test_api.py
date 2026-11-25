"""
tests/test_api.py
-----------------
Integration tests for FastAPI REST API endpoints.
"""

import json
from importlib import import_module

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


def test_research_stream_and_rest_share_final_retry_state(monkeypatch):
    graph = import_module("deep_research.graph")
    api_module = import_module("deep_research.api")
    monkeypatch.setattr(graph, "retrieve_node", lambda state: {"documents": []})
    monkeypatch.setattr(graph, "grade_documents_node", lambda state: {"web_search_needed": True})
    monkeypatch.setattr(graph, "transform_query_node", lambda state: {"transformed_query": state["raw_query"]})
    monkeypatch.setattr(graph, "web_search_node", lambda state: {"loop_step": 1})
    monkeypatch.setattr(graph, "generate_node", lambda state: {
        "final_response": f"Draft {state['loop_step']} [1]",
        "citations": [{"citation_id": "[1]", "source": "Policy", "quote": f"Draft {state['loop_step']}"}],
    })
    monkeypatch.setattr(graph, "check_hallucination_node", lambda state: {
        "hallucination_grade": "grounded" if state["loop_step"] == 2 else "hallucinated",
    })
    monkeypatch.setattr(api_module, "research_graph", graph.build_research_graph())

    payload = {"query": "What is the standard fossil loan period?"}
    response = client.post("/api/research/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
    assert events[0]["event"] == "start"
    assert events[-1]["event"] == "complete"
    streamed = events[-1]["data"]
    rest_response = client.post("/api/research", json=payload)
    assert rest_response.status_code == 200
    rest = rest_response.json()
    assert streamed.pop("execution_time_seconds") >= 0
    assert rest.pop("execution_time_seconds") >= 0
    assert streamed == rest
    assert rest["loop_step"] == 2
    assert [citation["quote"] for citation in rest["citations"]] == ["Draft 2"]
