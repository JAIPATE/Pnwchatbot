# Tech Stack Decision Record (TSDR) - Technology Choices

## Title
TSDR-001: Technology Stack Selection for PNW Knowledge Chatbot

## Status
Accepted

## Context
Following the choice of a Client-Server Layered Monolith Architecture (ADR-001), we must select the technology stack (programming languages, web frameworks, frontend UI, database engine, and AI libraries) to implement the system.

We evaluate candidates using the 5 key decision dimensions outlined in the course curriculum:
1. **AI Support Strength**
2. **Popularity & Community Answers**
3. **Ecosystem Maturity**
4. **Deployment Simplicity**
5. **Path to Next Architecture**

## Candidates Evaluated

- **Stack A**: Python + FastAPI + React + SQLite (Dev) / PostgreSQL (Prod) + Gemini API / Vector Index
- **Stack B**: Java + Spring Boot (MVC) + Thymeleaf + Hibernate + PostgreSQL
- **Stack C**: Node.js + Express + EJS Server-Rendered Views + PostgreSQL

## Decision
We select **Stack A (Python + FastAPI + React + SQLite/PostgreSQL)** as the project's official technology stack.

### Stack Breakdown:
- **Backend Framework**: Python 3.11+ with **FastAPI** & Uvicorn (Asynchronous, fast, auto-generated OpenAPI docs).
- **Frontend Framework**: **React** SPA with Vite & Vanilla CSS (Purdue Northwest Dark & Gold design tokens).
- **Database**: **SQLite** (for local zero-config development) and **PostgreSQL** (for production deployment with `db/schema.sql`).
- **AI / RAG Pipeline**: Grounded Python RAG Engine using Gemini API / Free Embedding models + Local Vector Keyword Indexing.

## Stack Comparison across 5 Dimensions

| Dimension | Stack A (Python/FastAPI/React) | Stack B (Spring Boot/Thymeleaf) | Stack C (Node.js/Express) |
|---|---|---|---|
| **1. AI Support Strength** | **HIGH** (Native Python AI/RAG ecosystem) | **MEDIUM** (Requires Java AI wrappers) | **MEDIUM** (Good JS AI SDKs) |
| **2. Popularity & Community** | **HIGH** (Dominant stack for modern AI web apps) | **HIGH** (Enterprise Java standard) | **HIGH** (Node ecosystem standard) |
| **3. Ecosystem Maturity** | **HIGH** (FastAPI & Pydantic v2 maturity) | **HIGH** (Decades of Spring maturity) | **HIGH** (Express maturity) |
| **4. Deployment Simplicity** | **HIGH** (Single `uvicorn main:app` executable) | **MEDIUM** (JVM build & WAR setup) | **HIGH** (Single `node server.js`) |
| **5. Path to Next Architecture** | **HIGH** (Decoupled React SPA & REST APIs ease microservices transition) | **MEDIUM** (Server-rendered views tie UI to Spring) | **MEDIUM** (EJS views tie UI to Express) |

## Consequences

### Positive
- **Best AI Integration**: Python is the standard for NLP, vector embeddings, chunking, and AI integration.
- **Fast Execution**: FastAPI provides async endpoint execution with automatic Pydantic request validation and interactive Swagger UI docs.
- **Modern UI**: React provides a vibrant, dynamic single-page web app experience for students.
- **Production Ready**: Clean migration path from local SQLite to cloud PostgreSQL via standard DDL (`db/schema.sql`).

### Negative
- Requires maintaining two package definitions (`pyproject.toml`/`requirements.txt` for Python backend, `package.json` if Node frontend tooling is used).
