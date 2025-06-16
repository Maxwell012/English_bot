from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    BIGINT,
    ForeignKey,
    TIMESTAMP,
    Integer,
    Boolean,
    Float
)

from src.database.database import metadata

flashcard = Table(
    "flashcard",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BIGINT, ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    Column("word_id", Integer, ForeignKey("word.id", ondelete="CASCADE"), nullable=False),
    Column("interval", Integer, nullable=False, default=1),  # days till next review
    Column("hardness", Float, nullable=False, default=2.5),  # ease factor
    Column("repetitions", Integer, nullable=False, default=0),
    Column("next_review", TIMESTAMP, nullable=False),
    Column("learned", Boolean, nullable=False, default=False),
    Column("created_at", TIMESTAMP, default=datetime.now),
    Column("updated_at", TIMESTAMP, default=datetime.now, onupdate=datetime.now),
)