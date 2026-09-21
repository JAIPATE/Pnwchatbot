# Software Specification (spec.md) - PNW Knowledge Chatbot

**Project Title**: Purdue University Northwest (PNW) Knowledge Chatbot  
**Status**: Approved  
**Methodology**: Spec-Driven Development (SDD) / GitHub Spec Kit  

---

## 1. Executive Summary

Students at Purdue University Northwest frequently encounter difficulties obtaining accurate, timely answers to common academic and policy questions. Official university policies, academic schedules, course prerequisites, and parking rules are scattered across multi-page PDF handbooks, nested website URLs, and complex HTML tables. Furthermore, policies differ between the **Hammond** and **Westville** campuses.

This project delivers a **Knowledge-Based Chatbot** and interactive student portal that ingests approved PNW documentation, structures complex tables and course prerequisite trees, enforces campus awareness, and provides **grounded, cited answers** while failing safely when data is unavailable.

---

## 2. Requirement Analysis & Input Sources

### A. Stakeholder Interview Summary (Dean of Students Office)
- **Director**: Staff spend substantial time answering repetitive student inquiries regarding add/drop dates, academic standing, grade appeals, and registration errors.
- **Service Coordinator (Jane)**: Primary concern is accuracy. The chatbot **must not quote incorrect or outdated policy information**.

### B. Student Interview Findings
- **Interview 1**: Student searched Google and MyPNW for parking ticket payment procedures but got stuck in link loops. Noted that existing bot ("Leo") only provides links.
- **Interview 2**: Student searched for Computer Science Ph.D. program information; search results failed to answer direct questions, forcing them to contact an advisor.
- **Interview 3**: Student received registration error code while scheduling classes; university search provided no direct solution.
- **Interview 4 (Graduate Student)**: Student needed Master's CS Plan of Study (POS) submission instructions, course selection details, and deadline information. Found information spread across multiple sites.

### C. Corpus Review & Technical Challenges Identified
1. **Multi-Level Links & Nested Pages (Parking & Policy Docs)**: Ingens must follow attached PDFs and sub-links to present full instructions (how to appeal/pay) instead of looping links.
2. **HTML Table Deadlines (Academic Schedule)**: Fall/Spring/Summer drop/add and refund percentage tables must be parsed cleanly (e.g., Markdown/JSON) so text splitters don't scramble dates.
3. **Fragmented Course Prerequisites & Campus Tags**: Prerequisites hidden in pop-ups must be combined into unified dependency summaries and campus tags (Hammond vs. Westville).

---

## 3. Core Functional Requirements

- **FR-1 [Grounded RAG Search]**: The system shall retrieve relevant document chunks from official PNW sources and generate answers containing explicit citation links.
- **FR-2 [Fail-Safe Guardrail]**: When retrieved document relevance score is below threshold, the chatbot shall output a polite refusal directing the student to official department contacts.
- **FR-3 [Campus Filtering]**: The system shall allow users to select their active campus (Hammond or Westville) and filter campus-specific course offerings and parking rules.
- **FR-4 [Academic Schedule Table Lookup]**: The system shall provide structured lookup for term deadlines (100% refund, 50% refund, drop deadlines) without scrambling dates.
- **FR-5 [Prerequisite Graph & Summary]**: The system shall combine course prerequisites into an interactive visual graph and clear text summary.
- **FR-6 [Real-Time Streaming SSE]**: The chatbot shall stream responses token-by-token over Server-Sent Events (SSE) for minimal latency.

---

## 4. Non-Functional Requirements

- **NFR-1 [Response Latency]**: Initial SSE stream token response shall commence within 1.5 seconds of user submission.
- **NFR-2 [Accuracy & Groundedness]**: 100% of factual statements in answers must match underlying seeded corpus documents.
- **NFR-3 [Usability & Aesthetics]**: Frontend UI must feature modern, dark/gold Purdue Northwest aesthetics, clean typography, responsive layout, and visual feedback.
- **NFR-4 [Extensibility]**: Code organization must follow layered architecture allowing new document sources to be indexed seamlessly.
