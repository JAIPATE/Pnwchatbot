#!/usr/bin/env python3
"""Offline RAG Ingestion CLI Script.

Performs document parsing (HTML/PDF), section-aware chunking, dense vector
embedding (FastEmbed BAAI/bge-small-en-v1.5), and stores chunks into a vector
database (PostgreSQL pgvector / SQLite fallback).

Usage:
    python ingest.py
    python ingest.py --source data/raw_documents --backend pgvector
    python ingest.py --backend sqlite --clear
"""

import argparse
import os
import sys
from backend.rag.chunker import TextChunker
from backend.rag.pipeline import RAGOfflinePipeline


def main():
    parser = argparse.ArgumentParser(
        description="PNW Knowledge Chatbot - RAG Offline Ingestion Pipeline",
    )
    parser.add_argument(
        "--source",
        "-s",
        default="data/raw_documents",
        help="Directory or file path of raw documents to ingest (default: data/raw_documents)",
    )
    parser.add_argument(
        "--backend",
        "-b",
        default=os.getenv("VECTOR_BACKEND", "pgvector"),
        choices=["pgvector", "sqlite"],
        help="Vector database backend (default: pgvector with SQLite fallback)",
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL connection URL",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Target maximum characters per chunk (default: 500)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=80,
        help="Overlap characters between chunks (default: 80)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vector database records before ingestion",
    )

    args = parser.parse_args()

    chunker = TextChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    pipeline = RAGOfflinePipeline(
        chunker=chunker,
        backend=args.backend,
        db_url=args.db_url,
    )

    summary = pipeline.run(source_path=args.source, clear_existing=args.clear)
    print("\n[SUCCESS] Ingestion completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
