"""
deep_research/tools.py
----------------------
Query Transformation and Web Search Fallback nodes for Corrective RAG.
1. Query Rewriter: Converts conversational user questions into targeted keyword search queries.
2. Web Search Tool: Searches the live web using DuckDuckGo (ddgs) when internal documents fail.
"""

import sys
import os
import warnings
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Windows PowerShell terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)

load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

try:
    from deep_research.state import DeepResearchState
except ModuleNotFoundError:
    from state import DeepResearchState


# =====================================================================
# 1. PYDANTIC SCHEMA: Strict Query Rewrite Output
# =====================================================================
class QueryRewrite(BaseModel):
    """Pydantic model for structured query rewrite."""
    search_query: str = Field(
        description="Optimized keyword search query stripped of conversational filler words."
    )
    rationale: str = Field(
        description="Brief explanation of why this search query will yield better web results."
    )


# =====================================================================
# 2. QUERY REWRITER PROMPT & CHAIN
# =====================================================================
REWRITER_SYSTEM_PROMPT = """You are an expert AI search query optimizer.
Your task is to take a user's conversational, complex, or messy question and rewrite it into a concise, high-signal web search query.

Rules:
1. Strip all conversational filler (e.g., 'Can you tell me', 'I was wondering', 'Please explain').
2. Keep the core subject, exact technical terms, version numbers, and specific entities.
3. Target factual search engine results (like documentation, announcements, or Wikipedia).
4. Do NOT answer the question. Only output the optimized search query."""

REWRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REWRITER_SYSTEM_PROMPT),
    ("human", "Original user question: {question}\n\nOptimized search query:")
])


def build_query_rewriter():
    """Builds the query transformation chain using Gemini."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0.0
    )
    return REWRITER_PROMPT | llm.with_structured_output(QueryRewrite)


# =====================================================================
# 3. LANGGRAPH NODE 1: Transform Query
# =====================================================================
def transform_query_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Rewrites the raw query into an optimized web search query.

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state update: {"transformed_query": str}
    """
    raw_query = state["raw_query"]
    print(f"\n[🔄 Query Rewriter Node] Analyzing query: '{raw_query}'")

    rewriter = build_query_rewriter()
    try:
        result: QueryRewrite = rewriter.invoke({"question": raw_query})
        optimized = result.search_query.strip()
        print(f"  • Optimized Web Query: '{optimized}'")
        print(f"  • Rationale: {result.rationale}")
        return {"transformed_query": optimized}
    except Exception as e:
        print(f"  • Rewriter Error: {e}. Falling back to raw query.")
        return {"transformed_query": raw_query}


# =====================================================================
# 4. LANGGRAPH NODE 2: Web Search Fallback
# =====================================================================
def web_search_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Searches live DuckDuckGo for the transformed query
    and appends web results to state["documents"].

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state update: {"documents": [...], "loop_step": 1}
    """
    query = state.get("transformed_query") or state.get("raw_query")
    print(f"\n[🌐 Web Search Node] Searching live web for: '{query}'")

    web_docs: List[Dict[str, Any]] = []

    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=3))

        for idx, item in enumerate(raw_results, start=1):
            title = item.get("title", "Web Result")
            snippet = item.get("body", "")
            url = item.get("href", "https://duckduckgo.com")

            web_docs.append({
                "content": f"Title: {title}\nSummary: {snippet}",
                "source": url,
                "doc_id": f"web_{idx}"
            })
            print(f"  • Web Result #{idx}: {title[:50]}... ({url[:40]}...)")

    except Exception as e:
        print(f"  • Web Search Error: {e}")

    # Note: loop_step increments by 1 via our Annotated reducer to prevent infinite loops!
    return {
        "documents": web_docs,
        "loop_step": 1
    }


# =====================================================================
# 5. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("Testing Query Rewriter & Web Search Nodes in isolation...")

    test_state: DeepResearchState = {
        "raw_query": "Hey there! Can you please tell me is there any latest movie of lord of the ring realsing in 2027 ?",
        "transformed_query": None,
        "documents": [],
        "web_search_needed": True,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0
    }

    # 1. Test Query Rewriter Node
    rewrite_update = transform_query_node(test_state)
    test_state.update(rewrite_update)

    # 2. Test Web Search Node
    search_update = web_search_node(test_state)

    print("\nResulting State Update from Web Search:")
    print(f"  Total Web Documents Fetched: {len(search_update['documents'])}")
    for doc in search_update["documents"]:
        print(f"\n  Source URL: {doc['source']}")
        print(f"  Snippet:    {doc['content'][:140]}...")