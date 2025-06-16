import sys
import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd()))

from config import (
    TOKEN_BOT,
    TELEGRAM_BOT_HOST,
    TELEGRAM_BOT_PORT,
    WEBHOOK_PATH,
    TELEGRAM_ADMIN_IDS
)
from src.services.Ngrok import Ngrok
from src.middlewares.UoWMiddleware import UoWMiddleware
from src.middlewares.AntiFloodMiddleware import AntiFloodMiddleware
from src.middlewares.AuthMiddleware import AuthMiddleware
from src.utils.commands import set_commands
from src.handlers import *
from src.dependencies import logger


app = web.Application()


async def on_startup(bot: Bot) -> None:
    # set webhooks
    ngrok = Ngrok()
    urls = await ngrok.get_public_urls()
    if not urls:
        await logger.error("No ngrok public urls found. Double check your API KEY and make sure that ngrok tunnel was run.")
        raise ValueError("No ngrok public urls found. Double check your API KEY and make sure that ngrok tunnel was run.")

    base_webhook_url = urls[0]
    await bot.set_webhook(f'{base_webhook_url}{WEBHOOK_PATH}', drop_pending_updates=True)

    # set commands
    await set_commands(bot=bot)

    # connect to a broker
    # await broker_producer.connect()


async def last_message(bot: Bot) -> None:
    for _id in TELEGRAM_ADMIN_IDS:
        try:
            await bot.send_message(chat_id=_id, text="<b>BOT STOPPED</b>")
        except Exception:
            pass


async def on_shutdown(bot: Bot) -> None:
    await last_message(bot)
    await bot.session.close()


def main():
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TOKEN_BOT, default=default)
    dp = Dispatcher(bot=bot)
    dp.startup.register(on_startup)

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # dp.message.outer_middleware(AntiFloodMiddleware())
    # dp.callback_query.outer_middleware(AntiFloodMiddleware())
    dp.message.outer_middleware(UoWMiddleware())
    dp.callback_query.outer_middleware(UoWMiddleware())
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())

    admin_handlers(dp)
    user_handlers(dp)
    error_handlers(dp)

    try:
        web.run_app(app, host=TELEGRAM_BOT_HOST, port=TELEGRAM_BOT_PORT)
    except Exception as ex:
        asyncio.run(logger.critical(f"Exception: {ex}", exc_info=True))
    finally:
        asyncio.run(on_shutdown(bot))

if __name__ == '__main__':
    main()
