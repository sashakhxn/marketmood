import praw
import os
from datetime import datetime
from typing import List, Dict, Any

class RedditCollector:
    def __init__(self):
        # Get environment variables directly without dotenv
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT")
        
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("Missing required Reddit API credentials")
            
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Target subreddits for retail investor discussions
        self.target_subreddits = [
            "wallstreetbets",
            "investing",
            "stocks",
            "stockmarket",
            "options"
        ]

    def collect_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Collect posts from a specific subreddit
        """
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)
        
        for post in subreddit.hot(limit=limit):
            post_data = {
                "id": post.id,
                "title": post.title,
                "text": post.selftext,
                "score": post.score,
                "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                "num_comments": post.num_comments,
                "subreddit": subreddit_name,
                "url": post.url,
                "author": str(post.author) if post.author else "[deleted]"
            }
            posts.append(post_data)
            
        return posts

    def collect_all_subreddits(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect posts from all target subreddits
        """
        all_posts = {}
        
        for subreddit in self.target_subreddits:
            try:
                posts = self.collect_posts(subreddit, limit)
                all_posts[subreddit] = posts
            except Exception as e:
                print(f"Error collecting posts from r/{subreddit}: {str(e)}")
                all_posts[subreddit] = []
                
        return all_posts

    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Collect comments from a specific post
        """
        comments = []
        submission = self.reddit.submission(id=post_id)
        
        # Expand all comments
        submission.comments.replace_more(limit=None)
        
        for comment in submission.comments.list():
            if hasattr(comment, 'body'):  # Skip MoreComments objects
                comment_data = {
                    "id": comment.id,
                    "text": comment.body,
                    "score": comment.score,
                    "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                    "author": str(comment.author) if comment.author else "[deleted]"
                }
                comments.append(comment_data)
                
        return comments[:limit]  # Limit the number of comments returned 