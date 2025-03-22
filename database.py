from supabase import create_client
import os
from typing import Dict, List, Any
from datetime import datetime
import json

class Database:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials")
            
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
    def store_post(self, post_data: Dict[str, Any]) -> None:
        """Store a Reddit post in the database"""
        try:
            self.supabase.table('posts').upsert(post_data).execute()
        except Exception as e:
            print(f"Error storing post: {str(e)}")
            raise
            
    def store_comment(self, comment_data: Dict[str, Any]) -> None:
        """Store a Reddit comment in the database"""
        try:
            self.supabase.table('comments').upsert(comment_data).execute()
        except Exception as e:
            print(f"Error storing comment: {str(e)}")
            raise
            
    def store_sentiment(self, sentiment_data: Dict[str, Any]) -> None:
        """Store sentiment analysis results"""
        try:
            self.supabase.table('sentiments').upsert(sentiment_data).execute()
        except Exception as e:
            print(f"Error storing sentiment: {str(e)}")
            raise
            
    def get_posts_by_subreddit(self, subreddit: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts from a specific subreddit"""
        try:
            response = self.supabase.table('posts')\
                .select('*')\
                .eq('subreddit', subreddit)\
                .order('created_utc', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting posts: {str(e)}")
            raise
            
    def get_comments_by_post(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get comments for a specific post"""
        try:
            response = self.supabase.table('comments')\
                .select('*')\
                .eq('post_id', post_id)\
                .order('created_utc', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting comments: {str(e)}")
            raise
            
    def get_posts_by_time_range(self, start_time: datetime, end_time: datetime, page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
        """Get posts within a time range with pagination"""
        try:
            start = (page - 1) * page_size
            response = self.supabase.table('posts').select('*').gte('created_utc', start_time.isoformat()).lte('created_utc', end_time.isoformat()).order('created_utc', desc=True).range(start, start + page_size - 1).execute()
            return response.data
        except Exception as e:
            print(f"Error getting posts by time range: {e}")
            return []
            
    def get_comments_by_time_range(self, start_time: datetime, end_time: datetime, page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
        """Get comments within a time range with pagination"""
        try:
            start = (page - 1) * page_size
            response = self.supabase.table('comments').select('*').gte('created_utc', start_time.isoformat()).lte('created_utc', end_time.isoformat()).order('created_utc', desc=True).range(start, start + page_size - 1).execute()
            return response.data
        except Exception as e:
            print(f"Error getting comments by time range: {e}")
            return []
            
    def get_sentiment_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get sentiment analysis results within a time range"""
        try:
            response = self.supabase.table('sentiments')\
                .select('*')\
                .gte('created_at', start_time.isoformat())\
                .lte('created_at', end_time.isoformat())\
                .order('created_at', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting sentiment by time range: {str(e)}")
            raise

    def store_daily_analysis(self, date, stock_mentions, word_frequencies, fear_greed_index, 
                            market_sentiment, trending_topics, risk_indicators):
        """
        Store daily market analysis in the database
        """
        try:
            query = """
            INSERT INTO daily_market_analysis 
            (date, stock_mentions, word_frequencies, fear_greed_index, 
             market_sentiment, trending_topics, risk_indicators)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET
                stock_mentions = EXCLUDED.stock_mentions,
                word_frequencies = EXCLUDED.word_frequencies,
                fear_greed_index = EXCLUDED.fear_greed_index,
                market_sentiment = EXCLUDED.market_sentiment,
                trending_topics = EXCLUDED.trending_topics,
                risk_indicators = EXCLUDED.risk_indicators
            """
            
            self.supabase.table('daily_market_analysis').upsert({
                "date": date,
                "stock_mentions": json.dumps(stock_mentions),
                "word_frequencies": json.dumps(word_frequencies),
                "fear_greed_index": fear_greed_index,
                "market_sentiment": json.dumps(market_sentiment),
                "trending_topics": json.dumps(trending_topics),
                "risk_indicators": json.dumps(risk_indicators)
            }).execute()
            
        except Exception as e:
            print(f"Error storing daily analysis: {str(e)}")
            raise

    def get_latest_market_analysis(self):
        """
        Get the most recent market analysis
        """
        try:
            response = self.supabase.table('daily_market_analysis').select('*').order('date', desc=True).limit(1).execute()
            result = response.data[0] if response.data else None
            
            if result:
                return {
                    "date": result['date'],
                    "stock_mentions": json.loads(result['stock_mentions']),
                    "word_frequencies": json.loads(result['word_frequencies']),
                    "fear_greed_index": result['fear_greed_index'],
                    "market_sentiment": json.loads(result['market_sentiment']),
                    "trending_topics": json.loads(result['trending_topics']),
                    "risk_indicators": json.loads(result['risk_indicators']),
                    "created_at": result['created_at']
                }
            return None
            
        except Exception as e:
            print(f"Error getting latest market analysis: {str(e)}")
            raise 