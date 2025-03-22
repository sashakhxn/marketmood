from http.server import BaseHTTPRequestHandler
from database import Database

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            database = Database()
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
                "fear_greed_index": analysis["fear_greed_index"],
                "market_sentiment": analysis["market_sentiment"],
                "risk_indicators": analysis["risk_indicators"],
                "date": analysis["date"],
                "last_updated": analysis["created_at"]
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str({"detail": str(e)}).encode()) 