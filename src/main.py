from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .reddit_collector import RedditCollector
from .database import Database
from .sentiment_analyzer import SentimentAnalyzer
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

# Initialize components
reddit_collector = RedditCollector()
database = Database()
sentiment_analyzer = SentimentAnalyzer()

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
            "reddit_api": "operational",
            "sentiment_analysis": "operational"
        }
    }

@app.get("/reddit/posts/{subreddit}")
async def get_subreddit_posts(subreddit: str, limit: int = 100):
    try:
        # Get posts from Reddit
        posts = reddit_collector.collect_posts(subreddit, limit)
        
        # Store posts in database
        for post in posts:
            database.store_post(post)
            
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
        
        # Store posts in database
        for subreddit_posts in all_posts.values():
            for post in subreddit_posts:
                database.store_post(post)
                
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reddit/comments/{post_id}")
async def get_post_comments(post_id: str, limit: int = 100):
    try:
        comments = reddit_collector.get_post_comments(post_id, limit)
        
        # Store comments in database
        for comment in comments:
            database.store_comment(comment)
            
        return {
            "post_id": post_id,
            "comments": comments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/post/{post_id}")
async def analyze_post(post_id: str):
    try:
        # Get post from database
        posts = database.get_posts_by_subreddit(post_id, limit=1)
        if not posts:
            raise HTTPException(status_code=404, detail="Post not found")
            
        post = posts[0]
        
        # Analyze sentiment
        sentiment_data = sentiment_analyzer.analyze_post(post)
        
        # Store sentiment analysis
        database.store_sentiment(sentiment_data)
        
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/comment/{comment_id}")
async def analyze_comment(comment_id: str):
    try:
        # Get comment from database
        comments = database.get_comments_by_post(comment_id, limit=1)
        if not comments:
            raise HTTPException(status_code=404, detail="Comment not found")
            
        comment = comments[0]
        
        # Analyze sentiment
        sentiment_data = sentiment_analyzer.analyze_comment(comment)
        
        # Store sentiment analysis
        database.store_sentiment(sentiment_data)
        
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 