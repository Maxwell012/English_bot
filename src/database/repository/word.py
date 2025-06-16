from src.database.models import word
from src.database.utils.SQLAlchemyRepository import SQLAlchemyRepository


class WordRepository(SQLAlchemyRepository):
    model = word
