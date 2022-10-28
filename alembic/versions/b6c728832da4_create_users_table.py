"""create users table

Revision ID: b6c728832da4
Revises: 9f749bcf4fbb
Create Date: 2022-10-20 11:19:51.749288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6c728832da4'
down_revision = '9f749bcf4fbb'
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
