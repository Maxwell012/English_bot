from datetime import datetime
from pydantic import PositiveInt, constr
from typing import Optional

from .base_schemas import (
    SchemaOut,
    SchemaToDB,
    SchemaFromDB,
    SchemaUpdate
)
from .common import EnglishLevel


username_str = constr(min_length=5, max_length=32)
name = constr(max_length=255)


class WordSchemaOut(SchemaOut):
    id: PositiveInt
    text: str
    translation: str
    example: Optional[str]
    level: EnglishLevel
    learned: bool

class WordSchemaFromDB(SchemaFromDB, WordSchemaOut):
    created_at: datetime

class WordSchemaToDB(SchemaToDB):
    text: str
    translation: str
    example: Optional[str] = None
    level: EnglishLevel

class WordSchemaUpdate(SchemaUpdate):
    text: Optional[str] = None
    translation: Optional[str] = None
    example: Optional[str] = None
    level: Optional[EnglishLevel] = None
    learned: Optional[bool] = None