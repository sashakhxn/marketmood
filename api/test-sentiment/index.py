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
            
            # Test cases with different types of market-related text
            test_cases = [
                {
                    "name": "Positive Price Movement",
                    "text": "The market is showing strong bullish signals today with major indices up 2%."
                },
                {
                    "name": "Negative Market Fear",
                    "text": "Market crash fears are growing as volatility spikes and trading volume drops."
                },
                {
                    "name": "Neutral Technical Analysis",
                    "text": "The S&P 500 is trading at its 50-day moving average with moderate volume."
                },
                {
                    "name": "Mixed Economic Indicators",
                    "text": "While unemployment is down, inflation concerns are rising in the market."
                },
                {
                    "name": "Company-Specific News",
                    "text": "Tech giant reports record earnings but warns of supply chain challenges."
                }
            ]
            
            results = []
            for test_case in test_cases:
                # Prepare the prompt
                prompt = f"""Analyze the sentiment of this text and provide:
1. A sentiment score between -1 (very negative) and 1 (very positive)
2. A sentiment label (positive, negative, or neutral)
3. A confidence score between 0 and 1

Text: {test_case['text']}

Respond in JSON format with these fields:
- sentiment_score
- sentiment_label
- confidence"""

                # Make the API request
                response = requests.post(
                    analyzer.api_url,
                    headers=analyzer.headers,
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
                
                results.append({
                    "name": test_case["name"],
                    "text": test_case["text"],
                    "sentiment_score": analysis["sentiment_score"],
                    "sentiment_label": analysis["sentiment_label"],
                    "confidence": analysis["confidence"]
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "results": results
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