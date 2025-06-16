from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description=f'👤 Войти'
        ),
        BotCommand(
            command='settings',
            description=f'⚙️ Настройки'
        ),
        BotCommand(
            command='support',
            description=f'✍ Помощь'
        ),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
