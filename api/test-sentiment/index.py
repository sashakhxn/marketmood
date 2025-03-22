from http.server import BaseHTTPRequestHandler
from sentiment_analyzer import SentimentAnalyzer

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize sentiment analyzer
            analyzer = SentimentAnalyzer()
            
            # Test with a simple text
            test_text = "The market is showing strong bullish signals today."
            
            # Analyze sentiment
            sentiment_score, sentiment_label, confidence = analyzer.analyze_text(test_text)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str({
                "status": "success",
                "test_text": test_text,
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "confidence": confidence
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str({
                "status": "error",
                "detail": str(e)
            }).encode()) 