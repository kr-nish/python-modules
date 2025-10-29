from fastapi import FastAPI
import os

app = FastAPI(title="Simple Fast API for Docker and CR")

APP_NAME = os.getenv("APP_NAME", "FastAPI APP")

@app.get("/health")
def health_check():
    return {
        "status" : "healthy",
        "service" : APP_NAME,
        "timestamp" :"2025-10-27T00:00:00Z"
    }

@app.get("/hello/{name}")
def greet(name:str):
    return {
        "message" : f"Hello, {name}! Welcome to {APP_NAME}",
        "version": "1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)