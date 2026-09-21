import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routers import chat, schedule, prereq, campus

app = FastAPI(
    title="Purdue University Northwest (PNW) Knowledge Chatbot API",
    description="API for PNW student knowledge assistant with grounded RAG, campus awareness, and fail-safe guardrails.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(schedule.router)
app.include_router(prereq.router)
app.include_router(campus.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "PNW Knowledge Chatbot",
        "version": "1.0.0"
    }

# Mount Frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "PNW Knowledge Chatbot API is running. Access /docs for API documentation."}
