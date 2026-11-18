"""
deep_research/api.py
--------------------
Production FastAPI REST API wrapper for DeepResearch-CRAG.
Exposes async endpoints for health checks, research query execution,
and custom document ingestion (.pdf, .txt, .md, .csv) with full CORS support.
"""

import sys
import io
import time
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure UTF-8 output encoding for Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from deep_research.graph import app as research_graph
from deep_research.state import DeepResearchState
from deep_research.retriever import add_custom_document
from deep_research.knowledge_base import INTERNAL_DOCUMENTS


# =====================================================================
# 1. PYDANTIC SCHEMAS (REQUEST & RESPONSE MODELS)
# =====================================================================
class ResearchRequest(BaseModel):
    """Payload for initiating a deep research workflow."""
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The research question or topic submitted by the user.",
        examples=["What are the core hours and remote work days allowed for employees?"]
    )


class CitationResponse(BaseModel):
    """Verified citation backing a factual claim."""
    citation_id: str = Field(..., description="Numerical inline identifier, e.g. '[1]'")
    source: str = Field(..., description="Document title or web URL")
    quote: str = Field(..., description="Verbatim supporting quote from the source")


class DocumentItem(BaseModel):
    """Document chunk inspected by the agent."""
    content: str
    source: str
    doc_id: Optional[str] = None


class ResearchResponse(BaseModel):
    """Comprehensive structured output from the Corrective-RAG state machine."""
    query: str
    transformed_query: Optional[str] = None
    final_response: str
    citations: List[CitationResponse]
    web_search_needed: bool
    hallucination_grade: Optional[str] = None
    loop_step: int
    documents_count: int
    execution_time_seconds: float


class HealthResponse(BaseModel):
    """System and dependency health check status."""
    status: str
    engine: str
    vector_store: str
    llm: str


class UploadResponse(BaseModel):
    """Response returned upon successful file ingestion into Qdrant."""
    filename: str
    chunks_indexed: int
    message: str


# In-memory registry of active documents
ACTIVE_DOCUMENTS: List[str] = [doc["title"] for doc in INTERNAL_DOCUMENTS]


# =====================================================================
# 2. FASTAPI APPLICATION CONFIGURATION
# =====================================================================
api = FastAPI(
    title="DeepResearch-CRAG Engine API",
    description="Autonomous Corrective-RAG & Self-RAG Research Engine powered by LangGraph, Qdrant & Gemini",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend clients (Vite / Next.js / React)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# 3. ROUTE HANDLERS
# =====================================================================
@api.get("/", tags=["System"])
async def root():
    """Root welcome endpoint linking to API documentation."""
    return {
        "project": "DeepResearch-CRAG",
        "version": "1.1.0",
        "documentation": "/docs",
        "health": "/api/health",
        "documents": "/api/documents"
    }


@api.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Returns the operational status of the CRAG service."""
    return HealthResponse(
        status="healthy",
        engine="LangGraph StateMachine",
        vector_store="In-Memory Qdrant",
        llm="Google Gemini Flash Lite"
    )


@api.get("/api/documents", response_model=List[str], tags=["Knowledge"])
async def list_documents():
    """Returns the list of all documents currently indexed in the active vector store."""
    return ACTIVE_DOCUMENTS


@api.post(
    "/api/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    tags=["Knowledge"]
)
async def upload_document(file: UploadFile = File(...)):
    """
    Ingests and indexes a user-uploaded file (.txt, .md, .pdf, .csv, .json)
    directly into the active Qdrant vector database.
    """
    filename = file.filename or "uploaded_document"
    contents = await file.read()

    text = ""
    # 1. Handle PDF files using pypdf
    if filename.lower().endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(contents))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages_text).strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF file '{filename}': {str(e)}"
            )
    else:
        # 2. Handle Text, Markdown, CSV, JSON
        try:
            text = contents.decode("utf-8", errors="replace").strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode text file '{filename}': {str(e)}"
            )

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file '{filename}' contains no readable text."
        )

    # 3. Embed & Index into Qdrant
    chunks_count = await asyncio.to_thread(add_custom_document, text, filename)

    if filename not in ACTIVE_DOCUMENTS:
        ACTIVE_DOCUMENTS.append(filename)

    return UploadResponse(
        filename=filename,
        chunks_indexed=chunks_count,
        message=f"Successfully indexed {chunks_count} chunk(s) from '{filename}' into Qdrant."
    )


@api.post(
    "/api/research",
    response_model=ResearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Research"]
)
async def execute_research(request: ResearchRequest):
    """
    Executes the full Corrective-RAG research workflow:
    1. Internal Vector Retrieval (Qdrant)
    2. Document Relevance Quality Gate (Self-RAG)
    3. Query Rewriting & Live DuckDuckGo Search (if needed)
    4. Grounded Synthesis with Verifiable Inline Footnotes
    5. Dual-Vector Hallucination & Relevance Audit
    """
    start_time = time.time()

    initial_state: DeepResearchState = {
        "raw_query": request.query.strip(),
        "transformed_query": None,
        "documents": [],
        "web_search_needed": False,
        "hallucination_grade": None,
        "final_response": None,
        "citations": [],
        "loop_step": 0,
    }

    try:
        # Run synchronous LangGraph execution in a non-blocking threadpool
        final_state: DeepResearchState = await asyncio.to_thread(
            research_graph.invoke,
            initial_state
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing research state machine: {str(e)}"
        )

    elapsed_time = round(time.time() - start_time, 2)

    # Format citations safely
    citations = [
        CitationResponse(
            citation_id=c.get("citation_id", "[?]"),
            source=c.get("source", "Unknown"),
            quote=c.get("quote", "")
        )
        for c in final_state.get("citations", [])
    ]

    return ResearchResponse(
        query=request.query,
        transformed_query=final_state.get("transformed_query"),
        final_response=final_state.get("final_response") or "Unable to generate an audited response.",
        citations=citations,
        web_search_needed=final_state.get("web_search_needed", False),
        hallucination_grade=final_state.get("hallucination_grade"),
        loop_step=final_state.get("loop_step", 0),
        documents_count=len(final_state.get("documents", [])),
        execution_time_seconds=elapsed_time,
    )


# =====================================================================
# 4. ENTRYPOINT FOR DIRECT EXECUTION
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting DeepResearch-CRAG FastAPI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("deep_research.api:api", host="127.0.0.1", port=8000, reload=False)
