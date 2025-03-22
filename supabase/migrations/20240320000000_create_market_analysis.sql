-- Create market_analysis table
CREATE TABLE IF NOT EXISTS market_analysis (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    analysis JSONB NOT NULL,
    data_sources TEXT[] NOT NULL,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_market_analysis_timestamp ON market_analysis(timestamp DESC); 