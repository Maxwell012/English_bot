from datetime import datetime
from pydantic import PositiveInt
from typing import Optional

from . import WordSchemaOut
from .base_schemas import (
    SchemaOut,
    SchemaToDB,
    SchemaFromDB,
    SchemaUpdate
)


class FlashcardSchemaOut(SchemaOut):
    id: PositiveInt
    word: WordSchemaOut
    interval: int
    hardness: float
    repetitions: int
    next_review: datetime
    learned: bool

class FlashcardSchemaFromDB(SchemaFromDB, FlashcardSchemaOut):
    id: PositiveInt
    user_id: PositiveInt
    word_id: PositiveInt
    interval: int
    hardness: float
    repetitions: int
    next_review: datetime
    learned: bool
    created_at: datetime
    updated_at: datetime

class FlashcardSchemaToDB(SchemaToDB):
    user_id: PositiveInt
    word_id: PositiveInt
    next_review: datetime

class FlashcardSchemaUpdate(SchemaUpdate):
    interval: Optional[int] = None
    hardness: Optional[float] = None
    repetitions: Optional[int] = None
    next_review: Optional[datetime] = None
    learned: Optional[bool] = None
