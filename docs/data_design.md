# Logical Data Design (data_design.md) - Entities & Relationships

This document specifies the logical data entities, attributes, and relationships extracted from the User Stories, Acceptance Criteria (ACs), and PNW document corpus.

---

## 🏢 Entities & Attributes

### 1. Campus
- `id` (Surrogate Primary Key, Integer)
- `code` (Unique campus code, e.g. "HAMMOND", "WESTVILLE")
- `name` (Full campus name, e.g. "Purdue University Northwest - Hammond Campus")
- `is_active` (Boolean)

### 2. Document
- `id` (Surrogate Primary Key, Integer)
- `title` (Document title, e.g. "PNW Student Handbook 2024-2025")
- `category` (Category: "POLICY", "PARKING", "ACADEMIC_CATALOG", "SCHEDULE", "ACCESSIBILITY")
- `source_url` (URL link to official PNW webpage or PDF document)
- `file_type` (File type: "PDF", "HTML", "WORD")
- `last_updated` (Date)

### 3. DocumentChunk
- `id` (Surrogate Primary Key, Integer)
- `document_id` (Foreign Key -> Document.id)
- `chunk_index` (Integer order index)
- `section_title` (Section heading, e.g. "Academic Integrity & Misconduct")
- `content` (Extracted raw text or markdown table content)
- `campus_id` (Foreign Key -> Campus.id, Nullable if applies to all campuses)

### 4. AcademicSchedule
- `id` (Surrogate Primary Key, Integer)
- `term` (Term name: "FALL_2026", "SPRING_2026", "SUMMER_2026")
- `event_name` (Event name, e.g. "100% Tuition Refund Deadline", "Last Day to Drop")
- `deadline_date` (Date)
- `refund_percentage` (Integer check: 0 to 100)
- `notes` (Additional term policy details)

### 5. CoursePrerequisite
- `id` (Surrogate Primary Key, Integer)
- `course_code` (Course code, e.g. "CS 30200")
- `course_title` (Course title, e.g. "Data Structures & Algorithms")
- `prerequisite_code` (Prerequisite course code, e.g. "CS 18000")
- `minimum_grade` (Required grade, e.g. "C")
- `campus_availability` (Text string: "HAMMOND_AND_WESTVILLE", "HAMMOND_ONLY", "WESTVILLE_ONLY")

### 6. ParkingRule
- `id` (Surrogate Primary Key, Integer)
- `campus_id` (Foreign Key -> Campus.id)
- `topic` (Topic: "TICKET_PAYMENT", "APPEAL_PROCESS", "PERMIT_TYPES", "VISITOR_PARKING")
- `rule_summary` (Concise step-by-step summary)
- `official_portal_url` (Link to MyPNW / Student Accounts Payment Portal)

### 7. UserConversation
- `id` (Surrogate Primary Key, Integer)
- `session_id` (Unique UUID string)
- `campus_id` (Foreign Key -> Campus.id)
- `created_at` (Timestamp)

### 8. ChatMessage
- `id` (Surrogate Primary Key, Integer)
- `conversation_id` (Foreign Key -> UserConversation.id)
- `sender` (Sender: "USER", "ASSISTANT")
- `message_text` (Text content of the message)
- `is_grounded` (Boolean)
- `citations_json` (JSON list of source document links and titles)
- `created_at` (Timestamp)

---

## 🔗 Relationships

- **One Campus can have many Document Chunks** (`Campus 1 -- * DocumentChunk`).
- **One Campus can have many Parking Rules** (`Campus 1 -- * ParkingRule`).
- **One Document can have many Document Chunks** (`Document 1 -- * DocumentChunk`).
- **One User Conversation can have many Chat Messages** (`UserConversation 1 -- * ChatMessage`).
- **One Course can have many Prerequisites** (`CoursePrerequisite` self-referential or mapping table).
