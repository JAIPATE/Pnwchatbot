"""RAG Offline Ingestion Pipeline and CLI Interface.

Performs document parsing, semantic chunking, dense vector embedding,
and persistence into vector databases (PostgreSQL pgvector / SQLite).
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backend.rag.chunker import DocumentChunk, TextChunker
from backend.rag.embedder import BaseEmbedder, get_embedder
from backend.rag.parser import ParsedDocument, UniversalParser
from backend.rag.vector_store import (
    BaseVectorStore,
    SearchResult,
    VectorStoreFactory,
)


class RAGOfflinePipeline:
    """End-to-end RAG Offline Pipeline: Ingests documents into vector databases."""

    def __init__(
        self,
        parser: Optional[UniversalParser] = None,
        chunker: Optional[TextChunker] = None,
        embedder: Optional[BaseEmbedder] = None,
        vector_store: Optional[BaseVectorStore] = None,
        backend: str = "pgvector",
        db_url: Optional[str] = None,
    ):
        self.parser = parser or UniversalParser()
        self.chunker = chunker or TextChunker(chunk_size=500, chunk_overlap=80)
        self.embedder = embedder or get_embedder()
        self.vector_store = vector_store or VectorStoreFactory.create(
            backend=backend,
            connection_string=db_url,
            dimension=self.embedder.dimension,
            allow_sqlite_fallback=True,
        )

    def parse_sources(self, source_path: Union[str, Path]) -> List[ParsedDocument]:
        """Step 1: Parse raw documents from a directory or specific file."""
        path = Path(source_path)
        if path.is_file():
            return [self.parser.parse_file(path)]
        elif path.is_dir():
            return self.parser.parse_directory(path)
        else:
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

    def chunk_documents(self, documents: List[ParsedDocument]) -> List[DocumentChunk]:
        """Step 2: Chunk documents into semantic pieces with retrieval metadata."""
        return self.chunker.chunk_documents(documents)

    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """Step 3: Generate dense vector embeddings for each chunk."""
        texts = [f"{c.document_title} - {c.section_title}: {c.content}" for c in chunks]
        return self.embedder.embed_texts(texts)

    def store_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> int:
        """Step 4: Store chunks and embeddings into the vector database."""
        return self.vector_store.store_chunks(chunks, embeddings)

    def run(
        self,
        source_path: Union[str, Path],
        clear_existing: bool = False,
    ) -> Dict[str, Any]:
        """Executes the full offline pipeline: Parse -> Chunk -> Embed -> Store."""
        print(f"[PIPELINE] Starting RAG Offline Pipeline on: {source_path}")

        if clear_existing:
            print("[PIPELINE] Clearing existing vector records...")
            self.vector_store.clear()

        # Step 1: Parse
        print("[PIPELINE] Step 1/4: Parsing documents...")
        docs = self.parse_sources(source_path)
        print(f"[PIPELINE] Parsed {len(docs)} document(s): {[d.title for d in docs]}")

        # Step 2: Chunk
        print("[PIPELINE] Step 2/4: Chunking document sections...")
        chunks = self.chunk_documents(docs)
        print(f"[PIPELINE] Generated {len(chunks)} total chunk(s)")

        # Step 3: Embed
        print(f"[PIPELINE] Step 3/4: Generating vector embeddings (dim={self.embedder.dimension})...")
        embeddings = self.embed_chunks(chunks)
        print(f"[PIPELINE] Successfully generated {len(embeddings)} embedding vector(s)")

        # Step 4: Store
        print("[PIPELINE] Step 4/4: Persisting chunks into vector database...")
        stored_count = self.store_chunks(chunks, embeddings)
        print(f"[PIPELINE] Ingested {stored_count} vector chunk(s) into database")

        stats = self.vector_store.get_stats()
        summary = {
            "status": "SUCCESS",
            "documents_parsed": len(docs),
            "chunks_generated": len(chunks),
            "chunks_stored": stored_count,
            "vector_store_stats": stats,
        }
        print(f"[PIPELINE] Offline pipeline completed successfully!\n{json.dumps(summary, indent=2)}")
        return summary

    def search(
        self,
        query: str,
        top_k: int = 5,
        campus: Optional[str] = None,
    ) -> List[SearchResult]:
        """Executes online similarity retrieval against the vector database."""
        query_embedding = self.embedder.embed_query(query)
        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            campus_filter=campus,
        )


def build_cli() -> argparse.ArgumentParser:
    """Constructs the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Purdue University Northwest (PNW) RAG Offline Ingestion Pipeline",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Ingest subcommand
    ingest_parser = subparsers.add_parser("ingest", help="Run end-to-end ingestion pipeline")
    ingest_parser.add_argument(
        "--source",
        "-s",
        default="data/raw_documents",
        help="Directory or file path containing raw documents (HTML/PDF/Text)",
    )
    ingest_parser.add_argument(
        "--backend",
        "-b",
        default="pgvector",
        choices=["pgvector", "sqlite"],
        help="Vector database backend (default: pgvector with SQLite fallback)",
    )
    ingest_parser.add_argument(
        "--db-url",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL connection string (optional)",
    )
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Maximum characters per chunk (default: 500)",
    )
    ingest_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=80,
        help="Overlap characters between chunks (default: 80)",
    )
    ingest_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vector store records before ingestion",
    )

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Execute vector similarity search")
    search_parser.add_argument("--query", "-q", required=True, help="Student query text")
    search_parser.add_argument(
        "--campus",
        "-c",
        choices=["All", "Hammond", "Westville"],
        default="All",
        help="Campus filter scope",
    )
    search_parser.add_argument("--top-k", "-k", type=int, default=3, help="Number of results to return")
    search_parser.add_argument(
        "--backend",
        "-b",
        default="pgvector",
        choices=["pgvector", "sqlite"],
        help="Vector database backend",
    )
    search_parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"))

    # Stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Display vector database statistics")
    stats_parser.add_argument(
        "--backend",
        "-b",
        default="pgvector",
        choices=["pgvector", "sqlite"],
        help="Vector database backend",
    )
    stats_parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"))

    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "ingest":
        chunker = TextChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
        pipeline = RAGOfflinePipeline(
            chunker=chunker,
            backend=args.backend,
            db_url=args.db_url,
        )
        pipeline.run(source_path=args.source, clear_existing=args.clear)

    elif args.command == "search":
        pipeline = RAGOfflinePipeline(backend=args.backend, db_url=args.db_url)
        results = pipeline.search(query=args.query, top_k=args.top_k, campus=args.campus)
        print(f"\n[QUERY] '{args.query}' (Campus: {args.campus})")
        print(f"[RESULTS] Found {len(results)} matching chunks:\n" + "=" * 60)
        for i, res in enumerate(results, 1):
            print(f"#{i} | Score: {res.score:.4f} | Document: {res.document_title}")
            print(f"     Section: {res.section_title} | Campus: {res.campus} | Source: {res.source_url}")
            print(f"     Content: {res.content[:200]}...")
            print("-" * 60)

    elif args.command == "stats":
        pipeline = RAGOfflinePipeline(backend=args.backend, db_url=args.db_url)
        stats = pipeline.vector_store.get_stats()
        print("\n[VECTOR DATABASE STATS]")
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
