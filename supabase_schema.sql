-- Futmatrix Supabase Schema
-- Tables that both Coach and Rivalizer agents will access

-- Players table
CREATE TABLE IF NOT EXISTS futmatrix_players (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    skill_level VARCHAR(50) DEFAULT 'intermediate',
    playstyle VARCHAR(50) DEFAULT 'balanced',
    status VARCHAR(20) DEFAULT 'offline',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table  
CREATE TABLE IF NOT EXISTS futmatrix_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    match_id UUID,
    performance_score DECIMAL(5,2),
    finishing_rating INTEGER CHECK (finishing_rating >= 1 AND finishing_rating <= 10),
    defending_rating INTEGER CHECK (defending_rating >= 1 AND defending_rating <= 10),
    strategy_rating INTEGER CHECK (strategy_rating >= 1 AND strategy_rating <= 10),
    consistency_score DECIMAL(5,2),
    improvement_areas TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Matches table
CREATE TABLE IF NOT EXISTS futmatrix_matches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id VARCHAR(255) NOT NULL,
    opponent_id VARCHAR(255),
    match_type VARCHAR(50) DEFAULT 'competitive',
    result VARCHAR(20), -- 'win', 'loss', 'draw'
    score VARCHAR(20),
    duration_minutes INTEGER,
    match_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rankings table
CREATE TABLE IF NOT EXISTS futmatrix_rankings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    skill_level VARCHAR(50) NOT NULL,
    ranking_points INTEGER DEFAULT 1000,
    tier VARCHAR(50) DEFAULT 'bronze',
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coaching sessions table
CREATE TABLE IF NOT EXISTS futmatrix_coaching_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    focus_areas TEXT[],
    recommendations TEXT,
    performance_targets JSONB,
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_futmatrix_players_user_id ON futmatrix_players(user_id);
CREATE INDEX IF NOT EXISTS idx_futmatrix_performance_user_id ON futmatrix_performance(user_id);
CREATE INDEX IF NOT EXISTS idx_futmatrix_matches_player_id ON futmatrix_matches(player_id);
CREATE INDEX IF NOT EXISTS idx_futmatrix_rankings_user_id ON futmatrix_rankings(user_id);
CREATE INDEX IF NOT EXISTS idx_futmatrix_coaching_sessions_user_id ON futmatrix_coaching_sessions(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE futmatrix_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE futmatrix_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE futmatrix_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE futmatrix_rankings ENABLE ROW LEVEL SECURITY;
ALTER TABLE futmatrix_coaching_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies (basic - can be customized based on auth requirements)
CREATE POLICY "Users can view their own data" ON futmatrix_players
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can view their own performance" ON futmatrix_performance
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can view their own matches" ON futmatrix_matches
    FOR SELECT USING (auth.uid()::text = player_id);

CREATE POLICY "Users can view rankings" ON futmatrix_rankings
    FOR SELECT USING (true);

CREATE POLICY "Users can view their own coaching sessions" ON futmatrix_coaching_sessions
    FOR SELECT USING (auth.uid()::text = user_id);