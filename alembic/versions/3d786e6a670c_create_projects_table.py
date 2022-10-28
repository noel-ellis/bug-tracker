"""create projects table

Revision ID: 3d786e6a670c
Revises: b6c728832da4
Create Date: 2022-10-20 11:50:10.496615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d786e6a670c'
down_revision = 'b6c728832da4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('projects',
                    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
                    sa.Column('name', sa.String, nullable=False),
                    sa.Column('description', sa.String, nullable=False),
                    sa.Column('start', sa.Date),
                    sa.Column('deadline', sa.Date),
                    sa.Column('status', sa.String, server_default='ongoing', nullable = False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('creator_id', sa.Integer, nullable=False),
                    )
    op.create_foreign_key('projects_users_fk', source_table='projects', referent_table='users', 
                        local_cols=['creator_id'], remote_cols=['id'], ondelete="CASCADE")

def downgrade() -> None:
    op.drop_constraint('projects_users_fk', table_name='projects')
    op.drop_table('projects')
    pass
