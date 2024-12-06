from flask import Flask, render_template, request, jsonify
from text_analyzer import TextAnalyzer
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
analyzer = TextAnalyzer()

# Garante que o diretório de dados existe
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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
    content = request.json.get('content', '')
    result = analyzer.analyze_text(content)
    return jsonify(result)

@app.route('/save', methods=['POST'])
def save():
    try:
        text_data = request.json
        text_data['id'] = str(uuid.uuid4())
        
        texts = load_saved_texts()
        texts.append(text_data)
        save_texts_to_file(texts)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_saved_texts', methods=['GET'])
def get_saved_texts():
    try:
        texts = load_saved_texts()
        return jsonify(texts)
    except Exception as e:
        return jsonify([])

@app.route('/delete_text/<text_id>', methods=['DELETE'])
def delete_text(text_id):
    try:
        texts = load_saved_texts()
        texts = [text for text in texts if text['id'] != text_id]
        save_texts_to_file(texts)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
