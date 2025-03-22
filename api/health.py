from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str({
            "status": "healthy",
            "services": {
                "api": "operational",
                "database": "operational",
                "reddit_api": "operational",
                "sentiment_analysis": "operational"
            }
        }).encode()) 