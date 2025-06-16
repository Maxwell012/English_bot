from aiogram.fsm.state import State, StatesGroup
from typing import Optional

from database.schemas.user import UserSchemaFromDB
from src.database.schemas import EnglishLevel


def get_state_object(state_str: str, state_group: type[StatesGroup], handle_errors: bool = False) -> Optional[State]:
    """
    Converts a string state representation into a State object for the given StatesGroup class.

    :param state_str: The string representation of the state (e.g., "FirstStartState:LANGUAGE" or "LANGUAGE").
    :param state_group: The class of the StatesGroup to which the state belongs.
    :param handle_errors: Whether to handle errors or not.
    :return: The corresponding State object if found, otherwise None.
    """
    # states = list(state_group.__states__)
    # return states[state_str]
    state_name = state_str.split(":")[-1]  # Extract only the state name (in case it's prefixed with the group name)
    state = getattr(state_group, state_name, None) if handle_errors else getattr(state_group, state_name)
    return state

def get_next_level(current_level: EnglishLevel) -> Optional[EnglishLevel]:
    match current_level:
        case EnglishLevel.A1:
            return EnglishLevel.A2
        case EnglishLevel.A2:
            return EnglishLevel.B1
        case EnglishLevel.B1:
            return EnglishLevel.B2
        case EnglishLevel.B2:
            return EnglishLevel.C1
        case EnglishLevel.C1:
            return None


def is_profile_complete(user: UserSchemaFromDB) -> bool:
    if (
        not user.language or
        not user.english_level or
        not user.notifications_per_day
    ):
        return False
    return True