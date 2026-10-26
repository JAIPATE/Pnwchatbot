#!/usr/bin/env python3
"""Convenience root CLI entrypoint for the PNW RAG Offline Pipeline.

Usage:
    python pipeline.py ingest [--source data/raw_documents] [--backend pgvector|sqlite]
    python pipeline.py search --query "How do I pay parking tickets at Hammond?"
    python pipeline.py stats
"""

from backend.rag.pipeline import main

if __name__ == "__main__":
    main()
