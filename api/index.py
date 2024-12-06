import os
from app import app
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# This is required for Vercel
app.debug = False

# Ensure all environment variables are set
required_env_vars = ['OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

if __name__ == '__main__':
    app.run()
