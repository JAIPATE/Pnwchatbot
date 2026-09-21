# Purdue University Northwest (PNW) Knowledge Chatbot

An AI-powered knowledge assistant and information platform designed for **Purdue University Northwest (PNW)** undergraduate and graduate students.

The chatbot provides **grounded answers** backed by official PNW policy documents, academic course catalogs, prerequisite dependency graphs, parking regulations, and term schedules, featuring campus awareness (Hammond vs. Westville) and fail-safe guardrails.

---

## 🌟 Key Features
- **Grounded AI Answers & Source Citations**: Answers are strictly grounded in official PNW documentation with explicit source links and popovers.
- **Fail-Safe Policy Guardrail**: Refuses ungrounded questions safely ("I don't know") and redirects students to academic advisors or official offices.
- **Multi-Campus Context**: Tailors policies and course availability based on the student's selected campus (**Hammond** or **Westville**).
- **Academic Schedule & Deadline Parser**: Displays term deadlines, refund percentages, and drop/add dates accurately without data scrambling.
- **Prerequisite Visualizer**: Solves and renders complex course prerequisite chains and campus availability tags.

---

## 🏗️ Tech Stack & Architecture
- **Architecture**: Layered Monolith (Client-Server, Single Database, Synchronous REST API + Streaming SSE Chat).
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic, Pytest.
- **Frontend**: React, Vite, Vanilla CSS Design System (PNW Dark & Gold Theme).
- **Database**: SQLite / PostgreSQL (DDL schemas with surrogate PKs, foreign keys, check constraints, indexes).
- **RAG Engine**: Grounded Vector & Keyword Chunk Retrieval with confidence scoring.

---

## 📁 Repository Structure
```
pnw-knowledge-chatbot/
├── docs/                     # Software Engineering & Spec Kit documentation
│   ├── constitution.md       # Project rules & guardrails
│   ├── assumptions_and_scope.md
│   ├── spec.md               # Software specification
│   ├── architecture_decision_record.md (ADR)
│   ├── tech_stack_decision_record.md
│   ├── user_stories_and_acs.md
│   ├── data_design.md        # Logical data design
│   ├── erd.md                # Mermaid ERD diagram
│   ├── plan.md & research.md
│   ├── quickstart.md
│   ├── tasks.md
│   └── contracts/            # OpenAPI API contracts
├── db/                       # Database DDL, queries & seed scripts
│   ├── schema.sql            # DDL create table statements
│   ├── sample_queries.sql    # Benchmark SQL queries
│   └── seed_data.py          # PNW corpus seeding
├── backend/                  # FastAPI backend application
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── services/
│   └── routers/
├── frontend/                 # React SPA frontend application
└── tests/                    # Automated pytest test suites
```

---

## 🚀 Quick Start
Refer to [`docs/quickstart.md`](file:///C:/Users/jayp9/.gemini/antigravity-ide/scratch/pnw-knowledge-chatbot/docs/quickstart.md) for full instructions on setup, running locally, and running tests.
