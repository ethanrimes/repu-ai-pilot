-- backend/api/database/schemas/tables.sql
-- Path: backend/api/database/schemas/tables.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- Customer Management
-- ============================================

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    firebase_uid VARCHAR(128) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    whatsapp_number VARCHAR(20),
    name VARCHAR(255),
    company_name VARCHAR(255),
    customer_type VARCHAR(20) DEFAULT 'retail',
    tax_id VARCHAR(50),
    address TEXT,
    city VARCHAR(100) DEFAULT 'Bogotá',
    preferred_language VARCHAR(2) DEFAULT 'es',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

-- ============================================
-- Inventory Management
-- ============================================

CREATE TABLE IF NOT EXISTS stock (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    supplier_id INTEGER,
    quantity_available INTEGER DEFAULT 0,
    warehouse_location VARCHAR(50),
    min_stock_level INTEGER DEFAULT 5,
    max_stock_level INTEGER DEFAULT 100,
    last_restocked TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    price_cop DECIMAL(12,2) NOT NULL,
    cost_cop DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'COP',
    price_type VARCHAR(20) DEFAULT 'retail',
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Order Management
-- ============================================

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    channel VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(30),
    subtotal_cop DECIMAL(12,2),
    tax_cop DECIMAL(12,2),
    shipping_cop DECIMAL(12,2),
    total_cop DECIMAL(12,2),
    notes TEXT,
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    article_id INTEGER NOT NULL,
    article_number VARCHAR(100),
    supplier_name VARCHAR(100),
    product_name VARCHAR(255),
    quantity INTEGER NOT NULL,
    unit_price_cop DECIMAL(12,2),
    discount_cop DECIMAL(12,2) DEFAULT 0,
    total_price_cop DECIMAL(12,2)
);

-- ============================================
-- Document Management
-- ============================================

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(50),
    file_path VARCHAR(500),
    content_hash VARCHAR(64),
    language VARCHAR(2) DEFAULT 'es',
    meta_data JSONB,
    is_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    embedding vector(1536),
    meta_data JSONB,
    tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Session Management
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    channel VARCHAR(20),
    current_state VARCHAR(50),
    intent VARCHAR(50),
    context JSONB,
    language VARCHAR(2) DEFAULT 'es',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    meta_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Analytics
-- ============================================

CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    session_id VARCHAR(128),
    customer_id INTEGER,
    meta_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);