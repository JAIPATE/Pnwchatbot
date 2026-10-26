# Architecture Decision Record (ADR) - System Architecture

## Title
ADR-001: Architecture Design for PNW Knowledge Chatbot

## Status
Accepted

## Context
The PNW Dean of Students office requires a knowledge chatbot system to assist undergraduate and graduate students with policy, course, prerequisite, and schedule inquiries.

The architecture must support:
1. Low latency user requests with real-time response feedback.
2. Structured relational queries (for exact academic schedule tables and course prerequisite chains) combined with un-structured document search (RAG for PDF policies and handbooks).
3. Clear maintainability, high readability, and rapid deployment by a small software engineering team.
4. Robust data consistency across student campus selections, session histories, and ingested corpus documents.

## Decision
We decide to adopt a **Client-Server, Monolithic, Layered Architecture** with a **Single Relational Database** and a **Hybrid Interaction Model (Synchronous REST + SSE Streaming)**.

### Architectural Dimensions Chosen:
1. **System Roles & Communication**: Client-Server Model
   - Client (React SPA) handles user interaction, visual rendering, campus selection, and chat state.
   - Server (FastAPI) centralizes business logic, RAG retrieval, fail-safe evaluation, and SQL database access.
2. **Deployment & Evolution**: Monolith
   - The entire system is packaged as a single deployable web application unit, minimizing network latency, deployment overhead, and complex service orchestration.
3. **Code Organization**: Layered Architecture
   - Code on the backend is structured by technical layers (`routers/` -> `services/` -> `models/` -> `db/`), enforcing single-direction dependency flow.
4. **Data & State Ownership**: Single Database (SQLite for local dev / PostgreSQL for production)
   - All modules (schedules, prerequisites, corpus documents, chat history) share a single relational database for simple transactional integrity and queries.
5. **Interaction Model**: Hybrid Synchronous REST & Server-Sent Events (SSE) Streaming
   - Standard CRUD operations (campus selection, schedule fetching, document lists) use synchronous REST endpoints.
   - Chat interactions use Server-Sent Events (SSE) streaming (`POST /api/chat/stream`) to stream generated tokens to the client with sub-second feedback.

## Alternatives Considered

1. **Microservices Architecture**:
   - *Rejected*: Unnecessary operational overhead, network latency, and deployment complexity for a single-domain knowledge chatbot.
2. **Event-Driven Architecture (Pub/Sub message queues like RabbitMQ/Kafka)**:
   - *Rejected*: User inquiries require immediate response feedback rather than asynchronous background processing.
3. **Feature-Based Frontend/Backend Split with Multiple Databases**:
   - *Rejected*: Single relational database provides simple JOINs between document chunks, campus tags, and course prerequisites without distributed transaction issues.

## Consequences

### Positive
- **Simplicity & Speed**: Rapid development, testing, and single-command deployment.
- **Data Integrity**: Unified relational constraints (Foreign Keys, NOT NULL, CHECK constraints) across all entities.
- **Great User Experience**: Streaming SSE provides instant response feedback to students.
- **Maintainability**: Layered structure makes code easy to navigate and extend.

### Negative
- Scalability is tied to scaling the single application instance horizontally or vertically (though more than sufficient for campus-wide scale).
- High coupling to the single database schema, requiring disciplined database migrations (`db/schema.sql`).
