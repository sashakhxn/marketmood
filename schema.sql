-- Create posts table
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT,
    score INTEGER NOT NULL,
    created_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    num_comments INTEGER NOT NULL,
    subreddit TEXT NOT NULL,
    url TEXT,
    author TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create comments table
CREATE TABLE comments (
    id TEXT PRIMARY KEY,
    post_id TEXT REFERENCES posts(id),
    text TEXT NOT NULL,
    score INTEGER NOT NULL,
    created_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    author TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sentiments table
CREATE TABLE sentiments (
    id SERIAL PRIMARY KEY,
    content_id TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('post', 'comment')),
    sentiment_score FLOAT NOT NULL,
    sentiment_label TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_posts_subreddit ON posts(subreddit);
CREATE INDEX idx_posts_created_utc ON posts(created_utc);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_created_utc ON comments(created_utc);
CREATE INDEX idx_sentiments_content_id ON sentiments(content_id);
CREATE INDEX idx_sentiments_content_type ON sentiments(content_type); 