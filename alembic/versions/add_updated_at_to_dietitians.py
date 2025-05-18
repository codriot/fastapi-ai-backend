"""add updated_at to dietitians

Revision ID: add_updated_at_to_dietitians
Revises: 0e9f47ae628b
Create Date: 2024-03-19 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'add_updated_at_to_dietitians'
down_revision: Union[str, None] = '0e9f47ae628b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Diyetisyenler tablosuna updated_at sütunu ekle
    op.add_column('dietitians', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Mevcut kayıtlar için updated_at değerini created_at ile aynı yap
    op.execute("UPDATE dietitians SET updated_at = created_at")
    
    # Sütunu NOT NULL yap
    op.alter_column('dietitians', 'updated_at', nullable=False)

def downgrade() -> None:
    # updated_at sütununu kaldır
    op.drop_column('dietitians', 'updated_at') 