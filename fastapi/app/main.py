from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.background import BackgroundTasks
from redis_utils import RedisStream
import os
import asyncio

app = FastAPI()

# Initialize RedisStream instance with Redis connection details
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
stream_name = "notification_stream"
redis_client = RedisStream(redis_host, redis_port, stream_name)

connected_clients = []

@app.post("/publish/")
async def publish_message(message: str):
    try:
        message_id = redis_client.publish_message({"message": message})
        return {"status": "Message published", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing message: {e}")

@app.get("/consume/")
async def consume_messages(count: int = 5):
    try:
        messages = redis_client.consume_messages(count)
        return {"status": "Messages consumed", "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consuming messages: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # keep the connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Background task to read from Redis Stream and send messages to WebSocket clients
async def notify_clients():
    last_id = "0"
    while True:
        new_messages = redis_client.blocking_read_from_stream(last_id)
        for message in new_messages:
            for client in connected_clients:
                await client.send_json(message)
        if new_messages:
            last_id = new_messages[-1]["id"]
        await asyncio.sleep(1)  # poll interval

# Run the background task when the app starts
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(notify_clients())
