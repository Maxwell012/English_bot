from src.database.models import user
from src.database.utils.SQLAlchemyRepository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = user
