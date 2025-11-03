from flask import Flask, jsonify
import pymongo
import os, time
from concurrent.futures import ThreadPoolExecutor
import requests

app = Flask(__name__)

MONGO_URL = os.getenv('MONGO_URL')
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()  # uses the DB from the URI
counters = db['counters']

@app.route('/write', methods=['POST'])
def write():
    counters.update_one({"_id": "global"}, {"$inc": {'value': 1}}, upsert=True)
    return jsonify({"status": "written", "time": time.time()})

@app.route('/read')
def read():
    doc = counters.find_one({'_id': 'global'})
    return jsonify({'value': doc['value'] if doc else 0, 'time': time.time()})

@app.route('/load_test')
def load_test():
    def worker():
        time.sleep(0.01)
        return requests.post('http://localhost:5001/write').json()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(10)]
        results = [f.result() for f in futures]

    time.sleep(0.1)
    read_res = requests.get('http://localhost:5001/read').json()
    return jsonify({"writes": len(results), 'final_value': read_res['value']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
