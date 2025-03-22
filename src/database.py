from supabase import create_client
import os
from typing import Dict, List, Any
from datetime import datetime

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
            
    def get_posts_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get posts within a time range"""
        try:
            response = self.supabase.table('posts')\
                .select('*')\
                .gte('created_utc', start_time.isoformat())\
                .lte('created_utc', end_time.isoformat())\
                .order('created_utc', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting posts by time range: {str(e)}")
            raise
            
    def get_comments_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get comments within a time range"""
        try:
            response = self.supabase.table('comments')\
                .select('*')\
                .gte('created_utc', start_time.isoformat())\
                .lte('created_utc', end_time.isoformat())\
                .order('created_utc', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting comments by time range: {str(e)}")
            raise
            
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