from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
app = Flask(__name__)
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = 'new-notes'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.route("/notes", methods=['POST'])
def publish_note():
    data = request.json
    if not data.get('title'):
        return jsonify({"error":"TITLE required"}), 400
    message = {
        'title': data['title'],
        'content': data.get('content', ''),
        'userId': data.get('userId', 'anonymous'),
        'timestamp':os.getenv('TIMESTAMP', 'now')
    }
    trace_id = str(uuid.uuid4())
    future = publisher.publish(topic_path, str(message).encode('utf-8'), trace_id=trace_id)
    future.result()
    return jsonify({'status':'published', "message_id": future.result(), 'trace_id': trace_id})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)

