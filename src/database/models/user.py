from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    BIGINT,
    String,
    TIMESTAMP,
    Integer
)

from src.database.schemas.user import UserStatusSchema
from src.database.database import metadata


user = Table(
    "user",
    metadata,
    Column("id", BIGINT, unique=True, nullable=False),
    Column("username", String(32), unique=True, nullable=True),
    Column("first_name", String(255), nullable=True),
    Column("last_name", String(255), nullable=True),
    Column("full_name", String(255), nullable=True),
    Column("language", String(2), nullable=True),
    Column("english_level", String(2), nullable=True),
    Column("notifications_per_day", Integer, nullable=True),
    Column("status", String(7), nullable=False, default=UserStatusSchema.ACTIVE),

    Column("created_at", TIMESTAMP, default=datetime.now),
    Column("updated_at", TIMESTAMP, onupdate=datetime.now, default=datetime.now)
)
