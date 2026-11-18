# DeepResearch-CRAG — Senior UI/UX Architecture & Design Masterplan

> **Role Perspective:** Senior Product Designer & Frontend UX Architect  
> **Product:** DeepResearch-CRAG (Autonomous Corrective-RAG & Self-RAG Workstation)  
> **Surface Mode:** `Operate` (Task Execution) + `Read` (High-Trust Long-Form Verification)  
> **Design System Companion:** [`DESIGN.md`](DESIGN.md)

---

## 1. Product Truth & UX Thesis

### Why Traditional "AI Chat UIs" Are Wrong for This Product
Most AI projects default to a **ChatGPT-style conversational bubble interface** (user bubble on right, assistant bubble on left). For a Corrective-RAG research engine, a chat UI is a UX failure for three reasons:
1. **Research is spatial, not linear:** Users need to read a synthesized answer *and* inspect source quotes simultaneously without scrolling past 10 chat turns.
2. **Trust requires auditability:** In legal, compliance, financial, or policy research, the user's primary anxiety is *"Did the model hallucinate this, or is it actually in the source?"* Hiding citations behind collapsed accordions creates cognitive friction.
3. **Multi-second AI workflows need honest state feedback:** An autonomous CRAG loop (Retrieve $\rightarrow$ Grade $\rightarrow$ Web Fallback $\rightarrow$ Synthesize $\rightarrow$ Fact Audit) takes several seconds. Generic spinning loaders make users think the system hung.

### The Core Design Thesis: **"Verifiable Precision"**
This interface is designed as an **Analytical Research Workstation**, not a chatbot. Every layout, typography, color, and interaction choice serves one goal: **minimizing the distance between a factual claim and its verifiable proof.**

---

## 2. User Personas & Psychological Context

| User Archetype | Context & Mindset | Primary Job to Be Done (JTBD) | What Causes Friction / Abandonment |
| :--- | :--- | :--- | :--- |
| **Compliance / Policy Analyst** | Time-constrained, high accountability, zero tolerance for false facts. | Verify whether an internal rule covers a scenario, or find external guidance with exact quotes. | Hidden citations, ambiguous confidence levels, bloated decorative UI. |
| **Technical / Engineering Lead** | Evaluating the system or troubleshooting complex domain questions. | Upload technical docs (`.pdf`/`.md`), run queries, and verify why the agent chose web fallback over local vectors. | Opaque "black box" waiting states, inability to abort a slow query, cluttered file lists. |
| **Hiring Manager / Design Reviewer** | Inspecting the project as a portfolio piece within 60 seconds. | Assess product maturity, design taste, visual restraint, and real functionality. | "AI slop" (purple/cyan gradients, nested card soup, placeholder marketing cards, fake telemetry). |

---

## 3. Information Architecture & Spatial Topology

### Desktop Layout (`>= 1024px`) — Asymmetric Two-Column Workstation

