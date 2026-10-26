-- ============================================================
-- Sample Benchmark SQL Queries (sample_queries.sql)
-- ============================================================

-- Query 1: Retrieve academic schedule deadlines for Fall 2026 ordered by deadline date
SELECT 
    term, 
    event_name, 
    deadline_date, 
    refund_percentage, 
    notes
FROM academic_schedules
WHERE term = 'FALL_2026'
ORDER BY deadline_date ASC;

-- Query 2: Retrieve course prerequisites for CS 30200 with campus availability
SELECT 
    course_code, 
    course_title, 
    prerequisite_code, 
    minimum_grade, 
    campus_availability
FROM course_prerequisites
WHERE course_code = 'CS 30200';

-- Query 3: Retrieve parking ticket payment rules for Hammond campus
SELECT 
    c.name AS campus_name, 
    pr.topic, 
    pr.rule_summary, 
    pr.official_portal_url
FROM parking_rules pr
JOIN campuses c ON pr.campus_id = c.id
WHERE c.code = 'HAMMOND' AND pr.topic = 'TICKET_PAYMENT';

-- Query 4: Search document chunks for policy keyword matching
SELECT 
    d.title AS document_title, 
    dc.section_title, 
    dc.content, 
    d.source_url
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id
WHERE dc.content LIKE '%parking%' OR dc.content LIKE '%ticket%'
LIMIT 5;

-- Query 5: Retrieve conversation history with message citations
SELECT 
    cm.sender, 
    cm.message_text, 
    cm.is_grounded, 
    cm.citations_json, 
    cm.created_at
FROM chat_messages cm
JOIN conversations c ON cm.conversation_id = c.id
WHERE c.session_id = 'sample-session-uuid-123'
ORDER BY cm.created_at ASC;
