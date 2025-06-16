import asyncio
import json
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aioredis

from RedisScheduler import RedisScheduler
from src.services.LoggerService import LoggerService


class TaskDispatcher:
    """
    Periodically fetch due tasks from RedisScheduler and dispatch them via Telegram Bot.
    """

    def __init__(
            self,
            bot: Bot,
            scheduler: RedisScheduler,
            logger = LoggerService("task_dispatcher"),
            interval: int = 60
    ):
        self.bot = bot
        self.scheduler = scheduler
        self.interval = interval
        self._task = None
        self.logger = logger

    async def _dispatcher_loop(self):
        """Background loop: fetch due tasks and send messages."""
        await self.scheduler.connect()
        while True:
            try:
                due_tasks = await self.scheduler.fetch_due()
                for task in due_tasks:
                    chat_id = task["chat_id"]
                    text = task["text"]
                    args = task.get("args", {})
                    # Send the message
                    await self.bot.send_message(chat_id, text, **args)
                    self.logger.info("Sent scheduled message to %s", chat_id)
            except Exception as e:
                await self.logger.error("Error in dispatcher loop: %s", e)

            await asyncio.sleep(self.interval)

    def start(self, dp: Dispatcher):
        """Register the dispatcher start handler to launch the loop."""
        async def on_startup(_):
            self._task = asyncio.create_task(self._dispatcher_loop())

        dp.startup.register(on_startup)