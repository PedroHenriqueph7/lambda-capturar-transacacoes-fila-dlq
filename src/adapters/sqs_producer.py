import json
from typing import Any, Dict

class SqsProducer:
    def __init__(self, client: Any, queue_url: str):
        self._client = client
        self._queue_url = queue_url

    def publish(self, payload: Dict[str, Any]) -> str:
        response = self._client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(payload)
        )
        return response.get("MessageId")