# Phased Execution Tasks (tasks.md)

Task breakdown across all 6 phases of the PNW Knowledge Chatbot development lifecycle.

---

## Phase 1: Setup & Scaffold (Completed)
- [x] Create project directory structure (`docs/`, `db/`, `backend/`, `frontend/`, `tests/`)
- [x] Initialize Git repository
- [x] Create `.gitignore`, `README.md`, `requirements.txt`, `pyproject.toml`
- [x] Commit Phase 1 setup

## Phase 2: Spec Kit & Software Engineering Documentation (In Progress)
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
- [ ] Commit Phase 2 documentation

## Phase 3: Physical Data Design & Database Layer
- [ ] Create `db/schema.sql` (PostgreSQL / SQLite DDL with PK, FK, CHECK constraints)
- [ ] Create `db/sample_queries.sql` (Benchmark SQL queries)
- [ ] Create `db/seed_data.py` (Ingest PNW corpus: Parking, Schedule, Prereqs, Handbook)
- [ ] Commit Phase 3 database

## Phase 4: FastAPI Backend & RAG Engine
- [ ] Build `backend/database.py` and models
- [ ] Build `backend/services/rag_service.py` with fail-safe guardrail
- [ ] Build `backend/services/prereq_service.py` & `schedule_service.py`
- [ ] Build FastAPI routers (`chat.py`, `schedule.py`, `prereq.py`, `campus.py`)
- [ ] Write backend unit tests in `tests/`
- [ ] Commit Phase 4 backend

## Phase 5: React Frontend UI & Interactive Tools
- [ ] Build React SPA frontend shell & PNW Gold/Dark design system
- [ ] Build `CampusSelector.jsx` modal
- [ ] Build `ChatWindow.jsx` with SSE streaming and citation popovers
- [ ] Build `ScheduleTable.jsx` and `PrereqGraph.jsx`
- [ ] Commit Phase 5 frontend

## Phase 6: Integration, Testing & Verification
- [ ] Perform E2E integration test
- [ ] Run backend & database test suite
- [ ] Generate final walkthrough documentation
- [ ] Final Commit
