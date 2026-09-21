import uuid
import json
import re
from typing import Dict, List, Tuple
from backend.database import execute_query, execute_insert

# Fail-Safe refusal message requirement from Constitution
FAIL_SAFE_REFUSAL = (
    "I am sorry, but I do not have enough official Purdue University Northwest policy information "
    "to answer your question accurately. To ensure you receive accurate information, please contact "
    "your Academic Advisor or the PNW Dean of Students Office at deanofstudents@pnw.edu."
)

def compute_similarity(query: str, text: str) -> float:
    """Computes keyword overlap score between query and document text."""
    query_words = set(re.findall(r'\w+', query.lower()))
    text_words = set(re.findall(r'\w+', text.lower()))
    
    if not query_words:
        return 0.0
        
    overlap = query_words.intersection(text_words)
    # Give extra weight to key domain terms
    domain_boost = 0.0
    key_terms = {'parking', 'ticket', 'refund', 'drop', 'prerequisite', 'schedule', 'deadline', 'phd', 'graduate', 'plan', 'study', 'appeal'}
    for term in overlap:
        if term in key_terms:
            domain_boost += 0.2
            
    score = (len(overlap) / len(query_words)) + domain_boost
    return min(score, 1.0)

def search_corpus(query: str, campus_id: int = 1) -> Tuple[List[Dict], float]:
    """Retrieves document chunks matching query and campus context."""
    chunks = execute_query(
        """
        SELECT 
            dc.id AS chunk_id,
            dc.section_title,
            dc.content,
            d.title AS document_title,
            d.source_url,
            dc.campus_id
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE dc.campus_id IS NULL OR dc.campus_id = ?
        """,
        (campus_id,)
    )
    
    scored_chunks = []
    max_score = 0.0
    for chunk in chunks:
        score = compute_similarity(query, chunk["section_title"] + " " + chunk["content"])
        if score > max_score:
            max_score = score
        if score > 0.15:
            scored_chunks.append((score, chunk))
            
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    results = [chunk for _, chunk in scored_chunks[:3]]
    return results, max_score

def get_or_create_conversation(session_id: str, campus_id: int) -> int:
    convs = execute_query("SELECT id FROM conversations WHERE session_id = ?", (session_id,))
    if convs:
        return convs[0]["id"]
    return execute_insert(
        "INSERT INTO conversations (session_id, campus_id) VALUES (?, ?)",
        (session_id, campus_id)
    )

def generate_rag_answer(query: str, campus_id: int = 1, session_id: str = None) -> Dict:
    if not session_id:
        session_id = str(uuid.uuid4())
        
    conv_id = get_or_create_conversation(session_id, campus_id)
    chunks, max_score = search_corpus(query, campus_id)
    
    # Check Fail-Safe Threshold (< 0.45 threshold)
    if max_score < 0.35 or not chunks:
        answer_text = FAIL_SAFE_REFUSAL
        is_grounded = False
        citations = []
    else:
        is_grounded = True
        citations = [
            {
                "document_title": c["document_title"],
                "section_title": c["section_title"],
                "source_url": c["source_url"]
            }
            for c in chunks
        ]
        
        # Build synthesis response
        primary_chunk = chunks[0]
        answer_text = (
            f"Based on official PNW documentation ({primary_chunk['document_title']}):\n\n"
            f"{primary_chunk['content']}\n\n"
            f"For further official details, see the source link below."
        )
        
    # Log user message
    execute_insert(
        "INSERT INTO chat_messages (conversation_id, sender, message_text, is_grounded, citations_json) VALUES (?, ?, ?, ?, ?)",
        (conv_id, "USER", query, 1, None)
    )
    
    # Log assistant response
    execute_insert(
        "INSERT INTO chat_messages (conversation_id, sender, message_text, is_grounded, citations_json) VALUES (?, ?, ?, ?, ?)",
        (conv_id, "ASSISTANT", answer_text, 1 if is_grounded else 0, json.dumps(citations))
    )
    
    return {
        "response_text": answer_text,
        "is_grounded": is_grounded,
        "citations": citations,
        "session_id": session_id
    }
