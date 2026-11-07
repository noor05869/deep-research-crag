"""
deep_research/graph.py
----------------------
LangGraph StateGraph assembly for DeepResearch-CRAG.
Wires together all nodes, conditional edges, and safety circuit breakers into an
executable Corrective-RAG & Self-RAG state machine:
1. Internal Vector Retrieval (Qdrant)
2. Document Relevance Grading (Self-RAG noise filter)
3. Query Rewriting & Live Web Search Fallback (DuckDuckGo)
4. Grounded Synthesis with Verifiable Citations
5. Dual-Audit Hallucination & Relevance Checker
"""

import sys
import os
import warnings
import logging
from typing import Dict, Any, Literal
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Windows PowerShell terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

load_dotenv()

from langgraph.graph import StateGraph, START, END

try:
    from deep_research.state import DeepResearchState
    from deep_research.retriever import retrieve_node
    from deep_research.grader import grade_documents_node
    from deep_research.tools import transform_query_node, web_search_node
    from deep_research.generator import generate_node
    from deep_research.evaluator import check_hallucination_node
except ModuleNotFoundError:
    from state import DeepResearchState
    from retriever import retrieve_node
    from grader import grade_documents_node
    from tools import transform_query_node, web_search_node
    from generator import generate_node
    from evaluator import check_hallucination_node


# =====================================================================
# 1. CONDITIONAL ROUTING FUNCTIONS (DECISION GATES)
# =====================================================================
def decide_to_generate(state: DeepResearchState) -> Literal["transform_query", "generate"]:
    """
    Conditional Routing Gate 1:
    Audits whether retrieved documents are sufficient to generate an answer.
    
    If internal documents are irrelevant or insufficient (web_search_needed == True),
    diverts the state machine to query transformation and live web search.
    Otherwise, routes straight to answer generation.
    """
    web_search_needed = state.get("web_search_needed", False)

    if web_search_needed:
        print("\n[🔀 Router: Gate 1] Insufficient/Irrelevant internal coverage -> Diverting to 'transform_query' (Web Search).")
        return "transform_query"
    else:
        print("\n[🔀 Router: Gate 1] Sufficient internal documents verified -> Routing directly to 'generate'.")
        return "generate"


def decide_evaluation(state: DeepResearchState) -> Literal["transform_query", "__end__"]:
    """
    Conditional Routing Gate 2:
    Audits the generated answer for factual grounding and relevance.
    Includes an anti-infinite loop circuit breaker.

    Routing outcomes:
    1. Circuit Breaker: If loop_step >= 3, terminate to prevent runaway API spend.
    2. Audit Passed ('grounded'): Deliver verified report to user (END).
    3. Audit Failed ('hallucinated'): Re-route to 'transform_query' to fetch corrective facts.
    """
    loop_step = state.get("loop_step", 0)

    # 1. Circuit Breaker Guard
    if loop_step >= 3:
        print(f"\n[⚠️ Router Circuit Breaker] Max corrective loops reached ({loop_step}/3). Forcing termination -> END.")
        return END

    # 2. Quality Audit Check
    hallucination_grade = state.get("hallucination_grade", "grounded")

    if hallucination_grade == "grounded":
        print("\n[🎯 Router: Gate 2] Answer verified (grounded & relevant) -> Routing to END.")
        return END
    else:
        print("\n[🔄 Router: Gate 2] Answer failed audit (hallucinated/off-topic) -> Re-routing to 'transform_query' for live search.")
        return "transform_query"


# =====================================================================
# 2. GRAPH ASSEMBLY & COMPILATION
# =====================================================================
def build_research_graph():
    """
    Constructs and compiles the complete Corrective-RAG StateGraph.

    Returns:
        CompiledStateGraph: The compiled executable state machine.
    """
    workflow = StateGraph(DeepResearchState)

    # 1. Register all nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("transform_query", transform_query_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("check_hallucination", check_hallucination_node)

    # 2. Define deterministic edges
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # 3. Define conditional edge: Grader -> (transform_query | generate)
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        }
    )

    # 4. Fallback search pipeline edges
    workflow.add_edge("transform_query", "web_search")
    workflow.add_edge("web_search", "generate")

    # 5. Generator to Evaluator edge
    workflow.add_edge("generate", "check_hallucination")

    # 6. Define conditional edge: Evaluator -> (transform_query | END)
    workflow.add_conditional_edges(
        "check_hallucination",
        decide_evaluation,
        {
            "transform_query": "transform_query",
            END: END,
        }
    )

    return workflow.compile()


# Create a reusable singleton instance of the compiled graph
app = build_research_graph()


# =====================================================================
# 3. HIGH-LEVEL EXECUTION API
# =====================================================================
def run_research(query: str) -> DeepResearchState:
    """
    Convenience function to run a query through the full research pipeline.

    Args:
        query: The raw user prompt or research question.

    Returns:
        Final DeepResearchState after all nodes and audits complete.
    """
    initial_state: DeepResearchState = {
        "raw_query": query,
        "transformed_query": None,
        "documents": [],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0,
    }
    return app.invoke(initial_state)


# =====================================================================
# 4. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 DeepResearch-CRAG: End-to-End State Machine Verification")
    print("=" * 70)

    # Test Query: Internal Company Policy (Should be resolved using internal vector store)
    test_query = "What are the core hours and remote work days allowed for employees?"
    print(f"\nUser Query: '{test_query}'\n")

    result = run_research(test_query)

    print("\n" + "=" * 70)
    print("🏁 FINAL GENERATED REPORT:")
    print("=" * 70)
    print(result.get("final_response", "No response generated."))

    print("\n📑 VERIFIED CITATIONS:")
    citations = result.get("citations", [])
    if citations:
        for cit in citations:
            print(f"  • {cit.get('citation_id')} Source: {cit.get('source')}")
            print(f"    Quote: \"{cit.get('quote')}\"\n")
    else:
        print("  • No citations recorded.")

    print(f"Final Loop Step Count: {result.get('loop_step')}")
    print(f"Hallucination Audit Result: {result.get('hallucination_grade')}")
