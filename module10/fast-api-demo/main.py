from fastapi import FastAPI, HTTPException, Depends, Query, status
from models import Item, OrderCreate, OrderResponse
import random
from typing import Dict, Annotated


app = FastAPI(title="Fast API with DI and Validation")

#Database session stimulation
def get_db():
    db = {"connection":"Database connected","session_id":random.randint(1000,9999)}
    print(f"[DB] Opening Session {db['session_id']}")
    try:
        yield db
    finally:
        db["connection"]="closed"
        print(f"[DB] Closing Session {db['session_id']}")

# Simulated Current user authentication

def get_current_user(token: str = Query(..., description="Pass your API key")):
    if token != "secretToken123":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
    return {"username":"Nishant", "role":"admin"}

@app.get("/")
def read_root():
    return {"message":"Welcome to Fast API !!!"}

@app.get("/hell0/{name}")
def read_name(name: str):
    return {"message":f"hello and Welcome, {name}"}

@app.post("/items/")
def create_item(item: Item):
    total_price = item.price + (item.tax or 0)
    return {"item_name" : item.name, "total_price": total_price}

@app.post("/orders/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Dict = Depends(get_db),
    user: Dict = Depends(get_current_user)):

    print(f"[Auth] User '{user['username']}' creating new order...")
    
    total_amount = sum(line.quantity + line.unit_price for line in order.items)
    items_count = sum(line.quantity for line in order.items)

    if total_amount <= 0: 
        raise HTTPException(status_code=400, detail="Total amount must be positive")
    
    resp = OrderResponse(
        order_id=order.order_id,
        customer_id=order.customer.id,
        total_amount=round(total_amount, 2),
        items_count=items_count
    )
    return resp

@app.get("/users/")
def get_users(db: Dict= Depends(get_db)):
    return {"db_status": db["connection"], "session_id": db["session_id"]}

# uvicorn main:app --reload