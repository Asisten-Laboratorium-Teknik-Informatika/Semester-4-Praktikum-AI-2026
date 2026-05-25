-- Lifelens Supabase Schema
-- Run this in your Supabase SQL Editor

-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    display_name TEXT DEFAULT 'teman',
    consent BOOLEAN DEFAULT FALSE,
    voice_choice TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Sessions Table
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    summary TEXT,
    risk_level TEXT CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    top_factors TEXT[], -- Array of strings
    session_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Daily Features Table (For Trend Analysis)
CREATE TABLE IF NOT EXISTS public.daily_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sleep_hours FLOAT4,
    workload_score FLOAT4,
    mood TEXT,
    sentiment_score FLOAT4,
    social_score FLOAT4,
    recovery_score FLOAT4,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- 5. Conversation Texts Table (Encrypted)
CREATE TABLE IF NOT EXISTS public.conversation_texts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    encrypted_text TEXT NOT NULL,
    sender TEXT CHECK (sender IN ('user', 'rina')),
    feedback_score INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (Optional, but recommended for production)
-- For now, we assume service role usage from backend.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_texts ENABLE ROW LEVEL SECURITY;

-- Create policies for service role (or authenticated users if using Supabase Auth)
-- For MVP, we'll allow all operations from the service role which is default.
