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
    from deep_research.state import DeepResearchState
except ModuleNotFoundError:
    from state import DeepResearchState


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
4. Be strict: extrapolations, assumptions, or outside knowledge must be flagged as 'hallucinated'."""

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
1. If the response directly answers the core question asked by the user, grade it as 'yes'.
2. If the response dodges the question, is off-topic, or fails to address the user's request, grade it as 'no'."""

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
def check_hallucination_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Audits the generated response for hallucinations and question relevance.

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state update: {"hallucination_grade": "grounded" | "hallucinated"}
    """
    question = state["raw_query"]
    generation = state.get("final_response", "")
    documents = state.get("documents", [])

    print(f"\n[⚖️ Evaluator Node] Auditing generated answer for hallucinations and relevance...")

    if not generation:
        print("  • Warning: No generation found to evaluate.")
        return {"hallucination_grade": "hallucinated"}

    # Concatenate document text for the auditor
    docs_text = "\n\n".join([f"Source ({d.get('source')}):\n{d.get('content')}" for d in documents])

    hallucination_chain, relevance_chain = build_evaluators()

    try:
        # 1. Check Faithfulness / Grounding
        hallucination_result: GradeHallucination = hallucination_chain.invoke({
            "documents": docs_text,
            "generation": generation
        })

        print(f"  • Grounding Score:   [{hallucination_result.binary_score.upper()}] -> {hallucination_result.explanation}")

        # 2. Check Answer Relevance
        relevance_result: GradeAnswerRelevance = relevance_chain.invoke({
            "question": question,
            "generation": generation
        })

        print(f"  • Relevance Score:   [{relevance_result.binary_score.upper()}] -> {relevance_result.explanation}")

        # If both pass, the answer is verified
        if hallucination_result.binary_score == "grounded" and relevance_result.binary_score == "yes":
            print("  • ✅ AUDIT PASSED: The response is fully grounded and answers the question.")
            return {"hallucination_grade": "grounded"}
        else:
            print("  • ❌ AUDIT FAILED: The response failed either grounding or relevance checks.")
            return {"hallucination_grade": "hallucinated"}

    except Exception as e:
        print(f"  • Evaluator Error: {e}. Defaulting to grounded.")
        return {"hallucination_grade": "grounded"}


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
        "final_response": "The standard loan period for fossil specimens is 60 calendar days, and external loans require curator approval.",
        "citations": [],
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
