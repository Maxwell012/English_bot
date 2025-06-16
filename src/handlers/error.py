from aiogram import Dispatcher
from aiogram.types import ErrorEvent
import html

from src.dependencies import logger
from src.config import TELEGRAM_ADMIN_IDS


async def error_handler(event: ErrorEvent):
    await logger.critical(f"Critical error caused by {event.exception}", exc_info=True)
    message = event.update.message
    if message:
        if message.from_user:
            if message.from_user.id in TELEGRAM_ADMIN_IDS:
                error_message = html.escape(str(event.exception.args))
                formatted_message = f"<code>{error_message}</code>"
                await message.answer(f"Произошла ошибка: {formatted_message}")
            else:
                await message.answer(
                    f"Произошла непредвиденная ошибка!\n"
                    f"Мы уже работает над ней."
                )


def register_handlers(dp: Dispatcher):
    dp.error.register(error_handler)
