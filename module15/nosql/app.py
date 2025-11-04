from flask import Flask, jsonify 
from google.cloud import firestore
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import time
import requests

load_dotenv()
app = Flask(__name__)
PROJECT_ID = os.getenv('PROJECT_ID')
DB_NAME = os.getenv("FIRESTORE_DB_NAME", "(default)")  
db = firestore.Client(project=PROJECT_ID, database=DB_NAME)
doc_ref =  db.collection('counter').document('global')


@app.route('/init', methods=["POST"])
def init():
    doc_ref.set({'value':0}, merge=True)
    return jsonify({'status':'initialized'})

@app.route('/write', methods=['POST'])
def write():
    doc_ref.update({'value': firestore.Increment(1)})
    return jsonify({'status': 'written', 'time': time.time()})

@app.route("/read")
def read():
    doc = doc_ref.get()
    value = doc.to_dict().get('value', 0) if doc.exists else 0
    return jsonify({'value': value, 'time': time.time()})
    
@app.route('/load_test/<int:count>')
def load_test(count):
    def worker(i):
        time.sleep(0.01)
        requests.post('http://localhost:6000/write')

    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        [executor.submit(worker, i) for i in range(count)]
    time.sleep(0.2)
    duration = time.time() - start
    read_val = read().json['value']
    return jsonify({'writes': count, 'final_value' : read_val, 'duration_sec': duration})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)