from http.server import BaseHTTPRequestHandler
from daily_processor import process_daily_data
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Process the daily data
            process_daily_data()
            
            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Daily data processing completed"
            }).encode())
            
        except Exception as e:
            # Return error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": str(e)
            }).encode()) 