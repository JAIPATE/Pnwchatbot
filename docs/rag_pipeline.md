# RAG Offline Pipeline: Parsing, Chunking, Embedding & Vector Database

## 1. Overview
The **Purdue University Northwest (PNW) Knowledge Chatbot** features an offline Retrieval-Augmented Generation (RAG) pipeline designed to process official university documents (HTML web pages and PDF handbooks), perform section-aware chunking, generate dense 384-dimensional vector embeddings, and store them into a high-performance vector database (**PostgreSQL pgvector** with HNSW indexing, supported by a standalone local SQLite/NumPy fallback).

---

## 2. Architecture & Pipeline Stages

```
   Raw Documents (HTML/PDF)
            │
            ▼
    [1. Universal Parser]
     (BeautifulSoup / pypdf)
            │
            ▼
    [2. Semantic Chunker]
(Section-Aware, Slid. Window)
            │
            ▼
     [3. Dense Embedder]
(FastEmbed BAAI/bge-small-en-v1.5)
            │
            ▼
   [4. Vector Database]
  (PostgreSQL pgvector / HNSW)
```

### Stage 1: Document Parsing (`backend/rag/parser.py`)
- **HTML Document Parser**: Utilizes `BeautifulSoup4` to remove non-content tags (`<script>`, `<style>`, `<nav>`), extract metadata attributes (`<meta name="category">`, `<meta name="source-url">`, `<meta name="campus">`), and structure document content into distinct semantic sections based on `<section>` elements and heading tags (`<h1>`–`<h4>`).
- **PDF Document Parser**: Utilizes `pypdf` to parse binary PDF documents, extract page text, infer headings, and preserve campus associations.
- **Universal Parser Dispatcher**: Automatically detects file extensions (`.html`, `.htm`, `.pdf`, `.txt`, `.md`) and dispatches to the corresponding parser.

### Stage 2: Section-Aware Chunking (`backend/rag/chunker.py`)
- **Strategy**: Respects structural document boundaries (headings, policy articles) before applying character/sentence level sliding window splitting.
- **Parameters**:
  - `chunk_size`: 500 characters (approx. 100–125 tokens)
  - `chunk_overlap`: 80 characters (approx. 15–20 tokens)
- **Metadata Preservation**: Every chunk retains `doc_id`, `document_title`, `category`, `source_url`, `campus` (`Hammond`, `Westville`, or `Both`), `section_title`, `chunk_index`, and character count.

### Stage 3: Dense Vector Embeddings (`backend/rag/embedder.py`)
- **Model**: `BAAI/bge-small-en-v1.5` (via `fastembed` ONNX Runtime).
- **Dimensionality**: 384 dimensions.
- **Normalization**: Unit $L_2$ vector normalization ($\|v\|_2 = 1.0$), ensuring that vector cosine distance directly correlates with semantic similarity.
- **Deterministic Embedder Fallback**: Provides reproducible unit-vector generation for test environments with zero external network overhead.

### Stage 4: Vector Database Storage (`backend/rag/vector_store.py`)
- **PostgreSQL pgvector (`PGVectorStore`)**:
  - Leverages PostgreSQL's `vector` extension: `CREATE EXTENSION IF NOT EXISTS vector;`.
  - Schema: `pnw_document_vectors` with column `embedding vector(384)`.
  - Indexing: **HNSW (Hierarchical Navigable Small World)** index with `vector_cosine_ops` for sub-millisecond approximate nearest neighbor (ANN) retrieval:
    ```sql
    CREATE INDEX idx_pnw_vectors_hnsw 
    ON pnw_document_vectors USING hnsw (embedding vector_cosine_ops);
    ```
  - Query:
    ```sql
    SELECT chunk_id, document_title, section_title, content,
           1 - (embedding <=> %s::vector) AS similarity
    FROM pnw_document_vectors
    WHERE campus = 'Both' OR campus = %s
    ORDER BY embedding <=> %s::vector ASC
    LIMIT %s;
    ```
