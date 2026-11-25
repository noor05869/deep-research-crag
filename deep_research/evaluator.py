"""
deep_research/evaluator.py
--------------------------
Hallucination and Answer Relevance Evaluator for Corrective RAG (Self-RAG).
Acts as an internal quality auditor before responses are finalized:
1. Checks Faithfulness: Is the generated response grounded in the retrieved documents?
2. Checks Relevance: Did the response actually answer the user's question?
"""

import sys
import os
import warnings
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Windows PowerShell terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")
# Silence Google GenAI SDK logging
logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from deep_research.state import DeepResearchState, MAX_CORRECTIVE_LOOPS
    from deep_research.generator import format_context_for_synthesis
except ModuleNotFoundError:
    from state import DeepResearchState, MAX_CORRECTIVE_LOOPS
    from generator import format_context_for_synthesis


# =====================================================================
# 1. PYDANTIC SCHEMAS: Strict Evaluation Output
# =====================================================================
class GradeHallucination(BaseModel):
    """Binary assessment of whether the answer is grounded in facts."""
    binary_score: Literal["grounded", "hallucinated"] = Field(
        description="Select 'grounded' if all claims are backed by the documents. Select 'hallucinated' if there are unverified facts."
    )
    explanation: str = Field(
        description="Factual breakdown of whether all statements are supported by the provided facts."
    )


class GradeAnswerRelevance(BaseModel):
    """Binary assessment of whether the answer resolves the user's query."""
    binary_score: Literal["yes", "no"] = Field(
        description="Select 'yes' if the answer directly addresses the question, 'no' if it is evasive or off-topic."
    )
    explanation: str = Field(
        description="Brief explanation of how the answer addresses the user's specific query."
    )


# =====================================================================
# 2. PROMPT TEMPLATES
# =====================================================================
HALLUCINATION_SYSTEM_PROMPT = """You are a rigorous, zero-tolerance fact-checking auditor.
Your job is to assess whether an LLM generation is strictly grounded in and supported by the reference documents.

Grading Rules:
1. Compare every statement in the generated answer against the reference documents.
2. If the answer contains ANY facts, numbers, dates, or assertions NOT present in the reference documents, grade it as 'hallucinated'.
3. If all claims are completely grounded in the documents, grade it as 'grounded'.
4. Each cited claim must be supported by the numbered document it cites.
5. Identify the specific unsupported claims or evidence needed to correct the answer."""

HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", HALLUCINATION_SYSTEM_PROMPT),
    (
        "human",
        "REFERENCE DOCUMENTS:\n{documents}\n\n"
        "GENERATED ANSWER:\n{generation}\n\n"
        "Perform hallucination audit:"
    )
])

ANSWER_RELEVANCE_SYSTEM_PROMPT = """You are an objective evaluator assessing whether a generated answer actually resolves the user's question.

Grading Rules:
1. Grade 'yes' only if the answer addresses every material part of the question.
2. Otherwise grade 'no' and specify the missing information needed to answer the question."""

ANSWER_RELEVANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ANSWER_RELEVANCE_SYSTEM_PROMPT),
    (
        "human",
        "USER QUESTION:\n{question}\n\n"
        "GENERATED ANSWER:\n{generation}\n\n"
        "Grade answer relevance:"
    )
])


