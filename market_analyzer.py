import os
import requests
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime, timedelta
import re
from collections import Counter
from textblob import TextBlob
import pandas as pd
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Missing DeepSeek API key")
            
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Stock symbol patterns
        self.stock_patterns = [
            r'\$[A-Z]{1,5}',  # $AAPL
            r'[A-Z]{1,5}',    # AAPL
            r'[A-Za-z]+ Inc\.',  # Apple Inc.
            r'[A-Za-z]+ Corp\.'  # Microsoft Corp.
        ]
        
    def batch_analyze_content(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a batch of posts/comments for comprehensive market insights
        """
        try:
            # Combine all text for analysis
            combined_text = " ".join([
                f"{content.get('title', '')} {content.get('text', '')}"
                for content in contents
            ])
            
            # Prepare the prompt for comprehensive analysis
            prompt = f"""Analyze this market-related content and provide:
1. List of mentioned stocks with their sentiment scores
2. Key news and updates
3. Market sentiment indicators (fear/greed)
4. Trending topics and themes
5. Risk indicators

Content: {combined_text}

Respond in JSON format with these fields:
- stocks: List of dicts with symbol, sentiment_score, mention_count
- news: List of dicts with title, category, sentiment
- market_sentiment: Dict with fear_greed_score, confidence
- trending_topics: List of dicts with topic, frequency, sentiment
- risk_indicators: Dict with volatility_score, contrarian_signals"""

            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            # Parse the response
            result = response.json()
            content = result['choices'][0]['message']['content']
            analysis = json.loads(content)
            
            return analysis
            
        except Exception as e:
            print(f"Error in batch analysis: {str(e)}")
            raise
            
    def extract_stock_mentions(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract stock symbols from text
        Returns: List of (symbol, count) tuples
        """
        mentions = []
        for pattern in self.stock_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                symbol = match.group().strip('$').strip('.')
                mentions.append(symbol)
        
        return Counter(mentions).most_common()
        
    def generate_word_frequencies(self, text: str, max_words: int = 100) -> List[Dict[str, Any]]:
        """
        Generate word frequencies for word cloud generation
        Returns: List of dicts with word and frequency
        """
        # Split text into words and count frequencies
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Convert to list of dicts
        return [
            {"word": word, "frequency": count}
            for word, count in word_counts.most_common(max_words)
        ]
        
    def calculate_fear_greed_index(self, sentiment_scores: List[float]) -> float:
        """
        Calculate fear/greed index from sentiment scores
        Returns: Score between 0 (extreme fear) and 100 (extreme greed)
        """
        if not sentiment_scores:
            return 50.0
            
        # Normalize sentiment scores to 0-100 range
        normalized_scores = [(score + 1) * 50 for score in sentiment_scores]
        return np.mean(normalized_scores)
        
    def analyze_market_trends(self, posts: List[Dict[str, Any]], 
                            comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive market trend analysis
        """
        # Combine all content
        all_content = posts + comments
        text_content = " ".join([
            f"{content.get('title', '')} {content.get('text', '')}"
            for content in all_content
        ])
        
        # Extract stock mentions
        stock_mentions = self.extract_stock_mentions(text_content)
        
        # Generate word frequencies
        word_frequencies = self.generate_word_frequencies(text_content)
        
        # Calculate sentiment scores
        sentiment_scores = [
            TextBlob(content.get('text', '')).sentiment.polarity
            for content in all_content
        ]
        
        # Calculate fear/greed index
        fear_greed_index = self.calculate_fear_greed_index(sentiment_scores)
        
        # Perform batch analysis
        batch_analysis = self.batch_analyze_content(all_content)
        
        return {
            "stock_mentions": stock_mentions,
            "word_frequencies": word_frequencies,
            "fear_greed_index": fear_greed_index,
            "batch_analysis": batch_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def analyze_stock_mentions(self, posts: List[Dict[str, Any]], 
                             comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze only stock mentions
        """
        # Combine all content
        all_content = posts + comments
        text_content = " ".join([
            f"{content.get('title', '')} {content.get('text', '')}"
            for content in all_content
        ])
        
        # Extract stock mentions
        stock_mentions = self.extract_stock_mentions(text_content)
        
        return {
            "stock_mentions": stock_mentions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def analyze_sentiment(self, posts: List[Dict[str, Any]], 
                         comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze only sentiment
        """
        # Combine all content
        all_content = posts + comments
        
        # Calculate sentiment scores
        sentiment_scores = [
            TextBlob(content.get('text', '')).sentiment.polarity
            for content in all_content
        ]
        
        # Calculate fear/greed index
        fear_greed_index = self.calculate_fear_greed_index(sentiment_scores)
        
        return {
            "fear_greed_index": fear_greed_index,
            "average_sentiment": np.mean(sentiment_scores) if sentiment_scores else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def analyze_wordcloud(self, posts: List[Dict[str, Any]], 
                         comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze only word frequencies for word cloud
        """
        # Combine all content
        all_content = posts + comments
        text_content = " ".join([
            f"{content.get('title', '')} {content.get('text', '')}"
            for content in all_content
        ])
        
        # Generate word frequencies
        word_frequencies = self.generate_word_frequencies(text_content)
        
        return {
            "word_frequencies": word_frequencies,
            "timestamp": datetime.utcnow().isoformat()
        } 