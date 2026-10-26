# Feature Specification: Purdue Northwest (PNW) Knowledge Chatbot

**Feature Branch**: `001-pnw-knowledge-chatbot`
**Created**: 2026-09-14
**Status**: Draft
**Input**: Comprehensive synthesis of Stakeholder Interviews (Dean of Students Director & Jane), User Interviews (Students 1-3), and Initial Corpus Review (3 PNW Official Documentation Sources).

---

## Clarifications

### Session 2026-10-26
- Q: How should the chatbot verify or enforce that access is scoped to registered PNW students while personal myPNW database integration remains out of scope? (FR-007) → A: Open web portal with no login required; prompts and system responses are scoped strictly to PNW student topics without requiring student authentication credentials.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Direct Grounded Answers for University Policies & Campus Services (Priority: P1)

As a registered PNW undergraduate or graduate student,
I want to ask direct questions about university policies, deadlines, parking citations, registration errors, and office locations,
So that I can receive immediate, accurate, and grounded answers without navigating multiple fragmented web pages.

**Why this priority**: Core value proposition identified by stakeholders and students. Eliminates repetitive questions for staff and saves students time.

**Independent Test**: Query the chatbot with specific questions (e.g., "How do I pay parking tickets at Hammond?", "What are the add/drop deadlines?"). The chatbot returns concise, accurate instructions grounded in official PNW documentation.

**Acceptance Scenarios**:

1. **Given** a student asks how to pay a parking citation,
   **When** the chatbot processes the query against the official PNW Traffic & Parking corpus,
   **Then** it responds with exact steps to pay or appeal virtual citations via the PNW portal link, distinguishing Hammond/Westville rules from West Lafayette rules.

2. **Given** a student asks for the Office of the Dean of Students location,
   **When** the student specifies their campus or asks generally,
   **Then** the chatbot clearly distinguishes between the Hammond campus location (SUL Room 313) and the Westville campus location (Library-Student Faculty Building Room 103).

---

### User Story 2 - Academic Requirements & Plan of Study (POS) Guidance (Priority: P1)

As a graduate or undergraduate student,
I want to query academic program requirements, registration procedures, and Plan of Study (POS) submission steps,
So that I can select required courses accurately and avoid registration delays or extra semesters.

**Why this priority**: Crucial student pain point where outdated/confusing information led to missed course requirements, registration errors, and delayed graduation.

**Independent Test**: Query "How do I submit my Computer Science MS Plan of Study?". The chatbot returns step-by-step instructions for completing the EPOS in myPNW and highlights required advisor approval steps.

**Acceptance Scenarios**:

1. **Given** a CS graduate student asking about POS requirements,
   **When** querying course selection and submission procedures,
   **Then** the chatbot outlines the myPNW EPOS workflow, notes required core/elective credits, and explicitly instructs the student to obtain advisor approval before final submission.

2. **Given** an undergraduate student asking about registration PINs or course prerequisites,
   **When** asking how to register for classes,
   **Then** the chatbot explains that academic advisor clearance is required to receive a registration PIN and directs the student to schedule an advising appointment.

---

### User Story 3 - Fail-Safe & Departmental Routing (Priority: P2)

As a student with a complex, personalized, or ungrounded inquiry,
I want the chatbot to fail safely when official information is absent or ambiguous,
So that I am not given inaccurate or hallucinated policy details.

**Why this priority**: Enforces Constitution Principle #2 (Fail Safely). Stakeholder Jane stressed that providing incorrect policy information is an unacceptable risk.

**Independent Test**: Submit a question regarding a hypothetical policy not in the corpus or a complex personal registration error. The system responds with an explicit "I don't know" / unsupported message and provides direct contact info for the appropriate PNW department.

**Acceptance Scenarios**:

1. **Given** a student query that cannot be answered using the grounded PNW document corpus,
   **When** the confidence or available reliable data is insufficient,
   **Then** the chatbot responds stating it cannot provide a reliable answer and provides the contact details (email/phone/office) for the Dean of Students or relevant academic department.

