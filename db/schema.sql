-- ============================================================
-- Physical Data Design (schema.sql)
-- Purdue University Northwest (PNW) Knowledge Chatbot
-- ============================================================

-- 1. Campuses Table
CREATE TABLE IF NOT EXISTS campuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- 2. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('POLICY', 'PARKING', 'ACADEMIC_CATALOG', 'SCHEDULE', 'ACCESSIBILITY', 'HANDBOOK')),
    source_url TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('PDF', 'HTML', 'WORD')),
    last_updated TEXT NOT NULL
);

-- 3. Document Chunks Table
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    campus_id INTEGER,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    section_title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
    FOREIGN KEY (campus_id) REFERENCES campuses (id) ON DELETE SET NULL
);

-- 4. Academic Schedules Table
CREATE TABLE IF NOT EXISTS academic_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL CHECK (term IN ('FALL_2026', 'SPRING_2026', 'SUMMER_2026')),
    event_name TEXT NOT NULL,
    deadline_date TEXT NOT NULL,
    refund_percentage INTEGER NOT NULL CHECK (refund_percentage >= 0 AND refund_percentage <= 100),
    notes TEXT
);

-- 5. Course Prerequisites Table
CREATE TABLE IF NOT EXISTS course_prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL,
    course_title TEXT NOT NULL,
    prerequisite_code TEXT NOT NULL,
    minimum_grade TEXT NOT NULL DEFAULT 'C',
    campus_availability TEXT NOT NULL CHECK (campus_availability IN ('HAMMOND_AND_WESTVILLE', 'HAMMOND_ONLY', 'WESTVILLE_ONLY'))
);

-- 6. Parking Rules Table
CREATE TABLE IF NOT EXISTS parking_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campus_id INTEGER NOT NULL,
    topic TEXT NOT NULL CHECK (topic IN ('TICKET_PAYMENT', 'APPEAL_PROCESS', 'PERMIT_TYPES', 'VISITOR_PARKING')),
    rule_summary TEXT NOT NULL,
    official_portal_url TEXT NOT NULL,
    FOREIGN KEY (campus_id) REFERENCES campuses (id) ON DELETE CASCADE
);

-- 7. Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    campus_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (campus_id) REFERENCES campuses (id) ON DELETE SET NULL
);

-- 8. Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender TEXT NOT NULL CHECK (sender IN ('USER', 'ASSISTANT')),
    message_text TEXT NOT NULL,
    is_grounded INTEGER NOT NULL DEFAULT 1 CHECK (is_grounded IN (0, 1)),
    citations_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_document_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_campus ON document_chunks(campus_id);
CREATE INDEX IF NOT EXISTS idx_academic_schedules_term ON academic_schedules(term);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_code ON course_prerequisites(course_code);
CREATE INDEX IF NOT EXISTS idx_parking_rules_campus ON parking_rules(campus_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON chat_messages(conversation_id);
