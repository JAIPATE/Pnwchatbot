import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.rag_service import generate_rag_answer

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def handle_chat_query(req: ChatRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    result = generate_rag_answer(req.query, req.campus_id, req.session_id)
    return result

@router.post("/stream")
async def handle_chat_stream(req: ChatRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
    result = generate_rag_answer(req.query, req.campus_id, req.session_id)
    text = result["response_text"]
    citations = result["citations"]
    is_grounded = result["is_grounded"]
    session_id = result["session_id"]
    
    async def event_generator():
        # Stream session metadata event first
        meta = json.dumps({"session_id": session_id, "is_grounded": is_grounded, "citations": citations})
        yield f"event: metadata\ndata: {meta}\n\n"
        await asyncio.sleep(0.05)
        
        # Stream text tokens
        words = text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            payload = json.dumps({"token": chunk})
            yield f"event: token\ndata: {payload}\n\n"
            await asyncio.sleep(0.02)
            
        yield "event: done\ndata: {}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
