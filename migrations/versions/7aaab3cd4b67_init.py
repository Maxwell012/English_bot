"""init

Revision ID: 7aaab3cd4b67
Revises: 
Create Date: 2025-03-04 13:51:26.988570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aaab3cd4b67'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('english_level', sa.String(length=2), nullable=True),
    sa.Column('notifications_per_day', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=7), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
