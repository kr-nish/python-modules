from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os, time
from concurrent.futures import ThreadPoolExecutor
import requests
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
DB_URL = os.getenv('DB_URL')

def get_conn():
    return psycopg2.connect(DB_URL)

@app.route("/write", methods=['POST'])
def write():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS counters (
                    id TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                );
            """)
            cur.execute("""
                INSERT INTO counters (id, value)
                VALUES ('global', 1)
                ON CONFLICT (id) DO UPDATE
                SET value = counters.value + 1;
            """)
            conn.commit()
            return jsonify({'status': "written", "time": time.time()})

@app.route("/read")
def read():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS counters (
                    id TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                );
            """)
            cur.execute("SELECT value FROM counters WHERE id = 'global';")
            row = cur.fetchone()
            return jsonify({'value': row['value'] if row else 0, 'time': time.time()})

@app.route('/load_test')
def load_test():
    def worker():
        time.sleep(0.01)
        return requests.post('http://localhost:5000/write').json()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(10)]
        results = [f.result() for f in futures]

    time.sleep(0.1)
    read_res = requests.get('http://localhost:5000/read').json()
    return jsonify({"writes": len(results), 'final_value': read_res['value']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)