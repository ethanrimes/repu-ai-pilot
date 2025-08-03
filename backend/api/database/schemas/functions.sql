-- backend/api/database/schemas/functions.sql
-- Path: backend/api/database/schemas/functions.sql

-- ============================================
-- Utility Functions
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- Vector Search Functions
-- ============================================

-- Search documents by embedding similarity
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    chunk_id int,
    document_id int,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id as chunk_id,
        dc.document_id,
        dc.content,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM document_chunks dc
    WHERE dc.metadata @> filter_metadata
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Hybrid search combining vector and keyword search
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    keyword_weight float DEFAULT 0.3
)
RETURNS TABLE (
    chunk_id int,
    document_id int,
    content text,
    score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH vector_search AS (
        SELECT 
            dc.id,
            dc.document_id,
            dc.content,
            1 - (dc.embedding <=> query_embedding) as vector_score
        FROM document_chunks dc
        ORDER BY dc.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    keyword_search AS (
        SELECT 
            dc.id,
            dc.document_id,
            dc.content,
            ts_rank_cd(to_tsvector('spanish', dc.content), 
                      plainto_tsquery('spanish', query_text)) as keyword_score
        FROM document_chunks dc
        WHERE to_tsvector('spanish', dc.content) @@ 
              plainto_tsquery('spanish', query_text)
        LIMIT match_count * 2
    )
    SELECT 
        COALESCE(v.id, k.id) as chunk_id,
        COALESCE(v.document_id, k.document_id) as document_id,
        COALESCE(v.content, k.content) as content,
        (COALESCE(v.vector_score, 0) * (1 - keyword_weight) + 
         COALESCE(k.keyword_score, 0) * keyword_weight) as score
    FROM vector_search v
    FULL OUTER JOIN keyword_search k ON v.id = k.id
    ORDER BY score DESC
    LIMIT match_count;
END;
$$;

-- ============================================
-- Business Logic Functions
-- ============================================

-- Get customer order history
CREATE OR REPLACE FUNCTION get_customer_order_history(
    p_customer_id int,
    p_limit int DEFAULT 10
)
RETURNS TABLE (
    order_id int,
    order_number varchar,
    order_date timestamp,
    total_cop decimal,
    status varchar,
    item_count bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id as order_id,
        o.order_number,
        o.created_at as order_date,
        o.total_cop,
        o.status,
        COUNT(oi.id) as item_count
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.customer_id = p_customer_id
    GROUP BY o.id
    ORDER BY o.created_at DESC
    LIMIT p_limit;
END;
$$;

-- Check stock availability
CREATE OR REPLACE FUNCTION check_stock_availability(
    p_article_id int,
    p_quantity int
)
RETURNS TABLE (
    available boolean,
    current_stock int,
    warehouse_location varchar
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.quantity_available >= p_quantity as available,
        s.quantity_available as current_stock,
        s.warehouse_location
    FROM stock s
    WHERE s.article_id = p_article_id
    ORDER BY s.quantity_available DESC
    LIMIT 1;
END;
$$;