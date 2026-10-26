"""Automated test suite for the RAG Offline Pipeline: Parsing, Chunking, Embedding, and Vector Storage."""

import os
from pathlib import Path
import numpy as np
import pytest

from backend.rag.chunker import DocumentChunk, TextChunker
from backend.rag.embedder import DeterministicEmbedder, FastEmbedder, get_embedder
from backend.rag.parser import HTMLDocumentParser, PDFDocumentParser, UniversalParser
from backend.rag.pipeline import RAGOfflinePipeline
from backend.rag.vector_store import PGVectorStore, SQLiteVectorStore, VectorStoreFactory

RAW_DOCS_DIR = Path("data/raw_documents")


class TestDocumentParsing:
    """Validates document parsing for HTML and PDF formats."""

    def test_parse_html_document(self):
        html_file = RAW_DOCS_DIR / "pnw_parking_regulations.html"
        assert html_file.exists(), f"Missing test file: {html_file}"

        parser = HTMLDocumentParser()
        doc = parser.parse(html_file)

        assert doc.file_type == "HTML"
        assert "Parking" in doc.title
        assert doc.category == "Parking & Campus Safety"
        assert "https://www.pnw.edu" in doc.source_url
        assert len(doc.sections) >= 3
        # Verify specific sections exist
        section_titles = [s.title for s in doc.sections]
        assert any("Virtual" in t for t in section_titles)
        assert any("Citations" in t or "Paying" in t for t in section_titles)

    def test_parse_pdf_document(self):
        pdf_file = RAW_DOCS_DIR / "pnw_classroom_behavior_policy.pdf"
        assert pdf_file.exists(), f"Missing test file: {pdf_file}"

        parser = PDFDocumentParser()
        doc = parser.parse(pdf_file)

        assert doc.file_type == "PDF"
        assert "Classroom Behavior" in doc.title or "Disruption" in doc.title
        assert len(doc.raw_text) > 200
        assert len(doc.sections) >= 1
        assert "Instructor" in doc.raw_text or "Disruptive" in doc.raw_text

    def test_universal_parser_directory(self):
        parser = UniversalParser()
        docs = parser.parse_directory(RAW_DOCS_DIR)

        assert len(docs) >= 3, "At least 3 documents must be parsed from corpus"
        types = {d.file_type for d in docs}
        assert "HTML" in types
        assert "PDF" in types


class TestChunking:
    """Validates semantic and sliding window chunking."""

    def test_chunker_basic(self):
        parser = UniversalParser()
        doc = parser.parse_file(RAW_DOCS_DIR / "pnw_parking_regulations.html")

        chunker = TextChunker(chunk_size=400, chunk_overlap=60)
        chunks = chunker.chunk_document(doc)

        assert len(chunks) >= 3
        for i, chunk in enumerate(chunks):
            assert chunk.doc_id == doc.doc_id
            assert chunk.document_title == doc.title
            assert chunk.source_url == doc.source_url
            assert chunk.chunk_index == i
            assert len(chunk.content) > 0
            assert chunk.char_count == len(chunk.content)
            assert chunk.token_count_estimate > 0

    def test_chunk_overlap_invalid(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, chunk_overlap=150)


class TestEmbedding:
    """Validates vector embedding generation and dimensional properties."""

    def test_deterministic_embedder(self):
        embedder = DeterministicEmbedder(dimension=384)
        texts = ["Parking ticket appeal Hammond", "Computer Science Plan of Study"]
        vectors = embedder.embed_texts(texts)

        assert len(vectors) == 2
        assert len(vectors[0]) == 384
        # Verify unit vector normalization (norm ~= 1.0)
        norm = np.linalg.norm(vectors[0])
        assert abs(norm - 1.0) < 1e-4

        # Verify determinism: identical text -> identical vector
        v_repeat = embedder.embed_texts(["Parking ticket appeal Hammond"])[0]
        assert np.allclose(vectors[0], v_repeat)

    def test_fastembedder_inference(self):
        embedder = FastEmbedder()
        assert embedder.dimension == 384

        texts = ["Purdue Northwest Hammond campus parking citation", "Financial aid drop deadline"]
        vectors = embedder.embed_texts(texts)

        assert len(vectors) == 2
        assert len(vectors[0]) == 384
        norm = np.linalg.norm(vectors[0])
        assert abs(norm - 1.0) < 1e-2

        # Test single query embedding
        query_vec = embedder.embed_query("How to pay parking fines?")
        assert len(query_vec) == 384