- **Local Fallback (`SQLiteVectorStore`)**:
  - Persists vector embeddings as binary blobs in SQLite.
  - Performs exact cosine similarity via NumPy vector dot product: $\cos(\theta) = \frac{u \cdot v}{\|u\| \|v\|}$.
  - Allows the full test suite and demo pipeline to operate reliably across any developer or grading machine without requiring an active PostgreSQL instance.

---

## 3. Ingested Official PNW Documents

The pipeline ingests official Purdue University Northwest documentation located in `data/raw_documents/`:

| Document Filename | Format | Official Title | Source URL | Campus Scope |
| :--- | :--- | :--- | :--- | :--- |
| `pnw_parking_regulations.html` | HTML | PNW Traffic & Parking Regulations | [https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/](https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/) | Both (Hammond & Westville) |
| `pnw_academic_regulations.html` | HTML | PNW Academic Regulations: Registration PINs, Add/Drop & Holds | [https://www.pnw.edu/registration/academic-regulations/](https://www.pnw.edu/registration/academic-regulations/) | Both |
| `pnw_cs_graduate_plan_of_study.html` | HTML | MS in Computer Science Electronic Plan of Study (EPOS) Guide | [https://www.pnw.edu/computer-science/graduate-programs/ms-plan-of-study/](https://www.pnw.edu/computer-science/graduate-programs/ms-plan-of-study/) | Both |
| `pnw_dean_of_students_advocacy.html` | HTML | Office of the Dean of Students Locations & Student Advocacy | [https://www.pnw.edu/dean-of-students/](https://www.pnw.edu/dean-of-students/) | Hammond (SUL 313) & Westville (LSF 103) |
| `pnw_classroom_behavior_policy.pdf` | PDF | Classroom Behavior & Disruption Policy (Faculty Senate 2021-01) | [https://www.pnw.edu/faculty-senate/policies/classroom-behavior/](https://www.pnw.edu/faculty-senate/policies/classroom-behavior/) | Both |

---

## 4. CLI Usage Instructions

The pipeline can be executed via the root convenience CLI (`python pipeline.py`) or via module execution (`python -m backend.rag.pipeline`).

### 1. Ingest Documents into Vector Database
```bash
# Ingest using default PostgreSQL pgvector (with automatic local fallback)
python pipeline.py ingest --source data/raw_documents

# Or explicitly ingest into SQLite local vector store
python pipeline.py ingest --source data/raw_documents --backend sqlite

# Re-index from scratch (clear existing records)
python pipeline.py ingest --source data/raw_documents --clear
```

### 2. Semantic Vector Search
```bash
# Search for parking citation procedures with campus filtering
python pipeline.py search --query "How do I pay parking citations at Hammond?" --campus Hammond

# Search for Computer Science Plan of Study (EPOS) guidelines
python pipeline.py search --query "How do I submit my Computer Science MS Plan of Study?"

# Search for Dean of Students office locations
python pipeline.py search --query "Where is the Office of the Dean of Students located?"
```

### 3. Inspect Vector Database Statistics
```bash
python pipeline.py stats
```

---

## 5. PostgreSQL pgvector Setup (Docker)

To launch a dedicated PostgreSQL instance with the `pgvector` extension pre-installed:

```bash
# Start PostgreSQL pgvector container in the background
docker compose up -d

# Verify container status
docker ps
```

The database initializes automatically with the DDL schema in [`db/pgvector_schema.sql`](file:///C:/Users/jayp9/.gemini/antigravity-ide/scratch/pnw-knowledge-chatbot/db/pgvector_schema.sql).

---

## 6. Automated Testing

Run the full automated test suite verifying parsing, chunking, embedding, vector storage, and end-to-end retrieval:

```bash
uv run pytest
```
*(All 19 tests pass successfully)*
