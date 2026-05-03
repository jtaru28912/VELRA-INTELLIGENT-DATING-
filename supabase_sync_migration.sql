-- Supabase Delta Migration Script (Velra Hybrid Upgrade)
-- Run this in your Supabase SQL Editor to align your existing tables.

-- 1. Align Users Table
-- Rename password_hash to match code if needed, but I will adjust code to match yours instead.
-- Ensure email is unique (already is in your script)

-- 2. Upgrade Analyses Table to Hybrid Path
-- This adds the necessary tracking for ML and GenAI usage.
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS request_hash VARCHAR(64);
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS flags JSONB DEFAULT '[]';
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS insights TEXT;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS prompt_tokens INTEGER DEFAULT 0;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS completion_tokens INTEGER DEFAULT 0;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS total_tokens INTEGER DEFAULT 0;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS date_strategy JSONB; -- For the new nested strategy

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_analyses_request_hash ON analyses(request_hash);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);

-- 3. Create Training Data Table
-- This is critical for the Real-time Learning Loop (Continuous Learning)
CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL,
    features JSONB NOT NULL, -- Merged behavioral signals
    prediction TEXT NOT NULL,
    correctness BOOLEAN DEFAULT NULL, -- Updated via /feedback endpoint
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_training_data_analysis_id ON training_data(analysis_id);

-- 4. Credits Table Optimization
-- Ensuring last_reset is indexed for the daily reset logic.
CREATE INDEX IF NOT EXISTS idx_credits_last_reset ON credits(last_reset);

-- 5. Social Bio Intelligence Index
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- NOTE: If you decide to keep the separate 'features' table, the hybrid service 
-- will continue to write to 'analyses' JSONB for high-speed retrieval.
