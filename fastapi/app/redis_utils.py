import redis
from typing import List, Dict

class RedisStream:
    def __init__(self, host: str, port: int, stream_name: str):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.stream_name = stream_name

    def publish_message(self, message: Dict[str, str]) -> str:
        message_id = self.client.xadd(self.stream_name, message)
        return message_id

    def consume_messages(self, count: int = 5) -> List[Dict[str, str]]:
        messages = self.client.xread({self.stream_name: "0"}, count=count, block=0)
        formatted_messages = [
            {"id": msg[0], "message": msg[1]} for _, msgs in messages for msg in msgs
        ]
        return formatted_messages

    def blocking_read_from_stream(self, last_id: str) -> List[Dict[str, str]]:
        messages = self.client.xread({self.stream_name: last_id}, block=1000)
        formatted_messages = [
            {"id": msg[0], "message": msg[1]} for _, msgs in messages for msg in msgs
        ]
        return formatted_messages
