-- Migration: Menambahkan feedback_score ke conversation_texts
-- Jalankan kode ini di Supabase SQL Editor

ALTER TABLE public.conversation_texts 
ADD COLUMN IF NOT EXISTS feedback_score INT DEFAULT 0;
