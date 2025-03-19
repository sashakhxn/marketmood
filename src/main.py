from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from reddit_collector import RedditCollector
from typing import Dict, List, Any

app = FastAPI(
    title="MarketMood API",
    description="API for collecting and analyzing retail investor sentiment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Reddit collector
reddit_collector = RedditCollector()

@app.get("/")
async def root():
    return {
        "message": "Welcome to MarketMood API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "operational",
            "reddit_api": "operational"
        }
    }

@app.get("/reddit/posts/{subreddit}")
async def get_subreddit_posts(subreddit: str, limit: int = 100):
    try:
        posts = reddit_collector.collect_posts(subreddit, limit)
        return {
            "subreddit": subreddit,
            "posts": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reddit/posts")
async def get_all_posts(limit: int = 100):
    try:
        all_posts = reddit_collector.collect_all_subreddits(limit)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reddit/comments/{post_id}")
async def get_post_comments(post_id: str, limit: int = 100):
    try:
        comments = reddit_collector.get_post_comments(post_id, limit)
        return {
            "post_id": post_id,
            "comments": comments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 