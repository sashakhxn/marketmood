from http.server import BaseHTTPRequestHandler
from database import Database
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get posts and comments from the last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            database = Database()
            posts = database.get_posts_by_time_range(start_time, end_time)
            comments = database.get_comments_by_time_range(start_time, end_time)
            
            # Get the latest analysis for word frequencies
            analysis = database.get_latest_market_analysis()
            
            if not analysis:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str({
                    "detail": "No market analysis available. Please try again later."
                }).encode())
                return
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str({
                "word_frequencies": analysis["word_frequencies"],
                "timestamp": analysis["created_at"]
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str({"detail": str(e)}).encode()) 