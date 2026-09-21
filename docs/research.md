# Technical Research & Decisions (research.md)

This document records the technical trade-offs, research findings, and selected engineering solutions for the PNW Knowledge Chatbot.

---

## 1. Table Data Integrity: RAG vs. Structured SQL

- **Problem**: Standard RAG text splitters chunk text by fixed character sizes (e.g. 500 chars). When applied to complex HTML academic schedule tables containing multiple terms (Fall, Spring, Summer) and refund percentages, splitters fragment columns and scramble deadlines.
- **Research Finding**: Storing schedule deadlines in structured relational SQL tables (`academic_schedules`) guarantees 100% data integrity for date queries, while keeping markdown tables in corpus chunks for general conversational retrieval.
- **Selected Solution**: **Hybrid approach**. Use structured SQL queries for exact deadline lookups and vector chunk search for general textual policies.

---

## 2. Streaming Response Mechanism: SSE vs WebSockets

- **Problem**: Chatbots generating answers character-by-character can feel slow if waiting for the complete response payload.
- **Research Finding**:
  - **WebSockets**: Bi-directional, requires custom connection keep-alive, overkill for simple client request -> server stream response.
  - **Server-Sent Events (SSE)**: HTTP-native, simple to implement in FastAPI (`EventSourceResponse` / `StreamingResponse`), robust auto-reconnection.
- **Selected Solution**: **Server-Sent Events (SSE)** via `POST /api/chat/stream`.

---

## 3. Groundedness Evaluation & Fail-Safe Thresholding

- **Problem**: LLMs may attempt to answer questions outside the PNW corpus (e.g. "How do I bake sourdough bread?").
- **Research Finding**: Computing cosine similarity + TF-IDF keyword overlap between user query and retrieved corpus chunks yields a groundedness score $S \in [0.0, 1.0]$.
- **Selected Solution**: If $S < 0.45$, the bot triggers the **Fail-Safe Policy** immediately, refusing speculative answers and returning Dean of Students office contact links.
