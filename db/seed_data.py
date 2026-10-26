import sqlite3
import os
from pathlib import Path

# Paths
DB_DIR = Path(__file__).parent
PROJECT_DIR = DB_DIR.parent
DB_PATH = DB_DIR / "pnw_database.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

def seed_database():
    print(f"[INFO] Initializing database at {DB_PATH}")
    
    # Remove existing DB file if clean re-seed is desired
    if DB_PATH.exists():
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Execute Schema DDL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("[INFO] Schema created successfully.")
    
    # 1. Seed Campuses
    cursor.executemany(
        "INSERT INTO campuses (code, name, is_active) VALUES (?, ?, ?)",
        [
            ("HAMMOND", "Purdue University Northwest - Hammond Campus", 1),
            ("WESTVILLE", "Purdue University Northwest - Westville Campus", 1)
        ]
    )
    
    # 2. Seed Documents
    documents_data = [
        (
            "PNW Parking Regulations & Fee Enforcement",
            "PARKING",
            "https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/",
            "HTML",
            "2026-08-01"
        ),
        (
            "PNW Academic Schedule & Tuition Refund Policy",
            "SCHEDULE",
            "https://www.pnw.edu/registrar/academic-schedule/",
            "HTML",
            "2026-08-15"
        ),
        (
            "PNW Academic Catalog & CS Course Prerequisites",
            "ACADEMIC_CATALOG",
            "https://catalog.pnw.edu/preview_program.php?catoid=5&poid=1338&returnto=271",
            "HTML",
            "2026-08-20"
        ),
        (
            "PNW Student Handbook 2024-2025",
            "HANDBOOK",
            "https://www.pnw.edu/concurrent-enrollment/wp-content/uploads/sites/4/2020/02/STUDENT-HANDBOOK.pdf",
            "PDF",
            "2024-02-01"
        ),
        (
            "PNW Classroom Behavior Policy",
            "POLICY",
            "https://www.pnw.edu/faculty-senate/wp-content/uploads/sites/71/2021/01/Classroom-Behavior-Policy.pdf",
            "PDF",
            "2021-01-15"
        ),
        (
            "PNW Graduate School Admission & Plan of Study Policy",
            "POLICY",
            "https://catalog.pnw.edu/content.php?catoid=4&navoid=154#admission-to-the-graduate-school",
            "HTML",
            "2026-07-10"
        ),
        (
            "PNW Academic Integrity Policy",
            "POLICY",
            "https://www.pnw.edu/dean-of-students/policies/academic-integrity-policy/",
            "HTML",
            "2026-06-01"
        ),
        (
            "PNW Accessibility Policy",
            "ACCESSIBILITY",
            "https://www.pnw.edu/accessibility-at-purdue-university-northwest/",
            "HTML",
            "2026-05-15"
        )
    ]
    cursor.executemany(
        "INSERT INTO documents (title, category, source_url, file_type, last_updated) VALUES (?, ?, ?, ?, ?)",
        documents_data
    )
    
    # 3. Seed Document Chunks
    chunks_data = [
        # Parking Chunks
        (1, 1, 0, "Parking Ticket Payment & Appeal Process", 
         "Students who receive a PNW parking ticket or citation must pay or file an appeal within 14 calendar days of issuance. Payment can be processed through the Student Accounts Portal on MyPNW or directly at the Bursar's office. To file a parking ticket appeal, students must fill out the online Parking Citation Appeal Form attached to the Parking Services webpage. Unpaid tickets will result in a transcript hold."),
        (1, 2, 1, "Campus Specific Parking Zones", 
         "Hammond Campus requires valid student parking permits in Lots 1, 2, and 3. Westville Campus permits are valid in all general student lots. Permits must be displayed on the rear-view mirror."),
        
        # Schedule Chunks
        (2, None, 0, "Fall 2026 Tuition Refund & Drop Deadlines", 
         "Fall 2026 Semester Schedule Deadlines:\n- 100% Tuition Refund: August 30, 2026\n- 80% Tuition Refund: September 6, 2026\n- 50% Tuition Refund: September 20, 2026\n- Last Day to Drop without Grade Penalty (W): October 25, 2026\n- Final Registration Drop Deadline: November 15, 2026"),
        (2, None, 1, "Spring 2026 Tuition Refund & Drop Deadlines", 
         "Spring 2026 Semester Schedule Deadlines:\n- 100% Tuition Refund: January 20, 2026\n- 80% Tuition Refund: January 27, 2026\n- 50% Tuition Refund: February 10, 2026\n- Last Day to Drop without Grade Penalty (W): March 22, 2026"),
         
        # Academic Catalog & Prerequisites Chunks
        (3, 1, 0, "Computer Science Major & Course Offerings", 
         "The Department of Computer Science offers undergraduate and graduate programs at the Hammond campus and Westville campus. Core courses include CS 18000 (Problem Solving & Object-Oriented Programming), CS 24000 (C Programming), CS 30200 (Data Structures & Algorithms), and CS 38100 (Analysis of Algorithms)."),
        (3, None, 1, "CS 30200 Prerequisites", 
         "Course: CS 30200 Data Structures. Prerequisites: CS 18000 (Minimum grade C) and MA 16100 Calculus I (Minimum grade C). Offered at Hammond and Westville campuses."),
         
        # Graduate Admission & Plan of Study (POS)
        (6, None, 0, "Graduate CS Plan of Study (POS) Workflow", 
         "Master's students in Computer Science must submit an official Plan of Study (POS) before completing 15 credit hours. The POS outlines required core courses, electives, and thesis/non-thesis options. Students must obtain approval from their assigned Academic Advisor before submitting the POS via the Graduate School portal."),
        (6, None, 1, "PNW Ph.D. Program Availability Note", 
         "Purdue University Northwest offers Master of Science (M.S.) degrees in Computer Science, Electrical Engineering, and Mechanical Engineering. PNW does not directly confer an independent Computer Science Ph.D. degree on campus; Ph.D. candidates enroll through joint programs with Purdue West Lafayette."),
         
        # Student Handbook & Behavior Policy
        (4, None, 0, "Student Responsibilities & Rights", 
         "The PNW Student Handbook outlines expectations for student conduct, academic integrity, campus safety, and grievance procedures. Students are responsible for reviewing rules on academic dishonesty, disruptive classroom behavior, and campus safety protocols."),
        (5, None, 0, "Classroom Behavior & Disruptions", 
         "Instructors have authority to manage the classroom environment. Disruptive behavior, unexcused absences, or harassment will result in referral to the Dean of Students Office.")
    ]
    cursor.executemany(
        "INSERT INTO document_chunks (document_id, campus_id, chunk_index, section_title, content) VALUES (?, ?, ?, ?, ?)",
        chunks_data
    )
    
    # 4. Seed Academic Schedules Table
    schedules_data = [
        ("FALL_2026", "Classes Begin", "2026-08-24", 100, "First day of full term classes"),
        ("FALL_2026", "100% Refund & Last Day to Add", "2026-08-30", 100, "Full refund period ends at 11:59 PM"),
        ("FALL_2026", "80% Refund Deadline", "2026-09-06", 80, "80% refund for course drops"),
        ("FALL_2026", "50% Refund Deadline", "2026-09-20", 50, "50% refund for course drops"),
        ("FALL_2026", "Last Day to Drop with W Grade", "2026-10-25", 0, "Grade of W assigned"),
        ("SPRING_2026", "Classes Begin", "2026-01-12", 100, "First day of spring semester"),
        ("SPRING_2026", "100% Refund & Last Day to Add", "2026-01-20", 100, "Full refund deadline"),
        ("SPRING_2026", "50% Refund Deadline", "2026-02-10", 50, "50% refund deadline"),
        ("SUMMER_2026", "100% Refund Deadline", "2026-06-05", 100, "Summer term add/drop deadline")
    ]
    cursor.executemany(
        "INSERT INTO academic_schedules (term, event_name, deadline_date, refund_percentage, notes) VALUES (?, ?, ?, ?, ?)",
        schedules_data
    )
    
    # 5. Seed Course Prerequisites Table
    prereqs_data = [
        ("CS 18000", "Problem Solving & Object-Oriented Programming", "CS 14900", "C", "HAMMOND_AND_WESTVILLE"),
        ("CS 24000", "Programming in C", "CS 18000", "C", "HAMMOND_AND_WESTVILLE"),
        ("CS 25100", "Data Structures & Algorithms I", "CS 18000", "C", "HAMMOND_ONLY"),
        ("CS 30200", "Data Structures", "CS 18000", "C", "HAMMOND_AND_WESTVILLE"),
        ("CS 30200", "Data Structures", "MA 16100", "C", "HAMMOND_AND_WESTVILLE"),
        ("CS 38100", "Analysis of Algorithms", "CS 30200", "C", "HAMMOND_ONLY"),
        ("CS 38100", "Analysis of Algorithms", "MA 26500", "C", "HAMMOND_ONLY"),
        ("CS 40800", "Software Engineering", "CS 30200", "C", "HAMMOND_AND_WESTVILLE")
    ]
    cursor.executemany(
        "INSERT INTO course_prerequisites (course_code, course_title, prerequisite_code, minimum_grade, campus_availability) VALUES (?, ?, ?, ?, ?)",
        prereqs_data
    )
    
    # 6. Seed Parking Rules Table
    parking_data = [
        (1, "TICKET_PAYMENT", 
         "Pay parking tickets within 14 calendar days via the Student Accounts Portal on MyPNW or at the Bursar's Office. Failure to pay will result in a transcript hold.",
         "https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/"),
        (1, "APPEAL_PROCESS", 
         "File a parking ticket appeal online within 14 calendar days using the Parking Citation Appeal Form on the Parking Services website.",
         "https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/"),
        (2, "TICKET_PAYMENT", 
         "Westville Campus parking fines must be paid at the Westville Student Accounts Office or online through MyPNW within 14 days.",
         "https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/")
    ]
    cursor.executemany(
        "INSERT INTO parking_rules (campus_id, topic, rule_summary, official_portal_url) VALUES (?, ?, ?, ?)",
        parking_data
    )
    
    conn.commit()
    conn.close()
    print("[INFO] Database successfully seeded with PNW corpus data.")

if __name__ == "__main__":
    seed_database()
