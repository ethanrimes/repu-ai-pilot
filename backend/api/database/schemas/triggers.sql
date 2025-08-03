-- backend/api/database/schemas/triggers.sql
-- Path: backend/api/database/schemas/triggers.sql

-- ============================================
-- Update Triggers
-- ============================================

-- Orders table updated_at trigger
DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Stock table updated_at trigger
DROP TRIGGER IF EXISTS update_stock_updated_at ON stock;
CREATE TRIGGER update_stock_updated_at 
    BEFORE UPDATE ON stock
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sessions last_activity trigger
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sessions 
    SET last_activity = CURRENT_TIMESTAMP
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_session_on_message ON conversation_messages;
CREATE TRIGGER update_session_on_message
    AFTER INSERT ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_activity();

-- ============================================
-- Row Level Security (RLS)
-- ============================================

-- Enable RLS on sensitive tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Customer policies
CREATE POLICY customers_self_select ON customers
    FOR SELECT USING (firebase_uid = auth.uid()::text);

CREATE POLICY customers_self_update ON customers
    FOR UPDATE USING (firebase_uid = auth.uid()::text);

-- Order policies
CREATE POLICY orders_customer_select ON orders
    FOR SELECT USING (customer_id IN (
        SELECT id FROM customers WHERE firebase_uid = auth.uid()::text
    ));

-- Session policies
CREATE POLICY sessions_customer_select ON sessions
    FOR SELECT USING (customer_id IN (
        SELECT id FROM customers WHERE firebase_uid = auth.uid()::text
    ));

-- Service role bypass
CREATE POLICY service_role_bypass_customers ON customers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY service_role_bypass_orders ON orders
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY service_role_bypass_sessions ON sessions
    FOR ALL USING (auth.role() = 'service_role');