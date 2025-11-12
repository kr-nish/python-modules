from fastapi import FastAPI, BackgroundTasks
from google.cloud import pubsub_v1
from google.cloud import firestore
import os
from dotenv import load_dotenv
import asyncio
import logging
import uuid

load_dotenv()
app = FastAPI()
PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_ID = 'new-notes'
SUB_ID = 'notes-sub'
logging.basicConfig(level=logging.INFO)

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
db = firestore.Client(project=PROJECT_ID)
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
subscription_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)

@app.on_event("startup")
async def startup_event():
    
    try:
        publisher.create_topic(request={"name": topic_path})
    except:
        pass
    try:
        subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})
    except:
        pass
   
    asyncio.create_task(pull_loop())

async def pull_loop():
    while True:
        try:
            response = subscriber.pull(
                request={"subscription": subscription_path, "max_messages": 10},
                timeout=30.0
            )
            for received_message in response.received_messages:
                message = received_message.message
                data = eval(message.data.decode('utf-8'))  
                trace_id = message.attributes.get('trace_id', 'unknown')
                logging.info(f"Subscriber received message: {data}, Trace ID: {trace_id}")
                
               
                db.collection('processed_notes').add({
                    'title': data['title'],
                    'userId': data['userId'],
                    'processed_at': firestore.SERVER_TIMESTAMP,
                    'trace_id': trace_id  
                })
                
                # ACK
                subscriber.acknowledge(
                    request={"subscription": subscription_path, "ack_ids": [received_message.ack_id]}
                )
                logging.info(f"Processed and ACKed with Trace ID: {trace_id}")
        except Exception as e:
            logging.error(f"Pull error: {e}")
        await asyncio.sleep(5)  

@app.get("/")
def health():
    return {"status": "Subscriber running", "subscription": SUB_ID}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)