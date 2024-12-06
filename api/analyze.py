from http.server import BaseHTTPRequestHandler
from text_analyzer import TextAnalyzer
import json

analyzer = TextAnalyzer()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        try:
            content = data.get('content', '')
            if not content:
                self._send_response({"error": "No content provided"}, status=400)
                return
                
            result = analyzer.analyze_text(content)
            self._send_response(result)
        except Exception as e:
            self._send_response({"error": str(e)}, status=500)
    
    def do_GET(self):
        self._send_response({"status": "API is running"})
    
    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
