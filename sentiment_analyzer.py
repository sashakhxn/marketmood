import os
import requests
from typing import Dict, Any, Tuple
import json

class SentimentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("Missing DeepSeek API key")
            
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def analyze_text(self, text: str) -> Tuple[float, str, float]:
        """
        Analyze the sentiment of a given text
        Returns: (sentiment_score, sentiment_label, confidence)
        """
        try:
            # Prepare the prompt for sentiment analysis
            prompt = f"""Analyze the sentiment of this text and provide:
1. A sentiment score between -1 (very negative) and 1 (very positive)
2. A sentiment label (positive, negative, or neutral)
3. A confidence score between 0 and 1

Text: {text}

Respond in JSON format with these fields:
- sentiment_score
- sentiment_label
- confidence"""

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
            
            return (
                analysis['sentiment_score'],
                analysis['sentiment_label'],
                analysis['confidence']
            )
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            raise
            
    def analyze_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a Reddit post
        """
        # Combine title and text for analysis
        text_to_analyze = f"{post_data['title']} {post_data.get('text', '')}"
        
        sentiment_score, sentiment_label, confidence = self.analyze_text(text_to_analyze)
        
        return {
            "content_id": post_data['id'],
            "content_type": "post",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": confidence
        }
        
    def analyze_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a Reddit comment
        """
        sentiment_score, sentiment_label, confidence = self.analyze_text(comment_data['text'])
        
        return {
            "content_id": comment_data['id'],
            "content_type": "comment",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": confidence
        } 