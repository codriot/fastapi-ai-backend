"""update user and message models

Revision ID: 0e9f47ae628b
Revises: 
Create Date: 2024-03-19 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0e9f47ae628b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Önce bağımlı tabloları sil
    op.execute("DROP TABLE IF EXISTS post_likes CASCADE")
    op.execute("DROP TABLE IF EXISTS post_saves CASCADE")
    op.execute("DROP TABLE IF EXISTS post_comments CASCADE")
    op.execute("DROP TABLE IF EXISTS posts CASCADE")
    
    # Diğer tabloları oluştur
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('auth_provider', sa.String(), nullable=True),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    
    op.create_table(
        'dietitians',
        sa.Column('dietitian_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('auth_provider', sa.String(), nullable=True),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('dietitian_id'),
        sa.UniqueConstraint('email')
    )
    
    op.create_table(
        'messages',
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )

def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('dietitians')
    op.drop_table('users') 