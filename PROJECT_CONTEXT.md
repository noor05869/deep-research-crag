# 🧠 DeepResearch-CRAG: Project Context & AI Engineer Roadmap

## 👤 Developer Profile & Goal
- **Name:** Noor Ullah
- **Background:** Senior Frontend Engineer (4+ years) transitioning into **Production AI Engineering**.
- **Target Role:** Remote AI Engineer ($3,000 – $5,000 / month).
- **Core Stack:** Python 3.12, LangGraph, Qdrant Vector DB, Google Gemini Flash, FastAPI, Docker.

---

## 🎯 What We Are Building & Why
**Project Name:** `deep-research-crag` (Autonomous Deep Research & Corrective-RAG Engine)

### The Problem It Solves:
Naive RAG systems (simple PDF chat wrappers) are fragile, prone to hallucinations, and blindly pass irrelevant context into LLMs. In enterprise settings, ungrounded answers are unacceptable.

### The Architecture:
This project implements a **Self-RAG (Self-Reflective RAG)** and **Corrective-RAG (CRAG)** state machine:
1. **Internal Retrieval:** Searches internal policy documents using local in-memory Qdrant vector embeddings (`BAAI/bge-small-en-v1.5`).
2. **Document Grading:** An automated quality-control node scores each chunk with strict Pydantic output (`yes`/`no`) to discard irrelevant noise.
3. **Query Transformation & Web Fallback:** If internal docs lack sufficient coverage, an LLM query rewriter strips conversational filler and searches the live web using DuckDuckGo (`ddgs`).
4. **Grounded Synthesis:** Generates a structured response with verified inline numerical citations (`[1]`, `[2]`).
5. **Hallucination & Relevance Audit:** Evaluates whether every single claim is factually grounded before the response is released.

---

## 🛠️ Step-by-Step Progress & Roadmap

| Step | Module / File | Description | Status |
| :---: | :--- | :--- | :---: |
| **Step 1** | `deep_research/state.py` | State Schema with `TypedDict` and `operator.add` reducers | ✅ Completed |
| **Step 2** | `deep_research/grader.py` | Document relevance grader (Self-RAG noise filter) | ✅ Completed |
| **Step 3** | `deep_research/retriever.py` | In-memory Qdrant vector retrieval & internal corpus | ✅ Completed |
| **Step 4** | `deep_research/tools.py` | Query rewriter & DuckDuckGo web search fallback | ✅ Completed |
| **Step 5** | `deep_research/generator.py` | Grounded answer synthesis with structured citations | ✅ Completed |
| **Step 6** | `deep_research/evaluator.py` | Hallucination checker & answer relevance auditor | ✅ Completed |
| **Step 7** | `deep_research/graph.py` | LangGraph StateGraph assembly (Wiring nodes & edges) | ✅ Completed |

---

## 📚 Pair-Programming & Learning Protocol
Whenever the user interacts with this project, the AI assistant MUST follow these rules:
1. **One Step at a Time:** Never skip ahead or dump the entire project at once.
2. **The "Why" & Purpose:** Before writing code, explain *why* this step is needed in production systems and *what* engineering problem it solves.
3. **The Technology Brief:** Explain the specific framework, library, or design pattern being used.
4. **Full Code Snippets:** Provide complete, runnable code snippets with clear inline comments.
5. **Code Walkthrough:** Explain what each function and line in the snippet accomplishes.
6. **Isolated Verification:** Provide a standalone test command so the user can run and verify the step immediately.
