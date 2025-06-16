from datetime import datetime
from pydantic import PositiveInt, constr
from enum import Enum
from typing import Optional

from .base_schemas import (
    SchemaOut,
    SchemaToDB,
    SchemaFromDB,
    SchemaUpdate
)
from .common import Languages
from .common import EnglishLevel


username_str = constr(min_length=5, max_length=32)
name = constr(max_length=255)


class UserStatusSchema(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class UserSchemaOut(SchemaOut):
    id: PositiveInt
    username: Optional[username_str]
    full_name: Optional[name]
    language: Optional[Languages]
    english_level: Optional[EnglishLevel]
    notifications_per_day: Optional[int]


class UserSchemaFromDB(SchemaFromDB, UserSchemaOut):
    first_name: Optional[name]
    last_name: Optional[name]
    status: UserStatusSchema

    created_at: datetime
    updated_at: datetime


class UserSchemaToDB(SchemaToDB):
    id: PositiveInt
    username: Optional[username_str] = None
    first_name: Optional[name] = None
    last_name: Optional[name] = None
    full_name: Optional[name] = None
    language: Optional[Languages] = None
    english_level: Optional[EnglishLevel] = None
    notifications_per_day: Optional[int] = None
    status: UserStatusSchema = UserStatusSchema.ACTIVE


class UserSchemaUpdate(SchemaUpdate):
    username: Optional[username_str] = None
    first_name: Optional[name] = None
    last_name: Optional[name] = None
    full_name: Optional[name] = None
    language: Optional[Languages] = None
    english_level: Optional[EnglishLevel] = None
    notifications_per_day: Optional[int] = None
    status: Optional[UserStatusSchema] = None
