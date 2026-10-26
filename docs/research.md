# Technical Research & Decisions (research.md)

This document records the technical trade-offs, research findings, and selected engineering solutions for the PNW Knowledge Chatbot.

---

## 1. Table Data Integrity: RAG vs. Structured SQL

- **Decision**: Adopt a hybrid storage and retrieval approach: store academic schedules in structured SQL tables (`academic_schedules`) for deterministic date/deadline lookups, while retaining raw markdown chunks in the vector/text store for natural language queries.
- **Rationale**: Standard RAG text splitters chunk text by fixed character sizes (e.g., 500 characters). When applied to multi-term HTML schedule tables (Fall, Spring, Summer) with refund percentages and add/drop dates, splitters fragment columns and scramble critical deadlines. Relational tables guarantee 100% data integrity for structured deadline filtering.
- **Alternatives Considered**:
  - *Pure RAG*: Scrambled deadlines and dates due to chunk boundaries cutting across table rows.
  - *Pure SQL with text match*: Inflexible for conversational policy questions that do not specify exact table parameters.

---

## 2. Streaming Response Mechanism: SSE vs. WebSockets

- **Decision**: Use Server-Sent Events (SSE) via `POST /api/chat/stream` for real-time token streaming.
- **Rationale**: SSE operates over standard HTTP, making it simpler to implement in FastAPI using `StreamingResponse`. It has native browser reconnection support, avoids connection keep-alive overhead, and fits the unidirectional client-request-to-server-stream interaction model.
- **Alternatives Considered**:
  - *WebSockets*: Bi-directional communication is unnecessary for single-prompt responses; adds connection state and proxying complexity.
  - *Polling / Chunked HTTP*: Inefficient network overhead and higher latency.

---

## 3. Groundedness Evaluation & Fail-Safe Thresholding

- **Decision**: Combine TF-IDF term overlap and Cosine Similarity scoring to compute a groundedness score $S \in [0.0, 1.0]$ with an explicit refusal threshold ($S < 0.45$).
- **Rationale**: To enforce Constitution Principle #2 (Fail Safely), queries with relevance score below $0.45$ automatically trigger the fail-safe response, refusing speculative generation and routing the student to the Dean of Students office or relevant academic department contacts.
- **Alternatives Considered**:
  - *LLM Self-Grading / Prompt Guard*: Non-deterministic, adds latency, and can hallucinate its own groundedness confidence.
  - *Keyword-Only Matching*: Highly brittle to student synonyms and natural phrasing variations.

---

## 4. Architecture Style: Client-Server Layered Monolith

- **Decision**: Build the application as a single deployable Layered Monolith containing a FastAPI backend and a React SPA frontend sharing a single relational database (SQLite/PostgreSQL).
- **Rationale**: Keeps development velocity high, minimizes network latency between components, simplifies transaction handling, and fits the team and domain scale without distributed orchestration overhead.
- **Alternatives Considered**:
  - *Microservices*: High operational complexity and network latency for a single-domain assistant.
  - *Serverless Functions*: Cold start latencies violate the sub-1.5s initial response latency goal.
