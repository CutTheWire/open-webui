"""add character_chat table

Revision ID: 8926d85a3658
Revises: 461111b60977
Create Date: 2026-06-27 07:40:41.036565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '8926d85a3658'
down_revision: Union[str, None] = '461111b60977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'character_chat',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('author', sa.Text(), nullable=False),
        sa.Column('views', sa.Text(), server_default='0', nullable=True),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('imageUrl', sa.Text(), nullable=False),
        sa.Column('gender', sa.Text(), server_default='', nullable=True),
        sa.Column('age', sa.Text(), server_default='', nullable=True),
        sa.Column('details', sa.Text(), server_default='', nullable=True),
        sa.Column('prompt', sa.Text(), server_default='', nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('character_chat')
