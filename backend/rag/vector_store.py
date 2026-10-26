"""Vector store abstractions and implementations: PostgreSQL pgvector and SQLite fallback."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union
import numpy as np
from backend.rag.chunker import DocumentChunk


@dataclass
class SearchResult:
    """Represents a matched chunk returned by similarity search."""
    chunk_id: str
    doc_id: str
    document_title: str
    category: str
    source_url: str
    campus: str
    section_title: str
    chunk_index: int
    content: str
    score: float
    metadata: Dict = field(default_factory=dict)


class BaseVectorStore(ABC):
    """Abstract interface for RAG vector databases."""

    @abstractmethod
    def initialize(self) -> None:
        """Create tables, vector extensions, and performance indexes."""
        pass

    @abstractmethod
    def store_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> int:
        """Store chunks along with their vector embeddings."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        campus_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """Perform cosine similarity search against stored embeddings."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Return collection statistics (chunk count, dimensions, etc.)."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored chunks and vectors."""
        pass


class PGVectorStore(BaseVectorStore):
    """PostgreSQL vector database store using pgvector extension and HNSW indexes."""

    DEFAULT_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://pnw_admin:pnw_secret_2026@localhost:5432/pnw_knowledge_db",
    )

    def __init__(self, connection_string: Optional[str] = None, dimension: int = 384):
        self.connection_string = connection_string or self.DEFAULT_URL
        self.dimension = dimension

    def _get_connection(self):
        import psycopg
        from pgvector.psycopg import register_vector
        conn = psycopg.connect(self.connection_string, autocommit=True)
        register_vector(conn)
        return conn

    def initialize(self) -> None:
        """Enables the pgvector extension and creates the vector table and HNSW index."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS pnw_document_vectors (
                        id SERIAL PRIMARY KEY,
                        chunk_id TEXT UNIQUE NOT NULL,
                        doc_id TEXT NOT NULL,
                        document_title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        source_url TEXT NOT NULL,
                        campus TEXT NOT NULL DEFAULT 'Both',
                        section_title TEXT NOT NULL,
                        chunk_index INT NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        embedding vector({self.dimension}) NOT NULL
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_pnw_vectors_hnsw 
                    ON pnw_document_vectors USING hnsw (embedding vector_cosine_ops);
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_pnw_vectors_campus 
                    ON pnw_document_vectors(campus);
                    """
                )

    def store_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks count must match embeddings count")
        if not chunks:
            return 0

        self.initialize()
        inserted = 0
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for chunk, emb in zip(chunks, embeddings):
                    cur.execute(
                        """
                        INSERT INTO pnw_document_vectors 
                            (chunk_id, doc_id, document_title, category, source_url, 
                             campus, section_title, chunk_index, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata;
                        """,
                        (
                            chunk.chunk_id,
                            chunk.doc_id,
                            chunk.document_title,
                            chunk.category,
                            chunk.source_url,
                            chunk.campus,
                            chunk.section_title,
                            chunk.chunk_index,
                            chunk.content,
                            json.dumps(chunk.metadata),
                            emb,
                        ),
                    )
                    inserted += 1
        return inserted

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        campus_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        self.initialize()
        results: List[SearchResult] = []
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if campus_filter and campus_filter != "All":
                    cur.execute(
                        """
                        SELECT chunk_id, doc_id, document_title, category, source_url,
                               campus, section_title, chunk_index, content, metadata,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM pnw_document_vectors
                        WHERE campus = 'Both' OR campus = %s
                        ORDER BY embedding <=> %s::vector ASC
                        LIMIT %s;
                        """,
                        (query_embedding, campus_filter, query_embedding, top_k),
                    )
                else:
                    cur.execute(
                        """
                        SELECT chunk_id, doc_id, document_title, category, source_url,
                               campus, section_title, chunk_index, content, metadata,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM pnw_document_vectors
                        ORDER BY embedding <=> %s::vector ASC
                        LIMIT %s;
                        """,
                        (query_embedding, query_embedding, top_k),
                    )

                rows = cur.fetchall()
                for row in rows:
                    results.append(
                        SearchResult(
                            chunk_id=row[0],
                            doc_id=row[1],
                            document_title=row[2],
                            category=row[3],
                            source_url=row[4],
                            campus=row[5],
                            section_title=row[6],
                            chunk_index=row[7],
                            content=row[8],
                            metadata=row[9] if isinstance(row[9], dict) else json.loads(row[9] or "{}"),
                            score=float(row[10]),
                        )
                    )
        return results

    def get_stats(self) -> Dict[str, Any]:
        self.initialize()
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*), COUNT(DISTINCT doc_id) FROM pnw_document_vectors;")
                total_chunks, total_docs = cur.fetchone()
                return {
                    "backend": "PostgreSQL (pgvector)",
                    "dimension": self.dimension,
                    "total_chunks": total_chunks,
                    "total_documents": total_docs,
                    "connection": self.connection_string.split("@")[-1] if "@" in self.connection_string else "pg",
                }

    def clear(self) -> None:
        self.initialize()
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE pnw_document_vectors RESTART IDENTITY;")


class SQLiteVectorStore(BaseVectorStore):
    """File-backed or in-memory SQLite vector store with NumPy cosine similarity."""

    DEFAULT_PATH = Path(__file__).parent.parent.parent / "db" / "vector_store.db"

    def __init__(self, db_path: Optional[Union[str, Path]] = None, dimension: int = 384):
        self.db_path = Path(db_path) if db_path else self.DEFAULT_PATH
        self.dimension = dimension
        self.initialize()

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pnw_document_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chunk_id TEXT UNIQUE NOT NULL,
                    doc_id TEXT NOT NULL,
                    document_title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    campus TEXT NOT NULL DEFAULT 'Both',
                    section_title TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    embedding_blob BLOB NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sqlite_campus ON pnw_document_vectors(campus);")
            conn.commit()

    def store_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks count must match embeddings count")
        if not chunks:
            return 0

        with self._get_connection() as conn:
            for chunk, emb in zip(chunks, embeddings):
                arr = np.array(emb, dtype=np.float32)
                conn.execute(
                    """
                    INSERT INTO pnw_document_vectors 
                        (chunk_id, doc_id, document_title, category, source_url, 
                         campus, section_title, chunk_index, content, metadata, embedding_blob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(chunk_id) DO UPDATE SET
                        content = excluded.content,
                        embedding_blob = excluded.embedding_blob,
                        metadata = excluded.metadata;
                    """,
                    (
                        chunk.chunk_id,
                        chunk.doc_id,
                        chunk.document_title,
                        chunk.category,
                        chunk.source_url,
                        chunk.campus,
                        chunk.section_title,
                        chunk.chunk_index,
                        chunk.content,
                        json.dumps(chunk.metadata),
                        arr.tobytes(),
                    ),
                )
            conn.commit()
        return len(chunks)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        campus_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        with self._get_connection() as conn:
            query_sql = "SELECT * FROM pnw_document_vectors"
            params = []
            if campus_filter and campus_filter != "All":
                query_sql += " WHERE campus = 'Both' OR campus = ?"
                params.append(campus_filter)

            cursor = conn.execute(query_sql, params)
            rows = cursor.fetchall()

        if not rows:
            return []

        scored_rows = []
        for r in rows:
            vec = np.frombuffer(r["embedding_blob"], dtype=np.float32)
            denom = np.linalg.norm(vec) * query_norm
            similarity = float(np.dot(vec, query_vec) / denom) if denom > 0 else 0.0
            scored_rows.append((similarity, r))

        scored_rows.sort(key=lambda x: x[0], reverse=True)

        results: List[SearchResult] = []
        for sim, r in scored_rows[:top_k]:
            results.append(
                SearchResult(
                    chunk_id=r["chunk_id"],
                    doc_id=r["doc_id"],
                    document_title=r["document_title"],
                    category=r["category"],
                    source_url=r["source_url"],
                    campus=r["campus"],
                    section_title=r["section_title"],
                    chunk_index=r["chunk_index"],
                    content=r["content"],
                    metadata=json.loads(r["metadata"] or "{}"),
                    score=sim,
                )
            )
        return results

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*), COUNT(DISTINCT doc_id) FROM pnw_document_vectors")
            total_chunks, total_docs = cursor.fetchone()
            return {
                "backend": "SQLite (NumPy vector search)",
                "dimension": self.dimension,
                "total_chunks": total_chunks,
                "total_documents": total_docs,
                "db_path": str(self.db_path),
            }

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM pnw_document_vectors;")
            conn.commit()


class VectorStoreFactory:
    """Instantiates the preferred vector store with automatic fallback handling."""

    @staticmethod
    def create(
        backend: str = "pgvector",
        connection_string: Optional[str] = None,
        dimension: int = 384,
        allow_sqlite_fallback: bool = True,
    ) -> BaseVectorStore:
        if backend.lower() in ["pgvector", "postgres", "postgresql"]:
            try:
                pg_store = PGVectorStore(connection_string=connection_string, dimension=dimension)
                pg_store.initialize()
                return pg_store
            except Exception as e:
                if allow_sqlite_fallback:
                    print(f"[INFO] PostgreSQL pgvector unavailable ({e}). Falling back to SQLite vector store.")
                    return SQLiteVectorStore(dimension=dimension)
                raise ConnectionError(f"Failed to connect to PostgreSQL pgvector: {e}")
        elif backend.lower() in ["sqlite", "local"]:
            return SQLiteVectorStore(dimension=dimension)
        else:
            raise ValueError(f"Unknown vector store backend: {backend}")
