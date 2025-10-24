from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import asyncio, json
from datetime import datetime
import redis.asyncio as redis
from typing import List
from starlette.websockets import WebSocketState
from .otel_config import instrument_app, create_span

SECRET_KEY = "this_is_a_fast_api_session_12"
ALGORITHM = "HS256"
REDIS_URL = "redis://redis:6379"
CHANNEL = "employees_events" #Pub/sub channel

app = FastAPI(title="Notification service", description="Real time notification via websocket events")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)

    asyncio.create_task(event_consumer())
    instrument_app(app)
    print("Notifictaion service has started with redis pub/sub")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(401, "Invalid token")
        return {"username":username}
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
@app.websocket("/ws/notification")
async def websocker_endpoint(websocket: WebSocket, current_user: dict = Depends(get_current_user)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message from {current_user['username']} : {data}")
    except WebSocketDisconnect:
        print(f"Client {current_user['username']} disconnected")
   

connected_clients: List[WebSocket] =[]

@app.websocket("/ws/chat")
async def chat_endpoint(websocket : WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try: 
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                if client.client_state == WebSocketState.CONNECTED:
                    await client.send_text(f"Chat: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def event_consumer():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(CHANNEL)
    async for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])

            for client in connected_clients:
                if client.client_state == WebSocketState.CONNECTED:
                    await client.send_json({"type": "notification", "event": event})
            print(f"Broadcasted event: {event}")