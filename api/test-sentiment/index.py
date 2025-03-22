from http.server import BaseHTTPRequestHandler
from sentiment_analyzer import SentimentAnalyzer
import json
import requests
import re
from datetime import datetime, timedelta
from requests.exceptions import Timeout

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize sentiment analyzer
            analyzer = SentimentAnalyzer()
            
            # Sample social media data (simulating what we'd get from Reddit/X)
            social_data = {
                "posts": [
                    {
                        "platform": "reddit",
                        "subreddit": "wallstreetbets",
                        "content": "🚀 GME is the play today! Diamond hands!",
                        "upvotes": 1500,
                        "comments": 200
                    },
                    {
                        "platform": "reddit",
                        "subreddit": "stocks",
                        "content": "NVDA earnings tomorrow - what are your predictions?",
                        "upvotes": 800,
                        "comments": 150
                    },
                    {
                        "platform": "twitter",
                        "hashtags": ["#stocks", "#trading"],
                        "content": "TSLA showing strong momentum today. Retail traders are bullish!",
                        "likes": 1200,
                        "retweets": 300
                    }
                ],
                "comments": [
                    {
                        "platform": "reddit",
                        "content": "AAPL is undervalued at current levels",
                        "upvotes": 500
                    },
                    {
                        "platform": "twitter",
                        "content": "Market looking bearish today. Time to buy puts?",
                        "likes": 400
                    }
                ]
            }
            
            # Prepare the prompt for analyzing retail sentiment
            prompt = f"""Analyze this social media data from retail traders and provide:
1. Trending stocks (most mentioned with sentiment)
2. Overall market sentiment
3. Fear/Greed indicators
4. Key themes/topics

Data: {json.dumps(social_data)}

Respond in JSON format with these fields:
- trending_stocks: list of objects with fields:
  * symbol: stock symbol
  * mentions: number of mentions
  * sentiment_score: between -1 and 1
  * sentiment_label: "positive", "negative", or "neutral"
- market_sentiment: object with fields:
  * score: between -1 and 1
  * label: "positive", "negative", or "neutral"
- fear_greed_index: number between 0 and 100
- key_themes: list of strings
- confidence: number between 0 and 1"""

            # Make the API request with timeout
            try:
                response = requests.post(
                    analyzer.api_url,
                    headers=analyzer.headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    },
                    timeout=25  # 25 second timeout
                )
            except Timeout:
                # Return a simplified response if the API times out
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "analysis": {
                        "trending_stocks": [
                            {
                                "symbol": "GME",
                                "mentions": 1,
                                "sentiment_score": 0.8,
                                "sentiment_label": "positive"
                            },
                            {
                                "symbol": "NVDA",
                                "mentions": 1,
                                "sentiment_score": 0.5,
                                "sentiment_label": "neutral"
                            },
                            {
                                "symbol": "TSLA",
                                "mentions": 1,
                                "sentiment_score": 0.7,
                                "sentiment_label": "positive"
                            },
                            {
                                "symbol": "AAPL",
                                "mentions": 1,
                                "sentiment_score": 0.6,
                                "sentiment_label": "positive"
                            }
                        ],
                        "market_sentiment": {
                            "score": 0.65,
                            "label": "positive"
                        },
                        "fear_greed_index": 65,
                        "key_themes": ["earnings", "momentum", "bullish sentiment"],
                        "confidence": 0.8
                    },
                    "timestamp": datetime.now().isoformat(),
                    "data_sources": ["reddit", "twitter"],
                    "note": "Using fallback analysis due to API timeout"
                }).encode())
                return
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            # Parse the response
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from markdown code block
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                analysis = json.loads(json_str)
            else:
                raise Exception("Could not find JSON in response")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "data_sources": ["reddit", "twitter"]
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = str(e)
            if "API request failed" in error_message:
                try:
                    error_details = json.loads(error_message.split("API request failed: ")[1])
                    error_message = f"DeepSeek API Error: {error_details}"
                except:
                    pass
            self.wfile.write(json.dumps({
                "status": "error",
                "detail": error_message
            }).encode()) 