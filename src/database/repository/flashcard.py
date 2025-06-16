from src.database.models import flashcard
from src.database.utils.SQLAlchemyRepository import SQLAlchemyRepository


class FlashcardRepository(SQLAlchemyRepository):
    model = flashcard
