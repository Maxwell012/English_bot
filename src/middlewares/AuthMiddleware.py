from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Optional

from handlers.classes import user_profile_fsm
from src.database.handlers import Handlers
from src.database.schemas import UserSchemaFromDB
from src.handlers.user import start
from utils.utils import is_profile_complete


class AuthMiddleware(BaseMiddleware):
    allowed_commands = {"/start", "/support"}
    allowed_callbacks_prefixes = {}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: [Message, CallbackQuery],
            data: Dict[str, Any]
    ):
        # commands not requiring registration
        if isinstance(event, Message):
            command = event.text.strip()
            if command in self.allowed_commands:
                return await handler(event, data)

        # callbacks not requiring registration
        if isinstance(event, CallbackQuery) and event.data:
            if any(event.data.startswith(prefix) for prefix in self.allowed_callbacks_prefixes):
                return await handler(event, data)

        uow = data.get("uow")
        telegram_id = event.from_user.id
        not_found_err_handler = Handlers.handle_not_found_error
        user: Optional[UserSchemaFromDB] = await not_found_err_handler(Handlers.user.get_one(uow, id=telegram_id))
        message = event if isinstance(event, Message) else event.message
        # if user does not exist -> run start command
        if not user: return await start(message, state=data["state"], uow=uow)

        data["user"] = user

        # if user did not complete his profile, there are 2 options:
        # 1) let pass specific callback queries related to profile completion (e.g., language_, level_, notification_)
        # 2) call fill_profile method to complete his profile
        if not is_profile_complete(user):
            if isinstance(event, CallbackQuery) and event.data:
                callbacks_prefixes = {"language_", "level_", "notification_"}
                if any(event.data.startswith(prefix) for prefix in callbacks_prefixes):
                    return await handler(event, data)

            return await user_profile_fsm.fill_profile(message=message, state=data["state"], user=user)

        return await handler(event, data)
