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
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

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
        
    def generate_wordcloud(self, text: str) -> bytes:
        """
        Generate word cloud from text
        Returns: PNG image as bytes
        """
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            max_words=100
        ).generate(text)
        
        # Convert to bytes
        img = wordcloud.to_image()
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
        
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
        
        # Generate word cloud
        wordcloud_img = self.generate_wordcloud(text_content)
        
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
            "wordcloud": wordcloud_img,
            "fear_greed_index": fear_greed_index,
            "batch_analysis": batch_analysis,
            "timestamp": datetime.utcnow().isoformat()
        } 