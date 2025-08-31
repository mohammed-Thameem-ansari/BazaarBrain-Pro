-- BazaarBrain-Pro Database Schema
-- Run this in your Supabase SQL Editor to create the required tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password TEXT, -- Optional if using Supabase auth
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table (receipts, OCR results)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    raw_input TEXT NOT NULL, -- Original input (image path, text, etc.)
    parsed_json JSONB NOT NULL, -- Structured JSON result from OCR
    source TEXT NOT NULL DEFAULT 'image', -- Source type (e.g., "image", "text", "receipt")
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simulations table (what-if analysis results)
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL, -- Original query text
    parameters JSONB NOT NULL, -- Parsed parameters used for simulation
    result JSONB NOT NULL, -- Simulation results
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source);

CREATE INDEX IF NOT EXISTS idx_simulations_user_id ON simulations(user_id);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at 
    BEFORE UPDATE ON transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_simulations_updated_at 
    BEFORE UPDATE ON simulations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
-- Uncomment these lines if you want to add test data

/*
-- Sample user
INSERT INTO users (email) VALUES ('test@bazaarbrain.com') ON CONFLICT (email) DO NOTHING;

-- Sample transaction
INSERT INTO transactions (user_id, raw_input, parsed_json, source) 
SELECT 
    u.id,
    'sample_receipt.jpg',
    '{"items": [{"name": "Coffee", "price": 3.50, "quantity": 1}], "total": 3.50, "vendor": "Starbucks", "date": "2024-01-15"}',
    'image'
FROM users u WHERE u.email = 'test@bazaarbrain.com';

-- Sample simulation
INSERT INTO simulations (user_id, query, parameters, result)
SELECT 
    u.id,
    'What if I increase coffee price by 10%?',
    '{"scenario": "increase_price", "item": "Coffee", "change": 10, "current_price": 3.50}',
    '{"estimated_profit_change": 0.35, "new_price": 3.85, "assumptions": "based on last 7 days of sales"}'
FROM users u WHERE u.email = 'test@bazaarbrain.com';
*/

-- Grant necessary permissions (adjust based on your Supabase setup)
-- These are typically handled automatically by Supabase
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Verify tables were created
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('users', 'transactions', 'simulations')
ORDER BY table_name, ordinal_position;

-- Day 6: Collective Orders table and triggers

-- Collective Orders table (persistent aggregation)
CREATE TABLE IF NOT EXISTS collective_orders (
        order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        aggregated_quantity INTEGER NOT NULL DEFAULT 0,
        price_per_unit NUMERIC(12,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Aggregation helper function: updates aggregated_quantity per product_id
CREATE OR REPLACE FUNCTION update_collective_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Recompute aggregated_quantity for all rows with this product_id
    UPDATE collective_orders co
    SET aggregated_quantity = sub.total_qty,
            updated_at = NOW()
    FROM (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM collective_orders
        WHERE product_id = NEW.product_id
        GROUP BY product_id
    ) AS sub
    WHERE co.product_id = sub.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on insert/update
DROP TRIGGER IF EXISTS trg_collective_aggregate_ins ON collective_orders;
CREATE TRIGGER trg_collective_aggregate_ins
AFTER INSERT ON collective_orders
FOR EACH ROW EXECUTE FUNCTION update_collective_aggregate();

DROP TRIGGER IF EXISTS trg_collective_aggregate_upd ON collective_orders;
CREATE TRIGGER trg_collective_aggregate_upd
AFTER UPDATE ON collective_orders
FOR EACH ROW EXECUTE FUNCTION update_collective_aggregate();

-- Sample data for collective orders (optional)
-- Insert three sample orders for product 'rice'
INSERT INTO collective_orders (user_id, product_id, quantity, price_per_unit)
SELECT u.id, 'rice', 50, 47.50 FROM users u LIMIT 1;
INSERT INTO collective_orders (user_id, product_id, quantity, price_per_unit)
SELECT u.id, 'rice', 75, 46.00 FROM users u LIMIT 1;
INSERT INTO collective_orders (user_id, product_id, quantity, price_per_unit)
SELECT u.id, 'sugar', 40, 38.00 FROM users u LIMIT 1;

