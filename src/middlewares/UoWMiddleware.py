from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.database.utils.UnitOfWork import UnitOfWork


class UoWMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        self.uow = UnitOfWork()
        async with self.uow:
            data["uow"] = self.uow
            result = await handler(event, data)
            await self.uow.commit()
        return result
