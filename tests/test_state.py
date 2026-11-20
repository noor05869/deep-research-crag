"""
tests/test_state.py
-------------------
Unit tests for DeepResearchState schema and state dictionary structures.
"""

from deep_research.state import DeepResearchState, merge_documents


def test_merge_documents_deduplication():
    """Verify that merge_documents prevents duplicate chunk IDs or contents."""
    existing = [
        {"doc_id": "doc_1", "content": "First unique chunk", "source": "Policy A"},
        {"doc_id": "doc_2", "content": "Second unique chunk", "source": "Policy B"},
    ]
    new = [
        {"doc_id": "doc_2", "content": "Second unique chunk", "source": "Policy B"},
        {"doc_id": "doc_3", "content": "Third unique chunk", "source": "Policy C"},
    ]

    merged = merge_documents(existing, new)

    assert len(merged) == 3
    doc_ids = [d["doc_id"] for d in merged]
    assert doc_ids == ["doc_1", "doc_2", "doc_3"]


def test_merge_documents_empty_existing():
    """Verify merge_documents handles empty initial state cleanly."""
    new = [{"doc_id": "doc_1", "content": "Initial chunk", "source": "Policy A"}]
    merged = merge_documents([], new)
    assert len(merged) == 1
    assert merged[0]["doc_id"] == "doc_1"


def test_state_structure_initialization():
    """Verify DeepResearchState keys and types conform to the contract."""
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

    assert state["raw_query"] == "What is the standard fossil loan period?"
    assert state["loop_step"] == 0
    assert state["web_search_needed"] is False
    assert state["documents"] == []
