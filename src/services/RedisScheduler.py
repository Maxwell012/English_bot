import asyncio
import json
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aioredis

from ..config import REDIS_HOST, REDIS_PORT
from LoggerService import LoggerService


def isoformat(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string in UTC."""
    return dt.astimezone(timezone.utc).isoformat()


def parse_isoformat(s: str) -> datetime:
    """Parse ISO 8601 string into a timezone-aware datetime."""
    return datetime.fromisoformat(s)


class RedisScheduler:
    """
    Scheduler for delayed Telegram messages using Redis sorted sets.

    Tasks are stored in a Redis sorted set named 'tasks', where the score is the
    UNIX timestamp (in seconds) when the message should be sent, and the value is
    a JSON-encoded dict containing the chat_id, text, and any additional args.
    """

    def __init__(self, redis_url: str = None, logger: LoggerService = LoggerService("redis_scheduler")) -> None:
        self.redis_url = redis_url if redis_url else f"redis://{REDIS_PORT}:{REDIS_PORT}"
        self.redis = None

        self.logger = logger

    async def connect(self):
        """Establish connection to Redis."""
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        self.logger.info("Connected to Redis at %s", self.redis_url)

    async def add_task(self, chat_id: int, text: str, send_at: datetime, **kwargs) -> None:
        """
        Schedule a new task.

        :param chat_id: Telegram chat ID
        :param text: Message text to send
        :param send_at: datetime when the message should be sent
        :param kwargs: Additional arguments to include in the payload
        """
        await self.__ensure_redis_connection()

        payload = {
            "chat_id": chat_id,
            "text": text,
            "send_at": isoformat(send_at),
            "args": kwargs,
        }
        timestamp = int(send_at.replace(tzinfo=timezone.utc).timestamp())
        await self.redis.zadd("tasks", {json.dumps(payload): timestamp})
        self.logger.info("Scheduled task for chat %s at %s", chat_id, payload["send_at"])

    async def fetch_due(self) -> list:
        """
        Fetch and remove all tasks whose scheduled time is <= now.

        :return: List of payload dicts for due tasks
        """
        await self.__ensure_redis_connection()

        now_ts = int(datetime.now(timezone.utc).timestamp())
        # Fetch due tasks
        raw_tasks = await self.redis.zrangebyscore("tasks", min=-1, max=now_ts)
        if not raw_tasks:
            return []

        # Remove them from the set
        await self.redis.zremrangebyscore("tasks", min=-1, max=now_ts)

        tasks = []
        for raw in raw_tasks:
            try:
                data = json.loads(raw)
                data["send_at"] = parse_isoformat(data["send_at"])
                tasks.append(data)
            except json.JSONDecodeError:
                await self.logger.error("Failed to decode task payload: %s", raw)
        return tasks


    async def __ensure_redis_connection(self) -> None:
        if self.redis is None:
            await self.connect()
