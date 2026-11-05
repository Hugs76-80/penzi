"""create users table

Revision ID: fd08062da1b5
Revises: 
Create Date: 2026-11-04 12:32:49.780835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd08062da1b5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('county', sa.String(length=50), nullable=True),
    sa.Column('town', sa.String(length=50), nullable=True),
    sa.Column('education', sa.String(length=50), nullable=True),
    sa.Column('profession', sa.String(length=50), nullable=True),
    sa.Column('marital_status', sa.String(length=30), nullable=True),
    sa.Column('religion', sa.String(length=30), nullable=True),
    sa.Column('ethnicity', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('registration_stage', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_table('users')
    
