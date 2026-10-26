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
- **Database**: SQLite / PostgreSQL with pgvector (DDL schemas with surrogate PKs, foreign keys, check constraints, indexes, HNSW vector index).
- **RAG Engine**: Offline Ingestion Pipeline (Parsing, Chunking, Dense Vector Embeddings via FastEmbed, PostgreSQL pgvector).

---

## ⚡ RAG Offline Pipeline

The offline pipeline extracts, chunks, embeds, and stores university documents into the vector database (**PostgreSQL pgvector** or local fallback):

```bash
# 1. Ingest official PNW documents into the vector database
python pipeline.py ingest --source data/raw_documents

# 2. Perform semantic vector search
python pipeline.py search --query "How do I pay parking citations at Hammond?" --campus Hammond

# 3. View vector database statistics
python pipeline.py stats
```

Full pipeline documentation: [`docs/rag_pipeline.md`](docs/rag_pipeline.md)

---

## 📁 Repository Structure
```
pnw-knowledge-chatbot/
├── pipeline.py               # CLI entrypoint for RAG offline pipeline
├── docker-compose.yml        # PostgreSQL with pgvector container
├── data/
│   └── raw_documents/        # Ingested official PNW HTML & PDF documents
├── docs/                     # Software Engineering & RAG documentation
│   ├── rag_pipeline.md       # RAG offline pipeline documentation
│   ├── constitution.md       # Project rules & guardrails
│   ├── spec.md               # Software specification
│   ├── tasks.md              # Tasks breakdown
│   └── quickstart.md
├── db/                       # Database DDL, queries & seed scripts
│   ├── pgvector_schema.sql   # PostgreSQL pgvector DDL with HNSW indexes
│   ├── schema.sql            # SQLite relational DDL
│   └── seed_data.py          # PNW corpus seeding
├── backend/                  # FastAPI backend application
│   ├── rag/                  # RAG offline pipeline package
│   │   ├── parser.py         # HTML & PDF universal parsers
│   │   ├── chunker.py        # Section-aware sliding window chunker
│   │   ├── embedder.py       # Dense vector embedders (FastEmbed / BAAI)
│   │   ├── vector_store.py   # PostgreSQL pgvector & SQLite vector stores
│   │   └── pipeline.py       # Pipeline orchestrator & CLI
│   ├── main.py
│   ├── database.py
│   └── services/
└── tests/                    # Automated pytest test suites
    ├── test_api.py
    ├── test_rag.py
    └── test_rag_pipeline.py  # Comprehensive RAG offline pipeline tests
```

---

## 🚀 Quick Start
Refer to [`docs/quickstart.md`](docs/quickstart.md) and [`docs/rag_pipeline.md`](docs/rag_pipeline.md) for full instructions on setup, running locally, and running tests.
