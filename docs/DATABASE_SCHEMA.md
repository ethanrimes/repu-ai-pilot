# docs/DATABASE_SCHEMA.md
# Path: docs/DATABASE_SCHEMA.md

# Database Schema Documentation

## Overview

The database uses PostgreSQL (via Supabase) with pgvector extension for embeddings.

## Core Tables

### customers
Stores customer information linked to Firebase Auth.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| firebase_uid | VARCHAR(128) | Firebase Auth UID |
| email | VARCHAR(255) | Unique email |
| phone | VARCHAR(20) | Phone number |
| whatsapp_number | VARCHAR(20) | WhatsApp number |
| name | VARCHAR(255) | Full name |
| company_name | VARCHAR(255) | Company (if B2B) |
| customer_type | VARCHAR(20) | retail/wholesale/mechanic |
| tax_id | VARCHAR(50) | NIT/CC |
| city | VARCHAR(100) | Colombian city |
| preferred_language | VARCHAR(2) | es/en |

### stock
Inventory tracking for articles.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| article_id | INTEGER | TecDoc article ID |
| supplier_id | INTEGER | TecDoc supplier ID |
| quantity_available | INTEGER | Current stock |
| warehouse_location | VARCHAR(50) | Warehouse code |
| min_stock_level | INTEGER | Reorder point |
| max_stock_level | INTEGER | Maximum stock |
| last_restocked | TIMESTAMP | Last restock date |

### prices
Pricing information for articles.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| article_id | INTEGER | TecDoc article ID |
| price_cop | DECIMAL(12,2) | Price in COP |
| cost_cop | DECIMAL(12,2) | Cost in COP |
| price_type | VARCHAR(20) | retail/wholesale |
| discount_percentage | DECIMAL(5,2) | Discount % |
| valid_from | DATE | Price start date |
| valid_to | DATE | Price end date |

### orders
Customer orders.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| customer_id | INTEGER | FK to customers |
| order_number | VARCHAR(50) | Unique order number |
| channel | VARCHAR(20) | web/whatsapp |
| status | VARCHAR(20) | Order status |
| payment_method | VARCHAR(30) | Payment method |
| total_cop | DECIMAL(12,2) | Total amount |
| created_at | TIMESTAMP | Order date |

### order_items
Line items for orders.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| order_id | INTEGER | FK to orders |
| article_id | INTEGER | TecDoc article ID |
| article_number | VARCHAR(100) | Article number |
| quantity | INTEGER | Quantity ordered |
| unit_price_cop | DECIMAL(12,2) | Unit price |
| total_price_cop | DECIMAL(12,2) | Line total |

### documents
Uploaded documents (manuals, policies).

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | VARCHAR(255) | Document title |
| document_type | VARCHAR(50) | Type of document |
| file_path | VARCHAR(500) | Storage path |
| content_hash | VARCHAR(64) | SHA256 hash |
| language | VARCHAR(2) | Document language |
| metadata | JSONB | Additional metadata |

### document_chunks
Chunked document content with embeddings.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| document_id | INTEGER | FK to documents |
| chunk_index | INTEGER | Chunk position |
| content | TEXT | Chunk text |
| embedding | vector(1536) | OpenAI embedding |
| tokens | INTEGER | Token count |

### sessions
Chat session tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| session_id | VARCHAR(128) | Unique session ID |
| customer_id | INTEGER | FK to customers |
| channel | VARCHAR(20) | web/whatsapp |
| current_state | VARCHAR(50) | FSM state |
| intent | VARCHAR(50) | Detected intent |
| context | JSONB | Session context |
| language | VARCHAR(2) | Session language |

### conversation_messages
Chat messages within sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| session_id | INTEGER | FK to sessions |
| role | VARCHAR(20) | user/assistant/system |
| content | TEXT | Message content |
| metadata | JSONB | Message metadata |
| created_at | TIMESTAMP | Message timestamp |

## Indexes

```sql
-- Customer indexes
CREATE INDEX idx_customers_firebase_uid ON customers(firebase_uid);
CREATE INDEX idx_customers_email ON customers(email);

-- Stock indexes
CREATE INDEX idx_stock_article_id ON stock(article_id);

-- Price indexes
CREATE INDEX idx_prices_article_id ON prices(article_id);
CREATE INDEX idx_prices_type ON prices(price_type);

-- Order indexes
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);

-- Document chunk indexes
CREATE INDEX idx_chunks_embedding ON document_chunks 
  USING ivfflat (embedding vector_cosine_ops);

-- Session indexes
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_state ON sessions(current_state);
```

## Functions

### Vector Similarity Search
```sql
CREATE FUNCTION search_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    chunk_id int,
    document_id int,
    content text,
    similarity float
)
```

## Row Level Security

RLS is enabled on sensitive tables:
- `customers` - Users can only see their own data
- `orders` - Users can only see their own orders
- `sessions` - Users can only see their own sessions
