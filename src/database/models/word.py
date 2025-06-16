from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    String,
    TIMESTAMP,
    Integer
)

from src.database.database import metadata

word = Table(
    "word",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("text", String(128), unique=True, nullable=False),
    Column("translation", String(256), nullable=False),
    Column("example", String(512), nullable=True),
    Column("level", String(2), nullable=False),  # A1, A2, B1, etc.
    Column("created_at", TIMESTAMP, default=datetime.now),
)