Instead of centered narrow columns or noisy multi-card dashboards, the workstation splits **Synthesis (Reading)** from **Evidence (Verification)** across a disciplined 12-column grid (`max-width: 1200px`):

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ [Top Bar]  DeepResearch-CRAG   │  Corpus: 3 Docs ▾  │  ● Engine Ready      │
├────────────────────────────────────────────────────────────────────────────┤
│ [Command Dock]                                                             │
│  🔍 Search indexed files or run live web research...    [Upload] [Research] │
│  Quick Scenarios: [Museum Policy] [Remote Schedule] [Live Web Fallback]    │
├────────────────────────────────────────────────────────────────────────────┤
│ [Verdict Strip]  ✓ Factually Grounded · Web Search · 6 chunks · Loop 1/3   │
├─────────────────────────────────────────┬──────────────────────────────────┤
│ [Zone B: Primary Reading Canvas (7/12)] │ [Zone C: Evidence Rail (5/12)]   │
│                                         │  Sticky top-20 · Tabs:           │
│  Synthesis Report               [Copy]  │  [ Citations (2) ] [ Trace ]     │
│  ─────────────────────────────────────  │  ──────────────────────────────  │
│  Approved employees may work remotely   │  [1] Employee Remote Work Policy │
│  up to three days per week, with        │  "Approved employees may work    │
│  Tuesday and Thursday as office days    │   remotely up to three days..."  │
│  [1].                                   │                                  │
│                                         │  [2] https://example.com/... ↗   │
│  (Line width locked to 65–68ch)         │  "Supporting external snippet..." │
└─────────────────────────────────────────┴──────────────────────────────────┘
```

### Why This Topology Works
* **Zero Eye-Jump Verification:** Reading the report on the left while scanning `[1]` and `[2]` on the right eliminates vertical scroll fatigue.
* **Single-Layer Surface Depth:** No cards nested inside cards. Depth comes from a restrained tonal step (`#09090b` canvas $\rightarrow$ `#111216` panel surface) separated by `1px solid #22242c` hairlines.
* **Prose Discipline:** The report column enforces a `65ch–68ch` measure so text remains effortless to scan even on ultra-wide monitors.

### Responsive Behavior (`< 1024px` Tablet & Mobile)
* **Stacking:** The 12-column grid collapses cleanly to a single vertical flow (`Verdict Strip` $\rightarrow$ `Synthesis Report` $\rightarrow$ `Evidence Section`).
* **Smart Citation Anchoring:** On mobile, tapping an inline `[1]` badge smoothly scrolls to `#citation-[1]` and applies a 1.5s focus highlight ring so the user never loses track of which quote they opened.
* **Touch Targets:** All interactive controls (buttons, example chips, citation tokens) maintain a minimum `36px–44px` hit area on touch screens.

---

## 4. Complete State & Edge-Case Matrix

A Senior UI/UX spec defines every state before code is written—especially failure, latency, and boundary states.

### State 1: First-Run / Empty State (Onboarding Through Action)
* **Anti-Pattern to Avoid:** Generic 3-card feature grids explaining "Noise Rejection / Web Fallback / Zero Hallucination" with decorative icon boxes.
* **Senior UX Pattern:** Show a concise **Interactive Capabilities Brief** paired with **3 distinct, 1-click test scenarios** right under the command input:
  1. *Internal Corpus Hit* ("What are the core hours and remote work days allowed for employees?")
  2. *Cross-Policy Check* ("What is the standard fossil loan period and curator approval rules?")
  3. *Out-of-Bounds Web Fallback* ("What are the latest updates on NASA Artemis moon mission in 2026?")
* **Session History (Recommended Upgrade):** Keep the last 5 completed queries in `localStorage` as quick clickable chips in a quiet sidebar or dropdown so returning users or reviewers can switch between previous verified reports instantly without waiting for another API round-trip.

### State 2: Document Ingestion & Corpus Management
* **Current Reality (`POST /api/upload` & `GET /api/documents`):** Users can upload `.pdf`, `.txt`, `.md`, `.csv`, and `.json`.
* **Scaling UX Issue:** Displaying every uploaded file as inline pills under the search bar works for 2–3 files, but breaks layout rhythm if a user uploads 10+ files.
* **Senior UX Solution:**
  * **Compact Corpus Pill:** Show `Corpus: 2 internal + N uploaded` in the top bar or immediately below the search bar as a single interactive popover trigger. Clicking it opens a clean list of all indexed documents (with file type icon and origin tag: `Built-in` vs `Uploaded`).
  * **Full-Zone Drag & Drop:** Allow dragging a `.pdf` or `.md` directly onto the command dock, highlighting the input border in solid Cobalt (`#3b82f6`) with a clear label: *"Drop document to index into Qdrant"*.
  * **Validation & Guardrails:** Reject unsupported extensions client-side *before* hitting the server, and show explicit feedback for empty/scanned PDFs (`"No extractable text found in scanned.pdf"`).

