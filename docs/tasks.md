# Phased Execution Tasks (tasks.md)

Task breakdown across all 6 phases of the PNW Knowledge Chatbot development lifecycle.

---

## Phase 1: Setup & Scaffold (Completed)
- [x] Create project directory structure (`docs/`, `db/`, `backend/`, `frontend/`, `tests/`)
- [x] Initialize Git repository
- [x] Create `.gitignore`, `README.md`, `requirements.txt`, `pyproject.toml`
- [x] Commit Phase 1 setup

## Phase 2: Spec Kit & Software Engineering Documentation (Completed)
- [x] Create `docs/constitution.md`
- [x] Create `docs/assumptions_and_scope.md`
- [x] Create `docs/spec.md`
- [x] Create `docs/user_stories_and_acs.md`
- [x] Create `docs/architecture_decision_record.md` (ADR)
- [x] Create `docs/tech_stack_decision_record.md` (TSDR)
- [x] Create `docs/data_design.md`
- [x] Create `docs/erd.md`
- [x] Create `docs/plan.md` & `docs/research.md`
- [x] Create `docs/quickstart.md`
- [x] Create `docs/contracts/openapi.json`
- [x] Commit Phase 2 documentation

## Phase 3: Physical Data Design & Database Layer (Completed)
- [x] Create `db/schema.sql` (PostgreSQL / SQLite DDL with PK, FK, CHECK constraints)
- [x] Create `db/sample_queries.sql` (Benchmark SQL queries)
- [x] Create `db/seed_data.py` (Ingest PNW corpus: Parking, Schedule, Prereqs, Handbook)
- [x] Commit Phase 3 database

## Phase 4: FastAPI Backend & RAG Engine (Completed)
- [x] Build `backend/database.py` and models
- [x] Build `backend/services/rag_service.py` with fail-safe guardrail
- [x] Build `backend/services/prereq_service.py` & `schedule_service.py`
- [x] Build FastAPI routers (`chat.py`, `schedule.py`, `prereq.py`, `campus.py`)
- [x] Write backend unit tests in `tests/`
- [x] Commit Phase 4 backend

## Phase 5: React Frontend UI & Interactive Tools (Completed)
- [x] Build React SPA frontend shell & PNW Gold/Dark design system
- [x] Build `CampusSelector.jsx` modal
- [x] Build `ChatWindow.jsx` with SSE streaming and citation popovers
- [x] Build `ScheduleTable.jsx` and `PrereqGraph.jsx`
- [x] Commit Phase 5 frontend

## Phase 6: Integration, Testing & Verification (Completed)
- [x] Perform E2E integration test
- [x] Run backend & database test suite (9 passed in 2.67s)
- [x] Generate final walkthrough documentation
- [x] Final Commit
