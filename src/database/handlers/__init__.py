from typing import Optional, Any, Coroutine, Union, List

from src.database.exceptions import NotFoundError
from src.database.schemas.base_schemas import Base

from .user import UserHandler
from .word import WordHandler
from .flashcard import FlashcardHandler

class Handlers:
    user = UserHandler()
    word = WordHandler()
    flashcard = FlashcardHandler()

    @staticmethod
    async def handle_not_found_error(coro: Coroutine[Any, Any, Any], return_if_err: Any = None) -> Optional[Union[Base | List[Base]]]:
        """
        Handle NotFoundError and return None instead of raising it.
        """
        try:
            return await coro
        except NotFoundError:
            return return_if_err