### State 3: Loading & Perceived Latency UX (Solving the 10–25s AI Wait)
Because `POST /api/research` runs multiple LLM calls (Grading, Rewriting, Web Search, Generation, Dual Audit), latency is noticeable.
* **Critical UX Flaw in Fake Timers:** Using `setTimeout` in `App.tsx` to guess which node is running creates **dishonest UI**—if internal docs pass immediately without web search, the UI might falsely claim `"Running DuckDuckGo search..."`.
* **Two-Tier UX Solution:**
  1. **Immediate Tactical UX (Frontend Only):**
     * Display a live **elapsed timer** (`Elapsed: 04.2s` in `tabular-nums`) and an explicit **Cancel / Abort (`Esc`)** button powered by `AbortController`. Giving users control reduces perceived wait frustration dramatically.
     * Render **geometry-matched skeleton placeholders** in the 7/5 layout (prose lines on the left, 2 evidence block skeletons on the right) to prevent jarring Cumulative Layout Shift (CLS) when the answer arrives.
  2. **Architectural UX Upgrade (Backend SSE Streaming):**
     * Add a `POST /api/research/stream` endpoint using `research_graph.stream()` so the frontend renders **100% truthful node transitions** in real time as LangGraph finishes each node.

### State 4: Success — Verified Grounded Response
* **Verdict Strip:** A single horizontal line replacing chunky stat cards:
  * Left: Green status check + `Factually Grounded` + knowledge source badge (`Internal Qdrant` vs `DuckDuckGo Web Fallback`).
  * Right: `6 chunks audited · Loop 1/3 · 8.42s` in crisp `tabular-nums` monospace.
* **Citation Synchronization:**
  * Inline tokens (`[1]`, `[2]`) are styled as interactive buttons, not passive superscripts.
  * **Hover Preview:** Hovering `[1]` reveals a lightweight popover showing the source name and first 120 characters of the quote without requiring a click.
  * **Click Lock:** Clicking `[1]` pins `#citation-[1]` in the right Evidence Rail with a subtle Cobalt focus border (`#3b82f6`) and scrolls it smoothly into view.
  * **Copy Fidelity:** Clicking `Copy` copies clean markdown/text of the synthesis *with* formatted footnote references appended at the bottom so pasting into Notion, Slack, or email retains attribution.

### State 5: Degraded / Audit Warning State (`hallucinated` or Circuit Breaker Tripped)
* If `hallucination_grade !== 'grounded'` or `loop_step >= 3`:
  * Do **not** present the report with the same calm styling as a verified output.
  * Upgrade the Verdict Strip to an explicit **Amber/Rose Audit Notice**:  
    *"Verification Warning: Max corrective loops reached (3/3). Some claims could not be strictly matched to retrieved quotes—review evidence manually."*
  * Never hide the partial output; surface it alongside whatever evidence was gathered so the user has diagnostic value.

### State 6: Error & Network Failure States
* **API Offline (`serverHealthy === false`):** Show a persistent, subtle inline banner below the header with the exact recovery command (`.venv\Scripts\uvicorn deep_research.api:api --port 8000`) rather than letting the user hit Research and fail blindly.
* **Request Failure:** Preserve the user's typed query in the input box, show a clear inline error notice naming the failure (`500`, network timeout, or validation error), and provide a 1-click **Retry** button.

---

## 5. Visual Design System & Token Rationale

This system strictly adheres to [`DESIGN.md`](DESIGN.md) and **Impeccable Style** anti-slop rules:

