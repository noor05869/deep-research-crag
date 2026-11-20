"""
tests/test_retriever.py
-----------------------
Unit tests for Qdrant vector retrieval, chunking, and dynamic file ingestion.
"""

from deep_research.retriever import retrieve_node, add_custom_document, splitter
from deep_research.state import DeepResearchState


def test_splitter_chunk_size_and_overlap():
    """Verify that chunk size and overlap parameters match the optimized configuration."""
    assert splitter._chunk_size == 1000
    assert splitter._chunk_overlap == 150


def test_retrieve_node_returns_candidate_chunks():
    """Verify that retrieve_node fetches top-k candidates into state['documents']."""
    state: DeepResearchState = {
        "raw_query": "What is the standard fossil loan period?",
        "transformed_query": None,
        "documents": [],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0,
    }

    result = retrieve_node(state)

    assert "documents" in result
    docs = result["documents"]
    assert len(docs) > 0
    assert len(docs) <= 5  # k=5
    assert "content" in docs[0]
    assert "source" in docs[0]


def test_dynamic_document_ingestion():
    """Verify custom document text can be indexed dynamically at runtime."""
    custom_text = (
        "Project Hepta Deployment Protocol:\n"
        "Step 1: Bootstrap the operator organization in the provisioning portal.\n"
        "Step 2: Log into the administrative dashboard at dev.toscoris.com/login.\n"
        "Step 3: Test locations, geofences, and roster members."
    )

    chunks_count = add_custom_document(custom_text, "hepta_testing_guide.txt")
    assert chunks_count >= 1
