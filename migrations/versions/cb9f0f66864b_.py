"""Food and fitness entities created for energy consumption and recording

Revision ID: cb9f0f66864b
Revises: 0605d081380a
Create Date: 2025-05-01 16:10:24.558147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb9f0f66864b'
down_revision = '0605d081380a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('fitness_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('activity_type', sa.String(length=64), nullable=True),
    sa.Column('duration', sa.Float(), nullable=True),
    sa.Column('calories_burned', sa.Float(), nullable=True),
    sa.Column('emotion', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('food_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('food_name', sa.String(length=64), nullable=True),
    sa.Column('quantity', sa.Float(), nullable=True),
    sa.Column('calories', sa.Float(), nullable=True),
    sa.Column('meal_type', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('food_entries')
    op.drop_table('fitness_entries')