### Color Architecture (Restrained Semantic System)
| Token Role | Hex / Value | Usage Rule |
| :--- | :--- | :--- |
| **Canvas (`bg-base`)** | `#09090b` | Primary application background. Eliminates eye strain during long reading. |
| **Surface (`bg-surface`)** | `#111216` | Report container, command input, evidence panel. Tonal separation without heavy shadows. |
| **Elevated (`bg-surface-hover`)** | `#18191f` | Interactive hover states, active citation cards, secondary buttons. |
| **Hairline (`border-subtle`)** | `#22242c` | Crisp `1px` structural boundaries separating layout zones. |
| **Text Primary** | `#f4f4f5` | Headings, report body text, primary button text. High contrast (`> 15:1` on canvas). |
| **Text Secondary** | `#a1a1aa` | Source snippets, telemetry metadata, descriptions (`> 7:1` contrast). |
| **Action / Citation (`accent`)** | `#2563eb` / `#3b82f6` | Strictly reserved for interactive citation tokens (`[1]`), focus rings, and active selection. |
| **Grounded (`status-grounded`)** | `#10b981` | Strictly reserved for `Factually Grounded` verification and `Ready` status dot. |
| **Fallback / Caution** | `#f59e0b` | Used when web fallback triggered or circuit breaker tripped. |

