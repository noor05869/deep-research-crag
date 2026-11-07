"""
src/deep_research/grader.py
----------------------------------------
Implements the Document Grader node for Corrective-RAG (CRAG).
Evaluates retrieved context documents for relevance against the user query.
Filters out noise and decides if a fallback Web Search is required.
"""

import os
import sys
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)

# Ensure UTF-8 output encoding for Windows PowerShell terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from typing import Literal, Dict, Any, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from deep_research.state import DeepResearchState
except ModuleNotFoundError:
    from state import DeepResearchState

load_dotenv()


# =====================================================================
# 1. PYDANTIC SCHEMA: Strict Binary Grading
# =====================================================================
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved document."""

    binary_score: Literal["yes", "no"] = Field(
        description="Document is relevant to the question: 'yes' or 'no'"
    )
    reasoning: str = Field(
        description="Brief 1-sentence explanation of why the document is or is not relevant."
    )


# =====================================================================
# 2. PROMPT & CHAIN SETUP
# =====================================================================
GRADER_SYSTEM_PROMPT = """You are an objective quality inspector grading the relevance of a retrieved document to a user query.

Evaluation Rules:
1. If the document contains semantic keywords, concepts, or direct facts related to the user's query, grade it as 'yes'.
2. It does not need to be a stringent test; the goal is to filter out completely irrelevant, noisy, or off-topic context.
3. If the document is irrelevant or off-topic, grade it as 'no'.
4. Provide a 1-sentence factual reasoning for your decision."""

GRADER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", GRADER_SYSTEM_PROMPT),
    (
        "human",
        "Retrieved Document:\n\n{document}\n\nUser Query: {question}\n\nGrade relevance:"
    ),
])


def build_document_grader():
    """Initializes the fast structured grader chain using Gemini."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0.0,  # Zero temperature for deterministic classification
    )
    # Force structured output conforming to our Pydantic schema
    return GRADER_PROMPT | llm.with_structured_output(GradeDocuments)


# =====================================================================
# 3. LANGGRAPH NODE FUNCTION: The State Transition
# =====================================================================
def grade_documents_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node that reads documents from the state, filters out irrelevant ones,
    and flags whether an external web search is needed.

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state dictionary update: {"documents": [...], "web_search_needed": bool}
    """
    question = state.get("transformed_query") or state.get("raw_query")
    documents = state.get("documents", [])

    print(f"\n[🔍 Grader Node] Inspecting {len(documents)} retrieved document(s)...")

    grader_chain = build_document_grader()
    filtered_docs: List[Dict[str, Any]] = []
    web_search_needed = False

    if not documents:
        print("[⚠️ Grader Node] Zero documents retrieved. Web search immediately required.")
        return {"documents": [], "web_search_needed": True}

    for idx, doc in enumerate(documents, start=1):
        content = doc.get("content", "")
        source = doc.get("source", "unknown")

        try:
            grade: GradeDocuments = grader_chain.invoke({
                "question": question,
                "document": content
            })

            if grade.binary_score.lower() == "yes":
                print(f"  • Doc #{idx} [{source[:30]}...]: ✅ RELEVANT -> {grade.reasoning}")
                filtered_docs.append(doc)
            else:
                print(f"  • Doc #{idx} [{source[:30]}...]: ❌ IRRELEVANT -> {grade.reasoning}")
                # Any noise or insufficient coverage flags that web search can supplement
                web_search_needed = True

        except Exception as e:
            print(f"  • Doc #{idx} Grading Error: {e}. Defaulting to keep.")
            filtered_docs.append(doc)

    # If all docs were rejected, we MUST trigger web search
    if len(filtered_docs) == 0:
        print("[🚨 Grader Node] All documents were rejected as irrelevant. Fallback to Web Search triggered.")
        web_search_needed = True

    return {
        "documents": filtered_docs,
        "web_search_needed": web_search_needed,
    }


# =====================================================================
# 4. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("Testing Document Grader Node in isolation...")

    test_state: DeepResearchState = {
        "raw_query": "How does Docker container memory limit work in Linux?",
        "transformed_query": None,
        "documents": [
            {
                "content": "Linux cgroups (control groups) allow the kernel to restrict and isolate memory allocation for processes inside a Docker container. When exceeded, the OOM killer triggers.",
                "source": "linux_kernel_docs.md",
                "score": 0.92
            },
            {
                "content": "Making homemade pizza requires bread flour with at least 12% protein content and a high-temperature pizza oven.",
                "source": "cooking_recipe.txt",
                "score": 0.35
            }
        ],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0
    }

    result = grade_documents_node(test_state)
    print("\nResulting State Update:")
    print(f"  Retained Documents: {len(result['documents'])}")
    print(f"  Web Search Needed:  {result['web_search_needed']}")