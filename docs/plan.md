# Implementation Plan: Purdue Northwest (PNW) Knowledge Chatbot

**Branch**: `001-pnw-knowledge-chatbot` | **Date**: 2026-10-26 | **Spec**: `docs/spec.md`

**Input**: Feature specification from `docs/spec.md`

**Note**: This plan outlines the technical design, architectural decisions, and verification gates for the PNW Knowledge Chatbot system in accordance with Spec-Driven Development.

---

## Summary

The Purdue University Northwest (PNW) Knowledge Chatbot provides registered undergraduate and graduate students with grounded answers to questions regarding academic policies, schedules, course prerequisite trees, and campus parking regulations. The system addresses the core student challenge of navigating scattered PDFs and ambiguous web loops by delivering cited answers, interactive prerequisite visualizers, structured academic calendar tables, and campus-specific filtering (Hammond vs. Westville).

The technical approach implements a **Layered Monolith** with a **FastAPI** backend, **SQLite / PostgreSQL** relational database, **TF-IDF + Cosine similarity** grounded RAG engine, and a **React SPA** frontend rendered with Vanilla CSS in the official PNW Gold and Dark visual identity. Real-time token streaming is provided via Server-Sent Events (SSE), and a deterministic fail-safe threshold ($S < 0.45$) guarantees that unsupported questions trigger polite refusals routing students to official university contacts.

---

## Technical Context

**Language/Version**: Python 3.11+, JavaScript (ES6+ / React 18)

**Primary Dependencies**: FastAPI 0.115+, Uvicorn 0.30+, Pydantic 2.8+, React 18, Pytest 8.3+

**Storage**: SQLite 3 (local development) / PostgreSQL 15+ (production target); normalized schema with foreign keys, check constraints, and indexed chunk lookups

**Testing**: Pytest for backend unit/integration tests (`tests/test_api.py`, `tests/test_rag.py`)

**Target Platform**: Linux / Cross-platform Web Service & Modern Browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web Service (FastAPI REST & SSE Backend) + Single Page Application (React Frontend)

**Performance Goals**:
- Initial SSE stream token response within 1.5s of query submission
- Full grounded answer generation and citation lookup in < 3.0s
- 95th percentile query latency < 2.0s

**Constraints**:
- 100% of factual policy statements grounded in official seeded PNW corpus
- Fail-safe guardrail triggers whenever confidence score $S < 0.45$, returning Dean of Students office contacts
- Strict campus distinction between Hammond and Westville rules
- Zero external LLM dependency required for local execution (deterministic vector/TF-IDF similarity engine)

**Scale/Scope**:
- ~10,000 enrolled PNW students
- 8 official university document sources, 24+ structured chunks
- 2 campuses (Hammond, Westville)
- 4 primary interaction domains: Policy RAG, Academic Schedule Lookups, Prerequisite Graph Traversal, Campus Switching

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Rule | Requirement / Verification | Status |
|------------------|----------------------------|--------|
| **1. Grounded Answers** | RAG engine verifies relevance score against official corpus chunks before synthesizing answer. 0% hallucinated policy. | **PASS** |
| **2. Fail Safely** | Sub-threshold queries ($S < 0.45$) trigger immediate refusal directing students to Dean of Students / Department contacts. | **PASS** |
| **3. Requirements Before Implementation** | All functional requirements (FR-1 to FR-6) and measurable criteria (NFR-1 to NFR-4) documented and test-covered. | **PASS** |
| **4. Official Citations** | Every grounded answer appends clickable links (`source_url`) and section titles to primary documentation sources. | **PASS** |
| **5. Multi-Campus Filtering** | Query engine respects selected `campus_id` filter to prevent cross-campus confusion (Hammond vs. Westville). | **PASS** |

---

## Project Structure

### Documentation (this feature)

```text
docs/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 technical research decisions & rationale
├── data-model.md        # Phase 1 logical entities, attributes & relationships
├── quickstart.md        # Phase 1 local setup & end-to-end verification guide
├── contracts/           # Phase 1 OpenAPI API interface specifications
│   └── openapi.json
├── spec.md              # Approved software specification & requirements
├── constitution.md      # Project governance principles & guardrails
├── tasks.md             # Phased execution tasks breakdown across all phases
├── architecture_decision_record.md # ADR-001 Architecture design decisions
├── tech_stack_decision_record.md   # TSDR-001 Tech stack selections
├── user_stories_and_acs.md         # Detailed user journeys & acceptance criteria
└── erd.md               # Entity Relationship Diagram (Mermaid)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app initialization, CORS, static mounting
├── database.py          # SQLite database connection & connection pooling
├── models/
│   └── schemas.py       # Pydantic schemas (ChatRequest, ChatResponse, ScheduleItem, etc.)
├── routers/
│   ├── campus.py        # Campus listing endpoint (GET /api/campus)
│   ├── chat.py          # Chat endpoints (POST /api/chat, POST /api/chat/stream)
│   ├── prereq.py        # Prerequisite graph endpoint (GET /api/prerequisites)
│   └── schedule.py      # Academic schedule endpoint (GET /api/schedule)
└── services/
    ├── prereq_service.py   # Prerequisite tree resolution & campus availability tags
    ├── rag_service.py      # TF-IDF + Cosine retrieval, scoring & fail-safe guardrail
    └── schedule_service.py # Term deadline lookup & refund calculations

frontend/
├── index.html           # React root DOM, campus selector modal, tab layout
├── app.js               # React SPA components, chat state, SSE stream parser
└── styles.css           # Vanilla CSS stylesheet (PNW Gold & Dark design system)

db/
├── schema.sql           # DDL schema: campuses, documents, document_chunks, academic_schedules, prerequisites, parking_rules
├── sample_queries.sql   # SQL benchmark queries for schedule, prereqs & chunks
└── seed_data.py         # PNW corpus parser & database seeder

tests/
├── test_api.py          # FastAPI endpoint integration tests
└── test_rag.py          # RAG similarity, citation matching & fail-safe unit tests
```

**Structure Decision**: A Web application client-server architecture with single relational database. Backend business logic is modularized into `routers/`, `services/`, and `models/`, cleanly isolated from frontend static assets and database schema scripts.

---

## Complexity Tracking

> **No Constitution violations detected.** The architecture uses standard, proven primitives (FastAPI, SQLite/PostgreSQL, React, Server-Sent Events) without unnecessary microservices, external queue dependencies, or heavy frameworks.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | *N/A* | *N/A* |