### Typography Rules
* **One Unified Sans Stack:** System UI sans (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`) for clean, familiar Operate/Read clarity.
* **Tabular Monospace (`font-mono tabular-nums`):** Used strictly for **measurements, latency, chunk counts, loop counters, and citation keys (`[1]`)**—never as a decorative "tech costume" for prose or headings.
* **Scale Hierarchy:**
  * Page Title (`h1`): `24px` (`1.5rem`), `font-semibold` (`600`), tracking `-0.02em`.
  * Section Headers (`h2`): `14px` (`0.875rem`), `font-semibold` (`600`), solid `#f4f4f5`.
  * Report Prose: `15px` (`0.9375rem`), `line-height: 1.65`, `max-width: 68ch`.
  * Telemetry / Micro-labels: `12px` (`0.75rem`).

### Intentional Motion Rules
* **150ms–200ms `ease-out`** for hover, focus, and citation highlight transitions.
* **Zero decorative animation:** No pulsing logos, no bouncing icons, no page-load entrance choreography. Motion exists solely to communicate state change (e.g., spinner during live network request, highlight fade when jumping to a citation).

---

## 6. Component Specifications & Interactive Details

### 1. `EvidenceRail` (Upgraded Right Column)
Transform the right column into a 2-tab inspection panel so users can audit both *content* and *system reasoning*:
* **Tab 1 — `Evidence (N)` (Default):**
  * Displays cited sources (`[1]`, `[2]`) with source title or clickable external URL (`target="_blank"`), plus verbatim supporting quotes.
  * Clicking a card highlights all matching `[N]` tokens inside the Synthesis Report (bidirectional binding!).
* **Tab 2 — `Audit Trace`:**
  * Surfaces the structured metadata already returned by `/api/research`:
    * Original Query vs. Rewritten Search Query (`transformed_query`)
    * Knowledge Route Taken (`Internal Qdrant Sufficient` vs `Triggered DuckDuckGo Fallback`)
    * Chunks Evaluated (`documents_count`) & Safety Loop Counter (`loop_step / 3`)
    * Hallucination Gate Verdict (`hallucination_grade`)

### 2. `CommandDock` (Unified Search + Upload)
* **Keyboard Shortcuts:**
  * `/` or `⌘K` (Windows: `Ctrl+K`) focuses the research input from anywhere.
  * `Enter` submits research query.
  * `Esc` aborts an in-flight request (when loading) or clears focus.
* **Primary vs Secondary Button Weight:**
  * `Research` is the single high-contrast primary action (`bg-zinc-100 text-zinc-950`).
  * `Upload` is a quiet secondary action (`bg-zinc-900 border-zinc-800 text-zinc-300`), ensuring visual hierarchy remains unambiguous.

---

## 7. Accessibility & Keyboard Contract (WCAG AA+)

1. **Color Contrast:** All body text (`#f4f4f5` / `#e4e4e7`) exceeds `12:1` on `#111216`; secondary captions (`#a1a1aa`) exceed `6.5:1`.
2. **Screen Reader Landmarks:**
   * `<header>` for global status & corpus context
   * `<main>` for search & report workstation
   * `<article aria-label="Synthesized Research Report">` for reading prose
   * `<aside aria-label="Citation Evidence">` for the evidence rail
   * `aria-live="polite"` on the loading status strip and upload confirmation banner so assistive tech announces completion.
3. **Focus Visibility:** Every button, input, example chip, and `[1]` citation badge carries an explicit `:focus-visible` ring (`ring-2 ring-blue-500 ring-offset-2 ring-offset-[#09090b]`).
4. **Reduced Motion:** Respect `@media (prefers-reduced-motion: reduce)` by replacing smooth scrolling with instant jumps and disabling transition fades.

---

## 8. UX Anti-Patterns Checklist ("What We Deliberately Refuse")

| Anti-Pattern ("AI Slop") | Why We Refuse It | What We Ship Instead |
| :--- | :--- | :--- |
| **Gradient Headings (`bg-clip-text`)** | Decorative distraction that reduces legibility and signals generic AI templates. | Solid `#f4f4f5` headings with crisp weight and spacing hierarchy. |
| **Purple / Cyan Neon Glows** | Visual cliché of unguided LLM interfaces (`shadow-indigo-500/20`). | Restrained Obsidian/Zinc surfaces with solid `#2563eb` semantic focus accents. |
| **Nested Cards Inside Cards** | Wastes space, creates cluttered border boxes, weakens hierarchy. | Single surface panels divided by clean `1px` hairlines and whitespace. |
| **4-Box Metric Hero Grids** | Bloats viewport above the actual answer the user came to read. | A single compact `VerdictStrip` displaying all 4 telemetry metrics cleanly. |
| **Fake `setTimeout` Stage Progress** | Lies to the user about what the backend is currently executing. | Honest elapsed timer + Cancel button (and SSE streaming for real node events). |
| **Eyebrow Kickers Above Titles** | Adds redundant metadata noise above headings that already explain themselves. | Clear, self-sufficient headings (`Synthesis Report`, `Source Evidence`). |

---

## 9. Prioritized Implementation Roadmap

If upgrading the existing `frontend/` codebase incrementally, execute in this order:

1. **P0 — Latency Control & Honesty (`App.tsx`, `PipelineTracker.tsx`)**
   * Remove fake `setTimeout` progress timers.
   * Wire `AbortController` so users can cancel long queries mid-flight via `Esc` or a **Cancel** button.
   * Add live elapsed time counter (`tabular-nums`) and geometry-matched loading skeletons.
2. **P1 — Bidirectional Citation & Audit Trace (`ReportViewer.tsx`, `CitationsSection.tsx`)**
   * Clicking a source card in the Evidence Rail highlights matching `[N]` badges in the prose.
   * Add a lightweight `Audit Trace` tab in the right rail displaying `transformed_query`, `loop_step`, `web_search_needed`, and `hallucination_grade`.
   * Upgrade `Copy` button to copy report text *plus* formatted source links.
3. **P2 — Scalable Corpus Management & Drag-and-Drop (`SearchBar.tsx`, `Header.tsx`)**
   * Move the growing list of indexed file pills into a compact `Corpus (N) ▾` popover/drawer.
   * Add drag-and-drop file ingestion directly onto the search dock + `Ctrl+K` / `/` shortcut.
4. **P3 — Session Query History & Real SSE Streaming (`api.py` + `App.tsx`)**
   * Persist recent verified queries in `localStorage` for instant switching.
   * Add `/api/research/stream` (Server-Sent Events) in FastAPI so LangGraph streams real node transitions (`retrieve` $\rightarrow$ `grade_documents` $\rightarrow$ `web_search` $\rightarrow$ `generate` $\rightarrow$ `check_hallucination`) directly to the UI.
