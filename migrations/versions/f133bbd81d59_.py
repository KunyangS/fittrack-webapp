"""Share entity for data sharing

Revision ID: f133bbd81d59
Revises: cb9f0f66864b
Create Date: 2025-05-07 01:03:35.928131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f133bbd81d59'
down_revision = 'cb9f0f66864b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('share_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sharer_user_id', sa.Integer(), nullable=False),
    sa.Column('sharee_user_id', sa.Integer(), nullable=False),
    sa.Column('data_categories', sa.String(length=512), nullable=False),
    sa.Column('time_range', sa.String(length=64), nullable=False),
    sa.Column('shared_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['sharee_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sharer_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sharer_user_id', 'sharee_user_id', 'data_categories', 'time_range', name='_sharer_sharee_data_time_uc')
    )


def downgrade():
    op.drop_table('share_entries')
