# DELETE THIS

"""create users table

Revision ID: 9f749bcf4fbb
Revises: 
Create Date: 2022-10-04 13:38:38.001885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f749bcf4fbb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('username', sa.String(), nullable=False, unique=True),
                    sa.Column('email', sa.String, nullable=False, unique=True),
                    sa.Column('password', sa.String, nullable=False),
                    sa.Column('name', sa.String),
                    sa.Column('surname', sa.String),
                    sa.Column('access', sa.String, server_default='user', nullable = False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
                    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
