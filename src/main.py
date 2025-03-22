from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .reddit_collector import RedditCollector
from .database import Database
from .sentiment_analyzer import SentimentAnalyzer
from .market_analyzer import MarketAnalyzer
from typing import Dict, List, Any
from datetime import datetime, timedelta
import io

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
market_analyzer = MarketAnalyzer()

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

@app.get("/market/trends")
async def get_market_trends(hours: int = 24):
    try:
        # Get posts and comments from the last N hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Analyze market trends
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/wordcloud")
async def get_wordcloud(hours: int = 24):
    try:
        # Get posts and comments from the last N hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Generate word cloud
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        # Return word cloud as PNG image
        return StreamingResponse(
            io.BytesIO(analysis["wordcloud"]),
            media_type="image/png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/stocks")
async def get_trending_stocks(hours: int = 24):
    try:
        # Get posts and comments from the last N hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Analyze market trends
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        return {
            "trending_stocks": analysis["stock_mentions"],
            "sentiment_analysis": analysis["batch_analysis"]["stocks"],
            "timestamp": analysis["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/sentiment")
async def get_market_sentiment(hours: int = 24):
    try:
        # Get posts and comments from the last N hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Analyze market trends
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        return {
            "fear_greed_index": analysis["fear_greed_index"],
            "market_sentiment": analysis["batch_analysis"]["market_sentiment"],
            "risk_indicators": analysis["batch_analysis"]["risk_indicators"],
            "timestamp": analysis["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/news")
async def get_market_news(hours: int = 24):
    try:
        # Get posts and comments from the last N hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Analyze market trends
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        return {
            "news": analysis["batch_analysis"]["news"],
            "trending_topics": analysis["batch_analysis"]["trending_topics"],
            "timestamp": analysis["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 