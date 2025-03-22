from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize Supabase client
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Get the latest analysis from the database
            result = supabase.table('market_analysis')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            if not result.data:
                raise Exception("No market analysis data found")
            
            latest_analysis = result.data[0]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "analysis": latest_analysis['analysis'],
                "timestamp": latest_analysis['timestamp'],
                "data_sources": latest_analysis['data_sources']
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "detail": str(e)
            }).encode()) 