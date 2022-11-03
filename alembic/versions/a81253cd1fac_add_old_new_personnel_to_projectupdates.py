"""add old/new personnel to ProjectUpdates

Revision ID: a81253cd1fac
Revises: 1f78c72c1670
Create Date: 2022-11-03 15:54:16.324957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a81253cd1fac'
down_revision = '1f78c72c1670'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('project_updates', sa.Column('personnel_change', sa.String))
    pass


def downgrade() -> None:
    op.drop_column('project_updates', 'personnel_change')
    pass
