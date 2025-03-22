-- Create daily market analysis table
CREATE TABLE daily_market_analysis (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    stock_mentions JSONB NOT NULL,
    word_frequencies JSONB NOT NULL,
    fear_greed_index FLOAT NOT NULL,
    market_sentiment JSONB NOT NULL,
    trending_topics JSONB NOT NULL,
    risk_indicators JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date)
);

-- Create index for quick date lookups
CREATE INDEX idx_daily_market_analysis_date ON daily_market_analysis(date); 