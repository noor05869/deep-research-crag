"""
deep_research/retriever.py
--------------------------
Internal Knowledge Base Retriever Node for Corrective RAG.
Splits internal policy documents, embeds them using local HuggingFace embeddings,
and retrieves top-k chunks into the LangGraph state.
Also supports dynamic ingestion of user-uploaded files at runtime.
"""

import sys
import os
import warnings
import logging
from typing import List, Dict, Any

# Ensure UTF-8 output encoding for Windows PowerShell terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")
logging.getLogger("google.genai").setLevel(logging.ERROR)

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

try:
    from deep_research.state import DeepResearchState
    from deep_research.knowledge_base import INTERNAL_DOCUMENTS
except ModuleNotFoundError:
    from state import DeepResearchState
    from knowledge_base import INTERNAL_DOCUMENTS


# =====================================================================
# 1. INITIALIZE VECTOR STORE IN MEMORY
# =====================================================================
print("[⚙️ Retriever] Initializing local vector database...")

# Lightweight 384-dimensional local embeddings (Zero API cost, CPU-friendly)
EMBEDDINGS = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Split documents into semantic paragraphs
splitter = RecursiveCharacterTextSplitter(
   chunk_size=1000,      # Increased from 400
    chunk_overlap=150,    # Increased from 50
    separators=["\n\n", "\n", ". "]
)

raw_docs = []
for item in INTERNAL_DOCUMENTS:
    chunks = splitter.split_text(item["content"])
    for idx, chunk in enumerate(chunks):
        raw_docs.append(Document(
            page_content=chunk.strip(),
            metadata={
                "source": item["title"],
                "doc_id": item["doc_id"],
                "chunk_id": f"{item['doc_id']}_c{idx+1}"
            }
        )
    )

# Create in-memory Qdrant instance
VECTORSTORE = QdrantVectorStore.from_documents(
    documents=raw_docs,
    embedding=EMBEDDINGS,
    location=":memory:",
    collection_name="internal_knowledge"
)
RETRIEVER = VECTORSTORE.as_retriever(search_kwargs={"k": 5})
print(f"[✅ Retriever Ready] Indexed {len(raw_docs)} chunks in memory.")


# =====================================================================
# 1B. DYNAMIC INGESTION: Add Custom Uploaded Documents
# =====================================================================
def add_custom_document(content: str, filename: str) -> int:
    """
    Splits, embeds, and indexes an uploaded file into the active Qdrant vector store.

    Args:
        content: Extracted raw text from the uploaded file (.txt, .md, .pdf, .csv).
        filename: Name of the file (e.g. 'annual_report.pdf') used for citation source attribution.

    Returns:
        int: Total number of chunk passages indexed into Qdrant.
    """
    if not content or not content.strip():
        print(f"[⚠️ Ingest] Empty content received for '{filename}'. Skipping.")
        return 0

    chunks = splitter.split_text(content.strip())
    new_docs = [
        Document(
            page_content=chunk.strip(),
            metadata={
                "source": filename,
                "doc_id": f"upload_{filename}",
                "chunk_id": f"upload_{filename}_c{idx+1}"
            }
        )
        for idx, chunk in enumerate(chunks) if chunk.strip()
    ]

    if new_docs:
        VECTORSTORE.add_documents(new_docs)
        print(f"[📄 Ingest] Successfully indexed {len(new_docs)} chunk(s) from '{filename}' into Qdrant.")

    return len(new_docs)


# =====================================================================
# 2. LANGGRAPH NODE FUNCTION
# =====================================================================
def retrieve_node(state: DeepResearchState) -> Dict[str, Any]:
    """
    LangGraph Node: Searches internal knowledge base for relevant chunks.

    Args:
        state: Current DeepResearchState

    Returns:
        Partial state dictionary update: {"documents": [...]}
    """
    query = state.get("transformed_query") or state.get("raw_query")
    print(f"\n[📚 Retriever Node] Searching internal knowledge base for: '{query}'")

    matched_docs = RETRIEVER.invoke(query)

    retrieved_items: List[Dict[str, Any]] = []
    for doc in matched_docs:
        retrieved_items.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Internal Knowledge Base"),
            "doc_id": doc.metadata.get("doc_id", "unknown"),
        })

    print(f"  • Retrieved {len(retrieved_items)} candidate chunk(s) from internal knowledge.")
    return {"documents": retrieved_items}


# =====================================================================
# 3. STANDALONE VERIFICATION TEST
# =====================================================================
if __name__ == "__main__":
    print("\nTesting Retriever Node in isolation...")

    test_state: DeepResearchState = {
        "raw_query": "How many days in advance must a fossil loan appointment be requested?",
        "transformed_query": None,
        "documents": [],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0
    }

    result = retrieve_node(test_state)

    print("\nResulting State Update (Documents retrieved):")
    for idx, d in enumerate(result["documents"], start=1):
        print(f"\n[{idx}] Source: {d['source']}")
        print(f"    Excerpt: {d['content'][:140]}...")
