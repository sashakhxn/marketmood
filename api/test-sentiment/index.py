from http.server import BaseHTTPRequestHandler
from sentiment_analyzer import SentimentAnalyzer
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize sentiment analyzer
            analyzer = SentimentAnalyzer()
            
            # Test with a simple text
            test_text = "The market is showing strong bullish signals today."
            
            # Make direct API call for debugging
            api_key = analyzer.api_key
            api_url = analyzer.api_url
            headers = analyzer.headers
            
            # Prepare the prompt
            prompt = f"""Analyze the sentiment of this text and provide:
1. A sentiment score between -1 (very negative) and 1 (very positive)
2. A sentiment label (positive, negative, or neutral)
3. A confidence score between 0 and 1

Text: {test_text}

Respond in JSON format with these fields:
- sentiment_score
- sentiment_label
- confidence"""

            # Make the API request
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            
            # Log the raw response for debugging
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "debug",
                "api_response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "text": response.text
                }
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