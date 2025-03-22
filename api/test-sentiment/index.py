from http.server import BaseHTTPRequestHandler
from sentiment_analyzer import SentimentAnalyzer
import json
import requests
import re

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
                "test_text": test_text,
                "sentiment_score": analysis["sentiment_score"],
                "sentiment_label": analysis["sentiment_label"],
                "confidence": analysis["confidence"]
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