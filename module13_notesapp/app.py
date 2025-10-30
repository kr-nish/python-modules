from flask import Flask, request, jsonify 
import json, os 
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    content = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)

#env and config
DB_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@db:5432/notesdb')
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def load_secret():
    secret_path = '/run/secrets/notes_encrypt.key'
    return open(secret_path, 'r').read().strip() if os.path.exists(secret_path) else None

ENCRYPT_KEY = load_secret()

import base64
def encrypt_context(content: str) -> str:
    if ENCRYPT_KEY:
        return base64.b64encode(content.encode()).decode()
    return content

def decrypt_content(encrypted: str) -> str:
    if ENCRYPT_KEY:
        return base64.b64decode(encrypted.encode()).decode()
    return encrypted



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.route('/health', methods=['GET'])
def health():
    try:
        with SessionLocal() as db:
            count = db.execute(text("SELECT COUNT(*) from notes")).scalar()
        return jsonify({"status": "healthy", "notes_count": count})
    except Exception as e:
        return jsonify({"status" :"not ready unhealthy", "error" : str(e)}), 503

@app.route('/notes', methods=['GET'])
def get_notes():
    with SessionLocal() as db:
        notes = db.query(Note).all()
        return jsonify({"content": decrypt_content(n.content), "timestamp": n.timestamp.isoformat()} for n in notes)

@app.route("/notes", methods=['POST'])
def add_note():
    if not request.is_json:
        return jsonify({"error":"JSON required"}), 400
    content = request.json.get('content')
    if not content:
        return jsonify({"error" :"Content required"}), 400
    with SessionLocal() as db:
        encrypted = encrypt_context(content)
        note = Note(content=encrypted)
        db.add(note)
        db.commit()
        return jsonify({"message":"Note added", "id": note.id}), 201

if __name__ == '__main__':
    print(f"DB_URL : {DB_URL}, Key: {'Loaded' if ENCRYPT_KEY else 'None'}")
    app.run(host='0.0.0.0', port=5000, debug=True)