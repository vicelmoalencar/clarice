from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Editor de Texto Inteligente</title>
            <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                #editor { height: 300px; }
            </style>
        </head>
        <body>
            <h1>Editor de Texto Inteligente</h1>
            <div id="editor"></div>
            <button onclick="analyzeText()">Analisar Texto</button>
            
            <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
            <script>
                var quill = new Quill('#editor', {
                    theme: 'snow'
                });
                
                function analyzeText() {
                    var text = quill.getText();
                    fetch('/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({content: text})
                    })
                    .then(response => response.json())
                    .then(data => alert(JSON.stringify(data, null, 2)))
                    .catch(error => console.error('Error:', error));
                }
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode())
