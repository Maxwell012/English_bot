from aiogram import Bot, Dispatcher

from config import TOKEN_BOT, REDIS_PORT, REDIS_HOST
from services.RedisScheduler import RedisScheduler
from services.TaskDispatcher import TaskDispatcher


REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(bot=bot)

# Instantiate scheduler and dispatcher
scheduler = RedisScheduler(REDIS_URL)
dispatcher = TaskDispatcher(bot, scheduler, interval=60)
dispatcher.start(dp)
