from fastapi import FastAPI, HTTPException
from redis_utils import RedisStream
import os

app = FastAPI()

# Initialize RedisStream instance with Redis connection details
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
stream_name = "notification_stream"
redis_client = RedisStream(redis_host, redis_port, stream_name)

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