class TestVectorStorage:
    """Validates vector database storage, indexing, and similarity retrieval."""

    def test_sqlite_vector_store_end_to_end(self, tmp_path):
        db_path = tmp_path / "test_vector.db"
        store = SQLiteVectorStore(db_path=db_path, dimension=384)
        embedder = DeterministicEmbedder(dimension=384)

        chunks = [
            DocumentChunk(
                chunk_id="chunk_1",
                doc_id="doc_park",
                document_title="Parking Rules",
                category="PARKING",
                source_url="https://pnw.edu/parking",
                campus="Hammond",
                section_title="Ticket Payments",
                chunk_index=0,
                content="Pay parking citations at the Hammond bursar office or online via myPNW within 14 days.",
            ),
            DocumentChunk(
                chunk_id="chunk_2",
                doc_id="doc_park",
                document_title="Parking Rules",
                category="PARKING",
                source_url="https://pnw.edu/parking",
                campus="Westville",
                section_title="Westville Lots",
                chunk_index=1,
                content="Westville campus student permits are valid across general student lots without assigned zones.",
            ),
            DocumentChunk(
                chunk_id="chunk_3",
                doc_id="doc_cs",
                document_title="CS Graduate Plan of Study",
                category="ACADEMIC",
                source_url="https://pnw.edu/cs",
                campus="Both",
                section_title="EPOS Submission",
                chunk_index=0,
                content="Submit your MS Computer Science Electronic Plan of Study (EPOS) before 15 credits.",
            ),
        ]

        texts = [c.content for c in chunks]
        embeddings = embedder.embed_texts(texts)

        # 1. Store
        stored = store.store_chunks(chunks, embeddings)
        assert stored == 3

        # 2. Stats
        stats = store.get_stats()
        assert stats["total_chunks"] == 3
        assert stats["total_documents"] == 2

        # 3. Search for parking
        query_vec = embedder.embed_query("parking citation payment")
        results = store.search(query_vec, top_k=2)
        assert len(results) > 0
        assert results[0].doc_id == "doc_park"
        assert results[0].score > 0.0

        # 4. Search with campus filter (Hammond only)
        hammond_results = store.search(query_vec, top_k=5, campus_filter="Hammond")
        for res in hammond_results:
            assert res.campus in ["Hammond", "Both"]

    def test_vector_store_factory_fallback(self):
        # When given an unreachable postgres connection, factory falls back to SQLite
        store = VectorStoreFactory.create(
            backend="pgvector",
            connection_string="postgresql://nonexistent:none@127.0.0.1:59999/dummy",
            allow_sqlite_fallback=True,
        )
        assert isinstance(store, SQLiteVectorStore)


class TestFullOfflinePipeline:
    """Validates the complete RAG offline pipeline ingestion and search workflow."""

    def test_run_offline_pipeline(self, tmp_path):
        db_path = tmp_path / "pipeline_vectors.db"
        vector_store = SQLiteVectorStore(db_path=db_path)
        embedder = FastEmbedder()
        pipeline = RAGOfflinePipeline(
            vector_store=vector_store,
            embedder=embedder,
        )

        # Run pipeline over the raw documents corpus (at least 3 documents: 4 HTML + 1 PDF)
        summary = pipeline.run(source_path=RAW_DOCS_DIR, clear_existing=True)

        assert summary["status"] == "SUCCESS"
        assert summary["documents_parsed"] >= 3
        assert summary["chunks_stored"] >= summary["documents_parsed"]

        # Test semantic search: Parking Inquiry
        results = pipeline.search("How do I pay parking citations at Hammond?", top_k=3, campus="Hammond")
        assert len(results) > 0
        top = results[0]
        assert "Parking" in top.document_title or "Traffic" in top.document_title or "citation" in top.content.lower()
        assert top.score > 0.4

        # Test semantic search: Plan of Study Inquiry
        results_epos = pipeline.search("How do I submit my Computer Science MS Plan of Study?", top_k=3)
        assert len(results_epos) > 0
        assert any("Plan of Study" in r.document_title or "EPOS" in r.content for r in results_epos)
