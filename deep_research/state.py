"""
src/deep_research/state.py
--------------------------
Defines the central State Schema for our Corrective RAG (CRAG) Agent.
This state acts as the shared memory whiteboard that flows through every node
in the LangGraph state machine.
"""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
import operator


def merge_documents(existing: List[Dict[str, Any]], new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Custom reducer function to merge retrieved documents without duplicates.
    Prevents duplicate chunks from blowing up the LLM context window.
    """
    if not existing:
        return new
    existing_ids = {doc.get("id") or doc.get("content")[:50] for doc in existing}
    merged = list(existing)
    for doc in new:
        doc_id = doc.get("id") or doc.get("content")[:50]
        if doc_id not in existing_ids:
            merged.append(doc)
            existing_ids.add(doc_id)
    return merged


class DeepResearchState(TypedDict):
    """
    The complete state payload passed between nodes in our LangGraph workflow.
    """

    # 1. User Inputs
    raw_query: str
    """The original raw question or research topic submitted by the user."""

    transformed_query: Optional[str]
    """The query optimized by our Query Rewriter node for vector or web search."""

    # 2. Retrieved Context & Knowledge
    documents: Annotated[List[Dict[str, Any]], merge_documents]
    """
    List of document chunks retrieved from internal vector store or external web.
    Each item contains: {"content": str, "source": str, "score": float}
    Annotated with merge_documents reducer to append unique documents across loops.
    """

    # 3. Decision Flags & Routing Signals
    web_search_needed: bool
    """Flag set to True by the Document Grader if internal documents are irrelevant or insufficient."""

    hallucination_grade: Optional[str]
    """Evaluation signal: 'grounded' if the answer is backed by facts, 'hallucinated' if not."""

    # 4. Final Output & Citations
    final_response: Optional[str]
    """The final synthesized research report generated for the user."""

    citations: Annotated[List[Dict[str, str]], operator.add]
    """
    List of verified citations backing the claims.
    Format: [{"citation_id": "[1]", "source": "https://...", "quote": "..."}]
    """

    # 5. Production Circuit Breakers (Anti-Infinite Loop)
    loop_step: Annotated[int, operator.add]
    """
    Counter incremented on each corrective loop.
    Acts as a safety circuit breaker: if loop_step >= 3, force termination to prevent runaway API costs.
    """                                                                                             