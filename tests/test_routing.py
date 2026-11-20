"""
tests/test_routing.py
---------------------
Unit tests for LangGraph conditional edge routing gates and circuit breakers.
"""

from langgraph.graph import END
from deep_research.graph import decide_to_generate, decide_evaluation
from deep_research.state import DeepResearchState


def test_decide_to_generate_direct():
    """When internal documents are sufficient (web_search_needed == False), route to generate."""
    state: DeepResearchState = {
        "raw_query": "Test query",
        "transformed_query": None,
        "documents": [{"content": "Valid doc", "source": "Source A"}],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0,
    }

    next_node = decide_to_generate(state)
    assert next_node == "generate"


def test_decide_to_generate_fallback():
    """When internal documents are insufficient (web_search_needed == True), route to transform_query."""
    state: DeepResearchState = {
        "raw_query": "Test query",
        "transformed_query": None,
        "documents": [],
        "web_search_needed": True,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0,
    }

    next_node = decide_to_generate(state)
    assert next_node == "transform_query"


def test_decide_evaluation_grounded_ends():
    """When generated response is grounded, route to END."""
    state: DeepResearchState = {
        "raw_query": "Test query",
        "transformed_query": None,
        "documents": [{"content": "Doc", "source": "Source"}],
        "web_search_needed": False,
        "hallucination_grade": "grounded",
        "final_response": "Verified answer [1].",
        "citations": [{"citation_id": "[1]", "source": "Source", "quote": "Doc"}],
        "loop_step": 0,
    }

    next_node = decide_evaluation(state)
    assert next_node == END


def test_decide_evaluation_circuit_breaker():
    """When loop_step >= 3, force termination to prevent infinite loops."""
    state: DeepResearchState = {
        "raw_query": "Test query",
        "transformed_query": None,
        "documents": [],
        "web_search_needed": True,
        "hallucination_grade": "hallucinated",
        "final_response": "Hallucinated answer",
        "citations": [],
        "loop_step": 3,
    }

    next_node = decide_evaluation(state)
    assert next_node == END