---

### User Story 4 - Citation & Source Transparency (Priority: P3)

As a student reviewing chatbot responses,
I want to see direct source links to official PNW web pages and documents for every answer provided,
So that I can independently verify the rules and access official submission forms.

**Why this priority**: Addresses student feedback regarding existing chatbot ("Leo") which only gave generic links; provides transparency while linking to primary official sources.

**Independent Test**: Ask any valid policy query. Ensure the output contains markdown links to the specific official PNW documentation source.

**Acceptance Scenarios**:

1. **Given** any generated response based on PNW corpus data,
   **When** rendering the final answer to the student,
   **Then** the chatbot appends clickable source links (e.g., `[PNW Registration Regulations](https://www.pnw.edu/registration/)`) pointing to the official source document.

---

### Edge Cases

- **Cross-Campus Confusion**: Queries mentioning generic "Purdue" rules that apply to West Lafayette (e.g., parking garages) must be filtered or explicitly flagged as non-applicable to PNW Hammond/Westville.
- **Outdated / Conflicting Information in Corpus**: When two corpus documents present conflicting rules, the system must prioritize the document with the most recent publication/effective date and note the dependency.
- **Personalized Student State**: For queries requiring specific individual data (e.g., "Why is there a hold on my student account?"), the system must instruct the student on how to check holds in myPNW and contact the Bursar or Registrar.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide answers grounded strictly in approved PNW documentation (Academic Regulations, Course Catalogs, Degree Maps, Parking Rules).
- **FR-002**: System MUST fail safely by declining to answer ("I don't know") and providing departmental contact information whenever corpus data is insufficient or ambiguous.
- **FR-003**: System MUST distinguish between PNW Hammond and PNW Westville campus specifications in all location- or service-dependent responses.
- **FR-004**: System MUST include direct reference links to official PNW web pages/documents for every generated answer.
- **FR-005**: System MUST provide clear guidance on academic procedures including Plan of Study (EPOS) workflows, registration PIN procedures, and grade appeal steps.
- **FR-006**: System MUST filter out non-PNW (e.g., Purdue West Lafayette) policies to prevent cross-campus misinformation.
- **FR-007**: System MUST provide open web portal access without requiring student login or authentication, scoping prompts, corpus data, and system responses strictly to registered PNW undergraduate and graduate student topics.
- **FR-008**: System MUST support query processing for common student topics: add/drop classes, academic standing, financial aid deadlines, parking, and registration errors.

### Key Entities

- **Document Corpus**: Collection of official PNW PDFs, HTML web pages, and policy handbooks categorized by department and campus.
- **Student Query**: Text question submitted by a student containing intent, topic, and optional campus context.
- **Grounded Answer**: Generated text response derived strictly from matching text chunks within the document corpus.
- **Department Contact**: Structured contact metadata (Department Name, Office Location, Email, Phone) mapped to topic categories for safe routing.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated answers are verified to be grounded in official PNW documentation (0% hallucinated policy information).
- **SC-002**: 100% of ungrounded or out-of-scope queries trigger the fail-safe response with appropriate departmental contact information.
- **SC-003**: Students receive answers with direct official source citations in under 3 seconds.
- **SC-004**: Campus-specific queries accurately identify Hammond vs. Westville details 100% of the time.

---

## Assumptions & Scope

### In-Scope
- Answering student questions on PNW policies, academic regulations, registration processes, plan of study workflows, and campus services.
- Open web portal access with queries and answers scoped to registered PNW student topics.
- Retrieval-augmented response generation using approved PNW document corpus.
- Fail-safe fallback and departmental routing.
- Source URL citation for all answers.

### Out-of-Scope
- Student authentication credentials or SSO/Purdue Career Account login barriers.
- Live integration with myPNW student database or private student academic records (grades, financial balance).
- Processing transactions (e.g., automatically submitting a plan of study or registering for a class on behalf of a student).
- Support for external public marketing inquiries or faculty internal administrative workflows.
