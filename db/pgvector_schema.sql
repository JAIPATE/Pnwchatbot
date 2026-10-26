-- ============================================================
-- PostgreSQL pgvector Schema Definition
-- Purdue University Northwest (PNW) Knowledge Chatbot
-- ============================================================

-- 1. Enable the pgvector extension for dense vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the document vector chunks table
CREATE TABLE IF NOT EXISTS pnw_document_vectors (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    doc_id TEXT NOT NULL,
    document_title TEXT NOT NULL,
    category TEXT NOT NULL,
    source_url TEXT NOT NULL,
    campus TEXT NOT NULL DEFAULT 'Both' CHECK (campus IN ('Both', 'Hammond', 'Westville')),
    section_title TEXT NOT NULL,
    chunk_index INT NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create HNSW Index for rapid approximate nearest neighbor (ANN) cosine similarity search
CREATE INDEX IF NOT EXISTS idx_pnw_vectors_hnsw 
ON pnw_document_vectors USING hnsw (embedding vector_cosine_ops);

-- 4. Create B-Tree Indexes for campus and category filtering
CREATE INDEX IF NOT EXISTS idx_pnw_vectors_campus ON pnw_document_vectors(campus);
CREATE INDEX IF NOT EXISTS idx_pnw_vectors_category ON pnw_document_vectors(category);
CREATE INDEX IF NOT EXISTS idx_pnw_vectors_doc ON pnw_document_vectors(doc_id);

-- ============================================================
-- Benchmark Vector Retrieval Query
-- ============================================================
-- Example Cosine Distance Query:
-- SELECT chunk_id, document_title, section_title, content,
--        1 - (embedding <=> '[... 384-dim query vector ...]'::vector) AS similarity
-- FROM pnw_document_vectors
-- WHERE (campus = 'Both' OR campus = 'Hammond')
-- ORDER BY embedding <=> '[... 384-dim query vector ...]'::vector ASC
-- LIMIT 5;
