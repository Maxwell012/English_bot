from logging import Logger
from typing import Optional

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from src.database.handlers import Handlers
from src.database.schemas import UserSchemaFromDB, Languages, UserSchemaUpdate, EnglishLevel
from src.database.utils.UnitOfWork import UnitOfWork
from src.keyboards.inline import get_level_inline, get_notification_frequency_inline, get_language_inline
from src.messages.user import choose_language, language_setting, choose_level, \
    choose_notification_frequency, level_setting, notification_setting, get_start_message
from src.states.user import UserProfileState


class UserProfileFSM:
    """
    Four main steps:
        - add language into DB
        - add level into DB
        - add notification in DB
    """

    # MESSAGES = {
    #     UserProfileState.LANGUAGE: {"text": choose_language, "reply_markup": get_language_inline},
    #     UserProfileState.ENGLISH_LEVEL: {"text": choose_level, "reply_markup": get_level_inline},
    #     UserProfileState.NOTIFICATION: {"text": choose_notification_frequency, "reply_markup": get_notification_frequency_inline}
    # }

    def __init__(self, logger: Logger, last_message: str = None, last_message_reply_markup: InlineKeyboardMarkup = None) -> None:
        self.logger = logger

    @staticmethod
    async def add_last_message(state: FSMContext, last_message: str, last_message_reply_markup: InlineKeyboardMarkup) -> None:
        await state.update_data({
            "last_message": last_message,
            "last_message_reply_markup": last_message_reply_markup
        })

    async def fill_profile(self, message: Message, state: FSMContext, user: UserSchemaFromDB) -> None:
        current_state = await state.get_state() if await state.get_state() else UserProfileState.LANGUAGE

        lan = user.language if user.language else Languages.English
        if current_state == UserProfileState.LANGUAGE:
            text = choose_language(lan)
            skip_button = True if user.language else False
            reply_markup = get_language_inline(skip_button)
        elif current_state == UserProfileState.ENGLISH_LEVEL:
            text = choose_level(lan)
            skip_button = True if user.english_level else False
            reply_markup = get_level_inline(lan, skip_button)
        else:
            text = choose_notification_frequency(lan)
            skip_button = True if user.notifications_per_day else False
            reply_markup = get_notification_frequency_inline(lan, skip_button)
        await message.answer(text, reply_markup=reply_markup)
        await state.update_data()
        await state.set_state(current_state)

    @staticmethod
    async def choose_language(message: Message, state: FSMContext, user: UserSchemaFromDB) -> None:
        language = message.from_user.language_code
        language = Languages(language) if language in Languages._value2member_map_ else Languages.ENGLISH
        skip_button = True if user.language else False
        await message.answer(choose_language(language), reply_markup=get_language_inline(skip_button))
        await state.set_state(UserProfileState.LANGUAGE)

    async def get_language(self, callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
        async def __edit_message_and_answer(user_language: Languages):
            await callback.message.edit_text(language_setting(user_language), reply_markup=None)
            skip_button = True if user.english_level else False
            await callback.message.answer(choose_level(user_language), reply_markup=get_level_inline(user_language, skip_button))
            await self.__handle_next_state(state)

        action = callback.data.split("_")[1]
        if action == "skip":
            await __edit_message_and_answer(user.language)
            return
        
        new_language = Languages(action)
        update_data = UserSchemaUpdate(language=new_language)
        await Handlers.user.update_one(uow, update_data, id=user.id)

        await __edit_message_and_answer(new_language)

    async def get_level(self, callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
        async def __edit_message_and_answer(user_english_level: EnglishLevel):
            await callback.message.edit_text(level_setting(user.language, user_english_level), reply_markup=None)
            skip_button = True if user.notifications_per_day else False
            await callback.message.answer(choose_notification_frequency(len),
                                          reply_markup=get_notification_frequency_inline(user.language, skip_button))
            await self.__handle_next_state(state)

        value = callback.data.split("_")[1]
        if value == "back":
            await callback.message.edit_text(choose_language(user.language), reply_markup=get_language_inline(True))
            await self.__handle_previous_state(state)
        elif value == "skip":
            await __edit_message_and_answer(user.english_level)
        else:
            level = EnglishLevel(value)
            update_data = UserSchemaUpdate(english_level=level)
            await Handlers.user.update_one(uow, update_data, id=user.id)

            await __edit_message_and_answer(level)

    async def get_notification_frequency(self, callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
        async def __edit_message_and_answer(user_notifications_per_day: int):
            await callback.message.edit_text(notification_setting(user.language, user_notifications_per_day),
                                reply_markup=None)
            # Sending the last message
            data = await state.get_data()
            await callback.message.answer(data.get("last_message"), reply_markup=data.get("last_message_reply_markup"))
            await self.__handle_next_state(state)

        value = callback.data.split("_")[1]
        if value == "back":
            await callback.message.edit_text(choose_level(user.language), reply_markup=get_level_inline(user.language, True))
            await self.__handle_previous_state(state)
        elif value == "skip":
            await __edit_message_and_answer(user.notifications_per_day)
        else:
            notifications_per_day = int(value)
            update_data = UserSchemaUpdate(notifications_per_day=notifications_per_day)
            await Handlers.user.update_one(uow, update_data, id=user.id)

            await __edit_message_and_answer(notifications_per_day)

    @staticmethod
    async def __send_last_message(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        await message.answer(data.get("last_message"), reply_markup=data.get("last_message_reply_markup"))

    async def __handle_next_state(self, state: FSMContext) -> None:
        next_state = await self.__get_next_state(state)
        self.logger.debug(next_state)
        if not next_state: return await state.clear()
        await state.set_state(next_state.state)

    @staticmethod
    async def __get_next_state(state: FSMContext) -> Optional[State]:
        states = list(UserProfileState.__states__)
        current_state_str_idx = states.index(await state.get_state())

        # if the current state is the last one, then return None
        if current_state_str_idx + 1 == len(states): return

        next_state = states[current_state_str_idx + 1]
        return next_state

    async def __handle_previous_state(self, state: FSMContext) -> None:
        previous_state = await self.__get_previous_state(state)
        self.logger.debug(previous_state)
        if not previous_state: raise ValueError("Attempt to get the previous state by being in the first one")
        await state.set_state(previous_state)

    @staticmethod
    async def __get_previous_state(state: FSMContext) -> Optional[State]:
        states = list(UserProfileState.__states__)
        current_state_str_idx = states.index(await state.get_state())

        # if the current state is the first one, then return None
        if current_state_str_idx == 0: return

        previous_state = states[current_state_str_idx - 1]
        return previous_state

