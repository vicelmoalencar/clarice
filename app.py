from flask import Flask, render_template, request, jsonify
from text_analyzer import TextAnalyzer
import json
import os
from datetime import datetime
import uuid
import tempfile

app = Flask(__name__)
analyzer = TextAnalyzer()

# Usando diretório temporário para ambiente serverless
DATA_DIR = tempfile.gettempdir()
TEXTS_FILE = os.path.join(DATA_DIR, 'saved_texts.json')

def load_saved_texts():
    if os.path.exists(TEXTS_FILE):
        with open(TEXTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_texts_to_file(texts):
    with open(TEXTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        content = request.json.get('content', '')
        if not content:
            return jsonify({"error": "No content provided"}), 400
        result = analyzer.analyze_text(content)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save', methods=['POST'])
def save():
    try:
        text_data = request.json
        if not text_data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        text_data['id'] = str(uuid.uuid4())
        texts = load_saved_texts()
        texts.append(text_data)
        save_texts_to_file(texts)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_saved_texts', methods=['GET'])
def get_saved_texts():
    try:
        texts = load_saved_texts()
        return jsonify(texts)
    except Exception as e:
        return jsonify([])

@app.route('/delete/<text_id>', methods=['DELETE'])
def delete_text(text_id):
    try:
        texts = load_saved_texts()
        texts = [t for t in texts if t['id'] != text_id]
        save_texts_to_file(texts)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
