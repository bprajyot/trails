from __future__ import annotations

import json
import os
from typing import Any, Dict

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = "queue:submissions"


class SubmissionQueue:
    def __init__(self, redis_url: str = REDIS_URL) -> None:
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def enqueue(self, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload)
        self.client.rpush(QUEUE_KEY, data)