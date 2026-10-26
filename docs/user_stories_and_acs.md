# User Stories & Acceptance Criteria (GitHub Issues)

This document contains executable User Stories and Acceptance Criteria (ACs) formatted according to GitHub Issue standards (`[Verb] + [Object]` title format, `Enhancement` label).

---

## Issue 1: Ask PNW policy questions with grounded answers

**Title**: Ask PNW policy questions  
**Label**: `enhancement`  
**Assignee**: `@self`  

### User Story
As a **currently registered student**,  
I want to **ask natural language questions about PNW policies, registration, parking, and deadlines**,  
so that **I can get immediate, clear answers without browsing multiple websites or calling staff**.

### Acceptance Criteria
- **AC1 [Grounded Answer]**: Given an official question about PNW policy, when the chatbot answers, the response must be strictly derived from ingested PNW documents.
- **AC2 [Citations Included]**: Given any factual policy answer, the system must display clickable citation links leading to the source document or section.
- **AC3 [Fail-Safe Trigger]**: Given an off-topic or ungrounded question (or low vector match score), the chatbot must respond with a fail-safe message ("I don't know / contact advisor") and provide office contact info.

---

## Issue 2: Select campus context for localized information

**Title**: Select campus context  
**Label**: `enhancement`  
**Assignee**: `@self`  

### User Story
As a **student attending Hammond or Westville campus**,  
I want to **select my primary campus location**,  
so that **the chatbot provides accurate course availability, prerequisite locations, and parking regulations specific to my campus**.

### Acceptance Criteria
- **AC4 [Campus Switcher]**: Given the user opens the application, the system displays a prominent selector for **Hammond Campus** or **Westville Campus**.
- **AC5 [Campus-Filtered Results]**: Given Hammond is selected, parking and prerequisite lookups return Hammond-specific rules and course availability.

---

## Issue 3: View academic schedule deadlines and drop/add dates

**Title**: View academic schedule deadlines  
**Label**: `enhancement`  
**Assignee**: `@self`  

### User Story
As a **student planning course registration**,  
I want to **view academic schedule deadlines for Fall, Spring, and Summer terms**,  
so that **I can verify 100% refund dates, drop deadlines, and late registration fees without date scrambling**.

### Acceptance Criteria
- **AC6 [Table Data Integrity]**: Given the user requests term deadlines, the system renders markdown/HTML tables maintaining clean row/column alignment.
- **AC7 [Current Date Check]**: Given an academic schedule lookup, the chatbot verifies dates against the current date to prevent quoting past or expired deadlines.

---

## Issue 4: Drill down into course prerequisites and visual graph

**Title**: View course prerequisites graph  
**Label**: `enhancement`  
**Assignee**: `@self`  

### User Story
As a **computer science student planning my Plan of Study**,  
I want to **see full prerequisite chains and visual graphs for courses**,  
so that **I can understand course dependencies and avoid registration errors or delayed graduation**.

### Acceptance Criteria
- **AC8 [Prerequisite Graph & Summary]**: Given a course query (e.g. "CS 30200 prerequisites"), the system displays a unified text summary and an interactive visual node graph showing all required prior courses.
