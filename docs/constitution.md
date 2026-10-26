# Project Constitution - PNW Knowledge Chatbot

This constitution defines the mandatory project-wide rules, non-negotiable architectural principles, and quality standards for the **Purdue University Northwest (PNW) Knowledge Chatbot**.

---

## 📜 Core Rules

### Rule 1: Grounded Answers
- All responses regarding university policies, tuition/fees, parking rules, academic schedules, and course prerequisites **must be strictly grounded** in official, approved PNW documentation.
- The chatbot **must never invent, extrapolate, or hallucinate** unsupported rules, deadlines, or requirements. Every factual response must include source references or citation links.

### Rule 2: Fail Safely
- When the system lacks sufficient reliable information or confidence in a user query, it **must fail safely**.
- Instead of returning a speculative answer, the chatbot must explicitly state:
  > *"I am sorry, but I do not have enough official PNW policy information to answer your question accurately. Please contact your Academic Advisor or the Dean of Students Office."*
- Direct contact links and department contacts must be provided upon safe failure.

### Rule 3: Requirements Before Implementation (Spec-Driven Development)
- No feature or component may be implemented without clear, reviewable, and testable requirements documented in `docs/spec.md` and `docs/user_stories_and_acs.md`.
- Technical design trade-offs must be evaluated and recorded in Architecture Decision Records (`docs/architecture_decision_record.md`) before code execution.

### Rule 4: Campus Context Awareness
- PNW operates across multiple campuses (**Hammond** and **Westville**).
- When a student asks about course availability, location-specific prerequisites, or parking rules, the system must account for or prompt the user for their target campus to avoid quoting conflicting campus policies.

### Rule 5: Preserved Data Integrity for Tables & Prerequisites
- Scraped HTML tables (e.g., Academic Schedules for Fall, Spring, Summer terms) must be parsed into clean structured formats (e.g., Markdown/JSON) that preserve exact dates and refund percentages.
- Scrambling dates or presenting outdated deadlines is strictly prohibited.
- Course prerequisites spanning multiple popups and tags must be aggregated into a single cohesive dependency summary or graph.

---

## 🛠️ Engineering Principles
- **Monolithic Layered Architecture**: Clear separation between Presentation (React Frontend), Business Logic (FastAPI Services & RAG Engine), and Data Access (SQL Persistence).
- **Data Integrity**: Database tables must enforce surrogate Primary Keys (`id`), strict data types (`DATE`, `INTEGER`, `BOOLEAN`), Foreign Key constraints with `ON DELETE CASCADE`, and `CHECK` constraints for numeric ranges.
- **Traceability & Testability**: Every user story must be accompanied by automated unit/integration tests (`pytest`).
