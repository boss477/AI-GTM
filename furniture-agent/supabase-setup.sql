-- Furniture Lead Agent - Supabase Setup
-- Project: https://aghavnajgmphznjpjpef.supabase.co
-- Run this in your Supabase SQL Editor

-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create furniture_leads table
CREATE TABLE IF NOT EXISTS furniture_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company TEXT,
    website TEXT,
    intent_signal TEXT,
    intent_score INTEGER,
    city TEXT,
    segment TEXT,
    decision_maker_role TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE furniture_leads ENABLE ROW LEVEL SECURITY;

-- 4. Create policy for anonymous/public insert (for demo purposes)
-- Note: For production, restrict to authenticated users only
CREATE POLICY "Allow anonymous inserts" ON furniture_leads
    FOR INSERT
    WITH CHECK (true);

-- 5. Create policy for public read access (for demo purposes)
CREATE POLICY "Allow public read" ON furniture_leads
    FOR SELECT
    USING (true);

-- 6. Create policy for public update (for demo purposes)
CREATE POLICY "Allow public update" ON furniture_leads
    FOR UPDATE
    USING (true);

-- 7. Create policy for public delete (for demo purposes)
CREATE POLICY "Allow public delete" ON furniture_leads
    FOR DELETE
    USING (true);

-- 8. Verify table was created
SELECT * FROM furniture_leads LIMIT 0;
