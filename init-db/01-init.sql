-- Initialize AI Agents Database with agent-specific schemas
-- This script creates the base structure for each agent's dedicated schema

-- Create custom roles
CREATE ROLE authenticator NOINHERIT;
CREATE ROLE anon;
CREATE ROLE authenticated;
CREATE ROLE service_role;

-- Grant basic permissions
GRANT anon TO authenticator;
GRANT authenticated TO authenticator;
GRANT service_role TO authenticator;

-- Set passwords
ALTER ROLE authenticator WITH PASSWORD 'authenticator123';

-- Create agent-specific schemas
CREATE SCHEMA IF NOT EXISTS agent_alpha;
CREATE SCHEMA IF NOT EXISTS agent_beta;

-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA agent_alpha TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA agent_beta TO anon, authenticated, service_role;

-- Grant table permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_alpha GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA agent_beta GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated, service_role;

-- Create shared tables in public schema
CREATE TABLE IF NOT EXISTS public.agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    session_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS public.message_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.agent_sessions(id),
    agent_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    message_type TEXT NOT NULL CHECK (message_type IN ('user_prompt', 'agent_response', 'system_notification')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON public.agent_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id ON public.agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_active ON public.agent_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_message_history_session_id ON public.message_history(session_id);
CREATE INDEX IF NOT EXISTS idx_message_history_agent_id ON public.message_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_message_history_created_at ON public.message_history(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for agent_sessions
CREATE TRIGGER update_agent_sessions_updated_at 
    BEFORE UPDATE ON public.agent_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message_history ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow all operations for service role" ON public.agent_sessions FOR ALL TO service_role;
CREATE POLICY "Allow all operations for service role" ON public.message_history FOR ALL TO service_role;

CREATE POLICY "Users can access their own sessions" ON public.agent_sessions 
    FOR ALL TO authenticated 
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

CREATE POLICY "Users can access their own messages" ON public.message_history 
    FOR ALL TO authenticated 
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

-- Allow anonymous access for now (can be restricted later)
CREATE POLICY "Allow anonymous access" ON public.agent_sessions FOR ALL TO anon;
CREATE POLICY "Allow anonymous access" ON public.message_history FOR ALL TO anon;

-- Initialize agent schema placeholders (will be populated by application)
-- Agent Alpha (Financial Advisor) will have its own tables
-- Agent Beta (Content Creator) will have its own tables

COMMENT ON SCHEMA agent_alpha IS 'Dedicated schema for Agent Alpha (Financial Advisor) - contains business-specific tables and data';
COMMENT ON SCHEMA agent_beta IS 'Dedicated schema for Agent Beta (Content Creator) - contains business-specific tables and data';

-- Log initialization
INSERT INTO public.message_history (agent_id, user_id, message_type, content, metadata) 
VALUES ('system', 'system', 'system_notification', 'Database initialized with agent-specific schemas', 
        '{"schemas": ["agent_alpha", "agent_beta"], "timestamp": "' || NOW() || '"}'::jsonb);