def build_evaluators():
    """Initializes the hallucination and relevance chains using Gemini Flash Lite."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0.0  # Zero temperature for deterministic audit
    )
    hallucination_grader = HALLUCINATION_PROMPT | llm.with_structured_output(GradeHallucination)
    relevance_grader = ANSWER_RELEVANCE_PROMPT | llm.with_structured_output(GradeAnswerRelevance)
    return hallucination_grader, relevance_grader


# =====================================================================
# 3. LANGGRAPH NODE FUNCTION: Hallucination Check
# =====================================================================
def failed_audit(state: DeepResearchState, grade: str, missing_evidence: str) -> Dict[str, Any]:
    update = {"hallucination_grade": grade, "missing_evidence": missing_evidence}
    if state.get("loop_step", 0) >= MAX_CORRECTIVE_LOOPS:
        update["final_response"] = "Unable to verify an answer with the available evidence."
        update["citations"] = []
    return update


def check_hallucination_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Audits the generated response for hallucinations and question relevance.

    Args:
        state: Current DeepResearchState

    Returns:
        Audit status, validated citations on success, or evidence gaps on rejection.
    """
    question = state["raw_query"]
    generation = state.get("final_response", "")
    documents = state.get("documents", [])

    print(f"\n[⚖️ Evaluator Node] Auditing generated answer for hallucinations and relevance...")

    markers = set(re.findall(r"\[\d+\]", generation or ""))
    citations = state.get("citations", [])
    citation_ids = {citation["citation_id"] for citation in citations}
    if not markers or markers != citation_ids or len(citations) != len(citation_ids):
        return failed_audit(state, "hallucinated", "Find evidence that can support the answer with valid citations.")

    chunks = {f"[{index}]": doc for index, doc in enumerate(documents, start=1)}
    verified_citations = []
    for citation in citations:
        chunk = chunks.get(citation["citation_id"])
        quote = citation["quote"].strip()
        if not chunk or not quote or quote not in chunk.get("content", ""):
            return failed_audit(state, "hallucinated", "Find evidence with an exact supporting excerpt.")
        verified_citations.append({**citation, "source": chunk.get("source", "Unknown Source"), "quote": quote})

    try:
        hallucination_chain, relevance_chain = build_evaluators()
        # Run Faithfulness and Answer Relevance checks concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_hallucination = executor.submit(
                hallucination_chain.invoke,
                {"documents": format_context_for_synthesis(documents), "generation": generation}
            )
            future_relevance = executor.submit(
                relevance_chain.invoke,
                {"question": question, "generation": generation}
            )
            hallucination_result: GradeHallucination = future_hallucination.result()
            relevance_result: GradeAnswerRelevance = future_relevance.result()

        print(f"  • Grounding Score:   [{hallucination_result.binary_score.upper()}] -> {hallucination_result.explanation}")
        print(f"  • Relevance Score:   [{relevance_result.binary_score.upper()}] -> {relevance_result.explanation}")

        # If both pass, the answer is verified
        if hallucination_result.binary_score == "grounded" and relevance_result.binary_score == "yes":
            print("  • ✅ AUDIT PASSED: The response is fully grounded and answers the question.")
            return {"hallucination_grade": "grounded", "citations": verified_citations, "missing_evidence": ""}
        else:
            print("  • ❌ AUDIT FAILED: The response failed either grounding or relevance checks.")
            gaps = []
            if hallucination_result.binary_score != "grounded":
                gaps.append(hallucination_result.explanation)
            if relevance_result.binary_score != "yes":
                gaps.append(relevance_result.explanation)
            return failed_audit(state, "hallucinated", " ".join(gaps))

    except Exception as e:
        print(f"  • Evaluator Error: {e}")
        return failed_audit(state, "audit_failed", state.get("missing_evidence", ""))


# =====================================================================
# 4. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("Testing Evaluator Node in isolation...\n")

    sample_context = [
        {
            "content": "The standard loan period for fossil specimens is 60 calendar days. External loans require curator approval.",
            "source": "Museum Fossil Collection Procedures"
        }
    ]

    # Test Case 1: Grounded answer (Should pass)
    grounded_state: DeepResearchState = {
        "raw_query": "What is the standard fossil loan period?",
        "transformed_query": None,
        "documents": sample_context,
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": "The standard loan period for fossil specimens is 60 calendar days [1].",
        "citations": [{
            "citation_id": "[1]",
            "source": sample_context[0]["source"],
            "quote": "The standard loan period for fossil specimens is 60 calendar days.",
        }],
        "loop_step": 0
    }

    print("-" * 60)
    print("TEST 1: Evaluating a Grounded Answer...")
    print("-" * 60)
    res_1 = check_hallucination_node(grounded_state)
    print(f"Result 1: {res_1}\n")

    # Test Case 2: Hallucinated answer (Should be caught and rejected)
    hallucinated_state: DeepResearchState = {
        "raw_query": "What is the standard fossil loan period?",
        "transformed_query": None,
        "documents": sample_context,
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": "The standard loan period is 90 business days, and borrowers get a free $500 travel stipend from the museum.",
        "citations": [],
        "loop_step": 0
    }

    print("-" * 60)
    print("TEST 2: Evaluating a Hallucinated Answer...")
    print("-" * 60)
    res_2 = check_hallucination_node(hallucinated_state)
    print(f"Result 2: {res_2}")
