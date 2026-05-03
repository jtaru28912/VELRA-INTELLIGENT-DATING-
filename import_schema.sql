-- PostgreSQL Ready Import Script for Velra Intelligence Platform
-- Generated: 2026-04-19

-- Enable necessary extensions if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Profiles Table (Understand Their World)
CREATE TABLE IF NOT EXISTS profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    source VARCHAR(20) NOT NULL, -- manual, instagram, linkedin, x, reddit
    extracted_traits JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- 3. Chat Analyses Table (The Truth)
CREATE TABLE IF NOT EXISTS chat_analyses (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    request_hash VARCHAR(64) NOT NULL,
    context VARCHAR(64) NOT NULL,
    messages JSONB NOT NULL,
    features JSONB NOT NULL,
    flags JSONB,
    seriousness_score INTEGER,
    interest_level VARCHAR(12), -- high, medium, low, declining
    pattern VARCHAR(280),
    insights TEXT,
    suggested_action VARCHAR(280),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chat_analyses_user_id ON chat_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_analyses_request_hash ON chat_analyses(request_hash);

-- 4. Training Data Table (Real-time Learning Loop)
CREATE TABLE IF NOT EXISTS training_data (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    analysis_id VARCHAR(36) NOT NULL,
    features JSONB NOT NULL,
    prediction VARCHAR(20) NOT NULL,
    correctness BOOLEAN DEFAULT NULL, -- updated via /feedback endpoint
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_training_data_user_id ON training_data(user_id);
CREATE INDEX IF NOT EXISTS idx_training_data_analysis_id ON training_data(analysis_id);

-- 5. Optional: Initial Data Cleanup helper
-- DELETE FROM training_data WHERE created_at < NOW() - INTERVAL '30 days';
