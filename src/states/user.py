from aiogram.fsm.state import StatesGroup, State


class UserProfileState(StatesGroup):
    LANGUAGE = State()
    ENGLISH_LEVEL = State()
    NOTIFICATION = State()
