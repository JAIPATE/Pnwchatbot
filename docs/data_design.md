# Logical Data Model (data-model.md) - Entities & Relationships

This document specifies the logical data entities, attributes, relationships, validation rules, and state transitions extracted from the User Stories, Acceptance Criteria (ACs), and PNW document corpus.

---

## 🏢 Entities & Attributes

### 1. Campus
- `id`: Integer (Primary Key, Autoincrement)
- `code`: String(30), Unique, Not Null (e.g., `"HAMMOND"`, `"WESTVILLE"`)
- `name`: String(100), Not Null (e.g., `"Purdue University Northwest - Hammond Campus"`)
- `is_active`: Boolean, Default `True`

### 2. Document
- `id`: Integer (Primary Key, Autoincrement)
- `title`: String(200), Not Null (e.g., `"PNW Student Handbook 2024-2025"`)
- `category`: Enum/String(50), Not Null (`"POLICY"`, `"PARKING"`, `"ACADEMIC_CATALOG"`, `"SCHEDULE"`, `"ACCESSIBILITY"`)
- `source_url`: String(500), Not Null (Official PNW webpage or PDF URL)
- `file_type`: String(20), Not Null (`"PDF"`, `"HTML"`, `"WORD"`)
- `last_updated`: Date/String, Not Null

### 3. DocumentChunk
- `id`: Integer (Primary Key, Autoincrement)
- `document_id`: Integer, Foreign Key -> `Document.id`, Not Null
- `chunk_index`: Integer, Not Null (Zero-based ordering within document)
- `section_title`: String(200), Not Null (e.g., `"Academic Integrity & Misconduct"`)
- `content`: Text, Not Null (Extracted text or markdown table content)
- `campus_id`: Integer, Foreign Key -> `Campus.id`, Nullable (Null if applicable to both campuses)

### 4. AcademicSchedule
- `id`: Integer (Primary Key, Autoincrement)
- `term`: String(50), Not Null (`"FALL_2026"`, `"SPRING_2026"`, `"SUMMER_2026"`)
- `event_name`: String(200), Not Null (e.g., `"100% Tuition Refund Deadline"`)
- `deadline_date`: Date, Not Null
- `refund_percentage`: Integer, Check `(refund_percentage >= 0 AND refund_percentage <= 100)`
- `notes`: Text, Nullable

### 5. CoursePrerequisite
- `id`: Integer (Primary Key, Autoincrement)
- `course_code`: String(20), Not Null (e.g., `"CS 30200"`)
- `course_title`: String(150), Not Null (e.g., `"Data Structures & Algorithms"`)
- `prerequisite_code`: String(20), Nullable (e.g., `"CS 18000"`)
- `minimum_grade`: String(5), Default `"C"`
- `campus_availability`: Enum/String(50), Not Null (`"HAMMOND_AND_WESTVILLE"`, `"HAMMOND_ONLY"`, `"WESTVILLE_ONLY"`)

### 6. ParkingRule
- `id`: Integer (Primary Key, Autoincrement)
- `campus_id`: Integer, Foreign Key -> `Campus.id`, Not Null
- `topic`: Enum/String(50), Not Null (`"TICKET_PAYMENT"`, `"APPEAL_PROCESS"`, `"PERMIT_TYPES"`, `"VISITOR_PARKING"`)
- `rule_summary`: Text, Not Null
- `official_portal_url`: String(500), Not Null

### 7. UserConversation
- `id`: Integer (Primary Key, Autoincrement)
- `session_id`: String(64), Unique, Not Null
- `campus_id`: Integer, Foreign Key -> `Campus.id`, Nullable
- `created_at`: Timestamp, Default Current Timestamp

### 8. ChatMessage
- `id`: Integer (Primary Key, Autoincrement)
- `conversation_id`: Integer, Foreign Key -> `UserConversation.id`, Not Null
- `sender`: Enum/String(20), Not Null (`"USER"`, `"ASSISTANT"`)
- `message_text`: Text, Not Null
- `is_grounded`: Boolean, Default `True`
- `citations_json`: Text / JSON, Nullable
- `created_at`: Timestamp, Default Current Timestamp

---

## 🔗 Relationships

- **Campus to DocumentChunk**: 1 to Many (`Campus 1 -- * DocumentChunk`, optional FK)
- **Campus to ParkingRule**: 1 to Many (`Campus 1 -- * ParkingRule`)
- **Document to DocumentChunk**: 1 to Many (`Document 1 -- * DocumentChunk`, cascade delete)
- **UserConversation to ChatMessage**: 1 to Many (`UserConversation 1 -- * ChatMessage`, ordered by `created_at`)
- **Campus to UserConversation**: 1 to Many (`Campus 1 -- * UserConversation`)

---

## 🛡️ Validation Rules

1. **Non-Empty Chat Query**: Incoming `query` string must not be empty or whitespace-only; triggers HTTP 400 if blank.
2. **Refund Percentage Boundary**: `refund_percentage` must be an integer between 0 and 100 inclusive (`CHECK (refund_percentage BETWEEN 0 AND 100)`).
3. **Groundedness Threshold**: If computed similarity score $S < 0.45$:
   - `is_grounded` is set to `False`
   - `response_text` must default to official fail-safe departmental contact refusal
   - Hallucinated or external ungrounded text generation is strictly disallowed
4. **Campus Code Uniqueness**: `Campus.code` must be unique and uppercase (`CHECK (code IN ('HAMMOND', 'WESTVILLE'))`).
5. **Course Code Format**: Course codes must adhere to standard department + number convention (e.g., `CS 30200`, `MA 16300`).

---

## 🔄 State Transitions

### Chat Query Lifecycle

```text
[User Input Received]
         │
         ▼
[Validate Query Payload] ──(Empty String)──> [HTTP 400 Bad Request]
         │ (Valid)
         ▼
[Retrieve Corpus Chunks & Calculate Score S]
         │
    ┌────┴────────────────────────┐
    │ S >= 0.45                   │ S < 0.45
    ▼                             ▼
[Grounded Response State]     [Fail-Safe Fallback State]
- is_grounded = True          - is_grounded = False
- Synthesize answer text      - Provide Dean of Students / Advising contacts
- Extract matching citations  - Empty or general policy citations
    │                             │
    └────┬────────────────────────┘
         │
         ▼
[Format JSON / Stream SSE Tokens]
         │
         ▼
[Completed & Client Rendered]
```
