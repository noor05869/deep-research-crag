"""
deep_research/generator.py
--------------------------
Grounded Synthesizer Node for Corrective RAG.
Reads the verified documents from state["documents"], synthesizes a concise,
authoritative answer with inline citation tags ([1], [2]), and extracts
structured citation metadata for auditability.
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
# 1. PYDANTIC SCHEMAS: Structured Response & Citations
# =====================================================================
class CitationItem(BaseModel):
    """Represents an individual source citation supporting a claim."""
    citation_id: str = Field(
        description="The numerical marker used in the answer, e.g., '[1]' or '[2]'."
    )
    source: str = Field(
        description="The document title or web URL where this fact originated."
    )
    quote: str = Field(
        description="Exact verbatim excerpt from the document proving the claim."
    )


class SynthesizedReport(BaseModel):
    """The complete grounded report containing the text and citation map."""
    answer: str = Field(
        description="Factual, structured research response with inline citation tags like [1] or [2]."
    )
    citations: List[CitationItem] = Field(
        default_factory=list,
        description="List of all citations corresponding to the numerical markers in the answer."
    )


# =====================================================================
# 2. PROMPT & CHAIN SETUP
# =====================================================================
GENERATOR_SYSTEM_PROMPT = """You are an expert AI Research Analyst and Enterprise Knowledge Assistant.
Your job is to synthesize a clear, comprehensive, and strictly factual answer to the user's question based ONLY on the provided numbered context documents.

Strict Directives:
1. FACTUAL GROUNDING: Rely exclusively on the provided context. Do NOT invent, assume, or extrapolate facts.
2. INLINE CITATIONS: Every factual claim, number, policy, or rule MUST be followed by an inline marker matching the source chunk, e.g., [1] or [2].
3. NO OUTSIDE KNOWLEDGE: If the provided documents do not contain enough information to fully answer the question, state clearly what is unknown.
4. CITATION MAPPING: For every marker used in your answer, you MUST create a matching CitationItem containing the source and an exact verbatim quote."""

GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", GENERATOR_SYSTEM_PROMPT),
    (
        "human",
        "CONTEXT DOCUMENTS:\n{formatted_context}\n\n"
        "USER QUESTION: {question}\n\n"
        "Synthesize grounded response:"
    )
])


def build_generator_chain():
    """Initializes the synthesis chain using Gemini Flash Lite with structured output."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0.1  # Very low temperature for factual accuracy
    )
    return GENERATOR_PROMPT | llm.with_structured_output(SynthesizedReport)


# =====================================================================
# 3. HELPER: Format Numbered Context
# =====================================================================
def format_context_for_synthesis(documents: List[Dict[str, Any]]) -> str:
    """
    Formats the list of documents into numbered blocks [1], [2], etc.
    so the LLM can reference them cleanly.
    """
    if not documents:
        return "No reference documents available."

    formatted_blocks = []
    for idx, doc in enumerate(documents, start=1):
        source = doc.get("source", "Unknown Source")
        content = doc.get("content", "").strip()
        formatted_blocks.append(f"[{idx}] Source: {source}\nContent:\n{content}")

    return "\n\n---\n\n".join(formatted_blocks)


# =====================================================================
# 4. LANGGRAPH NODE FUNCTION: Generate
# =====================================================================
def generate_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Synthesizes the final response and citations from state["documents"].

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state update: {"final_response": str, "citations": [...]}
    """
    question = state["raw_query"]
    documents = state.get("documents", [])

    print(f"\n[✍️ Generator Node] Synthesizing grounded answer from {len(documents)} document(s)...")

    if not documents:
        print("  • Warning: Zero documents in state. Returning fallback notice.")
        return {
            "final_response": "I apologize, but I could not find verified internal documents or web results to answer your question.",
            "citations": []
        }

    formatted_context = format_context_for_synthesis(documents)
    generator_chain = build_generator_chain()

    try:
        report: SynthesizedReport = generator_chain.invoke({
            "formatted_context": formatted_context,
            "question": question
        })

        print(f"  • Successfully synthesized response with {len(report.citations)} verified citation(s).")

        return {
            "final_response": report.answer,
            "citations": [c.model_dump() for c in report.citations]
        }

    except Exception as e:
        print(f"  • Generation Error: {e}")
        return {
            "final_response": f"An error occurred while generating the answer: {str(e)}",
            "citations": []
        }


# =====================================================================
# 5. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("Testing Generator Node in isolation...")

    test_state: DeepResearchState = {
        "raw_query": "What are the rules for research loans at the museum, and how long can fossils be borrowed?",
        "transformed_query": None,
        "documents": [
            {
                "content": "Researchers must request an appointment at least ten business days before a collection visit. Include the research purpose and accession numbers of interest. External loans require curator approval and a signed loan agreement. The standard loan period is 60 calendar days.",
                "source": "Museum Fossil Collection Procedures",
                "doc_id": "doc_museum_001"
            },
            {
                "content": "Borrowers must obtain written permission before sampling, scanning with treatments, or making any permanent alteration.",
                "source": "Museum Fossil Collection Procedures",
                "doc_id": "doc_museum_001"
            }
        ],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0
    }

    result = generate_node(test_state)

    print("\n" + "=" * 80)
    print("FINAL GENERATED RESPONSE:")
    print("=" * 80)
    print(result["final_response"])

    print("\n" + "=" * 80)
    print("STRUCTURED CITATIONS MAP:")
    print("=" * 80)
    for c in result["citations"]:
        print(f"\n{c['citation_id']} Source: {c['source']}")
        print(f"    Verbatim Quote: \"{c['quote']}\"")