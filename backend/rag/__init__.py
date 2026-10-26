"""RAG (Retrieval-Augmented Generation) package for Purdue University Northwest (PNW) Knowledge Chatbot.

Modules:
    parser: Extracts clean text and metadata from HTML and PDF documents.
    chunker: Breaks documents into semantic/contextual chunks with overlap and metadata.
    embedder: Computes dense vector embeddings using fast ONNX models (FastEmbed BAAI/bge-small-en-v1.5).
    vector_store: Vector database interfaces supporting PostgreSQL pgvector with SQLite fallback.
    pipeline: Offline ingestion orchestrator and CLI tools.
"""

from backend.rag.parser import UniversalParser, ParsedDocument
from backend.rag.chunker import TextChunker, DocumentChunk
from backend.rag.embedder import FastEmbedder, get_embedder
from backend.rag.vector_store import (
    BaseVectorStore,
    PGVectorStore,
    SQLiteVectorStore,
    VectorStoreFactory,
    SearchResult
)
from backend.rag.pipeline import RAGOfflinePipeline

__all__ = [
    "UniversalParser",
    "ParsedDocument",
    "TextChunker",
    "DocumentChunk",
    "FastEmbedder",
    "get_embedder",
    "BaseVectorStore",
    "PGVectorStore",
    "SQLiteVectorStore",
    "VectorStoreFactory",
    "SearchResult",
    "RAGOfflinePipeline",
]
