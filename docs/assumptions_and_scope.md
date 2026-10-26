# Assumptions & Scope - PNW Knowledge Chatbot

This document defines the operational boundaries, user personas, and explicit scope constraints for the Purdue University Northwest Knowledge Chatbot system.

---

## 🎯 Target User Roles (In-Scope)

1. **Currently Registered Undergraduate Students**:
   - Students inquiring about adding/dropping courses, academic schedule deadlines, refund percentages, registration errors, prerequisite graphs, and campus parking regulations.
2. **Currently Registered Graduate Students**:
   - Graduate students inquiring about CS Master's/Ph.D. program availability, Plan of Study (POS) submission workflows, advisor approval requirements, and graduate school admission policies.

---

## 🚫 Out-of-Scope User Roles & Use Cases

- **Faculty & University Staff**: Administration or teaching staff looking for payroll, employee benefits, or internal faculty senate tools.
- **Prospective / Future Applicants**: General inquiries from non-admitted students that require CRM integration or admissions application processing.
- **Automated Registration Execution**: The chatbot is an **informational assistant**, not an automated registration bot. It does not perform course registration directly in the student portal (MyPNW).

---

## 🏢 Campus Assumptions & Boundaries

- **Supported Campuses**:
  - **Hammond Campus**
  - **Westville Campus**
- **Data Source Corpus**:
  - PNW Parking Regulations & Fees Document (PDF & Web)
  - PNW Academic Schedule & Deadline Tables (Fall, Spring, Summer)
  - PNW Academic Catalog & Course Prerequisites
  - PNW Graduate School Admission & Policy Webpages
  - PNW Student Handbook (PDF)
  - PNW Classroom Behavior Policy (PDF)
  - PNW Information Services Policies
  - PNW Academic Integrity Policy

---

## ⚡ Technical Assumptions

1. **Local & Cloud Deployability**: System runs seamlessly locally via Uvicorn/FastAPI + React SPA or on managed cloud services.
2. **Synchronous & SSE Streaming API**: User conversations support real-time token streaming over Server-Sent Events (SSE) for immediate visual feedback.
3. **Database Engine**: Relational database (SQLite locally / PostgreSQL in production) storing structured tables for schedules, prerequisites, parking rules, vector chunks, and conversation histories.
