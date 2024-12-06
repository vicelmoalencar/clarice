import os
import sys
from http.server import BaseHTTPRequestHandler
from app import app
import nltk

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Download NLTK data to temp directory
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    nltk.data.path.append(nltk_data_dir)
    
    logger.info("Downloading NLTK data...")
    nltk.download('punkt', download_dir=nltk_data_dir)
    nltk.download('stopwords', download_dir=nltk_data_dir)
    nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
    logger.info("NLTK data downloaded successfully")
except Exception as e:
    logger.error(f"Error downloading NLTK data: {str(e)}")
    raise

# This is required for Vercel
app.debug = False

# Ensure all environment variables are set
required_env_vars = ['OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

logger.info("All environment variables are set")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Serve index.html
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Replace Flask template variables with actual paths
            content = content.replace("{{ url_for('static', filename='css/style.css') }}", "/static/css/style.css")
            content = content.replace("{{ url_for('static', filename='js/main.js') }}", "/static/js/main.js")
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == '__main__':
    app.run()
