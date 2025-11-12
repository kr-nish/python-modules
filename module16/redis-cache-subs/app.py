from fastapi import FastAPI
from google.cloud import pubsub_v1
import redis
import os
from dotenv import load_dotenv
import asyncio
import logging
import json

load_dotenv()
app = FastAPI()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = 'new_notes'
SUB_ID = 'cache-sub'
REDIS_URL = os.getenv("REDIS_URL")
TTL = 300
logging.basicConfig(level=logging.INFO)

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
r = redis.from_url(REDIS_URL)
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
subscription_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)


@app.on_event("startup")
async def startup():
    while True:
        try:
            response = subscriber.pull(request={"subscription": subscription_path, "max_messages": 5}, timeout=30)
            for msg in response.received_messages:
                data = json.loads(msg.message.data.decode('utf-8'))
                key = f"note:{data['userId']}:{data['title']}"
                r.set(key, json.dumps(data), ex=TTL)
                logging.info(f"Cached {key} with TTL {TTL}s (LRU eviction active)")
                subscriber.acknowledge(request={"subscription":subscription_path, "ack_ids":[msg.ack_id]})
        except Exception as e:
            logging.error(f"Cache sub error: {e}")
        await asyncio.sleep(5)

app.get("/cache/{user_id}/{title}")
def get_cached(user_id: str, title: str):
    key= f"note: {user_id}:{title}"
    cached = r.get(key)
    if cached:
        return {"cached" : json.loads(cached), "hit":True}
    return {"error" : "cache miss", "hit": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)