"""
deep_research
-------------
Autonomous Deep Research & Corrective-RAG (CRAG) Agent package.
"""

from deep_research.state import DeepResearchState
from deep_research.grader import grade_documents_node
from deep_research.retriever import retrieve_node
from deep_research.tools import transform_query_node, web_search_node
from deep_research.generator import generate_node
from deep_research.evaluator import check_hallucination_node
from deep_research.graph import app, build_research_graph, run_research
from deep_research.api import api

__all__ = [
    "DeepResearchState",
    "grade_documents_node",
    "retrieve_node",
    "transform_query_node",
    "web_search_node",
    "generate_node",
    "check_hallucination_node",
    "app",
    "build_research_graph",
    "run_research",
    "api",
]
