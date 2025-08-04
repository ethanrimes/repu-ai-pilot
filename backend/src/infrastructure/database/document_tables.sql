-- backend/src/infrastructure/database/document_tables.sql
-- Path: backend/src/infrastructure/database/document_tables.sql

-- ============================================
-- Document Management Tables
-- ============================================

-- Main documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    document_type VARCHAR(50), -- manual, policy, faq, diagnostic, installation, etc.
    category VARCHAR(100), -- faqs, legal, policies, shipping_info, store_info, tech_docs
    subcategory VARCHAR(100), -- diagnostics, fluids, installation, manuals, services, torque
    content TEXT,
    content_hash VARCHAR(64) UNIQUE, -- SHA256 for deduplication
    language VARCHAR(2) DEFAULT 'es',
    meta_data JSONB DEFAULT '{}', -- Store additional meta_data
    hierarchy JSONB DEFAULT '{}', -- Store file path hierarchy
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks for vector search
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding dimension
    meta_data JSONB DEFAULT '{}',
    tokens INTEGER,
    chunk_strategy VARCHAR(50) DEFAULT 'recursive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link documents to TecDoc article IDs
CREATE TABLE IF NOT EXISTS document_article_links (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    article_id INTEGER NOT NULL, -- TecDoc article ID
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, article_id)
);

-- Link documents to vehicle IDs
CREATE TABLE IF NOT EXISTS document_vehicle_links (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    vehicle_id INTEGER NOT NULL, -- TecDoc vehicle ID
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, vehicle_id)
);

-- ============================================
-- Indexes for Performance
-- ============================================

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_subcategory ON documents(subcategory);
CREATE INDEX IF NOT EXISTS idx_documents_language ON documents(language);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);

-- Chunk indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100); -- Adjust lists parameter based on data size

-- Link table indexes
CREATE INDEX IF NOT EXISTS idx_doc_article_links_doc_id ON document_article_links(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_article_links_article_id ON document_article_links(article_id);
CREATE INDEX IF NOT EXISTS idx_doc_vehicle_links_doc_id ON document_vehicle_links(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_vehicle_links_vehicle_id ON document_vehicle_links(vehicle_id);

-- ============================================
-- Full Text Search
-- ============================================

-- Add full text search columns
ALTER TABLE documents ADD COLUMN IF NOT EXISTS search_vector tsvector;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Update search vectors
UPDATE documents SET search_vector = to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(content, ''));
UPDATE chunks SET search_vector = to_tsvector('spanish', content);

-- Create GIN indexes for full text search
CREATE INDEX IF NOT EXISTS idx_documents_search ON documents USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_chunks_search ON chunks USING GIN(search_vector);

-- ============================================
-- Triggers
-- ============================================

-- Update search vector on document change
CREATE OR REPLACE FUNCTION update_document_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('spanish', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_document_search_vector_trigger ON documents;
CREATE TRIGGER update_document_search_vector_trigger
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_document_search_vector();

-- Update search vector on chunk change
CREATE OR REPLACE FUNCTION update_chunk_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('spanish', NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_chunk_search_vector_trigger ON chunks;
CREATE TRIGGER update_chunk_search_vector_trigger
    BEFORE INSERT OR UPDATE ON chunks
    FOR EACH ROW EXECUTE FUNCTION update_chunk_search_vector();