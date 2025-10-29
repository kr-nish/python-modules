from flask import Flask, request, jsonify 
import json, os 
from datetime import datetime

app = Flask(__name__)

DATA_FILE = os.getenv('NOTE_STORAGE_PATH','/app/data') + '/notes.json'

def load_notes():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip()
            if not content:  
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
        return []

def save_notes(notes):
    with open(DATA_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status" :"healthy", "service" :"Notes API"})

@app.route('/notes', methods=['GET'])
def get_notes():
    notes = load_notes()
    return jsonify(notes)

@app.route("/notes", methods=['POST'])
def add_note():
    content = request.json.get('content')
    if not content:
        return jsonify({"Error" :"Content required"}), 400
    notes  = load_notes()
    notes.append({"content" : content, "timestamp": datetime.now().isoformat()})
    save_notes(notes)
    return jsonify({"message" : "Note added"}), 201

if __name__ == '__main__':
    os.makedirs('/app/data', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)