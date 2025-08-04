-- backend/api/database/schemas/indexes.sql
-- Path: backend/api/database/schemas/indexes.sql

-- Customer indexes
CREATE INDEX IF NOT EXISTS idx_customers_firebase_uid ON customers(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(customer_type);
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city);

-- Stock indexes
CREATE INDEX IF NOT EXISTS idx_stock_article_id ON stock(article_id);
CREATE INDEX IF NOT EXISTS idx_stock_warehouse ON stock(warehouse_location);
CREATE INDEX IF NOT EXISTS idx_stock_quantity ON stock(quantity_available);

-- Price indexes
CREATE INDEX IF NOT EXISTS idx_prices_article_id ON prices(article_id);
CREATE INDEX IF NOT EXISTS idx_prices_type ON prices(price_type);
CREATE INDEX IF NOT EXISTS idx_prices_validity ON prices(valid_from, valid_to);

-- Order indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);

-- Order items indexes
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_article_id ON order_items(article_id);

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_documents_language ON documents(language);

-- Document chunk indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks 
    USING ivfflat (embedding vector_cosine_ops);

-- Session indexes
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(current_state);
CREATE INDEX IF NOT EXISTS idx_sessions_channel ON sessions(channel);

-- Message indexes
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON conversation_messages(created_at);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_events(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_session ON analytics_events(session_id);